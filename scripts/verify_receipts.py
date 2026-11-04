"""Verify exported receipt hashes; does not prove chain origin."""
import hashlib
import json
import sys
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def verify(receipts):
    if not isinstance(receipts, list) or not 1 <= len(receipts) <= 3:
        raise ValueError('Expected 1-3 receipts')
    previous = '0' * 64
    for index, raw in enumerate(receipts):
        receipt = json.loads(raw) if isinstance(raw, str) else dict(raw)
        expected = receipt.pop('receipt_hash')
        if sha(receipt) != expected:
            raise ValueError('Receipt hash mismatch')
        if receipt['previous_hash'] != previous or receipt['attempt'] != index + 1:
            raise ValueError('Broken receipt sequence')
        if receipt['decision_hash'] != sha(receipt['decision']):
            raise ValueError('Decision hash mismatch')
        previous = expected
    return previous


if __name__ == '__main__':
    result = verify(json.loads(Path(sys.argv[1]).read_text()))
    print('Receipt chain verified:', result)
