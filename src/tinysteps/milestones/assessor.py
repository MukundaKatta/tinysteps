"""Developmental assessment comparing child progress to expected timeline."""

from datetime import date

from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import (
    Assessment,
    Child,
    ConcernLevel,
    DevelopmentDomain,
    DomainAssessment,
)


class DevelopmentAssessor:
    """Compares a child's developmental progress to CDC/WHO expected timelines.

    Evaluates each developmental domain and provides an overall assessment
    including concern levels for potential delays.
    """

    def __init__(self, db: MilestoneDatabase | None = None) -> None:
        self.db = db or MilestoneDatabase()

    def assess(self, child: Child, assessment_date: date | None = None) -> Assessment:
        """Perform a comprehensive developmental assessment.

        Args:
            child: The child to assess.
            assessment_date: Date of assessment (defaults to today).

        Returns:
            A complete Assessment with domain-level and overall results.
        """
        assessment_date = assessment_date or date.today()
        age_months = child.age_in_months_at(assessment_date)
        achieved_ids = {am.milestone_id for am in child.achieved_milestones}

        domain_assessments: dict[DevelopmentDomain, DomainAssessment] = {}

        for domain in DevelopmentDomain:
            domain_assessments[domain] = self._assess_domain(
                domain, age_months, achieved_ids
            )

        overall_concern = self._compute_overall_concern(domain_assessments)

        assessment = Assessment(
            child_name=child.name,
            assessment_date=assessment_date,
            age_months=age_months,
            domain_assessments=domain_assessments,
            overall_concern_level=overall_concern,
        )

        return assessment

    def _assess_domain(
        self,
        domain: DevelopmentDomain,
        age_months: float,
        achieved_ids: set[str],
    ) -> DomainAssessment:
        """Assess a single developmental domain."""
        domain_milestones = self.db.get_by_domain(domain)

        # Milestones expected to be achieved by this age
        expected = [
            m for m in domain_milestones if m.expected_month_max <= age_months
        ]
        achieved_count = sum(1 for m in expected if m.id in achieved_ids)
        expected_count = len(expected)

        percentage = (achieved_count / expected_count * 100) if expected_count > 0 else 100.0

        # Milestones that are concerning if not achieved
        concern_milestones = [
            m
            for m in domain_milestones
            if m.concern_if_not_by_month <= age_months and m.id not in achieved_ids
        ]

        # Upcoming milestones
        upcoming = [
            m
            for m in domain_milestones
            if m.expected_month_min > age_months
            and m.expected_month_min <= age_months + 3
        ]

        concern_level = self._compute_concern_level(
            percentage, len(concern_milestones), expected_count
        )

        return DomainAssessment(
            domain=domain,
            achieved_count=achieved_count,
            expected_count=expected_count,
            percentage=percentage,
            concern_level=concern_level,
            missed_milestones=concern_milestones,
            upcoming_milestones=upcoming,
        )

    def _compute_concern_level(
        self,
        percentage: float,
        concern_milestone_count: int,
        expected_count: int,
    ) -> ConcernLevel:
        """Compute concern level for a domain based on achievement data."""
        if concern_milestone_count == 0 and percentage >= 80:
            return ConcernLevel.NONE

        if concern_milestone_count == 0 and percentage >= 60:
            return ConcernLevel.MONITOR

        if concern_milestone_count <= 1:
            if percentage >= 60:
                return ConcernLevel.MONITOR
            return ConcernLevel.MILD

        if concern_milestone_count <= 2:
            return ConcernLevel.MILD if percentage >= 50 else ConcernLevel.MODERATE

        if concern_milestone_count <= 3:
            return ConcernLevel.MODERATE

        return ConcernLevel.SIGNIFICANT

    def _compute_overall_concern(
        self, domain_assessments: dict[DevelopmentDomain, DomainAssessment]
    ) -> ConcernLevel:
        """Compute overall concern level from domain assessments."""
        concern_order = [
            ConcernLevel.NONE,
            ConcernLevel.MONITOR,
            ConcernLevel.MILD,
            ConcernLevel.MODERATE,
            ConcernLevel.SIGNIFICANT,
        ]

        max_concern = ConcernLevel.NONE
        domains_with_concerns = 0

        for da in domain_assessments.values():
            if concern_order.index(da.concern_level) > concern_order.index(max_concern):
                max_concern = da.concern_level
            if da.concern_level not in (ConcernLevel.NONE, ConcernLevel.MONITOR):
                domains_with_concerns += 1

        # Escalate if multiple domains have concerns
        if domains_with_concerns >= 3 and max_concern == ConcernLevel.MILD:
            return ConcernLevel.MODERATE
        if domains_with_concerns >= 2 and max_concern == ConcernLevel.MODERATE:
            return ConcernLevel.SIGNIFICANT

        return max_concern
