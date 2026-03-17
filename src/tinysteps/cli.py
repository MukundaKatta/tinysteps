"""Command-line interface for TinySteps milestone tracker."""

from datetime import date, datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from tinysteps.analyzer.concerns import EarlyConcernDetector
from tinysteps.analyzer.percentile import PercentileCalculator
from tinysteps.analyzer.recommendations import ActivityRecommender
from tinysteps.milestones.assessor import DevelopmentAssessor
from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.milestones.tracker import MilestoneTracker
from tinysteps.models import DevelopmentDomain
from tinysteps.report import generate_report

console = Console()


def _get_tracker(data_dir: Optional[str] = None) -> MilestoneTracker:
    """Create a tracker instance."""
    path = Path(data_dir) if data_dir else None
    return MilestoneTracker(data_dir=path)


@click.group()
@click.option("--data-dir", default=None, help="Directory for data storage")
@click.pass_context
def cli(ctx: click.Context, data_dir: Optional[str]) -> None:
    """TinySteps - Baby Milestone Tracker.

    Track your child's developmental milestones based on CDC/WHO guidelines.
    """
    ctx.ensure_object(dict)
    ctx.obj["data_dir"] = data_dir


@cli.command("add-child")
@click.option("--name", required=True, help="Child's name")
@click.option(
    "--birthdate",
    required=True,
    help="Child's date of birth (YYYY-MM-DD)",
)
@click.pass_context
def add_child(ctx: click.Context, name: str, birthdate: str) -> None:
    """Add a new child profile."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    try:
        bd = datetime.strptime(birthdate, "%Y-%m-%d").date()
        child = tracker.add_child(name, bd)
        console.print(f"[green]Added child: {child.name} (born {child.birthdate})[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("list-children")
@click.pass_context
def list_children(ctx: click.Context) -> None:
    """List all tracked children."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    children = tracker.list_children()
    if not children:
        console.print("[yellow]No children tracked yet. Use 'add-child' to add one.[/yellow]")
        return

    table = Table(title="Tracked Children")
    table.add_column("Name", style="bold")
    table.add_column("Birthdate")
    table.add_column("Age (months)", justify="right")
    table.add_column("Milestones Logged", justify="right")

    for child in children:
        table.add_row(
            child.name,
            str(child.birthdate),
            f"{child.age_in_months:.1f}",
            str(len(child.achieved_milestones)),
        )

    console.print(table)


@cli.command("log-milestone")
@click.option("--child", required=True, help="Child's name")
@click.option("--milestone", required=True, help="Milestone ID")
@click.option("--date", "achieved_date", default=None, help="Date achieved (YYYY-MM-DD, default: today)")
@click.option("--notes", default=None, help="Optional notes")
@click.pass_context
def log_milestone(
    ctx: click.Context,
    child: str,
    milestone: str,
    achieved_date: Optional[str],
    notes: Optional[str],
) -> None:
    """Log a milestone achievement for a child."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    try:
        ad = (
            datetime.strptime(achieved_date, "%Y-%m-%d").date()
            if achieved_date
            else date.today()
        )
        achieved = tracker.log_milestone(child, milestone, ad, notes)
        ms = tracker.db.get_by_id(milestone)
        name = ms.name if ms else milestone
        console.print(f"[green]Logged milestone '{name}' for {child} on {ad}[/green]")
    except (KeyError, ValueError) as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("list-milestones")
@click.option("--domain", type=click.Choice(["motor", "cognitive", "language", "social"]), default=None)
@click.option("--age", type=float, default=None, help="Filter by expected age (months)")
def list_milestones(domain: Optional[str], age: Optional[float]) -> None:
    """List available milestones."""
    db = MilestoneDatabase()
    milestones = db.all_milestones

    if domain:
        d = DevelopmentDomain(domain)
        milestones = [m for m in milestones if m.domain == d]

    if age is not None:
        milestones = [m for m in milestones if m.expected_month_min <= age <= m.expected_month_max]

    table = Table(title="Developmental Milestones")
    table.add_column("ID", style="dim")
    table.add_column("Domain")
    table.add_column("Milestone")
    table.add_column("Expected Age", justify="center")
    table.add_column("Concern If Not By", justify="center")

    for m in milestones:
        table.add_row(
            m.id,
            m.domain.value.capitalize(),
            m.name,
            f"{m.expected_month_min}-{m.expected_month_max}mo",
            f"{m.concern_if_not_by_month}mo",
        )

    console.print(table)


@cli.command("assess")
@click.option("--child", required=True, help="Child's name")
@click.pass_context
def assess(ctx: click.Context, child: str) -> None:
    """Run a developmental assessment for a child."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    try:
        child_obj = tracker.get_child(child)
        assessor = DevelopmentAssessor(tracker.db)
        assessment = assessor.assess(child_obj)

        table = Table(title=f"Assessment for {child}")
        table.add_column("Domain", style="bold")
        table.add_column("Achieved / Expected", justify="center")
        table.add_column("Progress", justify="center")
        table.add_column("Concern Level", justify="center")

        for domain in DevelopmentDomain:
            da = assessment.domain_assessments[domain]
            table.add_row(
                domain.value.capitalize(),
                f"{da.achieved_count}/{da.expected_count}",
                f"{da.percentage:.0f}%",
                da.concern_level.value.upper(),
            )

        console.print(table)
        console.print(
            f"\nOverall Concern Level: [bold]{assessment.overall_concern_level.value.upper()}[/bold]"
        )
    except KeyError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("recommend")
