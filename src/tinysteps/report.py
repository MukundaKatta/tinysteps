"""Report generation for developmental progress."""

from datetime import date
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from tinysteps.analyzer.concerns import EarlyConcernDetector
from tinysteps.analyzer.percentile import PercentileCalculator
from tinysteps.analyzer.recommendations import ActivityRecommender
from tinysteps.milestones.assessor import DevelopmentAssessor
from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import (
    Assessment,
    Child,
    ConcernLevel,
    DevelopmentDomain,
)


CONCERN_COLORS = {
    ConcernLevel.NONE: "green",
    ConcernLevel.MONITOR: "yellow",
    ConcernLevel.MILD: "dark_orange",
    ConcernLevel.MODERATE: "red",
    ConcernLevel.SIGNIFICANT: "bold red",
}

DOMAIN_LABELS = {
    DevelopmentDomain.MOTOR: "Motor Skills",
    DevelopmentDomain.COGNITIVE: "Cognitive",
    DevelopmentDomain.LANGUAGE: "Language",
    DevelopmentDomain.SOCIAL: "Social-Emotional",
}


def generate_report(
    child: Child,
    console: Optional[Console] = None,
    at_date: Optional[date] = None,
) -> None:
    """Generate and display a comprehensive developmental report.

    Args:
        child: The child to report on.
        console: Rich Console for output (creates one if not provided).
        at_date: Date to assess at (defaults to today).
    """
    console = console or Console()
    at_date = at_date or date.today()
    db = MilestoneDatabase()

    age_months = child.age_in_months_at(at_date)

    # Header
    console.print()
    console.print(
        Panel(
            f"[bold]{child.name}[/bold]\n"
            f"Born: {child.birthdate.isoformat()}\n"
            f"Age: {age_months:.1f} months\n"
            f"Assessment Date: {at_date.isoformat()}",
            title="[bold blue]TinySteps Developmental Report[/bold blue]",
            border_style="blue",
        )
    )

    # Assessment
    assessor = DevelopmentAssessor(db)
    assessment = assessor.assess(child, at_date)

    # Domain Summary Table
    _print_domain_summary(console, assessment)

    # Percentiles
    calc = PercentileCalculator(db)
    domain_percentiles = calc.domain_percentiles(child, at_date)
    overall_percentile = calc.overall_percentile(child, at_date)
    _print_percentiles(console, domain_percentiles, overall_percentile)

    # Concerns
    detector = EarlyConcernDetector(db)
    concerns = detector.detect_concerns(child, at_date)
    if concerns:
        _print_concerns(console, concerns)

    # Upcoming Milestones
    _print_upcoming(console, assessment)

    # Activity Recommendations
    recommender = ActivityRecommender(db)
    recs = recommender.get_recommendations(child, at_date, max_recommendations=5)
    if recs:
        _print_recommendations(console, recs)

    # Overall Summary
    _print_overall_summary(console, assessment, overall_percentile)
    console.print()


def _print_domain_summary(console: Console, assessment: Assessment) -> None:
    """Print domain assessment summary table."""
    table = Table(title="Domain Assessment Summary", show_header=True)
    table.add_column("Domain", style="bold")
    table.add_column("Achieved", justify="center")
    table.add_column("Expected", justify="center")
    table.add_column("Progress", justify="center")
    table.add_column("Status", justify="center")

    for domain in DevelopmentDomain:
        da = assessment.domain_assessments.get(domain)
        if da is None:
            continue
        color = CONCERN_COLORS.get(da.concern_level, "white")
        status = da.concern_level.value.upper()
        progress_bar = _progress_bar(da.percentage)

        table.add_row(
            DOMAIN_LABELS[domain],
            str(da.achieved_count),
            str(da.expected_count),
            progress_bar,
            f"[{color}]{status}[/{color}]",
        )

    console.print(table)


