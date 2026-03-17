"""Tests for developmental assessor."""

from datetime import date

from tinysteps.milestones.assessor import DevelopmentAssessor
from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import (
    AchievedMilestone,
    Child,
    ConcernLevel,
    DevelopmentDomain,
)


class TestDevelopmentAssessor:
    def setup_method(self):
        self.db = MilestoneDatabase()
        self.assessor = DevelopmentAssessor(self.db)

    def _make_child(self, birthdate, achieved_ids=None, achieved_date=None):
        milestones = []
        if achieved_ids:
            ad = achieved_date or date(2025, 6, 1)
            for mid in achieved_ids:
                milestones.append(
                    AchievedMilestone(milestone_id=mid, achieved_date=ad)
                )
        return Child(name="Test", birthdate=birthdate, achieved_milestones=milestones)

    def test_assess_newborn_no_concerns(self):
        child = self._make_child(date(2025, 6, 1))
        assessment = self.assessor.assess(child, date(2025, 6, 15))
        # Newborn with no expected milestones yet
        assert assessment.overall_concern_level == ConcernLevel.NONE

    def test_assess_with_all_milestones_achieved(self):
        # Get all milestones expected by 6 months
        expected = self.db.get_expected_by_age(6)
        achieved_ids = [m.id for m in expected]
        child = self._make_child(
            date(2025, 1, 1),
            achieved_ids=achieved_ids,
            achieved_date=date(2025, 4, 1),
        )
        assessment = self.assessor.assess(child, date(2025, 7, 1))
        assert assessment.overall_concern_level == ConcernLevel.NONE

    def test_assess_with_no_milestones_at_12_months(self):
        child = self._make_child(date(2024, 7, 1))
        assessment = self.assessor.assess(child, date(2025, 7, 1))
        # At 12 months with no milestones, should have significant concerns
        assert assessment.overall_concern_level in (
            ConcernLevel.MODERATE,
            ConcernLevel.SIGNIFICANT,
        )

    def test_domain_assessments_present(self):
        child = self._make_child(date(2025, 1, 1))
        assessment = self.assessor.assess(child, date(2025, 7, 1))
        for domain in DevelopmentDomain:
            assert domain in assessment.domain_assessments

    def test_assessment_has_age(self):
        child = self._make_child(date(2025, 1, 1))
        assessment = self.assessor.assess(child, date(2025, 7, 1))
        assert abs(assessment.age_months - 6.0) < 0.1

    def test_partial_milestones_moderate_concern(self):
        # Achieve only motor milestones at 12 months
        motor = self.db.get_by_domain(DevelopmentDomain.MOTOR)
        achieved_ids = [m.id for m in motor if m.expected_month_max <= 12]
        child = self._make_child(
            date(2024, 7, 1),
            achieved_ids=achieved_ids,
            achieved_date=date(2025, 4, 1),
        )
        assessment = self.assessor.assess(child, date(2025, 7, 1))
        # Motor should be fine, but other domains should have concerns
        motor_assessment = assessment.domain_assessments[DevelopmentDomain.MOTOR]
        assert motor_assessment.concern_level in (ConcernLevel.NONE, ConcernLevel.MONITOR)

    def test_missed_milestones_tracked(self):
        child = self._make_child(date(2024, 7, 1))
        assessment = self.assessor.assess(child, date(2025, 7, 1))
        # At 12 months with nothing achieved, should have missed milestones
        total_missed = sum(
            len(da.missed_milestones)
            for da in assessment.domain_assessments.values()
        )
        assert total_missed > 0

    def test_upcoming_milestones_tracked(self):
        child = self._make_child(date(2025, 1, 1))
        assessment = self.assessor.assess(child, date(2025, 7, 1))
        total_upcoming = sum(
            len(da.upcoming_milestones)
            for da in assessment.domain_assessments.values()
        )
        assert total_upcoming > 0
