import asyncio
import json
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from traceguard.agent import TraceGuardAgent
from traceguard.tools import seal_audit_ledger

app = typer.Typer(help="TraceGuard Autonomous DevSecOps & Attack Surface Agent", no_args_is_help=True)
console = Console()

@app.command()
def audit(
    target: str = typer.Option(..., "--target", "-t", help="Target username or domain to audit"),
    output: str = typer.Option(None, "--output", "-o", help="Custom output path for audit receipt")
):
    """
    Executes an autonomous attack surface reconnaissance and posture audit.
    """
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║   TRACEGUARD :: AUTONOMOUS ATTACK SURFACE AGENT (v1.0.0)    ║
    ║   Powered by Meta Llama 3 • Cryptographic SHA-256 Ledger     ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    
    agent = TraceGuardAgent(target=target)
    
    with console.status(f"[bold green]Running autonomous agent loop on target: {target}...", spinner="dots"):
        result = asyncio.run(agent.run_autonomous_audit())

    console.print("\n[bold yellow]⚡ Agent Execution Trace:[/bold yellow]")
    for log_entry in result["audit_log"]:
        console.print(f"  [dim]{log_entry}[/dim]")
        
    synthesis = result["threat_synthesis"]
    cvss = synthesis["cvss_score"]
    grade = synthesis["risk_grade"]
    
    grade_color = "red" if grade in ["CRITICAL", "HIGH"] else "yellow" if grade == "MEDIUM" else "green"
    
    # CVSS Summary Card
    console.print("\n")
    console.print(Panel(
        f"[bold]Target:[/bold] {target}\n"
        f"[bold]Exposure Score:[/bold] [{grade_color}]{cvss} / 10.0 ({grade})[/{grade_color}]\n"
        f"[bold]Summary:[/bold] {synthesis['attack_chain_summary']}",
        title="[bold red]Threat Posture Assessment[/bold red]",
        border_style=grade_color
    ))

    # Findings Table
    vulns = synthesis["vulnerabilities"]
    if vulns:
        table = Table(title="Correlated Attack Vectors & Remediation Matrix", show_header=True, header_style="bold magenta")
        table.add_column("Vector", style="cyan", width=24)
        table.add_column("Severity", width=10)
        table.add_column("Discovered Evidence", style="white")
        table.add_column("Actionable Patch", style="green")

        for v in vulns:
            sev_color = "red" if v["severity"] == "HIGH" else "yellow"
            table.add_row(
                v["vector"],
                f"[{sev_color}]{v['severity']}[/{sev_color}]",
                v["finding"],
                v["remediation"]
            )
        console.print(table)
    else:
        console.print("[bold green]✔ No active exposure vectors discovered on public perimeter.[/bold green]")

    # Cryptographic Seal Card & JSON Export
    seal = result["cryptographic_seal"]
    file_path = output if output else f"audit_{target}.json"
    with open(file_path, "w") as f:
        json.dump(result, f, indent=2)

    console.print("\n")
    console.print(Panel(
        f"[bold green]✔ CANONICAL SHA-256 AUDIT SEAL:[/bold green]\n[cyan]{seal}[/cyan]\n\n"
        f"[dim]Saved Audit Receipt:[/dim] [bold white]{file_path}[/bold white]\n"
        f"[dim]Timestamp (UTC):[/dim] {result['timestamp_utc']}\n"
        f"[dim]Integrity State:[/dim] MATHEMATICALLY SEALED (Tamper-Evident)",
        title="[bold green]Cryptographic Audit Ledger[/bold green]",
        border_style="green"
    ))

@app.command()
def verify(file_path: str = typer.Argument(..., help="Path to the audit JSON file")):
    """
    Cryptographically verifies whether an audit receipt has been altered.
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except Exception as exc:
        console.print(f"[bold red]Error opening file:[/bold red] {exc}")
        raise typer.Exit(1)

    recorded_seal = data.get("cryptographic_seal")
    if not recorded_seal:
        console.print("[bold red]Invalid audit receipt: No cryptographic seal present.[/bold red]")
        raise typer.Exit(1)

    # Reconstruct payload exactly as it was when sealed
    verification_payload = {
        "target": data.get("target"),
        "timestamp_utc": data.get("timestamp_utc"),
        "observations": data.get("observations"),
        "threat_synthesis": data.get("threat_synthesis")
    }

    recomputed_seal = seal_audit_ledger(verification_payload)

    if recomputed_seal == recorded_seal:
        console.print(Panel(
            f"[bold green]✔ INTEGRITY VERIFIED — ZERO TAMPERING DETECTED[/bold green]\n\n"
            f"[bold]Recorded Seal:[/bold]   {recorded_seal}\n"
            f"[bold]Recomputed Seal:[/bold] {recomputed_seal}\n\n"
            f"[dim]This report is mathematically proven to be identical to the state at generation.[/dim]",
            title="[bold green]Tamper Verification Passed[/bold green]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold red]✖ INTEGRITY COMPROMISED — AUDIT TAMPERING DETECTED[/bold red]\n\n"
            f"[bold]Recorded Seal:[/bold]   {recorded_seal}\n"
            f"[bold]Recomputed Seal:[/bold] {recomputed_seal}\n\n"
            f"[red]The contents of this audit report have been modified since it was cryptographically signed.[/red]",
            title="[bold red]Tamper Verification Failed[/bold red]",
            border_style="red"
        ))

if __name__ == "__main__":
    app()
