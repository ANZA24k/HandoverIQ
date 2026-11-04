"""Local SDK demo with synthetic records and mocked AI, never live consensus."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from test_handover import add, close, document, canon, addr, mock_assessment
from gltest.direct import VMContext, create_address, deploy_contract


def run(scenario):
    vm = VMContext()
    wallets = [create_address(x) for x in ('supplier', 'warehouse', 'customer')]
    terms = {'shipment_id': 'SHIP-2026-0042', 'quantity': 100, 'unit': 'sealed cartons',
             'route': [addr(x) for x in wallets],
             'requirements': 'All 100 sealed cartons must arrive intact, dry and with matching seal S-0042.'}
    vm.sender = wallets[0]
    with vm.activate():
        contract = deploy_contract(ROOT / 'contracts/handover_iq.py', vm, canon(terms), sdk_version="v0.2.16")
        env = (vm, contract, wallets, terms)
        for wallet in wallets:
            vm.sender = wallet
            contract.accept_terms(json.loads(contract.get_terms())['terms_hash'])
        add(env, document(0))
        if scenario != 'gap':
            add(env, document(1))
        finding = 'CLEAR'
        if scenario == 'damage':
            add(env, document(kind='DAMAGE', narrative='Shipment SHIP-2026-0042 arrived with wet and crushed cartons; seal S-0042 was broken.'))
            finding = 'CONFLICT'
        elif scenario == 'unclear':
            finding = 'UNCLEAR'
        mock_assessment(env, finding)
        close(env)
        receipt = json.loads(contract.evaluate())
        assert vm.run_validator()
        return receipt


if __name__ == '__main__':
    for name in ('verified', 'gap', 'damage', 'unclear'):
        r = run(name)
        print(json.dumps({'mode': 'LOCAL_MOCKED_AI', 'scenario': name, 'decision': r['decision'], 'receipt_hash': r['receipt_hash']}))
