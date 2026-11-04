import hashlib
import json
from pathlib import Path

import pytest
from gltest.direct import VMContext, create_address, deploy_contract

CONTRACT = Path(__file__).resolve().parents[1] / 'contracts/handover_iq.py'


def addr(value):
    return ("0x" + value.hex()) if isinstance(value, bytes) else str(value).lower()


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


@pytest.fixture
def env():
    vm = VMContext()
    wallets = [create_address(x) for x in ('supplier', 'warehouse', 'customer', 'outsider')]
    terms = {'shipment_id': 'SHIP-2026-0042', 'quantity': 100, 'unit': 'sealed cartons',
             'route': [addr(x) for x in wallets[:3]],
             'requirements': 'All 100 sealed cartons must arrive intact, dry and with matching seal S-0042.'}
    vm.sender = wallets[0]
    with vm.activate():
        c = deploy_contract(CONTRACT, vm, canon(terms))
        for w in wallets[:3]:
            vm.sender = w
            c.accept_terms(json.loads(c.get_terms())['terms_hash'])
        vm.sender = wallets[0]
        yield vm, c, wallets, terms


def document(leg=0, **changes):
    d = {'shipment_id': 'SHIP-2026-0042', 'leg': leg, 'kind': 'HANDOVER', 'quantity': 100,
         'timestamp': 1793746800 + leg * 3600,
         'narrative': 'Shipment SHIP-2026-0042: 100 sealed cartons transferred and received intact and dry. Seal S-0042 matched. No damage or reservations.'}
    return dict(d, **changes)


def add(env, doc=None, countersign=True):
    vm, c, ws, _ = env
    doc = doc or document()
    leg = doc['leg']
    vm.sender = ws[leg]
    doc_id = c.submit_evidence(canon(doc))
    if countersign:
        vm.sender = ws[leg + 1]
        c.attest_evidence(doc_id)
    return doc_id


def close(env):
    vm, c, ws, _ = env
    for w in ws[:3]:
        vm.sender = w
        c.close_submission()


def mock_assessment(env, finding='CLEAR', overrides=None):
    vm, c, _, _ = env
    docs = json.loads(c.get_state())['documents']
    findings = [{'document_id': x['id'], 'finding': finding,
                 'quote': x['document']['narrative'] if finding != 'UNCLEAR' else ''} for x in docs]
    if overrides:
        overrides(findings)
    vm.clear_mocks()
    vm.mock_llm('HANDOVERIQ_ASSESS_V1', canon({'findings': findings}))
    vm.mock_llm('HANDOVERIQ_GROUND_V1', canon({'grounded': True}))
    return findings


def evaluate(env, finding='CLEAR'):
    mock_assessment(env, finding)
    close(env)
    return json.loads(env[1].evaluate())


def complete(env):
    add(env, document(0))
    add(env, document(1))


def test_verified_and_receipt_integrity(env):
    complete(env)
    receipt = evaluate(env)
    assert receipt['decision'] == {'outcome': 'VERIFIED', 'reasons': []}
    assert env[0].run_validator()
    stored = receipt.pop('receipt_hash')
    assert stored == sha(canon(receipt))
    assert receipt['decision_hash'] == sha(canon(receipt['decision']))
    assert json.loads(env[1].get_receipt(0))['receipt_hash'] == stored
    with pytest.raises(Exception, match='terminal'):
        env[1].evaluate()


def test_missing_handover(env):
    add(env)
    assert evaluate(env)['decision']['outcome'] == 'CUSTODY_GAP'


def test_missing_counter_signature(env):
    add(env, countersign=False)
    add(env, document(1))
    assert evaluate(env)['decision']['outcome'] == 'CUSTODY_GAP'


def test_quantity_conflict(env):
    add(env, document(quantity=99))
    add(env, document(1))
    assert evaluate(env)['decision']['outcome'] == 'DISPUTED'


def test_chronology_conflict(env):
    add(env, document(timestamp=1793759999))
    add(env, document(1))
    assert evaluate(env)['decision']['outcome'] == 'DISPUTED'


def test_semantic_damage_conflict(env):
    complete(env)
    add(env, document(kind='DAMAGE', narrative='Inspection SHIP-2026-0042: cartons arrived wet and crushed. Carrier denies accepting undamaged cartons.'))
    assert evaluate(env, 'CONFLICT')['decision']['outcome'] == 'DISPUTED'


def test_semantic_ambiguity(env):
    complete(env)
    assert evaluate(env, 'UNCLEAR')['decision']['outcome'] == 'INCONCLUSIVE'


