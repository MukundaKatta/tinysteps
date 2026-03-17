"""Milestone tracking functionality."""

import json
from datetime import date
from pathlib import Path
from typing import Optional

from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import AchievedMilestone, Child


class MilestoneTracker:
    """Tracks achieved milestones for children with persistent storage.

    Manages child profiles and logs achieved milestones with dates
    and optional notes. Data is stored in a JSON file.
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self.db = MilestoneDatabase()
        self.data_dir = data_dir or Path.home() / ".tinysteps"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._data_file = self.data_dir / "children.json"
        self._children: dict[str, Child] = {}
        self._load()

    def _load(self) -> None:
        """Load children data from disk."""
        if self._data_file.exists():
            data = json.loads(self._data_file.read_text())
            for name, child_data in data.items():
                self._children[name] = Child.model_validate(child_data)

    def _save(self) -> None:
        """Save children data to disk."""
        data = {
            name: child.model_dump(mode="json")
            for name, child in self._children.items()
        }
        self._data_file.write_text(json.dumps(data, indent=2, default=str))

    def add_child(self, name: str, birthdate: date) -> Child:
        """Add a new child profile."""
        if name in self._children:
            raise ValueError(f"Child '{name}' already exists")
        child = Child(name=name, birthdate=birthdate)
        self._children[name] = child
        self._save()
        return child

    def get_child(self, name: str) -> Child:
        """Get a child by name."""
        if name not in self._children:
            raise KeyError(f"Child '{name}' not found")
        return self._children[name]

    def list_children(self) -> list[Child]:
        """List all tracked children."""
        return list(self._children.values())

    def remove_child(self, name: str) -> None:
        """Remove a child profile."""
        if name not in self._children:
            raise KeyError(f"Child '{name}' not found")
        del self._children[name]
        self._save()

    def log_milestone(
        self,
        child_name: str,
        milestone_id: str,
        achieved_date: date,
        notes: Optional[str] = None,
    ) -> AchievedMilestone:
        """Log that a child has achieved a milestone.

        Args:
            child_name: Name of the child.
            milestone_id: ID of the milestone achieved.
            achieved_date: Date the milestone was achieved.
            notes: Optional notes about the achievement.

        Returns:
            The recorded AchievedMilestone.

        Raises:
            KeyError: If child or milestone not found.
            ValueError: If milestone already logged.
        """
        child = self.get_child(child_name)
        milestone = self.db.get_by_id(milestone_id)
        if milestone is None:
            raise KeyError(f"Milestone '{milestone_id}' not found")

        # Check for duplicate
        existing_ids = {am.milestone_id for am in child.achieved_milestones}
        if milestone_id in existing_ids:
            raise ValueError(
                f"Milestone '{milestone_id}' already logged for {child_name}"
            )

        achieved = AchievedMilestone(
            milestone_id=milestone_id,
            achieved_date=achieved_date,
            notes=notes,
        )
        child.achieved_milestones.append(achieved)
        self._save()
        return achieved

    def remove_milestone(self, child_name: str, milestone_id: str) -> None:
        """Remove a logged milestone from a child's record."""
        child = self.get_child(child_name)
        original_count = len(child.achieved_milestones)
        child.achieved_milestones = [
            am for am in child.achieved_milestones if am.milestone_id != milestone_id
        ]
        if len(child.achieved_milestones) == original_count:
            raise KeyError(
                f"Milestone '{milestone_id}' not found for {child_name}"
            )
        self._save()

    def get_achieved_milestones(self, child_name: str) -> list[AchievedMilestone]:
        """Get all achieved milestones for a child."""
        child = self.get_child(child_name)
        return child.achieved_milestones

    def get_achieved_milestone_ids(self, child_name: str) -> set[str]:
        """Get the set of achieved milestone IDs for a child."""
        child = self.get_child(child_name)
        return {am.milestone_id for am in child.achieved_milestones}

    def get_pending_milestones(self, child_name: str) -> list:
        """Get milestones expected by the child's age but not yet achieved."""
        child = self.get_child(child_name)
        achieved_ids = self.get_achieved_milestone_ids(child_name)
        expected = self.db.get_expected_by_age(child.age_in_months)
        return [m for m in expected if m.id not in achieved_ids]
