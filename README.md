<div align="center">

# 🛡️ TraceGuard

**Autonomous DevSecOps & Attack Surface Intelligence Agent**  
*Built for the Meta AI Developer Hackathon 2026*

[![Meta Llama 3](https://img.shields.io/badge/Model-Meta%20Llama%203-blue.svg)](https://ai.meta.com/)
[![Modal Serverless](https://img.shields.io/badge/Compute-Modal%20Serverless-green.svg)](https://modal.com/)
[![Integrity](https://img.shields.io/badge/Audit%20Ledger-SHA--256%20Sealed-brightgreen.svg)](#cryptographic-audit-ledger)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📌 Overview

**TraceGuard** is an autonomous DevSecOps agent engineered to detect, correlate, and remediate identity-driven attack vectors across modern developer supply chains. 

Adversaries routinely leverage public Git commit telemetry (names, internal emails, commit patterns) and correlate them with loose perimeter DNS hygiene (missing SPF/DMARC policies) to execute targeted credential stuffing and spear-phishing campaigns. TraceGuard eliminates this blind spot by running an autonomous ReAct reasoning loop that:

1. **Probes Public Git Surface:** Uncovers developer identities, non-corporate author metadata, and repository footprints.
2. **Audits Perimeter DNS Hygiene:** Queries DNS TXT infrastructure for SPF/DMARC spoofing vectors.
3. **Pivots to Darknet Threat Intelligence:** Cross-references exposed identities against public breach corpora.
4. **Synthesizes CVSS Exposure:** Calculates an actionable threat graph with structured remediation patches.
5. **Cryptographically Seals Proof-of-Audit:** Compiles every finding into a canonical SHA-256 tamper-evident receipt.

---

## 🏗️ Architecture

[ Target Input ]
│
[ Sanitizer / Regex ]
│
┌──────────────┴──────────────┐
▼                             ▼
[ GitHub Metadata ]           [ DNS TXT Resolver ]
│                             │
└──────────────┬──────────────┘
▼
[ Threat Intelligence ]
│
▼
┌───────────────────────────────────┐
│   TraceGuard Autonomous Agent     │
│   (Meta Llama 3 Reasoning Engine) │
└─────────────────┬─────────────────┘
▼
┌───────────────────────────────────┐
│    Cryptographic Ledger Sealer    │
│    (Canonical SHA-256 Digest)     │
└─────────────────┬─────────────────┘
▼
[ Colorized CLI / Tamper-Evident JSON ]

---

## ⚡ Quick Start

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/priyanshujha12/traceguard-agent.git
cd traceguard-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
