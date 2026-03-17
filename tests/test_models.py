"""Tests for TinySteps data models."""

from datetime import date

import pytest

from tinysteps.models import (
    AchievedMilestone,
    Assessment,
    Child,
    ConcernLevel,
    DevelopmentDomain,
    DomainAssessment,
    Milestone,
)


class TestDevelopmentDomain:
    def test_domain_values(self):
        assert DevelopmentDomain.MOTOR == "motor"
        assert DevelopmentDomain.COGNITIVE == "cognitive"
        assert DevelopmentDomain.LANGUAGE == "language"
        assert DevelopmentDomain.SOCIAL == "social"

    def test_all_domains(self):
        domains = list(DevelopmentDomain)
        assert len(domains) == 4


class TestMilestone:
    def test_create_milestone(self):
        m = Milestone(
            id="test-milestone",
            name="Test Milestone",
            description="A test milestone",
            domain=DevelopmentDomain.MOTOR,
            expected_month_min=3,
            expected_month_max=6,
            concern_if_not_by_month=9,
        )
        assert m.id == "test-milestone"
        assert m.domain == DevelopmentDomain.MOTOR
        assert m.expected_month_min == 3
        assert m.expected_month_max == 6
        assert m.concern_if_not_by_month == 9


class TestChild:
    def test_create_child(self):
        child = Child(name="Emma", birthdate=date(2025, 1, 15))
        assert child.name == "Emma"
        assert child.birthdate == date(2025, 1, 15)
        assert child.achieved_milestones == []

    def test_age_in_months(self):
        # Use a fixed date for testing
        child = Child(name="Test", birthdate=date(2025, 1, 1))
        age = child.age_in_months_at(date(2025, 7, 1))
        assert abs(age - 6.0) < 0.1

    def test_age_in_months_at(self):
        child = Child(name="Test", birthdate=date(2025, 1, 15))
        age = child.age_in_months_at(date(2025, 4, 15))
        assert abs(age - 3.0) < 0.1

    def test_age_in_months_at_partial(self):
        child = Child(name="Test", birthdate=date(2025, 1, 1))
        age = child.age_in_months_at(date(2025, 1, 16))
        assert age == pytest.approx(0.5, abs=0.1)

    def test_child_with_milestones(self):
        child = Child(
            name="Emma",
            birthdate=date(2025, 1, 15),
            achieved_milestones=[
                AchievedMilestone(
                    milestone_id="motor-head-lift-prone",
                    achieved_date=date(2025, 2, 1),
                    notes="During tummy time",
                )
            ],
        )
        assert len(child.achieved_milestones) == 1
        assert child.achieved_milestones[0].milestone_id == "motor-head-lift-prone"


class TestAchievedMilestone:
    def test_create_achieved(self):
        am = AchievedMilestone(
            milestone_id="motor-head-lift-prone",
            achieved_date=date(2025, 3, 1),
        )
        assert am.milestone_id == "motor-head-lift-prone"
        assert am.notes is None

    def test_achieved_with_notes(self):
        am = AchievedMilestone(
            milestone_id="motor-head-lift-prone",
            achieved_date=date(2025, 3, 1),
            notes="First time during tummy time!",
        )
        assert am.notes == "First time during tummy time!"


class TestDomainAssessment:
    def test_default_values(self):
        da = DomainAssessment(domain=DevelopmentDomain.MOTOR)
        assert da.achieved_count == 0
        assert da.expected_count == 0
        assert da.percentage == 0.0
        assert da.concern_level == ConcernLevel.NONE
        assert da.missed_milestones == []
        assert da.upcoming_milestones == []


class TestAssessment:
    def test_create_assessment(self):
        a = Assessment(
            child_name="Emma",
            age_months=6.0,
        )
        assert a.child_name == "Emma"
        assert a.overall_concern_level == ConcernLevel.NONE
        assert a.overall_percentile is None


class TestConcernLevel:
    def test_concern_ordering(self):
        levels = [
            ConcernLevel.NONE,
            ConcernLevel.MONITOR,
            ConcernLevel.MILD,
            ConcernLevel.MODERATE,
            ConcernLevel.SIGNIFICANT,
        ]
        assert len(levels) == 5
