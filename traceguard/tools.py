import json
import hashlib
import httpx
import dns.resolver
from typing import Dict, Any, List

# ---------------------------------------------------------
# Tool 1: Inspect Public Git Commits for Leaked Metadata
# ---------------------------------------------------------
async def probe_public_commit_exposure(username: str) -> Dict[str, Any]:
    """
    Queries public GitHub activity events to discover exposed committer names,
    author emails, and repository touchpoints.
    """
    url = f"https://api.github.com/users/{username}/events/public"
    headers = {"User-Agent": "TraceGuard-Security-Agent/1.0"}
    
    findings = {
        "target": username,
        "exposed_emails": [],
        "exposed_names": [],
        "active_repositories": [],
        "commit_count_scanned": 0,
        "error": None
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                findings["error"] = f"GitHub user '{username}' not found."
                return findings
            elif resp.status_code != 200:
                findings["error"] = f"GitHub API returned status {resp.status_code}."
                return findings
            
            events = resp.json()
            for event in events:
                if event.get("type") == "PushEvent":
                    repo_name = event.get("repo", {}).get("name", "")
                    if repo_name and repo_name not in findings["active_repositories"]:
                        findings["active_repositories"].append(repo_name)
                    
                    commits = event.get("payload", {}).get("commits", [])
                    for commit in commits:
                        findings["commit_count_scanned"] += 1
                        author = commit.get("author", {})
                        email = author.get("email", "")
                        name = author.get("name", "")
                        
                        # Filter out GitHub noreply privacy aliases
                        if email and "noreply.github.com" not in email:
                            if email not in findings["exposed_emails"]:
                                findings["exposed_emails"].append(email)
                        if name and name not in findings["exposed_names"]:
                            findings["exposed_names"].append(name)
                            
        except Exception as exc:
            findings["error"] = f"Network probe failed: {str(exc)}"
            
    return findings


# ---------------------------------------------------------
# Tool 2: Audit Domain DNS Perimeter (SPF / DMARC Hygiene)
# ---------------------------------------------------------
def audit_domain_dns_perimeter(domain: str) -> Dict[str, Any]:
    """
    Inspects DNS TXT records of an email domain to verify email spoofing defenses
    (SPF and DMARC enforcement).
    """
    audit = {
        "domain": domain,
        "has_spf": False,
        "spf_record": None,
        "has_dmarc": False,
        "dmarc_record": None,
        "vulnerabilities": []
    }
    
    resolver = dns.resolver.Resolver()
    resolver.timeout = 5.0
    resolver.lifetime = 5.0

    # 1. Audit SPF
    try:
        answers = resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt_str = rdata.to_text().strip('"')
            if txt_str.startswith("v=spf1"):
                audit["has_spf"] = True
                audit["spf_record"] = txt_str
                break
    except Exception:
        audit["has_spf"] = False

    if not audit["has_spf"]:
        audit["vulnerabilities"].append({
            "severity": "HIGH",
            "issue": "Missing SPF Record",
            "impact": f"Attackers can forge emails directly pretending to be @{domain}."
        })

    # 2. Audit DMARC
    dmarc_domain = f"_dmarc.{domain}"
    try:
        answers = resolver.resolve(dmarc_domain, "TXT")
        for rdata in answers:
            txt_str = rdata.to_text().strip('"')
            if txt_str.startswith("v=DMARC1"):
                audit["has_dmarc"] = True
                audit["dmarc_record"] = txt_str
                if "p=none" in txt_str:
                    audit["vulnerabilities"].append({
                        "severity": "MEDIUM",
                        "issue": "DMARC Policy is set to 'none'",
                        "impact": "Domain monitoring is enabled, but forged emails are not rejected."
                    })
                break
    except Exception:
        audit["has_dmarc"] = False

    if not audit["has_dmarc"]:
        audit["vulnerabilities"].append({
            "severity": "HIGH",
            "issue": "Missing DMARC Record",
            "impact": f"Mail providers cannot verify authenticity for {domain}, enabling CEO spoofing/phishing."
        })

    return audit


# ---------------------------------------------------------
# Tool 3: Query Darknet & Historical Breach Intelligence
# ---------------------------------------------------------
async def check_breach_intelligence(email: str) -> Dict[str, Any]:
    """
    Checks public breach intelligence indices (XposedOrNot) for compromised
    historical passwords or credentials associated with an exposed email.
    """
    url = f"https://api.xposedornot.com/v1/check-email/{email}"
    findings = {
        "email": email,
        "is_breached": False,
        "breaches": [],
        "risk_level": "LOW"
    }
    
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                breach_list = data.get("breaches", [[]])[0] if data.get("breaches") else []
                if breach_list:
                    findings["is_breached"] = True
                    findings["breaches"] = breach_list
                    findings["risk_level"] = "CRITICAL" if len(breach_list) >= 3 else "HIGH"
        except Exception:
            # Fallback if rate-limited or offline
            pass
            
    return findings


# ---------------------------------------------------------
# Tool 4: Cryptographic SHA-256 Audit Ledger Sealing
# ---------------------------------------------------------
def seal_audit_ledger(audit_payload: Dict[str, Any]) -> str:
    """
    Generates a deterministic canonical SHA-256 digest over the full audit
    findings. Any modification to findings invalidates this seal.
    """
    canonical_json = json.dumps(audit_payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
