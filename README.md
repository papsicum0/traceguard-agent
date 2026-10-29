# TraceGuard: Autonomous DevSecOps Sentinel & Threat Gatekeeper

TraceGuard is an autonomous DevSecOps audit agent built for modern CI/CD supply chains. It combines static Git commit forensics, external perimeter DNS authentication checks, and automated secret/entropy detection with LLM threat synthesis powered by **Meta Llama 3.1 8B Instruct** hosted on **Modal (NVIDIA A10G)**.

TraceGuard incorporates an active **Mechanistic Interpretability Probe** targeting Layer 16 residual stream activations to verify LLM inference integrity before enforcing security policy gates.

---

## Key Features

- **Autonomous Threat Synthesis**: Evaluates repository commit surfaces and perimeter posture using Meta Llama 3.1 8B Instruct.
- **Layer 16 Interpretability Probe**: Measures hidden-state activation vector norms ($\Vert{}h_{\{16\}}\Vert{}$) to detect anomalous inference behavior or adversarial prompt tampering.
- **Perimeter & DNS Forensics**: Audits SPF, DKIM, and DMARC enforcement across commit author domains to prevent email spoofing attacks.
- **Credential & Secret Scanning**: Regex- and entropy-based heuristics identify exposed access tokens (Modal, GitHub, AWS, private keys) before code promotion.
- **Tamper-Evident Ledger**: Generates canonical JSON audit ledgers validated by SHA-256 integrity digests.
- **CI/CD Policy Gate Enforcement**: Programmatically passes or halts pipeline execution (`--fail-on high`) based on composite CVSS v3.1 risk scores.

---

## Architecture Overview

```text
Local / CI Runner (cli.py)
 ├── 1. Git Forensics (Commit Author Analysis)
 ├── 2. DNS Perimeter Auditing (SPF / DMARC Verification)
 ├── 3. Secret & Credential Scanning
 ├── 4. Modal A10G Cloud Backend
 │    ├── Meta Llama 3.1 8B Instruct
 │    └── Layer 16 Residual Stream Activation Probe
 ├── 5. Threat Assessment & Correlation Matrix
 ├── 6. Tamper-Evident SHA-256 Ledger Export
 └── 7. CI/CD Gate Enforcement (--fail-on [threshold])
