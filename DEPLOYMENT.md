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

The Python runner is pinned in the source header. Direct tests explicitly select GenVM v0.2.16, and CI sets GENVM_VERSION=v0.2.16 for the linter; this avoids a broken latest-release artifact URL and keeps cold-cache runs reproducible. Set `export GENVM_VERSION=v0.2.16` for local lint/schema/type checks. `genvm-lint check` and `genvm-lint schema` validate it against the downloaded SDK. A newer available runner is an informational notice; it is not silently substituted. Tests use genlayer-test 0.29.2 and the live helper uses genlayer-py 0.16.3 with the explicit `studionet` chain preset. Do not point it at Studio-dev/Bradbury without adapting the SDK/fee policy and network definition.

Fee-free Studionet simulator funding and stable SDK compatibility are assumptions of this helper. Paid networks require fee profiling, appropriate caps and separate operational review. This is not a mainnet deployment guide.

## Public deployment evidence

The final address, source hash, transaction hashes, successful execution checks and live outcome are in `docs/deployment.json`. `docs/live-state.json` and `docs/live-receipts.json` contain the resulting public state and assessment. See the deployment evidence section in README for the readable links and actual result.

## Completed Studionet run

Contract: [0x67c12C61b4e0D8bA814b1BbF6038dcb42BbbA2f6](https://explorer-studio.genlayer.com/address/0x67c12C61b4e0D8bA814b1BbF6038dcb42BbbA2f6). Synthetic data only.

Outcome: **VERIFIED**, with `assessment.ok=true`, two independently validated CLEAR findings and grounded quotations. All eleven transactions below finalized with successful GenVM execution. No external AI responses were mocked. The adverse outcomes are covered by local tests with mocked AI; they have not all been exercised on a live network.

| Step | Finalized transaction |
|---|---|
| deploy | [0x0dae2c79629ac52986da6bdca769ca5062ab1f5459ca6237ef8fb59e4c4c5c94](https://explorer-studio.genlayer.com/tx/0x0dae2c79629ac52986da6bdca769ca5062ab1f5459ca6237ef8fb59e4c4c5c94) |
| warehouse_accepts | [0xccb2126aaf97c6b4cc47fd6b0f708dbd730c936cb9abdce973e97262905382ae](https://explorer-studio.genlayer.com/tx/0xccb2126aaf97c6b4cc47fd6b0f708dbd730c936cb9abdce973e97262905382ae) |
| customer_accepts | [0x5d484ed9fca0d1766a5359995c3ea8693937615d265f60ae33c915cf9370102f](https://explorer-studio.genlayer.com/tx/0x5d484ed9fca0d1766a5359995c3ea8693937615d265f60ae33c915cf9370102f) |
| submit_leg_0 | [0x2f4177a733bfbd7cb8447c3387210d86868207f5325d109a82549e1f0731b915](https://explorer-studio.genlayer.com/tx/0x2f4177a733bfbd7cb8447c3387210d86868207f5325d109a82549e1f0731b915) |
| countersign_leg_0 | [0xcdbf0e9b5584805aae079becd8d9669679f989cedd037a335984575a2900467a](https://explorer-studio.genlayer.com/tx/0xcdbf0e9b5584805aae079becd8d9669679f989cedd037a335984575a2900467a) |
| submit_leg_1 | [0xc5e293cd8cf87aec821be8e8dfb66dd0cb5b4960f2d115d8289945cf1f08ee31](https://explorer-studio.genlayer.com/tx/0xc5e293cd8cf87aec821be8e8dfb66dd0cb5b4960f2d115d8289945cf1f08ee31) |
| countersign_leg_1 | [0x83c5cca63495dfb0dbce54f85febd27a5d0b0301ca05083a909b3a0f1eb7961a](https://explorer-studio.genlayer.com/tx/0x83c5cca63495dfb0dbce54f85febd27a5d0b0301ca05083a909b3a0f1eb7961a) |
| close_0 | [0x1ba6306e20b3e615b41adb570fc8db0f4dcaebd9671a2886c98946b922b6f228](https://explorer-studio.genlayer.com/tx/0x1ba6306e20b3e615b41adb570fc8db0f4dcaebd9671a2886c98946b922b6f228) |
| close_1 | [0x4cfef0b838eca7424981196e934dfed5d4fb7bb446c2adbe8209e47bde418a1c](https://explorer-studio.genlayer.com/tx/0x4cfef0b838eca7424981196e934dfed5d4fb7bb446c2adbe8209e47bde418a1c) |
| close_2 | [0x1273d94e963522b92d5e599478d85ea8215dcd7b4d84796108050b6806f9574a](https://explorer-studio.genlayer.com/tx/0x1273d94e963522b92d5e599478d85ea8215dcd7b4d84796108050b6806f9574a) |
| evaluate | [0x4cfdd2a69e734250c5ed2326e5596485804c0f45e60c5de659c8c20e67541116](https://explorer-studio.genlayer.com/tx/0x4cfdd2a69e734250c5ed2326e5596485804c0f45e60c5de659c8c20e67541116) |
