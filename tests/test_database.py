"""Tests for milestone database."""

from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import DevelopmentDomain


class TestMilestoneDatabase:
    def setup_method(self):
        self.db = MilestoneDatabase()

    def test_has_milestones(self):
        assert len(self.db.all_milestones) > 50

    def test_all_domains_represented(self):
        domains = {m.domain for m in self.db.all_milestones}
        assert DevelopmentDomain.MOTOR in domains
        assert DevelopmentDomain.COGNITIVE in domains
        assert DevelopmentDomain.LANGUAGE in domains
        assert DevelopmentDomain.SOCIAL in domains

    def test_get_by_id(self):
        m = self.db.get_by_id("motor-walks-independently")
        assert m is not None
        assert m.name == "Walks independently"
        assert m.domain == DevelopmentDomain.MOTOR

    def test_get_by_id_not_found(self):
        assert self.db.get_by_id("nonexistent") is None

    def test_get_by_domain(self):
        motor = self.db.get_by_domain(DevelopmentDomain.MOTOR)
        assert len(motor) > 10
        assert all(m.domain == DevelopmentDomain.MOTOR for m in motor)

    def test_get_expected_by_age(self):
        # At 12 months, many milestones should be expected
        expected = self.db.get_expected_by_age(12)
        assert len(expected) > 10

        # All expected milestones should have max_month <= 12
        for m in expected:
            assert m.expected_month_max <= 12

    def test_get_expected_by_age_zero(self):
        expected = self.db.get_expected_by_age(0)
        assert len(expected) == 0

    def test_get_upcoming(self):
        upcoming = self.db.get_upcoming(6, lookahead_months=3)
        assert len(upcoming) > 0
        for m in upcoming:
            assert m.expected_month_min > 6
            assert m.expected_month_min <= 9

    def test_get_concern_milestones(self):
        concerns = self.db.get_concern_milestones(12)
        assert len(concerns) > 5
        for m in concerns:
            assert m.concern_if_not_by_month <= 12

    def test_search(self):
        results = self.db.search("walk")
        assert len(results) > 0
        assert any("walk" in m.name.lower() or "walk" in m.description.lower() for m in results)

    def test_search_no_results(self):
        results = self.db.search("xyznonexistent")
        assert len(results) == 0

    def test_milestone_age_consistency(self):
        """Verify that expected_month_min <= expected_month_max <= concern_if_not_by_month."""
        for m in self.db.all_milestones:
            assert m.expected_month_min <= m.expected_month_max, (
                f"{m.id}: min ({m.expected_month_min}) > max ({m.expected_month_max})"
            )
            assert m.expected_month_max <= m.concern_if_not_by_month, (
                f"{m.id}: max ({m.expected_month_max}) > concern ({m.concern_if_not_by_month})"
            )

    def test_unique_ids(self):
        ids = [m.id for m in self.db.all_milestones]
        assert len(ids) == len(set(ids)), "Duplicate milestone IDs found"

    def test_covers_0_to_36_months(self):
        """Verify milestones cover the full 0-36 month range."""
        milestones = self.db.all_milestones
        min_month = min(m.expected_month_min for m in milestones)
        max_month = max(m.expected_month_max for m in milestones)
        assert min_month == 0
        assert max_month == 36
