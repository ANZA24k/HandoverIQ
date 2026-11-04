# Evidence format and reproducibility

The contract accepts authenticated on-chain text records, not external URLs. Submitted JSON is parsed under a closed schema and normalized to sorted, compact, ASCII-escaped JSON. Raw whitespace/key-order differences do not produce different IDs. Every material field, including the original narrative text, is covered by the document ID. Normalization is not Unicode equivalence normalization: different Unicode strings produce different hashes.

## Terms

```json
{
  "shipment_id": "SHIP-2026-0042",
  "quantity": 100,
  "unit": "sealed cartons",
  "route": ["0x1111111111111111111111111111111111111111", "0x2222222222222222222222222222222222222222"],
  "requirements": "All 100 sealed cartons must arrive intact and dry, with seal S-0042 matching."
}
```

Example wallets are placeholders, not controlled production identities. Replace them before deployment. The creator must be one of the route wallets.

## Document

```json
{
  "shipment_id": "SHIP-2026-0042",
  "leg": 0,
  "kind": "HANDOVER",
  "quantity": 100,
  "timestamp": 1793746800,
  "narrative": "Shipment SHIP-2026-0042: 100 sealed cartons transferred and received intact and dry. Seal S-0042 matched. No damage or reservations."
}
```

`leg=0` connects route wallets 0 and 1. Kinds are HANDOVER, INSPECTION and DAMAGE. A handover must receive both endpoint attestations. Each submission is attributed to its transaction sender; an attestation records that wallet's endorsement of the entire content ID. Paper-signature verification and issuer credential registries are outside v1.

## Hashes

`C(x) = json.dumps(x, sort_keys=True, separators=(",",":"), ensure_ascii=True)` and `H(s) = SHA256(UTF8(s))`.

- `terms_hash = H(C(normalized_terms))`
- `document_id = H(C({version, terms_hash, document}))`
- `input_hash = H(C({terms_hash, documents, attestations}))`; documents include ID and submitter in submission order, attestations are sorted wallet lists.
- `decision_hash = H(C(decision))`
- `receipt_hash = H(C(receipt without receipt_hash))`
- First `previous_hash` is 64 zeroes; subsequent receipts reference the last receipt's hash.

Use `python scripts/verify_receipts.py receipts.json` to recompute receipt and decision hashes and verify the sequence. Export a JSON array of the strings/objects returned by `get_receipt(index)`. Hash verification detects edits but alone does not establish that a receipt came from the chain: separately verify the deployed code, contract address, transaction success and finalized state.

## Validation evidence

`tests/test_handover.py` runs SDK direct-mode tests, with real contract storage/ABI behavior and mocked external AI. It explicitly invokes captured validator functions for agreement, independent disagreement, forged proposals, missing quote grounding and error results. This does not simulate validator selection, protocol rotations or live AI provider behavior.

Synthetic fixture scenarios are in `fixtures/scenarios.json`. The damage and injection examples must not be represented as real shipment reports. Live deployment status and transaction references, if available, are recorded in DEPLOYMENT.md and docs/deployment.json; local mock receipts are labelled as such.
