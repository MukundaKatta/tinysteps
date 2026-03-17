"""Percentile calculation for child developmental progress."""

import math
from datetime import date
from typing import Optional

from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import Child, DevelopmentDomain


class PercentileCalculator:
    """Computes a child's developmental percentile.

    Uses a simplified statistical model based on the ratio of achieved
    milestones to expected milestones, adjusted by how early or late each
    milestone was achieved relative to the typical age range.

    This provides an approximation -- clinical percentiles require
    standardized assessment tools administered by professionals.
    """

    def __init__(self, db: Optional[MilestoneDatabase] = None) -> None:
        self.db = db or MilestoneDatabase()

    def overall_percentile(
        self, child: Child, at_date: Optional[date] = None
    ) -> float:
        """Calculate overall developmental percentile (0-100).

        Args:
            child: The child to evaluate.
            at_date: Date to evaluate at (defaults to today).

        Returns:
            Percentile value between 0 and 100.
        """
        domain_percentiles = self.domain_percentiles(child, at_date)
        if not domain_percentiles:
            return 50.0
        return sum(domain_percentiles.values()) / len(domain_percentiles)

    def domain_percentiles(
        self, child: Child, at_date: Optional[date] = None
    ) -> dict[DevelopmentDomain, float]:
        """Calculate percentile for each developmental domain.

        Args:
            child: The child to evaluate.
            at_date: Date to evaluate at (defaults to today).

        Returns:
            Dictionary mapping each domain to its percentile.
        """
        at_date = at_date or date.today()
        age_months = child.age_in_months_at(at_date)

        # Build lookup of achieved milestones with their achieved age in months
        achieved_map: dict[str, float] = {}
        for am in child.achieved_milestones:
            achieved_age = child.age_in_months_at(am.achieved_date)
            achieved_map[am.milestone_id] = achieved_age

        results: dict[DevelopmentDomain, float] = {}
        for domain in DevelopmentDomain:
            results[domain] = self._domain_percentile(
                domain, age_months, achieved_map
            )
        return results

    def _domain_percentile(
        self,
        domain: DevelopmentDomain,
        age_months: float,
        achieved_map: dict[str, float],
    ) -> float:
        """Calculate percentile for a single domain."""
        milestones = self.db.get_by_domain(domain)

        # Only consider milestones relevant to the child's age
        relevant = [m for m in milestones if m.expected_month_min <= age_months]

        if not relevant:
            return 50.0

        scores: list[float] = []

        for m in relevant:
            mid_expected = (m.expected_month_min + m.expected_month_max) / 2.0
            range_months = max(m.expected_month_max - m.expected_month_min, 1)

            if m.id in achieved_map:
                achieved_age = achieved_map[m.id]
                # How early or late relative to midpoint, normalized by range
                z = (mid_expected - achieved_age) / range_months
                # Convert to a 0-1 score using sigmoid-like function
                score = self._sigmoid(z)
            else:
                # Not achieved: penalize based on how far past expected
                if age_months > m.expected_month_max:
                    overdue = age_months - m.expected_month_max
                    # Stronger penalty for milestones past the concern threshold
                    if age_months > m.concern_if_not_by_month:
                        score = max(0.0, 0.2 - overdue * 0.02)
                    else:
                        score = max(0.1, 0.4 - overdue * 0.05)
                else:
                    # Within expected range but not yet achieved
                    score = 0.45
            scores.append(score)

        if not scores:
            return 50.0

        # Average score mapped to percentile (0-100)
        avg_score = sum(scores) / len(scores)
        percentile = round(min(99.0, max(1.0, avg_score * 100)), 1)
        return percentile

    @staticmethod
    def _sigmoid(x: float) -> float:
        """Sigmoid function mapping z-score to 0-1 range."""
        return 1.0 / (1.0 + math.exp(-x * 2))
