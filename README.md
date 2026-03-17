# TinySteps - Baby Milestone Tracker

A comprehensive developmental milestone tracker for babies aged 0-36 months, based on CDC/WHO guidelines.

## Features

- Track developmental milestones across four domains: Motor, Cognitive, Language, and Social-Emotional
- Compare your child's progress against CDC/WHO expected timelines
- Detect potential developmental delays early
- Calculate developmental percentiles
- Get age-appropriate activity recommendations
- Generate detailed progress reports

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Add a child profile
tinysteps add-child --name "Emma" --birthdate "2025-01-15"

# Log a milestone
tinysteps log-milestone --child "Emma" --milestone "rolls-over" --date "2025-05-20"

# Check developmental assessment
tinysteps assess --child "Emma"

# Get activity recommendations
tinysteps recommend --child "Emma"

# Generate a progress report
tinysteps report --child "Emma"
```

## Milestone Domains

- **Motor**: Gross and fine motor skills (rolling, crawling, walking, grasping)
- **Cognitive**: Problem-solving, object permanence, cause and effect
- **Language**: Babbling, first words, sentence formation
- **Social-Emotional**: Social smiling, attachment, cooperative play

## Data Sources

Milestones are based on CDC "Learn the Signs. Act Early." program and WHO developmental standards.

## Author

Mukunda Katta