def test_empty_evidence_and_attempt_bound(env):
    close(env)
    hashes = []
    for i in range(3):
        r = json.loads(env[1].evaluate())
        assert r['decision']['outcome'] == 'INCONCLUSIVE'
        assert r['attempt'] == i + 1
        assert r['previous_hash'] == (hashes[-1] if hashes else '0' * 64)
        hashes.append(r['receipt_hash'])
    with pytest.raises(Exception, match='limit'):
        env[1].evaluate()


@pytest.mark.parametrize('bad', ['oops', '{}', '{"findings":[]}', '{"findings":[],"findings":[]}', '{"findings":NaN}'])
def test_malformed_llm_fails_closed(env, bad):
    complete(env)
    env[0].mock_llm('HANDOVERIQ_ASSESS_V1', bad)
    close(env)
    r = json.loads(env[1].evaluate())
    assert r['decision']['outcome'] == 'INCONCLUSIVE'
    assert env[0].run_validator()


def test_bad_quote_fails_closed(env):
    complete(env)
    mock_assessment(env, overrides=lambda fs: fs[0].update(quote='Fabricated quotation with no source match'))
    close(env)
    assert json.loads(env[1].evaluate())['decision']['outcome'] == 'INCONCLUSIVE'


def test_independent_validator_disagrees(env):
    complete(env)
    evaluate(env)
    mock_assessment(env, 'CONFLICT')
    assert not env[0].run_validator()


def test_validator_rejects_changed_source_quote(env):
    complete(env)
    evaluate(env)
    fs = mock_assessment(env)
    fs[0]['quote'] = 'Fabricated quotation with no source match'
    forged = canon({'ok': True, 'assessment': {'findings': fs}})
    assert not env[0].run_validator(leader_result=forged)


def test_validator_rejects_cherry_picked_grounding(env):
    complete(env)
    evaluate(env)
    env[0].clear_mocks()
    mock_assessment(env)
    # Replace mocks so grounding independently rejects a contextually false excerpt.
    env[0].clear_mocks()
    docs = json.loads(env[1].get_state())['documents']
    fs = [{'document_id': d['id'], 'finding': 'CLEAR', 'quote': d['document']['narrative']} for d in docs]
    env[0].mock_llm('HANDOVERIQ_ASSESS_V1', canon({'findings': fs}))
    env[0].mock_llm('HANDOVERIQ_GROUND_V1', '{"grounded":false}')
    assert not env[0].run_validator()


@pytest.mark.parametrize('forged', ['{}', '{"ok":true}', '{"ok":false,"error":"ASSESSMENT_UNAVAILABLE"}', '{"ok":1,"assessment":{}}'])
def test_validator_rejects_forged_outputs(env, forged):
    complete(env)
    evaluate(env)
    assert not env[0].run_validator(leader_result=forged)


def test_validator_error_result_rejected(env):
    complete(env)
    evaluate(env)
    assert not env[0].run_validator(leader_error=ValueError('failure'))


@pytest.mark.parametrize('change', [{'quantity': True}, {'quantity': -1}, {'timestamp': True}, {'timestamp': 4102444801}, {'leg': -1}, {'leg': 2}, {'kind': 'OTHER'}, {'shipment_id': 'other'}, {'narrative': 'x'}, {'narrative': 'x'*4001}, {'quantity': 1.5}, {'extra': 1}])
def test_invalid_document(env, change):
    with pytest.raises(Exception):
        add(env, document(**change))
    assert json.loads(env[1].get_state())['documents'] == []


def test_unknown_unauthorized_and_duplicate(env):
    vm, c, ws, _ = env
    vm.sender = ws[3]
    for call in (lambda: c.submit_evidence(canon(document())), c.close_submission, c.evaluate,
                 lambda: c.accept_terms(json.loads(c.get_terms())['terms_hash'])):
        with pytest.raises(Exception, match='Unauthorized'):
            call()
    vm.sender = ws[2]
    with pytest.raises(Exception, match="leg's parties"):
        c.submit_evidence(canon(document()))
    doc_id = add(env)
    vm.sender = ws[0]
    with pytest.raises(Exception, match='Duplicate'):
        c.submit_evidence(canon(document()))
    with pytest.raises(Exception, match='Already attested'):
        c.attest_evidence(doc_id)
    with pytest.raises(Exception, match='Unknown'):
        c.attest_evidence('no-document')
    vm.sender = ws[2]
    with pytest.raises(Exception, match="leg's party"):
        c.attest_evidence(doc_id)


