---
type: source
author: "Apple Inc. (Apple Security Research blog)"
date: 2024-06-10
venue: "Apple Security Research blog, security.apple.com (retrieved 2026-10-11)"
url: "https://security.apple.com/blog/private-cloud-compute/"
tags: [source, vendor-blog, privacy, cloud-ai, confidential-computing, attestation, apple, hosted-inference, locality-pillar]
---
# Apple Security 2024 – Private Cloud Compute: A new frontier for AI privacy in the cloud

**Raw file**: `raw/local_inference/Apple Security 2024 - Private Cloud Compute, a new frontier for AI privacy in the cloud_ingested.md`

## Overview
Apple's initial technical overview, published 10 June 2024 before launch, of **Private Cloud Compute (PCC)**: the server system that runs Apple Intelligence requests too complex for the on-device model, using larger foundation models. Apple frames the problem directly: cloud AI "requires unencrypted access to the user's request and accompanying personal data", which "precludes the use of end-to-end encryption". PCC therefore tries to make the privacy guarantees of hosted inference **technically enforceable and externally verifiable** rather than contractual. It uses five requirements: stateless computation, enforceable guarantees, no privileged runtime access, non-targetability and verifiable transparency. They are implemented with custom Apple-silicon servers, a hardened OS, and cryptographic attestation of every software image. The post is a vendor's own description, and many commitments are in the future tense ("When we launch…").

## Key Insights
1. **Why ordinary cloud AI cannot give strong privacy (intro).** Apple names three problems:
   - guarantees are "difficult to verify and enforce": a new service version may add logging, and a TLS-terminating load balancer "may end up logging thousands of user requests wholesale during a troubleshooting session";
   - there is no runtime transparency: a client cannot confirm the server runs unmodified software;
   - privileged administrator access (SSH, break-glass) is hard to limit, and is a target for credential theft.

   By contrast, on-device data "is by definition disaggregated and not subject to any centralized point of attack".
2. **Five core requirements ("Designing Private Cloud Compute").**
   - **Stateless computation:** data used "exclusively for the purpose of fulfilling the user's request", never available "not even to Apple staff, not even during active processing", and not retained "including via logging or for debugging".
   - **Enforceable guarantees:** no reliance on external components such as load balancers.
   - **No privileged runtime access:** no interfaces that let site reliability staff bypass the guarantees.
   - **Non-targetability:** attacking one user should require a broad, detectable compromise.
   - **Verifiable transparency:** researchers "must be able to verify" that production software matches what they inspected.
3. **Node design.** Custom servers with Secure Enclave and Secure Boot, a hardened subset of iOS/macOS, Code Signing with a trust cache loaded by the Secure Enclave (no JIT, no runtime code injection), and an ML stack written in Swift for memory safety. There are **no remote shells, no Developer Mode and no general-purpose logging**; only "pre-specified, structured, and audited logs and metrics can leave the node". Data-volume keys are randomised on every reboot and never persisted (cryptographic erasure).
4. **Request path.** The device encrypts each request directly to the public keys of **attested** PCC nodes. Load balancers and privacy gateways stay outside the trust boundary and cannot decrypt. Each request goes only to a **subset** of nodes, so a single compromised node sees only a small share of traffic.
5. **Non-targetability ("target diffusion").** Request metadata carries no identifying information. Requests are authorised with single-use **RSA Blind Signature** credentials and routed through a third-party **OHTTP relay** that hides the source IP. Hardware is imaged and sealed at manufacturing, revalidated in the data centre under a third-party observer, and certified per node. Devices refuse nodes they cannot validate.
6. **Verifiable transparency.** Apple commits to:
   - publish "software images of every production build of PCC", with measurements in an "append-only and cryptographically tamper-proof transparency log", within 90 days of inclusion in the log;
   - provide a Virtual Research Environment on Apple-silicon Macs;
   - publish part of the security-critical source code and give bounty rewards.

   Devices will send data only to nodes "that can cryptographically attest to running publicly listed software". Apple notes that similar mechanisms exist only in specialised forms (Intel SGX, AWS Nitro attestation).

## Relevance to GroundOne
- **The best case for hosted privacy, and how much it costs.** PCC is probably the strongest published design for private hosted LLM inference. It needed custom server silicon, a purpose-built OS, a cryptographic transparency log, anonymising relays, a hardened supply chain and a bug-bounty programme. This makes the thesis's argument precise: hosted inference *can* be made much more private, but only with infrastructure that ordinary API providers do not offer. Even then, the provider still sees the plaintext request while processing it, which is why Apple needs all the other guarantees. See [[Privacy and Data Sovereignty]].
- **The trust that remains.** PCC moves trust rather than removing it. The user must still trust:
  - Apple's hardware and Secure Enclave, and the manufacturing and validation process;
  - the correctness of the attestation chain and the transparency log;
  - that published images are actually inspected by independent researchers;
  - that the relay operator and the load balancer do not collude (Apple itself names this joint compromise as the case statistical auditing must catch).

  Verification is possible only for researchers with time and tools, not for an individual user. A local verifier like GroundOne needs none of this, because the document never leaves the device. The trusted computing base is the user's own machine and open weights ([[On-Device Inference]], [[Open-Weight Models]]).
- **Apple ranks on-device first.** Apple calls on-device processing "the cornerstone for the security and privacy of user data" and uses PCC only when the device model is not capable enough. That is a vendor endorsement of the thesis's ordering: local when possible, verifiable hosted only when necessary ([[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[Edge-Cloud Collaborative Inference]]).
- **Regulatory angle.** PCC's statelessness and no-retention design matches GDPR principles such as purpose and storage limitation and security (Arts. 5, 25, 32; [[EU 2016 - Regulation (EU) 2016-679, General Data Protection Regulation (GDPR)]]). However, a hosted request is still a transmission to a processor, which local inference avoids altogether.
- **Contrast case.** In the [[Navier-Stokes Credit Dispute (2026)]], a provider could not rule out that de-identified usage data had helped improve its models. PCC is designed so that the provider cannot make such use even if it wanted to. Most hosted services offer only policy statements, not this kind of technical guarantee.

## Links
- Concepts: [[Privacy and Data Sovereignty]], [[On-Device Inference]], [[Edge-Cloud Collaborative Inference]], [[Navier-Stokes Credit Dispute (2026)]], [[Open-Weight Models]], [[Apple Silicon and MLX]]
- Related sources: [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[EU 2016 - Regulation (EU) 2016-679, General Data Protection Regulation (GDPR)]]
