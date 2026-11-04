# Intelligent Contracts submission

## Title

HandoverIQ — Supply Chain Custody Verification

## Description

HandoverIQ is a standalone GenLayer Intelligent Contract for shipment custody assessment. Route participants accept immutable shipment terms, submit content-hashed delivery/inspection/damage records and countersign handovers with their wallets. GenLayer leaders and validators independently assess every document, compare semantic findings and verify contextual quotations. Deterministic rules check shipment IDs, quantities, route coverage, countersignatures and chronological consistency. Outcomes: VERIFIED, CUSTODY_GAP, DISPUTED and INCONCLUSIVE. Includes strict schemas, bounded evaluation attempts, prompt-injection defenses, append-only hash-linked receipts, synthetic fixtures, 56 passing SDK direct-mode tests and GenVM lint/schema/type validation. This is documentary assessment, not proof of physical delivery or legal liability. Live on Studionet: 11 finalized successful transactions; real AI assessment returned VERIFIED. See DEPLOYMENT.md and docs/deployment.json.

## Evidence links

- Repository: https://github.com/ANZA24k/HandoverIQ
- Contract source: https://github.com/ANZA24k/HandoverIQ/blob/main/contracts/handover_iq.py
- Explorer contract: https://explorer-studio.genlayer.com/address/0x67c12C61b4e0D8bA814b1BbF6038dcb42BbbA2f6
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0x0dae2c79629ac52986da6bdca769ca5062ab1f5459ca6237ef8fb59e4c4c5c94
- Live evidence: https://github.com/ANZA24k/HandoverIQ/blob/main/docs/deployment.json
- Tests: https://github.com/ANZA24k/HandoverIQ/blob/main/tests/test_handover.py
- CI: https://github.com/ANZA24k/HandoverIQ/actions

Category: Intelligent Contracts (standalone primitive). All live fixture data is synthetic. Local tests mock external AI and explicitly exercise validator logic; they are not a live model accuracy benchmark.
