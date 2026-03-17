"""Tests for analyzer modules: concerns, percentile, recommendations."""

from datetime import date

import pytest

from tinysteps.analyzer.concerns import EarlyConcernDetector
from tinysteps.analyzer.percentile import PercentileCalculator
from tinysteps.analyzer.recommendations import ActivityRecommender
from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import (
    AchievedMilestone,
    Child,
    ConcernLevel,
    DevelopmentDomain,
)


def _make_child(birthdate, achieved=None):
    milestones = []
    if achieved:
        for mid, ad in achieved:
            milestones.append(AchievedMilestone(milestone_id=mid, achieved_date=ad))
    return Child(name="Test", birthdate=birthdate, achieved_milestones=milestones)


class TestEarlyConcernDetector:
    def setup_method(self):
        self.db = MilestoneDatabase()
        self.detector = EarlyConcernDetector(self.db)

    def test_no_concerns_newborn(self):
        child = _make_child(date(2025, 6, 1))
        flags = self.detector.detect_concerns(child, date(2025, 6, 15))
        assert len(flags) == 0

    def test_concerns_at_12_months_no_milestones(self):
        child = _make_child(date(2024, 7, 1))
        flags = self.detector.detect_concerns(child, date(2025, 7, 1))
        assert len(flags) > 0

    def test_concerns_sorted_by_severity(self):
        child = _make_child(date(2024, 1, 1))
        flags = self.detector.detect_concerns(child, date(2025, 7, 1))
        if len(flags) >= 2:
            severity_order = {
                ConcernLevel.SIGNIFICANT: 0,
                ConcernLevel.MODERATE: 1,
                ConcernLevel.MILD: 2,
                ConcernLevel.MONITOR: 3,
                ConcernLevel.NONE: 4,
            }
            for i in range(len(flags) - 1):
                assert severity_order[flags[i].concern_level] <= severity_order[flags[i + 1].concern_level]

    def test_no_concerns_when_all_achieved(self):
        concern_milestones = self.db.get_concern_milestones(6)
        achieved = [(m.id, date(2025, 3, 1)) for m in concern_milestones]
        child = _make_child(date(2025, 1, 1), achieved=achieved)
        flags = self.detector.detect_concerns(child, date(2025, 7, 1))
        assert len(flags) == 0

    def test_concerns_by_domain(self):
        child = _make_child(date(2024, 7, 1))
        by_domain = self.detector.get_concerns_by_domain(child, date(2025, 7, 1))
        assert DevelopmentDomain.MOTOR in by_domain
        assert DevelopmentDomain.COGNITIVE in by_domain

    def test_has_significant_concerns(self):
        child = _make_child(date(2023, 1, 1))
        # At 30+ months with nothing achieved
        assert self.detector.has_significant_concerns(child, date(2025, 7, 1))

    def test_concern_flag_has_message(self):
        child = _make_child(date(2024, 7, 1))
        flags = self.detector.detect_concerns(child, date(2025, 7, 1))
        if flags:
            assert len(flags[0].message) > 0
            assert flags[0].months_overdue > 0


class TestPercentileCalculator:
    def setup_method(self):
        self.db = MilestoneDatabase()
        self.calc = PercentileCalculator(self.db)

    def test_overall_percentile_range(self):
        child = _make_child(date(2025, 1, 1))
        pct = self.calc.overall_percentile(child, date(2025, 7, 1))
        assert 1.0 <= pct <= 99.0

    def test_domain_percentiles(self):
        child = _make_child(date(2025, 1, 1))
        pcts = self.calc.domain_percentiles(child, date(2025, 7, 1))
        assert len(pcts) == 4
        for domain in DevelopmentDomain:
            assert domain in pcts
            assert 1.0 <= pcts[domain] <= 99.0

    def test_high_percentile_with_early_achievement(self):
        # Achieve milestones early
        achieved = [
            ("motor-head-lift-prone", date(2025, 1, 15)),
            ("motor-smooth-arm-movements", date(2025, 1, 20)),
            ("motor-head-steady", date(2025, 2, 15)),
            ("motor-hands-to-mouth", date(2025, 2, 15)),
            ("motor-pushes-down-legs", date(2025, 2, 20)),
            ("motor-pushes-up-tummy", date(2025, 3, 1)),
        ]
        child = _make_child(date(2025, 1, 1), achieved=achieved)
        pcts = self.calc.domain_percentiles(child, date(2025, 5, 1))
        # Motor percentile should be relatively high
        assert pcts[DevelopmentDomain.MOTOR] > 40

    def test_low_percentile_with_no_achievement(self):
        child = _make_child(date(2024, 7, 1))
        pcts = self.calc.domain_percentiles(child, date(2025, 7, 1))
        # All should be below 50 with nothing achieved at 12 months
        for pct in pcts.values():
            assert pct < 50

    def test_newborn_gets_default_percentile(self):
        child = _make_child(date(2025, 7, 1))
        pct = self.calc.overall_percentile(child, date(2025, 7, 1))
        # Very new baby, should be around 50
        assert 40 <= pct <= 60


class TestActivityRecommender:
    def setup_method(self):
        self.db = MilestoneDatabase()
        self.recommender = ActivityRecommender(self.db)

    def test_recommendations_for_newborn(self):
        child = _make_child(date(2025, 6, 1))
        recs = self.recommender.get_recommendations(child, date(2025, 6, 15))
        assert len(recs) > 0

    def test_recommendations_limited(self):
        child = _make_child(date(2025, 1, 1))
        recs = self.recommender.get_recommendations(
            child, date(2025, 7, 1), max_recommendations=3
        )
        assert len(recs) <= 3

    def test_recommendations_have_details(self):
        child = _make_child(date(2025, 1, 1))
        recs = self.recommender.get_recommendations(child, date(2025, 7, 1))
        if recs:
            rec = recs[0]
            assert len(rec.activity) > 0
            assert len(rec.description) > 0
            assert rec.duration_minutes > 0
            assert rec.milestone is not None

    def test_recommendations_by_domain(self):
        child = _make_child(date(2025, 1, 1))
        recs = self.recommender.get_recommendations_by_domain(
            child, DevelopmentDomain.MOTOR, date(2025, 7, 1)
        )
        for rec in recs:
            assert rec.milestone.domain == DevelopmentDomain.MOTOR

    def test_recommendations_prioritize_overdue(self):
        # Child at 12 months with no milestones - should get early milestone activities
        child = _make_child(date(2024, 7, 1))
        recs = self.recommender.get_recommendations(child, date(2025, 7, 1))
        if recs:
            # First recommendations should be for overdue milestones
            assert recs[0].milestone.expected_month_max <= 12