def test_submission_and_attestation_freeze(env):
    vm, c, ws, _ = env
    doc_id = add(env, countersign=False)
    vm.sender = ws[1]
    c.close_submission()
    with pytest.raises(Exception, match='closed'):
        c.attest_evidence(doc_id)
    with pytest.raises(Exception, match='closed'):
        c.submit_evidence(canon(document(1)))
    with pytest.raises(Exception, match='Every party'):
        c.evaluate()
    # Another party can still add evidence until its own close.
    vm.sender = ws[0]
    c.submit_evidence(canon(document(kind='INSPECTION')))


def test_wrong_terms_hash(env):
    with pytest.raises(Exception, match='hash mismatch'):
        env[1].accept_terms('0'*64)


def test_leg_limit(env):
    for i in range(4):
        add(env, document(timestamp=1793746800+i))
    with pytest.raises(Exception, match='Leg evidence limit'):
        add(env, document(timestamp=1793746900))


def test_duplicate_json_keys(env):
    raw = canon(document()).replace('"quantity":100', '"quantity":99,"quantity":100')
    with pytest.raises(Exception, match='Invalid JSON'):
        env[1].submit_evidence(raw)


def test_terms_hash_canonical_and_immutable(env):
    _, c, _, terms = env
    assert json.loads(c.get_terms())['terms_hash'] == sha(canon(terms))
    before = c.get_terms()
    complete(env)
    evaluate(env)
    assert before == c.get_terms()


@pytest.mark.parametrize('changes', [{'quantity':True}, {'quantity':0}, {'unit':''}, {'requirements':'short'}, {'extra':0}, {'route':['0x'+'0'*40]*2}, {'route':['invalid','wallet']}, {'route':[]}])
def test_invalid_terms(changes):
    vm = VMContext()
    a, b = create_address('supplier'), create_address('customer')
    vm.sender = a
    terms = {'shipment_id':'X', 'quantity':100, 'unit':'cartons', 'requirements':'All cartons must arrive intact.', 'route':[addr(a),addr(b)]}
    terms.update(changes)
    with vm.activate(), pytest.raises(Exception):
        deploy_contract(CONTRACT, vm, canon(terms))


def test_requires_every_partys_acceptance():
    vm = VMContext()
    a, b = create_address('supplier'), create_address('customer')
    vm.sender = a
    terms = {'shipment_id':'SHIP-2026-0042', 'quantity':100, 'unit':'cartons', 'requirements':'All cartons must arrive intact.', 'route':[addr(a),addr(b)]}
    with vm.activate():
        c = deploy_contract(CONTRACT, vm, canon(terms))
        with pytest.raises(Exception, match='accept terms'):
            c.submit_evidence(canon(document()))
        with pytest.raises(Exception, match='accept terms'):
            c.close_submission()


def test_retry_preserves_first_receipt_and_can_resolve(env):
    complete(env)
    mock_assessment(env, 'UNCLEAR')
    close(env)
    first = env[1].evaluate()
    mock_assessment(env, 'CLEAR')
    second = json.loads(env[1].evaluate())
    assert second['decision']['outcome'] == 'VERIFIED'
    assert second['previous_hash'] == json.loads(first)['receipt_hash']
    assert second['input_hash'] == json.loads(first)['input_hash']
    assert env[1].get_receipt(0) == first
    assert env[0].run_validator()


def test_deterministic_conflict_survives_ai_failure(env):
    add(env, document(quantity=98))
    add(env, document(1))
    env[0].mock_llm('HANDOVERIQ_ASSESS_V1', '{}')
    close(env)
    result = json.loads(env[1].evaluate())
    assert result['decision']['outcome'] == 'DISPUTED'
    assert 'ASSESSMENT_UNAVAILABLE' in result['decision']['reasons']


def test_validator_accepts_different_valid_contextual_quotes(env):
    complete(env)
    evaluate(env)
    mock_assessment(env, overrides=lambda fs: fs[0].update(quote='100 sealed cartons transferred and received intact and dry.'))
    assert env[0].run_validator()


def test_global_document_limit():
    vm = VMContext()
    ws = [create_address('limit-' + str(i)) for i in range(6)]
    terms = {'shipment_id': 'SHIP-2026-0042', 'quantity': 100, 'unit': 'cartons',
             'route': [addr(w) for w in ws], 'requirements': 'All cartons must arrive intact and dry.'}
    vm.sender = ws[0]
    with vm.activate():
        c = deploy_contract(CONTRACT, vm, canon(terms))
        for w in ws:
            vm.sender = w
            c.accept_terms(json.loads(c.get_terms())['terms_hash'])
        for leg in range(4):
            vm.sender = ws[leg]
            for i in range(4):
                c.submit_evidence(canon(document(leg, timestamp=1793746800 + leg * 3600 + i)))
        vm.sender = ws[4]
        with pytest.raises(Exception, match='Evidence limit'):
            c.submit_evidence(canon(document(4)))
