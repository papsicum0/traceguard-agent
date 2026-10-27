import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
from traceguard.tools import (
    probe_public_commit_exposure,
    audit_domain_dns_perimeter,
    check_breach_intelligence,
    seal_audit_ledger
)

class TraceGuardAgent:
    def __init__(self, target: str):
        self.target = target
        self.observations: Dict[str, Any] = {}
        self.audit_log: List[str] = []
        
    def log(self, message: str):
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        self.audit_log.append(f"[{timestamp}] {message}")

    async def run_autonomous_audit(self) -> Dict[str, Any]:
        """
        Executes the ReAct agent loop:
        1. Probe public surface.
        2. Analyze findings & dynamically branch into email/domain audits.
        3. Synthesize attack vectors & assign CVSS baseline score.
        4. Cryptographically seal the audit ledger.
        """
        self.log(f"Initiating autonomous perimeter reconnaissance against target: {self.target}")
        
        # --- Step 1: Probe Identity & Git Exposure ---
        self.log("Dispatching Tool: probe_public_commit_exposure")
        git_findings = await probe_public_commit_exposure(self.target)
        self.observations["git_recon"] = git_findings
        
        discovered_emails = git_findings.get("exposed_emails", [])
        self.observations["breaches"] = []
        self.observations["dns_audits"] = []
        
        # --- Step 2: Dynamic Tool Dispatch based on Recon Findings ---
        if discovered_emails:
            self.log(f"Discovered {len(discovered_emails)} exposed developer email(s). Pivoting to identity threat analysis...")
            for email in discovered_emails[:3]:  # Top exposures
                # Tool 2: Darknet Breach Intelligence
                self.log(f"Dispatching Tool: check_breach_intelligence on {email}")
                breach_info = await check_breach_intelligence(email)
                self.observations["breaches"].append(breach_info)
                
                # Tool 3: Domain DNS Perimeter Check
                if "@" in email:
                    domain = email.split("@")[1]
                    self.log(f"Dispatching Tool: audit_domain_dns_perimeter on {domain}")
                    dns_info = audit_domain_dns_perimeter(domain)
                    self.observations["dns_audits"].append(dns_info)
        else:
            # Fallback if no direct emails discovered in recent commits
            self.log("No plaintext emails found in recent commits. Auditing target domain directly if applicable.")
            test_domain = f"{self.target}.com" if not "." in self.target else self.target
            dns_info = audit_domain_dns_perimeter(test_domain)
            self.observations["dns_audits"].append(dns_info)

        # --- Step 3: Adversarial Threat Synthesis ---
        self.log("Synthesizing Adversarial Attack Graph & CVSS exposure...")
        synthesis = self._synthesize_threat_matrix()
        
        # --- Step 4: Cryptographic Ledger Sealing ---
        self.log("Computing SHA-256 canonical cryptographic seal...")
        audit_payload = {
            "target": self.target,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "observations": self.observations,
            "threat_synthesis": synthesis
        }
        
        canonical_seal = seal_audit_ledger(audit_payload)
        audit_payload["cryptographic_seal"] = canonical_seal
        audit_payload["audit_log"] = self.audit_log
        
        return audit_payload

    def _synthesize_threat_matrix(self) -> Dict[str, Any]:
        """
        Synthesizes vulnerabilities into an attack correlation matrix.
        """
        vulnerabilities = []
        cvss_base = 0.0
        
        # Evaluate Git exposures
        exposed_emails = self.observations.get("git_recon", {}).get("exposed_emails", [])
        if exposed_emails:
            cvss_base += 3.5
            vulnerabilities.append({
                "vector": "METADATA_LEAK",
                "severity": "MEDIUM",
                "finding": f"Exposed committer email addresses: {', '.join(exposed_emails)}",
                "remediation": "Configure git user.email to use GitHub private noreply privacy alias."
            })
            
        # Evaluate breach exposure
        for breach in self.observations.get("breaches", []):
            if breach.get("is_breached"):
                cvss_base += 2.5
                vulnerabilities.append({
                    "vector": "CREDENTIAL_REUSE",
                    "severity": "HIGH",
                    "finding": f"Email {breach['email']} compromised in {len(breach['breaches'])} breach dump(s).",
                    "remediation": "Enforce FIDO2/WebAuthn MFA and immediate credential rotation."
                })

        # Evaluate DNS hygiene
        for dns_audit in self.observations.get("dns_audits", []):
            for vuln in dns_audit.get("vulnerabilities", []):
                cvss_base += 1.5 if vuln["severity"] == "HIGH" else 0.8
                vulnerabilities.append({
                    "vector": "PERIMETER_IMPERSONATION",
                    "severity": vuln["severity"],
                    "finding": f"{dns_audit['domain']}: {vuln['issue']} - {vuln['impact']}",
                    "remediation": f"Deploy strict DNS TXT policy for {dns_audit['domain']}."
                })

        final_cvss = min(round(cvss_base, 1), 10.0)
        risk_grade = "CRITICAL" if final_cvss >= 8.0 else "HIGH" if final_cvss >= 6.0 else "MEDIUM" if final_cvss >= 3.5 else "LOW"
        
        return {
            "cvss_score": final_cvss,
            "risk_grade": risk_grade,
            "vulnerabilities": vulnerabilities,
            "attack_chain_summary": (
                "Reconnaissance pivot identified. Adversaries can cross-reference exposed "
                "commit identities with corporate perimeter mail records to stage targeted spear-phishing."
                if vulnerabilities else "No high-severity exposure vectors discovered."
            )
        }
