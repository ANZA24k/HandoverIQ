# Security and limitations

## Trust boundaries

The immutable terms are agreed by all route wallets. Only each leg's two endpoints can submit and attest its evidence. A sender cannot reopen its submission window. There is no administrator, upgrade, delegate, withdrawal, settlement, token transfer or liability decision. Deploy a new contract for corrections, revised terms or additional evidence; preserve the original assessment link.

Authentication is GenLayer transaction-wallet attribution and an explicit wallet attestation over a content ID, not verification of handwritten signatures, organizational identity, document issuer credentials or physical custody. Participants can collude, omit evidence or attest false reports. AI consensus does not eliminate this risk. Public data must be reviewed and redacted before submission; do not put private customer information on-chain.

## Consensus and prompt injection

Both leader and validators read all locked terms and evidence, execute independent semantic assessments, validate exact output fields and check verbatim quotations. Validators compare decision-critical per-document findings, then independently judge the leader's quotations against complete source context. Surrounding negation and contradictory evidence are explicitly relevant. All embedded text is labelled untrusted data; instructions embedded in it should be classified UNCLEAR, not obeyed.

Prompt injection remains a model risk. A majority of validators can share the same reasoning error. Literal quote membership alone cannot prove entailment; the independent contextual grounding call is necessary. Tests exercise the validation gates using mocks; they do not certify real-model accuracy or injection immunity.

Malformed AI responses and provider failures become the same bounded ASSESSMENT_UNAVAILABLE category. Validators only agree with it if their own independent assessment also fails. No external error text is persisted. Disagreement is not caught and relabelled as success. Protocol retries/appeals are distinct from the three application evaluation attempts.

## Availability and resource risks

Every participant must voluntarily accept terms and close submissions; an uncooperative wallet can block evaluation forever. This is deliberate unanimous closure, with no deadline, forced close or dispute-resolution authority. A leg endpoint can use its leg's four-document capacity with poor evidence; evidence is append-only. Only register cooperative participants and treat refusal/spam outside this contract's scope.

Bounded input sizes, document counts and attempts constrain application work, but model/token/gas costs are still network-dependent and need profiling before paid deployment. Full evidence lives on-chain and may be expensive. There are no network requests, redirects, SSRF paths or mutable remote evidence; the web-retrieval threat surface is eliminated by the v1 evidence format.

## Report a problem

Open a repository issue with a minimal synthetic reproduction. Never include private keys, shipment secrets or personal data. This project has not received an external security audit and is intended for experimental documentary assessment.
