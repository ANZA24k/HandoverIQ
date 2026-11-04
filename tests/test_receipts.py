import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('verify', Path(__file__).parents[1] / 'scripts/verify_receipts.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def receipt():
    r = {'attempt':1, 'previous_hash':'0'*64, 'decision':{'outcome':'INCONCLUSIVE','reasons':[]}}
    r['decision_hash'] = verify.sha(r['decision'])
    r['receipt_hash'] = verify.sha(r)
    return r


def test_verify_export():
    r = receipt()
    assert verify.verify([r]) == r['receipt_hash']


def test_tamper_rejected():
    r = receipt()
    r['decision']['outcome'] = 'VERIFIED'
    with pytest.raises(ValueError, match='hash mismatch'):
        verify.verify([r])


def test_reordered_history_rejected():
    r = receipt()
    r['attempt'] = 2
    r.pop('receipt_hash')
    r['receipt_hash'] = verify.sha(r)
    with pytest.raises(ValueError, match='sequence'):
        verify.verify([r])
