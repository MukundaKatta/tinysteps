"""Data models for TinySteps milestone tracker."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DevelopmentDomain(str, Enum):
    """Developmental domains for milestone tracking."""

    MOTOR = "motor"
    COGNITIVE = "cognitive"
    LANGUAGE = "language"
    SOCIAL = "social"


class Milestone(BaseModel):
    """A developmental milestone based on CDC/WHO guidelines."""

    id: str = Field(description="Unique milestone identifier")
    name: str = Field(description="Human-readable milestone name")
    description: str = Field(description="Detailed description of the milestone")
    domain: DevelopmentDomain = Field(description="Developmental domain")
    expected_month_min: int = Field(
        description="Earliest typical month for achieving this milestone"
    )
    expected_month_max: int = Field(
        description="Latest typical month before concern is warranted"
    )
    concern_if_not_by_month: int = Field(
        description="Month by which absence may indicate a delay"
    )


class AchievedMilestone(BaseModel):
    """A milestone that has been achieved by a child."""

    milestone_id: str
    achieved_date: date
    notes: Optional[str] = None


class Child(BaseModel):
    """A child profile for milestone tracking."""

    name: str = Field(description="Child's name")
    birthdate: date = Field(description="Child's date of birth")
    achieved_milestones: list[AchievedMilestone] = Field(default_factory=list)

    @property
    def age_in_months(self) -> float:
        """Calculate child's current age in months."""
        today = date.today()
        months = (today.year - self.birthdate.year) * 12 + (
            today.month - self.birthdate.month
        )
        day_fraction = (today.day - self.birthdate.day) / 30.0
        return months + day_fraction

    def age_in_months_at(self, at_date: date) -> float:
        """Calculate child's age in months at a specific date."""
        months = (at_date.year - self.birthdate.year) * 12 + (
            at_date.month - self.birthdate.month
        )
        day_fraction = (at_date.day - self.birthdate.day) / 30.0
        return months + day_fraction


class ConcernLevel(str, Enum):
    """Level of developmental concern."""

    NONE = "none"
    MONITOR = "monitor"
    MILD = "mild"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"


class DomainAssessment(BaseModel):
    """Assessment result for a single developmental domain."""

    domain: DevelopmentDomain
    achieved_count: int = 0
    expected_count: int = 0
    percentage: float = 0.0
    concern_level: ConcernLevel = ConcernLevel.NONE
    missed_milestones: list[Milestone] = Field(default_factory=list)
    upcoming_milestones: list[Milestone] = Field(default_factory=list)


class Assessment(BaseModel):
    """Complete developmental assessment for a child."""

    child_name: str
    assessment_date: date = Field(default_factory=date.today)
    age_months: float
    domain_assessments: dict[DevelopmentDomain, DomainAssessment] = Field(
        default_factory=dict
    )
    overall_concern_level: ConcernLevel = ConcernLevel.NONE
    overall_percentile: Optional[float] = None
    recommendations: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
