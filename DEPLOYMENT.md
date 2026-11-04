# Deployment and live verification

The contract has no privileged configuration and no constructor owner override. Deploy one instance for each shipment. The deploying wallet must be a participant in the immutable route.

## Studio

1. Open https://studio.genlayer.com and load `contracts/handover_iq.py`.
2. Select a test wallet belonging to your route. Fund it with the built-in test faucet.
3. Paste your terms as the constructor's single `terms_json` string. Example format: `fixtures/live-terms.json`, with your own wallet addresses.
4. Deploy with normal validator consensus, not leader-only execution.
5. Confirm FINALIZED **and successful execution**, then save the contract address and transaction link. Finalization alone can finalize a failed execution.
6. Execute the workflow in README with each participant's wallet. Query `get_terms`, `get_state`, and `get_receipt` after finalization.

## Reproducible live synthetic demo

```bash
pip install -r requirements-dev.txt
python scripts/studionet_demo.py
```

This script creates three disposable test wallets in ignored `.demo-accounts.json` with file permissions 0600. It requests synthetic test tokens from Studionet's simulator faucet. It never imports existing user keys, uses mainnet, transfers user assets or publishes private keys.

The checked-in `docs/deployment.json` describes our existing demonstration, and its wallet credentials are intentionally not published. To run your own **new** demo, use a fresh copy without `docs/deployment.json`; the script refuses to impersonate the published wallets. Remove any old `.demo-accounts.json` only if you deliberately want new demo identities. Keep your private local wallet file while resuming a run. This demonstration file is not a production wallet backup.

The script immediately records submitted hashes in `docs/deployment.json`, then polls that same transaction to FINALIZED and verifies SUCCESS. Resume after a polling timeout by running the same script. Never delete a pending manifest to retry. A crash during the broadcast-before-checkpoint window requires manual nonce/chain-history reconciliation before sending again.

The demo performs deployment, two terms acceptances, two handovers, two countersignatures, three closures and one evaluation: eleven consensus transactions. It saves public state and receipt exports, including the outcome actually returned. Reads are separate from those eleven transactions. No AI output or validator response is mocked in this live script.

## Runtime compatibility

The Python runner is pinned in the source header. `genvm-lint check` and `genvm-lint schema` validate it against the downloaded SDK. A newer available runner is an informational notice; it is not silently substituted. Tests use genlayer-test 0.29.2 and the live helper uses genlayer-py 0.16.3 with the explicit `studionet` chain preset. Do not point it at Studio-dev/Bradbury without adapting the SDK/fee policy and network definition.

Fee-free Studionet simulator funding and stable SDK compatibility are assumptions of this helper. Paid networks require fee profiling, appropriate caps and separate operational review. This is not a mainnet deployment guide.

## Public deployment evidence

The final address, source hash, transaction hashes, successful execution checks and live outcome are in `docs/deployment.json`. `docs/live-state.json` and `docs/live-receipts.json` contain the resulting public state and assessment. See the deployment evidence section in README for the readable links and actual result.