@click.option("--child", required=True, help="Child's name")
@click.option("--domain", type=click.Choice(["motor", "cognitive", "language", "social"]), default=None)
@click.option("--max", "max_recs", type=int, default=5, help="Maximum recommendations")
@click.pass_context
def recommend(
    ctx: click.Context,
    child: str,
    domain: Optional[str],
    max_recs: int,
) -> None:
    """Get activity recommendations for a child."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    try:
        child_obj = tracker.get_child(child)
        recommender = ActivityRecommender(tracker.db)

        if domain:
            d = DevelopmentDomain(domain)
            recs = recommender.get_recommendations_by_domain(child_obj, d)
        else:
            recs = recommender.get_recommendations(child_obj, max_recommendations=max_recs)

        if not recs:
            console.print("[green]No specific recommendations at this time. Keep up the great work![/green]")
            return

        for rec in recs[:max_recs]:
            console.print(f"\n[bold green]{rec.activity}[/bold green]")
            console.print(f"  {rec.description}")
            if rec.materials:
                console.print(f"  [dim]Materials: {', '.join(rec.materials)}[/dim]")
            console.print(f"  [dim]Duration: ~{rec.duration_minutes} min | Supports: {rec.milestone.name}[/dim]")

    except KeyError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("report")
@click.option("--child", required=True, help="Child's name")
@click.pass_context
def report(ctx: click.Context, child: str) -> None:
    """Generate a comprehensive developmental report."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    try:
        child_obj = tracker.get_child(child)
        generate_report(child_obj, console)
    except KeyError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("concerns")
@click.option("--child", required=True, help="Child's name")
@click.pass_context
def concerns(ctx: click.Context, child: str) -> None:
    """Check for developmental concerns."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    try:
        child_obj = tracker.get_child(child)
        detector = EarlyConcernDetector(tracker.db)
        flags = detector.detect_concerns(child_obj)

        if not flags:
            console.print("[green]No developmental concerns detected. Great job![/green]")
            return

        for flag in flags:
            console.print(f"  {flag.message}")

    except KeyError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("percentile")
@click.option("--child", required=True, help="Child's name")
@click.pass_context
def percentile(ctx: click.Context, child: str) -> None:
    """Calculate developmental percentile."""
    tracker = _get_tracker(ctx.obj["data_dir"])
    try:
        child_obj = tracker.get_child(child)
        calc = PercentileCalculator(tracker.db)
        domain_pcts = calc.domain_percentiles(child_obj)
        overall = calc.overall_percentile(child_obj)

        table = Table(title=f"Percentiles for {child}")
        table.add_column("Domain", style="bold")
        table.add_column("Percentile", justify="center")

        for domain in DevelopmentDomain:
            pct = domain_pcts[domain]
            table.add_row(domain.value.capitalize(), f"{pct:.0f}th")

        table.add_row("[bold]Overall[/bold]", f"[bold]{overall:.0f}th[/bold]")
        console.print(table)

    except KeyError as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    cli()
