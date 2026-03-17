"""CDC/WHO developmental milestone database for 0-36 months."""

from tinysteps.models import DevelopmentDomain, Milestone


class MilestoneDatabase:
    """Database of CDC/WHO developmental milestones for ages 0-36 months.

    Milestones are organized across four developmental domains:
    Motor, Cognitive, Language, and Social-Emotional.

    Based on CDC "Learn the Signs. Act Early." program and
    WHO Motor Development Study milestones.
    """

    def __init__(self) -> None:
        self._milestones: list[Milestone] = self._build_milestone_database()
        self._by_id: dict[str, Milestone] = {m.id: m for m in self._milestones}

    @property
    def all_milestones(self) -> list[Milestone]:
        """Return all milestones."""
        return list(self._milestones)

    def get_by_id(self, milestone_id: str) -> Milestone | None:
        """Get a milestone by its ID."""
        return self._by_id.get(milestone_id)

    def get_by_domain(self, domain: DevelopmentDomain) -> list[Milestone]:
        """Get all milestones for a given domain."""
        return [m for m in self._milestones if m.domain == domain]

    def get_expected_by_age(self, age_months: float) -> list[Milestone]:
        """Get milestones expected to be achieved by a given age in months."""
        return [m for m in self._milestones if m.expected_month_max <= age_months]

    def get_upcoming(
        self, age_months: float, lookahead_months: int = 3
    ) -> list[Milestone]:
        """Get milestones coming up in the next few months."""
        return [
            m
            for m in self._milestones
            if m.expected_month_min > age_months
            and m.expected_month_min <= age_months + lookahead_months
        ]

    def get_concern_milestones(self, age_months: float) -> list[Milestone]:
        """Get milestones that should be achieved by now (concern if missing)."""
        return [m for m in self._milestones if m.concern_if_not_by_month <= age_months]

    def search(self, query: str) -> list[Milestone]:
        """Search milestones by name or description."""
        query_lower = query.lower()
        return [
            m
            for m in self._milestones
            if query_lower in m.name.lower() or query_lower in m.description.lower()
        ]

    def _build_milestone_database(self) -> list[Milestone]:
        """Build the complete CDC/WHO milestone database."""
        milestones: list[Milestone] = []
        milestones.extend(self._motor_milestones())
        milestones.extend(self._cognitive_milestones())
        milestones.extend(self._language_milestones())
        milestones.extend(self._social_milestones())
        return milestones

    def _motor_milestones(self) -> list[Milestone]:
        """CDC/WHO motor development milestones 0-36 months."""
        return [
            # 0-2 months
            Milestone(
                id="motor-head-lift-prone",
                name="Lifts head when on tummy",
                description="When placed on tummy, baby can briefly lift head off the surface",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=0,
                expected_month_max=1,
                concern_if_not_by_month=2,
            ),
            Milestone(
                id="motor-smooth-arm-movements",
                name="Makes smoother arm movements",
                description="Arm movements become less jerky and more fluid",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=1,
                expected_month_max=2,
                concern_if_not_by_month=3,
            ),
            # 2-4 months
            Milestone(
                id="motor-head-steady",
                name="Holds head steady unsupported",
                description="Can hold head steady without support when held upright",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=2,
                expected_month_max=4,
                concern_if_not_by_month=4,
            ),
            Milestone(
                id="motor-pushes-down-legs",
                name="Pushes down on legs on hard surface",
                description="When feet are on a hard surface, pushes down with legs",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=2,
                expected_month_max=4,
                concern_if_not_by_month=5,
            ),
            Milestone(
                id="motor-hands-to-mouth",
                name="Brings hands to mouth",
                description="Can bring hands to mouth deliberately",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=2,
                expected_month_max=4,
                concern_if_not_by_month=4,
            ),
            Milestone(
                id="motor-pushes-up-tummy",
                name="Pushes up on arms during tummy time",
                description="Can push up to elbows or hands when on tummy",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=3,
                expected_month_max=4,
                concern_if_not_by_month=5,
            ),
            # 4-6 months
            Milestone(
                id="motor-rolls-tummy-to-back",
                name="Rolls from tummy to back",
                description="Can roll over from tummy to back independently",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=3,
                expected_month_max=5,
                concern_if_not_by_month=6,
            ),
            Milestone(
                id="motor-rolls-back-to-tummy",
                name="Rolls from back to tummy",
                description="Can roll over from back to tummy independently",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=4,
                expected_month_max=6,
                concern_if_not_by_month=7,
            ),
            Milestone(
                id="motor-reaches-grasps-toy",
                name="Reaches for and grasps toy",
                description="Reaches for a toy and can grasp it",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=3,
                expected_month_max=5,
                concern_if_not_by_month=6,
            ),
            Milestone(
                id="motor-transfers-hand-to-hand",
                name="Transfers objects between hands",
                description="Can pass a toy or object from one hand to the other",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=5,
                expected_month_max=7,
                concern_if_not_by_month=8,
            ),
            # 6-9 months
            Milestone(
                id="motor-sits-without-support",
                name="Sits without support",
                description="Can sit independently without using hands for support",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=5,
                expected_month_max=7,
                concern_if_not_by_month=9,
            ),
            Milestone(
                id="motor-raking-grasp",
                name="Uses raking grasp",
                description="Rakes small objects toward self with fingers",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=6,
                expected_month_max=8,
                concern_if_not_by_month=9,
            ),
            Milestone(
                id="motor-stands-with-support",
                name="Stands holding on to something",
                description="Pulls to standing and can stand while holding furniture",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=6,
                expected_month_max=9,
                concern_if_not_by_month=10,
            ),
            # 9-12 months
            Milestone(
                id="motor-crawls",
                name="Crawls",
                description="Moves forward on hands and knees or by scooting",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=7,
                expected_month_max=10,
                concern_if_not_by_month=12,
            ),
            Milestone(
                id="motor-pincer-grasp",
                name="Uses pincer grasp",
                description="Picks up small objects between thumb and index finger",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=8,
                expected_month_max=10,
                concern_if_not_by_month=12,
            ),
            Milestone(
                id="motor-pulls-to-stand",
                name="Pulls to stand",
                description="Pulls self up to standing position using furniture",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=8,
                expected_month_max=10,
                concern_if_not_by_month=12,
            ),
            Milestone(
                id="motor-cruises",
                name="Cruises along furniture",
                description="Walks while holding onto furniture for support",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=8,
                expected_month_max=11,
                concern_if_not_by_month=13,
            ),
            # 12-18 months
            Milestone(
                id="motor-walks-independently",
                name="Walks independently",
                description="Takes several independent steps without holding on",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=9,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="motor-stoops-to-pick-up",
                name="Stoops to pick up objects",
                description="Bends over or squats to pick up a toy and stands back up",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="motor-stacks-two-blocks",
                name="Stacks two blocks",
                description="Can stack at least two small blocks on top of each other",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="motor-drinks-from-cup",
                name="Drinks from cup",
                description="Can drink from an open cup with some spilling",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="motor-uses-spoon",
                name="Feeds self with spoon",
                description="Attempts to use a spoon to feed self, with some spilling",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=13,
                expected_month_max=18,
                concern_if_not_by_month=21,
            ),
            # 18-24 months
            Milestone(
                id="motor-walks-up-stairs-help",
                name="Walks up stairs with help",
                description="Can walk up steps with an adult holding hand or using railing",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=16,
                expected_month_max=20,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="motor-runs",
                name="Runs",
                description="Can run, though may not be fully coordinated",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=14,
                expected_month_max=20,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="motor-kicks-ball",
                name="Kicks a ball",
                description="Can kick a ball forward",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=18,
                expected_month_max=22,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="motor-stacks-four-blocks",
                name="Stacks four or more blocks",
                description="Can stack at least four small blocks into a tower",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=18,
                expected_month_max=22,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="motor-scribbles",
                name="Scribbles with crayon",
                description="Can make marks on paper with a crayon or marker",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=15,
                expected_month_max=18,
                concern_if_not_by_month=21,
            ),
            # 24-36 months
            Milestone(
                id="motor-jumps-both-feet",
                name="Jumps off the ground with both feet",
                description="Can jump up with both feet leaving the ground",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=22,
                expected_month_max=28,
                concern_if_not_by_month=30,
            ),
            Milestone(
                id="motor-walks-up-stairs-alternating",
                name="Walks up stairs alternating feet",
                description="Goes up stairs placing one foot on each step",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=36,
            ),
            Milestone(
                id="motor-pedals-tricycle",
                name="Pedals a tricycle",
                description="Can pedal a tricycle or similar ride-on toy",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=36,
            ),
            Milestone(
                id="motor-turns-pages",
                name="Turns book pages one at a time",
                description="Can turn the pages of a book one page at a time",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=23,
                expected_month_max=28,
                concern_if_not_by_month=30,
            ),
            Milestone(
                id="motor-copies-circle",
                name="Copies a circle",
                description="Can draw or copy a circle shape",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=30,
                expected_month_max=36,
                concern_if_not_by_month=36,
            ),
            Milestone(
                id="motor-strings-beads",
                name="Strings large beads",
                description="Can thread large beads onto a string",
                domain=DevelopmentDomain.MOTOR,
                expected_month_min=28,
                expected_month_max=34,
                concern_if_not_by_month=36,
            ),
        ]

    def _cognitive_milestones(self) -> list[Milestone]:
        """CDC/WHO cognitive development milestones 0-36 months."""
        return [
            # 0-2 months
            Milestone(
                id="cog-focuses-face",
                name="Focuses on faces",
                description="Can focus on a face within 8-12 inches",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=0,
                expected_month_max=1,
                concern_if_not_by_month=2,
            ),
            Milestone(
                id="cog-follows-moving-object",
                name="Follows moving objects with eyes",
                description="Visually tracks a slowly moving object or face",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=1,
                expected_month_max=2,
                concern_if_not_by_month=3,
            ),
            Milestone(
                id="cog-recognizes-people",
                name="Recognizes familiar people at a distance",
                description="Shows recognition of familiar faces and objects",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=2,
                expected_month_max=4,
                concern_if_not_by_month=5,
            ),
            # 4-6 months
            Milestone(
                id="cog-mouths-objects",
                name="Brings things to mouth to explore",
                description="Explores objects by putting them in mouth",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=3,
                expected_month_max=5,
                concern_if_not_by_month=6,
            ),
            Milestone(
                id="cog-reaches-with-one-hand",
                name="Reaches for toy with one hand",
                description="Reaches for a toy using one hand purposefully",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=4,
                expected_month_max=6,
                concern_if_not_by_month=7,
            ),
            Milestone(
                id="cog-shows-curiosity",
                name="Shows curiosity and tries to get out-of-reach things",
                description="Actively tries to get objects that are out of reach",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=5,
                expected_month_max=7,
                concern_if_not_by_month=8,
            ),
            # 6-9 months
            Milestone(
                id="cog-object-permanence",
                name="Looks for hidden objects",
                description="Understands object permanence - looks for a toy that has been hidden",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=6,
                expected_month_max=9,
                concern_if_not_by_month=10,
            ),
            Milestone(
                id="cog-cause-effect",
                name="Explores cause and effect",
                description="Bangs, shakes, and throws objects to see what happens",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=7,
                expected_month_max=9,
                concern_if_not_by_month=11,
            ),
            Milestone(
                id="cog-watches-falling-object",
                name="Watches path of falling object",
                description="Visually follows an object as it falls",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=6,
                expected_month_max=8,
                concern_if_not_by_month=10,
            ),
            # 9-12 months
            Milestone(
                id="cog-finds-hidden-object",
                name="Finds hidden objects easily",
                description="Can find an object after seeing it hidden under a cover",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=8,
                expected_month_max=10,
                concern_if_not_by_month=12,
            ),
            Milestone(
                id="cog-explores-objects",
                name="Explores objects in many ways",
                description="Shakes, bangs, throws, and drops objects to explore them",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=9,
                expected_month_max=12,
                concern_if_not_by_month=14,
            ),
            Milestone(
                id="cog-puts-in-container",
                name="Puts things in and out of container",
                description="Deliberately puts objects into a container and takes them out",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=9,
                expected_month_max=12,
                concern_if_not_by_month=15,
            ),
            Milestone(
                id="cog-pokes-with-finger",
                name="Pokes with index finger",
                description="Uses index finger to poke and explore objects",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=9,
                expected_month_max=12,
                concern_if_not_by_month=14,
            ),
            # 12-18 months
            Milestone(
                id="cog-uses-objects-correctly",
                name="Uses objects correctly",
                description="Uses everyday objects correctly (phone, cup, brush)",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="cog-simple-pretend-play",
                name="Simple pretend play",
                description="Engages in simple pretend play like feeding a doll",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=14,
                expected_month_max=18,
                concern_if_not_by_month=21,
            ),
            Milestone(
                id="cog-points-to-show",
                name="Points to show interest",
                description="Points at things to show you something interesting",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            # 18-24 months
            Milestone(
                id="cog-simple-shape-sorter",
                name="Uses simple shape sorter",
                description="Can match shapes to holes in a shape sorter",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=18,
                expected_month_max=22,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="cog-completes-puzzle",
                name="Completes simple puzzles",
                description="Can complete puzzles with 3-4 pieces",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=20,
                expected_month_max=24,
                concern_if_not_by_month=27,
            ),
            Milestone(
                id="cog-names-picture",
                name="Names items in a picture book",
                description="Can point to and name familiar pictures in a book",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=18,
                expected_month_max=22,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="cog-stacks-rings",
                name="Stacks rings on peg in order",
                description="Places rings on a stacking toy in size order",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=18,
                expected_month_max=24,
                concern_if_not_by_month=27,
            ),
            # 24-36 months
            Milestone(
                id="cog-sorts-shapes-colors",
                name="Sorts shapes and colors",
                description="Can sort objects by shape and color",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="cog-pretend-play-complex",
                name="Plays make-believe with dolls and animals",
                description="Engages in complex pretend play with imagination",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="cog-completes-3-4-puzzle",
                name="Completes 3-4 piece puzzles",
                description="Can complete puzzles with 3-4 interlocking pieces",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="cog-turns-door-handles",
                name="Turns door handles and screws lids",
                description="Can turn knobs, handles, and screw/unscrew lids",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="cog-understands-two",
                name="Understands concept of 'two'",
                description="Begins to understand the concept of counting and 'two'",
                domain=DevelopmentDomain.COGNITIVE,
                expected_month_min=30,
                expected_month_max=36,
                concern_if_not_by_month=36,
            ),
        ]

    def _language_milestones(self) -> list[Milestone]:
        """CDC/WHO language development milestones 0-36 months."""
        return [
            # 0-2 months
            Milestone(
                id="lang-startles-sounds",
                name="Startles at loud sounds",
                description="Reacts to loud sounds by startling or crying",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=0,
                expected_month_max=1,
                concern_if_not_by_month=2,
            ),
            Milestone(
                id="lang-coos",
                name="Coos and makes gurgling sounds",
                description="Makes cooing and gurgling vowel sounds",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=1,
                expected_month_max=3,
                concern_if_not_by_month=4,
            ),
            Milestone(
                id="lang-turns-to-sounds",
                name="Turns head toward sounds",
                description="Turns head or eyes in the direction of sounds",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=2,
                expected_month_max=4,
                concern_if_not_by_month=5,
            ),
            # 4-6 months
            Milestone(
                id="lang-babbles",
                name="Babbles with consonant sounds",
                description="Makes babbling sounds with consonants like 'ba', 'da', 'ma'",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=4,
                expected_month_max=6,
                concern_if_not_by_month=7,
            ),
            Milestone(
                id="lang-responds-to-name",
                name="Responds to own name",
                description="Turns or looks when name is called",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=5,
                expected_month_max=7,
                concern_if_not_by_month=9,
            ),
            Milestone(
                id="lang-responds-to-emotions",
                name="Responds to vocal emotions",
                description="Responds differently to happy, sad, or angry tones of voice",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=5,
                expected_month_max=7,
                concern_if_not_by_month=8,
            ),
            # 6-9 months
            Milestone(
                id="lang-strings-vowels",
                name="Strings vowels together when babbling",
                description="Makes longer babbling sounds stringing vowels: 'ah', 'eh', 'oh'",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=6,
                expected_month_max=8,
                concern_if_not_by_month=9,
            ),
            Milestone(
                id="lang-understands-no",
                name="Understands 'no'",
                description="Shows understanding of the word 'no' by pausing or stopping",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=7,
                expected_month_max=9,
                concern_if_not_by_month=10,
            ),
            Milestone(
                id="lang-mama-dada-nonspecific",
                name="Says 'mama' or 'dada' nonspecifically",
                description="Says 'mama' or 'dada' but not yet directed at parents",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=7,
                expected_month_max=9,
                concern_if_not_by_month=10,
            ),
            # 9-12 months
            Milestone(
                id="lang-mama-dada-specific",
                name="Says 'mama' and 'dada' for the right parent",
                description="Uses 'mama' and 'dada' specifically for the correct parent",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=9,
                expected_month_max=12,
                concern_if_not_by_month=14,
            ),
            Milestone(
                id="lang-responds-simple-requests",
                name="Responds to simple spoken requests",
                description="Can follow simple verbal instructions like 'come here'",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=9,
                expected_month_max=12,
                concern_if_not_by_month=14,
            ),
            Milestone(
                id="lang-uses-gestures",
                name="Uses simple gestures",
                description="Uses gestures like waving bye-bye and shaking head no",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=9,
                expected_month_max=12,
                concern_if_not_by_month=14,
            ),
            Milestone(
                id="lang-tries-repeat-words",
                name="Tries to repeat words",
                description="Attempts to copy or repeat words you say",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=10,
                expected_month_max=13,
                concern_if_not_by_month=15,
            ),
            # 12-18 months
            Milestone(
                id="lang-one-to-three-words",
                name="Says 1-3 words besides 'mama' and 'dada'",
                description="Has vocabulary of a few single words used meaningfully",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="lang-points-body-parts",
                name="Points to one body part",
                description="Can point to at least one body part when asked",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=14,
                expected_month_max=18,
                concern_if_not_by_month=20,
            ),
            Milestone(
                id="lang-follows-one-step",
                name="Follows one-step directions",
                description="Follows simple one-step verbal instructions without gestures",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=14,
                expected_month_max=18,
                concern_if_not_by_month=21,
            ),
            # 18-24 months
            Milestone(
                id="lang-ten-words",
                name="Says at least 10 words",
                description="Uses 10 or more single words meaningfully",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=18,
                expected_month_max=21,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="lang-points-named-objects",
                name="Points to things in a book when named",
                description="Can identify named pictures or objects by pointing",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=18,
                expected_month_max=21,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="lang-two-word-phrases",
                name="Says two-word phrases",
                description="Combines two words like 'more milk' or 'daddy go'",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=18,
                expected_month_max=24,
                concern_if_not_by_month=27,
            ),
            Milestone(
                id="lang-points-body-parts-named",
                name="Points to at least two body parts when named",
                description="Can identify and point to multiple body parts on request",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=18,
                expected_month_max=22,
                concern_if_not_by_month=24,
            ),
            # 24-36 months
            Milestone(
                id="lang-two-to-four-word-sentences",
                name="Uses 2-4 word sentences",
                description="Speaks in short sentences of two to four words",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="lang-follows-two-step",
                name="Follows two-step instructions",
                description="Can follow two-step instructions like 'pick up the ball and put it on the table'",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="lang-names-familiar-items",
                name="Names items in a picture book",
                description="Can name many familiar items when looking at picture books",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=24,
                expected_month_max=28,
                concern_if_not_by_month=30,
            ),
            Milestone(
                id="lang-strangers-understand",
                name="Strangers can understand most words",
                description="Speech is clear enough that strangers understand most of it",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=36,
            ),
            Milestone(
                id="lang-says-first-name",
                name="Says first name",
                description="Can say their own first name when asked",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=27,
                expected_month_max=33,
                concern_if_not_by_month=36,
            ),
            Milestone(
                id="lang-uses-pronouns",
                name="Uses pronouns (I, me, you)",
                description="Starts using pronouns like I, me, you, we in speech",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=36,
            ),
            Milestone(
                id="lang-asks-what-where-who",
                name="Asks 'what', 'where', 'who' questions",
                description="Begins asking simple questions starting with what, where, who",
                domain=DevelopmentDomain.LANGUAGE,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=36,
            ),
        ]

    def _social_milestones(self) -> list[Milestone]:
        """CDC/WHO social-emotional development milestones 0-36 months."""
        return [
            # 0-2 months
            Milestone(
                id="social-social-smile",
                name="Social smile",
                description="Smiles spontaneously in response to people",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=1,
                expected_month_max=2,
                concern_if_not_by_month=3,
            ),
            Milestone(
                id="social-self-soothes",
                name="Begins to self-soothe",
                description="May bring hands to mouth or suck on fist to calm down",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=1,
                expected_month_max=3,
                concern_if_not_by_month=4,
            ),
            # 2-4 months
            Milestone(
                id="social-smiles-spontaneously",
                name="Smiles spontaneously at people",
                description="Freely and regularly smiles at familiar faces",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=2,
                expected_month_max=4,
                concern_if_not_by_month=5,
            ),
            Milestone(
                id="social-enjoys-playing",
                name="Enjoys playing with people",
                description="Actively engages with and enjoys interacting with people",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=3,
                expected_month_max=5,
                concern_if_not_by_month=6,
            ),
            Milestone(
                id="social-copies-movements",
                name="Copies some movements and facial expressions",
                description="Imitates smiles, frowns, or facial movements",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=3,
                expected_month_max=5,
                concern_if_not_by_month=6,
            ),
            # 4-6 months
            Milestone(
                id="social-mirror-smile",
                name="Likes to look at self in mirror",
                description="Shows interest and smiles at own reflection",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=4,
                expected_month_max=6,
                concern_if_not_by_month=7,
            ),
            Milestone(
                id="social-laughs",
                name="Laughs",
                description="Produces social laughter in response to interactions",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=3,
                expected_month_max=5,
                concern_if_not_by_month=6,
            ),
            # 6-9 months
            Milestone(
                id="social-stranger-anxiety",
                name="Shows stranger anxiety",
                description="May be anxious or clingy around unfamiliar people",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=6,
                expected_month_max=9,
                concern_if_not_by_month=12,
            ),
            Milestone(
                id="social-has-favorites",
                name="Has favorite toys",
                description="Shows clear preference for certain toys over others",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=6,
                expected_month_max=9,
                concern_if_not_by_month=12,
            ),
            Milestone(
                id="social-peekaboo",
                name="Plays peek-a-boo",
                description="Enjoys and participates in peek-a-boo games",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=6,
                expected_month_max=9,
                concern_if_not_by_month=12,
            ),
            # 9-12 months
            Milestone(
                id="social-separation-anxiety",
                name="Shows separation anxiety",
                description="Becomes upset when familiar caregivers leave",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=8,
                expected_month_max=12,
                concern_if_not_by_month=14,
            ),
            Milestone(
                id="social-clings-to-adults",
                name="Clings to familiar adults",
                description="Holds onto or clings to familiar caregivers",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=8,
                expected_month_max=12,
                concern_if_not_by_month=14,
            ),
            Milestone(
                id="social-repeats-for-attention",
                name="Repeats actions that get attention",
                description="Deliberately repeats actions that get laughs or reactions",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=9,
                expected_month_max=12,
                concern_if_not_by_month=15,
            ),
            # 12-18 months
            Milestone(
                id="social-hands-you-book",
                name="Hands you a book to read",
                description="Brings objects to show or share, wants you to read",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="social-plays-pat-a-cake",
                name="Plays simple pretend games",
                description="Engages in simple pretend and imitative games",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=12,
                expected_month_max=15,
                concern_if_not_by_month=18,
            ),
            Milestone(
                id="social-shows-affection",
                name="Shows affection to familiar people",
                description="Hugs, cuddles, or kisses familiar people",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=12,
                expected_month_max=18,
                concern_if_not_by_month=21,
            ),
            Milestone(
                id="social-explores-with-parent-near",
                name="Explores with parent nearby",
                description="Moves away from parent but checks back frequently",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=14,
                expected_month_max=18,
                concern_if_not_by_month=21,
            ),
            # 18-24 months
            Milestone(
                id="social-temper-tantrums",
                name="May have temper tantrums",
                description="Displays strong emotions including tantrums when frustrated",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=15,
                expected_month_max=20,
                concern_if_not_by_month=24,
            ),
            Milestone(
                id="social-plays-alongside",
                name="Plays alongside other children",
                description="Engages in parallel play - plays near other children",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=18,
                expected_month_max=24,
                concern_if_not_by_month=27,
            ),
            Milestone(
                id="social-shows-defiance",
                name="Shows increasing independence",
                description="Says 'no' to adults and shows desire for independence",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=18,
                expected_month_max=22,
                concern_if_not_by_month=24,
            ),
            # 24-36 months
            Milestone(
                id="social-copies-adults",
                name="Copies adults and friends",
                description="Imitates adults and other children in play and behavior",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=24,
                expected_month_max=28,
                concern_if_not_by_month=30,
            ),
            Milestone(
                id="social-takes-turns",
                name="Takes turns in games",
                description="Can take turns during simple games and activities",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="social-shows-concern",
                name="Shows concern for crying friend",
                description="Displays empathy and concern when others are upset",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="social-wide-range-emotions",
                name="Shows wide range of emotions",
                description="Expresses many emotions: happy, sad, angry, surprised",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=24,
                expected_month_max=30,
                concern_if_not_by_month=33,
            ),
            Milestone(
                id="social-separates-easily",
                name="Separates easily from parents",
                description="Can separate from parents without excessive distress",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=30,
                expected_month_max=36,
                concern_if_not_by_month=36,
            ),
            Milestone(
                id="social-plays-with-children",
                name="Plays with other children",
                description="Engages in cooperative play with other children",
                domain=DevelopmentDomain.SOCIAL,
                expected_month_min=30,
                expected_month_max=36,
                concern_if_not_by_month=36,
            ),
        ]
