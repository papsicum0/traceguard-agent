def generate_remediation_patches(audit_results: list) -> list:
    remediation_records = []

    for item in audit_results:
        if not item.get("auditable"):
            continue

        domain = item["domain"]
        patches = []

        if item.get("spf") == "missing":
            patches.append({
                "type": "TXT",
                "host": "@",
                "fqdn": domain,
                "value": f"v=spf1 include:_spf.{domain} ~all",
                "guidance": "Restricts outbound mail servers and sets soft-fail for unauthorized hosts."
            })

        if item.get("dmarc") == "missing":
            patches.append({
                "type": "TXT",
                "host": "_dmarc",
                "fqdn": f"_dmarc.{domain}",
                "value": f"v=DMARC1; p=reject; rua=mailto:security-reports@{domain}; sp=reject; aspf=r;",
                "guidance": "Instructs receiving MTAs to reject unauthenticated mail claiming origin from this domain."
            })

        if patches:
            remediation_records.append({
                "domain": domain,
                "patches": patches
            })

    return remediation_records