def _print_percentiles(
    console: Console,
    domain_percentiles: dict[DevelopmentDomain, float],
    overall: float,
) -> None:
    """Print percentile information."""
    table = Table(title="Developmental Percentiles", show_header=True)
    table.add_column("Domain", style="bold")
    table.add_column("Percentile", justify="center")
    table.add_column("Interpretation", justify="left")

    for domain in DevelopmentDomain:
        pct = domain_percentiles.get(domain, 50.0)
        interp = _percentile_interpretation(pct)
        color = "green" if pct >= 50 else "yellow" if pct >= 25 else "red"
        table.add_row(
            DOMAIN_LABELS[domain],
            f"[{color}]{pct:.0f}th[/{color}]",
            interp,
        )

    overall_color = "green" if overall >= 50 else "yellow" if overall >= 25 else "red"
    table.add_row(
        "[bold]Overall[/bold]",
        f"[bold {overall_color}]{overall:.0f}th[/bold {overall_color}]",
        _percentile_interpretation(overall),
        style="bold",
    )

    console.print(table)


def _print_concerns(console: Console, concerns: list) -> None:
    """Print developmental concerns."""
    console.print()
    console.print("[bold red]Developmental Concerns[/bold red]")
    console.print()

    for flag in concerns[:10]:
        color = CONCERN_COLORS.get(flag.concern_level, "white")
        console.print(f"  [{color}]{flag.message}[/{color}]")

    if len(concerns) > 10:
        console.print(f"  ... and {len(concerns) - 10} more concerns")
    console.print()


def _print_upcoming(console: Console, assessment: Assessment) -> None:
    """Print upcoming milestones."""
    upcoming: list = []
    for da in assessment.domain_assessments.values():
        upcoming.extend(da.upcoming_milestones)

    if not upcoming:
        return

    table = Table(title="Upcoming Milestones (Next 3 Months)", show_header=True)
    table.add_column("Domain", style="bold")
    table.add_column("Milestone")
    table.add_column("Expected Age", justify="center")

    for m in sorted(upcoming, key=lambda x: x.expected_month_min)[:10]:
        table.add_row(
            DOMAIN_LABELS[m.domain],
            m.name,
            f"{m.expected_month_min}-{m.expected_month_max} months",
        )

    console.print(table)


def _print_recommendations(console: Console, recs: list) -> None:
    """Print activity recommendations."""
    console.print()
    console.print("[bold green]Recommended Activities[/bold green]")
    console.print()

    for i, rec in enumerate(recs, 1):
        console.print(
            Panel(
                f"[bold]{rec.activity}[/bold]\n"
                f"{rec.description}\n\n"
                f"[dim]Materials: {', '.join(rec.materials) if rec.materials else 'None needed'}[/dim]\n"
                f"[dim]Duration: ~{rec.duration_minutes} minutes[/dim]\n"
                f"[dim]Supports: {rec.milestone.name} ({DOMAIN_LABELS[rec.milestone.domain]})[/dim]",
                border_style="green",
            )
        )


def _print_overall_summary(
    console: Console, assessment: Assessment, percentile: float
) -> None:
    """Print overall summary and disclaimers."""
    color = CONCERN_COLORS.get(assessment.overall_concern_level, "white")
    level = assessment.overall_concern_level.value.upper()

    console.print(
        Panel(
            f"Overall Status: [{color}]{level}[/{color}]\n"
            f"Overall Percentile: {percentile:.0f}th\n\n"
            f"[dim italic]Note: This assessment is for informational purposes only "
            f"and does not replace professional evaluation. If you have concerns "
            f"about your child's development, please consult your pediatrician.[/dim italic]",
            title="[bold]Summary[/bold]",
            border_style="blue",
        )
    )


def _progress_bar(percentage: float) -> str:
    """Create a simple text progress bar."""
    filled = int(percentage / 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"{bar} {percentage:.0f}%"


def _percentile_interpretation(percentile: float) -> str:
    """Provide human-readable percentile interpretation."""
    if percentile >= 75:
        return "Above average"
    if percentile >= 50:
        return "Average"
    if percentile >= 25:
        return "Below average - monitor"
    if percentile >= 10:
        return "Well below average - discuss with pediatrician"
    return "Significantly below - seek evaluation"
