# HandoverIQ

A standalone GenLayer Intelligent Contract for assessing the documentary custody chain of a shipment. Suppliers, warehouses, carriers and customers lock an ordered wallet route and shipment requirements, attest handover records and obtain an auditable outcome. It does not assign legal liability or prove physical delivery.

**One immutable shipment per deployment. No frontend, backend oracle, token or payout.** GenLayer is central: leader and validator nodes independently review the same submitted evidence using real `gl.nondet.exec_prompt` calls under `gl.vm.run_nondet_unsafe`. Validators compare every document's classification and independently verify the leader's contextual quotations. There is no schema-only consensus or off-chain verdict shortcut.

## Quick start

Requires Python 3.12+.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
genvm-lint check contracts/handover_iq.py
genvm-lint schema contracts/handover_iq.py --output /tmp/abi.json
python scripts/demo.py
```

`demo.py` runs SDK direct-mode scenarios with mocked external AI; it is not evidence of a live consensus run. See [DEPLOYMENT.md](DEPLOYMENT.md) and [EVIDENCE.md](EVIDENCE.md) for live status and verification.

## Workflow

1. A route participant deploys the contract with `terms_json`: shipment ID, positive integer quantity, unit, ordered route of 2–6 distinct wallets, and textual requirements. Creator acceptance is implicit.
2. Every other route wallet calls `accept_terms(expected_hash)` with the hash from `get_terms()`. No evidence can be submitted before unanimous acceptance.
3. An endpoint of a route leg calls `submit_evidence(document_json)`. It records an immutable document and the sender's attestation, returning a SHA-256 document ID. The other endpoint calls `attest_evidence(document_id)` to countersign a handover.
4. Each wallet calls `close_submission()` after reviewing all evidence. Closing is irrevocable for that wallet: it cannot submit or attest again. Others may still submit until they close, so inspect the final state before closing. There is no owner override.
5. Once everyone has closed, any route participant calls `evaluate()`. Read its receipt with `get_receipt(0)`. Up to three attempts are allowed only while the latest outcome is INCONCLUSIVE; prior receipts remain intact.

All evidence is full bounded plaintext submitted in the transaction and retained on-chain. No mutable URLs, PDFs, images, web fetches or hidden extraction services are trusted. If converting a delivery note or inspection report to text, review the transcript before attesting. Wallet authentication proves who submitted/attested those exact bytes, not who authored the original paper document.

## Outcomes and precedence

| Outcome | Rule |
|---|---|
| DISPUTED | Any submitted quantity differs from the locked total, handover timestamps contradict route order, or any documentary finding is CONFLICT. Highest priority. |
| CUSTODY_GAP | Nonempty evidence exists but a route leg has no HANDOVER record or a handover lacks both endpoint attestations. This remains a supported procedural finding even if AI assessment is unavailable. |
| INCONCLUSIVE | No documents, unavailable/invalid AI output, or any UNCLEAR finding without a higher priority discrepancy. |
| VERIFIED | Every leg has handover evidence, every handover has both attestations, deterministic checks pass, and every document is independently classified CLEAR with grounded quotations. |

The model supplies CLEAR, CONFLICT or UNCLEAR per document, never the final outcome. All submitted reports are included; users cannot select a favorable subset at evaluation. There are no partial shipments, quantity tolerances, unit conversions, clock tolerances or split/merged routes in v1. Equal adjacent handover times are allowed. Inspection/damage times are recorded but only HANDOVER times are used for route chronology. Timestamps are participant claims rather than trusted physical event clocks.

## Bounded execution and auditability

- 2–6 route wallets, at most 5 legs; 16 documents total and 4 per leg.
- Terms: 4,096 UTF-8 bytes; requirements: 20–1,500 bytes.
- Document JSON: 6,144 bytes; narrative: 20–4,000 bytes. Strict fields, duplicate JSON keys rejected; integer fields reject booleans.
- Quantity: 1–1,000,000,000 in terms, 0–1,000,000,000 in reports. Unix seconds: 0–4,102,444,800.
- One leader AI assessment; validators independently assess all documents plus run one grounding review. No in-call retry loops.
- Canonical ASCII-escaped JSON with sorted keys and compact separators. Document IDs bind version, terms hash and the complete structured document. Receipts bind the complete input snapshot, derived decision, assessment, attempt and previous receipt hash.
- Consensus disagreement rejects the proposed result and may leave the transaction undetermined with no state changes. An error receipt is appended only when nodes agree on assessment unavailability. Availability errors never produce VERIFIED.

See [SECURITY.md](SECURITY.md), [EVIDENCE.md](EVIDENCE.md), [docs/abi.json](docs/abi.json) and [SUBMISSION.md](SUBMISSION.md).
