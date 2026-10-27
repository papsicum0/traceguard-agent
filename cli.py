import os
import re
import json
from typing import Optional
import typer
import dns.resolver
from git import Repo
import modal
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
app = typer.Typer(
    help="TraceGuard: Autonomous DevSecOps Threat Synthesis Engine powered by Meta Llama 3.1"
)

def extract_git_telemetry(repo_path: str = "."):
    """Scans the local Git history for author identities and potential leaked credentials."""
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except Exception:
        return {"error": "Not a valid git repository", "authors": [], "emails": [], "potential_leaks": []}

    commits = list(repo.iter_commits(max_count=25))
    authors = set()
    emails = set()
    leaks = []

    secret_pattern = re.compile(
        r"(?i)(api[_-]?key|secret|token|password|auth|private_key)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{12,})"
    )

    for commit in commits:
        if commit.author.name:
            authors.add(commit.author.name)
        if commit.author.email:
            emails.add(commit.author.email)

        for parent in commit.parents:
            diffs = parent.diff(commit, create_patch=True)
            for diff in diffs:
                patch_str = diff.diff.decode("utf-8", errors="ignore")
                matches = secret_pattern.findall(patch_str)
                for key_name, val in matches:
                    masked = val[:4] + "*" * (len(val) - 4)
                    leaks.append(f"Exposed {key_name} ({masked}) in commit {commit.hexsha[:7]}")

    return {
        "authors": list(authors),
        "emails": list(emails),
        "potential_leaks": leaks
    }

def check_dns_posture(domain: str):
    """Audits DNS SPF and DMARC perimeter security protections."""
    posture = {"domain": domain, "has_spf": False, "has_dmarc": False}
    
    # Check SPF
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for rdata in answers:
            if "v=spf1" in rdata.to_text():
                posture["has_spf"] = True
                break
    except Exception:
        posture["has_spf"] = False

    # Check DMARC
    try:
        dmarc_answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        for rdata in dmarc_answers:
            if "v=DMARC1" in rdata.to_text():
                posture["has_dmarc"] = True
                break
    except Exception:
        posture["has_dmarc"] = False

    return posture

@app.command()
def scan(
    repo_path: str = typer.Argument(".", help="Path to the repository to audit"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Custom domain to inspect for DNS posture")
):
    """
    Run an end-to-end DevSecOps scan and synthesize CVSS threat intelligence via Meta Llama 3.1 on Modal.
    """
    # Normalize path if 'scan' is passed directly
    if repo_path == "scan":
        repo_path = "."

    console.print(Panel.fit(
        "[bold cyan]TRACEGUARD[/bold cyan] | [bold red]Autonomous DevSecOps Threat Synthesis[/bold red]\n"
        "[dim]Engine: Meta Llama 3.1 8B Instruct | Runtime: Modal Cloud GPU (A10G)[/dim]",
        border_style="cyan"
    ))

    # 1. Local Git Commit Forensics
    console.print(f"[bold yellow][*] Running Git commit forensics on path:[/bold yellow] [white]{repo_path}[/white]")
    git_data = extract_git_telemetry(repo_path)
    
    found_emails = git_data.get("emails", [])
    console.print(f"    Discovered [bold]{len(found_emails)}[/bold] author identity record(s).")
    if git_data.get("potential_leaks"):
        console.print(f"    [bold red][!] Detected {len(git_data['potential_leaks'])} high-entropy secret leak(s)[/bold red]")

    # Identify target domain for perimeter check
    target_domain = domain
    if not target_domain:
        for em in found_emails:
            if "@" in em and not em.endswith("noreply.github.com"):
                target_domain = em.split("@")[-1]
                break
    if not target_domain:
        target_domain = "internal-infra.local"

    # 2. Local DNS Posture Check
    console.print(f"[bold yellow][*] Auditing perimeter email security posture on:[/bold yellow] [white]{target_domain}[/white]")
    dns_data = check_dns_posture(target_domain)
    console.print(f"    SPF Record: {'[bold green]Present[/bold green]' if dns_data['has_spf'] else '[bold red]Missing[/bold red]'}")
    console.print(f"    DMARC Record: {'[bold green]Present[/bold green]' if dns_data['has_dmarc'] else '[bold red]Missing[/bold red]'}")

    # Build Telemetry Payload
    telemetry_payload = {
        "git_recon": git_data,
        "dns_posture": dns_data
    }
    telemetry_str = json.dumps(telemetry_payload, indent=2)

    # 3. Call Remote Llama 3.1 Model on Modal
    raw_response = ""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task("[green]Dispatching telemetry to Meta Llama 3.1 A10G container...", total=None)
        
        try:
            try:
                SynthesizerCls = modal.Cls.from_name("traceguard-threat-engine", "LlamaSynthesizer")
            except AttributeError:
                SynthesizerCls = modal.Cls.lookup("traceguard-threat-engine", "LlamaSynthesizer")
            
            synthesizer = SynthesizerCls()
            raw_response = synthesizer.synthesize.remote(telemetry_str)
        except Exception as e:
            console.print(f"[bold red][Error querying Modal backend]:[/bold red] {e}")
            raise typer.Exit(code=1)

    # 4. Resilient JSON Extraction (filters model conversational preambles)
    json_match = re.search(r"(\{.*\})", raw_response, re.DOTALL)
    clean_json = json_match.group(1).strip() if json_match else raw_response.strip()

    # 5. Display Formatted Threat Report
    try:
        report = json.loads(clean_json)
        score = report.get("cvss_score", "N/A")
        grade = str(report.get("risk_grade", "UNKNOWN")).upper()
        grade_color = "red" if grade in ["CRITICAL", "HIGH"] else "yellow"

        console.print("\n")
        console.print(Panel(
            f"[bold {grade_color}]Composite CVSS: {score} | Risk Severity: {grade}[/bold {grade_color}]\n\n"
            f"[bold white]Attack Chain Synthesis:[/bold white]\n{report.get('attack_chain_summary', '')}",
            title="Threat Assessment Report",
            border_style=grade_color
        ))

        table = Table(
            title="Correlated Vulnerabilities & Actionable Remediation",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Severity", justify="center", width=12)
        table.add_column("Finding & Vector", style="cyan", ratio=2)
        table.add_column("Remediation", style="green", ratio=2)

        for v in report.get("vulnerabilities", []):
            sev = str(v.get("severity", "MEDIUM")).upper()
            c = "red" if sev in ["CRITICAL", "HIGH"] else "yellow"
            finding_text = f"[bold]{v.get('finding', '')}[/bold]\n[dim]{v.get('vector', '')}[/dim]"
            table.add_row(f"[{c}]{sev}[/{c}]", finding_text, v.get("remediation", ""))

        console.print(table)

    except Exception:
        console.print("\n[bold yellow][Raw Engine Output][/bold yellow]")
        console.print(raw_response)

if __name__ == "__main__":
    app()
