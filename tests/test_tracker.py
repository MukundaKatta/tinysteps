"""Tests for milestone tracker."""

import tempfile
from datetime import date
from pathlib import Path

import pytest

from tinysteps.milestones.tracker import MilestoneTracker


class TestMilestoneTracker:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tracker = MilestoneTracker(data_dir=Path(self.tmp_dir))

    def test_add_child(self):
        child = self.tracker.add_child("Emma", date(2025, 1, 15))
        assert child.name == "Emma"
        assert child.birthdate == date(2025, 1, 15)

    def test_add_duplicate_child(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        with pytest.raises(ValueError):
            self.tracker.add_child("Emma", date(2025, 6, 1))

    def test_get_child(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        child = self.tracker.get_child("Emma")
        assert child.name == "Emma"

    def test_get_child_not_found(self):
        with pytest.raises(KeyError):
            self.tracker.get_child("Nonexistent")

    def test_list_children(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        self.tracker.add_child("Liam", date(2025, 3, 20))
        children = self.tracker.list_children()
        assert len(children) == 2

    def test_remove_child(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        self.tracker.remove_child("Emma")
        assert len(self.tracker.list_children()) == 0

    def test_remove_child_not_found(self):
        with pytest.raises(KeyError):
            self.tracker.remove_child("Nonexistent")

    def test_log_milestone(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        achieved = self.tracker.log_milestone(
            "Emma", "motor-head-lift-prone", date(2025, 2, 1)
        )
        assert achieved.milestone_id == "motor-head-lift-prone"
        assert achieved.achieved_date == date(2025, 2, 1)

    def test_log_milestone_with_notes(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        achieved = self.tracker.log_milestone(
            "Emma", "motor-head-lift-prone", date(2025, 2, 1), notes="First time!"
        )
        assert achieved.notes == "First time!"

    def test_log_milestone_invalid_child(self):
        with pytest.raises(KeyError):
            self.tracker.log_milestone("Nonexistent", "motor-head-lift-prone", date(2025, 2, 1))

    def test_log_milestone_invalid_milestone(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        with pytest.raises(KeyError):
            self.tracker.log_milestone("Emma", "nonexistent-milestone", date(2025, 2, 1))

    def test_log_duplicate_milestone(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        self.tracker.log_milestone("Emma", "motor-head-lift-prone", date(2025, 2, 1))
        with pytest.raises(ValueError):
            self.tracker.log_milestone("Emma", "motor-head-lift-prone", date(2025, 3, 1))

    def test_get_achieved_milestones(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        self.tracker.log_milestone("Emma", "motor-head-lift-prone", date(2025, 2, 1))
        self.tracker.log_milestone("Emma", "motor-head-steady", date(2025, 4, 1))
        achieved = self.tracker.get_achieved_milestones("Emma")
        assert len(achieved) == 2

    def test_get_achieved_milestone_ids(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        self.tracker.log_milestone("Emma", "motor-head-lift-prone", date(2025, 2, 1))
        ids = self.tracker.get_achieved_milestone_ids("Emma")
        assert "motor-head-lift-prone" in ids

    def test_remove_milestone(self):
        self.tracker.add_child("Emma", date(2025, 1, 15))
        self.tracker.log_milestone("Emma", "motor-head-lift-prone", date(2025, 2, 1))
        self.tracker.remove_milestone("Emma", "motor-head-lift-prone")
        assert len(self.tracker.get_achieved_milestones("Emma")) == 0

    def test_persistence(self):
        """Data should persist across tracker instances."""
        self.tracker.add_child("Emma", date(2025, 1, 15))
        self.tracker.log_milestone("Emma", "motor-head-lift-prone", date(2025, 2, 1))

        # Create new tracker with same data dir
        tracker2 = MilestoneTracker(data_dir=Path(self.tmp_dir))
        child = tracker2.get_child("Emma")
        assert child.name == "Emma"
        assert len(child.achieved_milestones) == 1

    def test_get_pending_milestones(self):
        self.tracker.add_child("Emma", date(2024, 1, 1))
        # Don't log any milestones - all should be pending
        pending = self.tracker.get_pending_milestones("Emma")
        assert len(pending) > 0
