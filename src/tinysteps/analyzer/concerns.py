"""Early concern detection for developmental delays."""

from datetime import date
from typing import Optional

from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import (
    Child,
    ConcernLevel,
    DevelopmentDomain,
    Milestone,
)


class ConcernFlag:
    """A flagged developmental concern."""

    def __init__(
        self,
        milestone: Milestone,
        concern_level: ConcernLevel,
        message: str,
        months_overdue: float,
    ) -> None:
        self.milestone = milestone
        self.concern_level = concern_level
        self.message = message
        self.months_overdue = months_overdue

    def __repr__(self) -> str:
        return f"ConcernFlag({self.milestone.id}, {self.concern_level.value})"


class EarlyConcernDetector:
    """Flags potential developmental delays based on missed milestones.

    Analyzes a child's achievement history against CDC/WHO timelines
    to identify milestones that have not been achieved by the expected
    concern age, and generates actionable flags.
    """

    def __init__(self, db: Optional[MilestoneDatabase] = None) -> None:
        self.db = db or MilestoneDatabase()

    def detect_concerns(
        self, child: Child, at_date: Optional[date] = None
    ) -> list[ConcernFlag]:
        """Detect developmental concerns for a child.

        Args:
            child: The child to evaluate.
            at_date: Date to evaluate at (defaults to today).

        Returns:
            List of ConcernFlag objects sorted by severity.
        """
        at_date = at_date or date.today()
        age_months = child.age_in_months_at(at_date)
        achieved_ids = {am.milestone_id for am in child.achieved_milestones}

        flags: list[ConcernFlag] = []

        for milestone in self.db.all_milestones:
            if milestone.id in achieved_ids:
                continue

            if milestone.concern_if_not_by_month <= age_months:
                months_overdue = age_months - milestone.concern_if_not_by_month
                concern_level = self._severity_for_overdue(months_overdue)
                message = self._build_message(milestone, months_overdue, concern_level)
                flags.append(
                    ConcernFlag(
                        milestone=milestone,
                        concern_level=concern_level,
                        message=message,
                        months_overdue=months_overdue,
                    )
                )

        # Sort by severity (most severe first), then by months overdue
        severity_order = {
            ConcernLevel.SIGNIFICANT: 0,
            ConcernLevel.MODERATE: 1,
            ConcernLevel.MILD: 2,
            ConcernLevel.MONITOR: 3,
            ConcernLevel.NONE: 4,
        }
        flags.sort(key=lambda f: (severity_order[f.concern_level], -f.months_overdue))

        return flags

    def get_concerns_by_domain(
        self, child: Child, at_date: Optional[date] = None
    ) -> dict[DevelopmentDomain, list[ConcernFlag]]:
        """Get concerns grouped by developmental domain."""
        flags = self.detect_concerns(child, at_date)
        by_domain: dict[DevelopmentDomain, list[ConcernFlag]] = {
            d: [] for d in DevelopmentDomain
        }
        for flag in flags:
            by_domain[flag.milestone.domain].append(flag)
        return by_domain

    def has_significant_concerns(
        self, child: Child, at_date: Optional[date] = None
    ) -> bool:
        """Check if there are any significant concerns."""
        flags = self.detect_concerns(child, at_date)
        return any(f.concern_level == ConcernLevel.SIGNIFICANT for f in flags)

    def _severity_for_overdue(self, months_overdue: float) -> ConcernLevel:
        """Determine concern severity based on how overdue a milestone is."""
        if months_overdue >= 6:
            return ConcernLevel.SIGNIFICANT
        if months_overdue >= 4:
            return ConcernLevel.MODERATE
        if months_overdue >= 2:
            return ConcernLevel.MILD
        return ConcernLevel.MONITOR

    def _build_message(
        self,
        milestone: Milestone,
        months_overdue: float,
        concern_level: ConcernLevel,
    ) -> str:
        """Build a descriptive message for a concern flag."""
        domain_name = milestone.domain.value.capitalize()
        overdue_str = f"{months_overdue:.1f}"

        if concern_level == ConcernLevel.SIGNIFICANT:
            prefix = "SIGNIFICANT CONCERN"
            advice = "Please consult your pediatrician as soon as possible."
        elif concern_level == ConcernLevel.MODERATE:
            prefix = "MODERATE CONCERN"
            advice = "Consider discussing with your pediatrician at the next visit."
        elif concern_level == ConcernLevel.MILD:
            prefix = "MILD CONCERN"
            advice = "Monitor closely and mention at next well-child visit."
        else:
            prefix = "MONITOR"
            advice = "Keep monitoring and encouraging this skill."

        return (
            f"[{prefix}] {domain_name}: '{milestone.name}' is {overdue_str} months "
            f"past the expected age. {advice}"
        )
