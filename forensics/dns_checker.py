import dns.resolver
import dns.exception

PUBLIC_WEBMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "ymail.com",
    "hotmail.com", "outlook.com", "live.com", "msn.com",
    "icloud.com", "me.com", "mac.com",
    "proton.me", "protonmail.com", "zoho.com", "aol.com"
}

def analyze_author_domain(email: str) -> dict:
    if not email or "@" not in email:
        return {
            "auditable": False,
            "domain": None,
            "spf": "invalid",
            "dmarc": "invalid",
            "reason": "Malformed or missing email address."
        }

    domain = email.split("@")[-1].strip().lower()

    if "noreply.github.com" in domain:
        return {
            "auditable": False,
            "domain": domain,
            "spf": "skipped",
            "dmarc": "skipped",
            "reason": "GitHub privacy/noreply address detected."
        }

    if domain in PUBLIC_WEBMAIL_DOMAINS:
        return {
            "auditable": False,
            "domain": domain,
            "spf": "present",
            "dmarc": "present",
            "status": "managed",
            "reason": "Verified public webmail provider (SPF/DMARC enforced at provider perimeter)."
        }

    resolver = dns.resolver.Resolver()
    resolver.timeout = 3.0
    resolver.lifetime = 3.0

    spf_status = "missing"
    spf_record = None
    try:
        answers = resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt_str = rdata.to_text().strip('"')
            if txt_str.startswith("v=spf1"):
                spf_status = "present"
                spf_record = txt_str
                break
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
            dns.resolver.NoNameservers, dns.exception.Timeout):
        spf_status = "missing"
    except Exception:
        spf_status = "error"

    dmarc_status = "missing"
    dmarc_record = None
    try:
        answers = resolver.resolve(f"_dmarc.{domain}", "TXT")
        for rdata in answers:
            txt_str = rdata.to_text().strip('"')
            if txt_str.startswith("v=DMARC1"):
                dmarc_status = "present"
                dmarc_record = txt_str
                break
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
            dns.resolver.NoNameservers, dns.exception.Timeout):
        dmarc_status = "missing"
    except Exception:
        dmarc_status = "error"

    return {
        "auditable": True,
        "domain": domain,
        "spf": spf_status,
        "dmarc": dmarc_status,
        "spf_record": spf_record,
        "dmarc_record": dmarc_record,
        "reason": "Corporate perimeter evaluated."
    }
