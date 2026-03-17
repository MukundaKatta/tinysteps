"""Age-appropriate activity recommendations for developmental support."""

from datetime import date
from typing import Optional

from tinysteps.milestones.database import MilestoneDatabase
from tinysteps.models import Child, DevelopmentDomain, Milestone


class ActivityRecommendation:
    """A recommended activity for supporting a developmental milestone."""

    def __init__(
        self,
        milestone: Milestone,
        activity: str,
        description: str,
        materials: list[str],
        duration_minutes: int = 10,
    ) -> None:
        self.milestone = milestone
        self.activity = activity
        self.description = description
        self.materials = materials
        self.duration_minutes = duration_minutes


class ActivityRecommender:
    """Suggests age-appropriate activities to support development.

    Provides activity recommendations based on the child's current age,
    achieved milestones, and upcoming milestones. Activities are mapped
    to specific developmental milestones.
    """

    def __init__(self, db: Optional[MilestoneDatabase] = None) -> None:
        self.db = db or MilestoneDatabase()
        self._activity_map = self._build_activity_map()

    def get_recommendations(
        self,
        child: Child,
        at_date: Optional[date] = None,
        max_recommendations: int = 10,
    ) -> list[ActivityRecommendation]:
        """Get activity recommendations for a child.

        Prioritizes activities for:
        1. Milestones that are overdue (not achieved past expected age)
        2. Milestones coming up next
        3. Recently achieved milestones (to reinforce)

        Args:
            child: The child to recommend activities for.
            at_date: Date to evaluate at (defaults to today).
            max_recommendations: Maximum number of recommendations.

        Returns:
            List of ActivityRecommendation objects.
        """
        at_date = at_date or date.today()
        age_months = child.age_in_months_at(at_date)
        achieved_ids = {am.milestone_id for am in child.achieved_milestones}

        recommendations: list[ActivityRecommendation] = []

        # Priority 1: Overdue milestones
        overdue = [
            m
            for m in self.db.all_milestones
            if m.expected_month_max <= age_months and m.id not in achieved_ids
        ]
        for m in overdue:
            rec = self._get_activity(m)
            if rec:
                recommendations.append(rec)

        # Priority 2: Upcoming milestones
        upcoming = self.db.get_upcoming(age_months, lookahead_months=3)
        for m in upcoming:
            if m.id not in achieved_ids:
                rec = self._get_activity(m)
                if rec:
                    recommendations.append(rec)

        # Priority 3: Current milestones not yet achieved
        current = [
            m
            for m in self.db.all_milestones
            if m.expected_month_min <= age_months <= m.expected_month_max
            and m.id not in achieved_ids
        ]
        for m in current:
            rec = self._get_activity(m)
            if rec and rec not in recommendations:
                recommendations.append(rec)

        return recommendations[:max_recommendations]

    def get_recommendations_by_domain(
        self, child: Child, domain: DevelopmentDomain, at_date: Optional[date] = None
    ) -> list[ActivityRecommendation]:
        """Get recommendations filtered by developmental domain."""
        all_recs = self.get_recommendations(child, at_date, max_recommendations=20)
        return [r for r in all_recs if r.milestone.domain == domain]

    def _get_activity(self, milestone: Milestone) -> Optional[ActivityRecommendation]:
        """Look up an activity for a specific milestone."""
        if milestone.id in self._activity_map:
            data = self._activity_map[milestone.id]
            return ActivityRecommendation(
                milestone=milestone,
                activity=data["activity"],
                description=data["description"],
                materials=data["materials"],
                duration_minutes=data.get("duration", 10),
            )
        # Generate a generic recommendation
        return ActivityRecommendation(
            milestone=milestone,
            activity=f"Practice: {milestone.name}",
            description=f"Encourage your child to practice: {milestone.description}. "
            f"Make it fun and celebrate any progress.",
            materials=["Age-appropriate toys"],
            duration_minutes=10,
        )

    def _build_activity_map(self) -> dict[str, dict]:
        """Build activity recommendations mapped to milestone IDs."""
        return {
            # Motor activities
            "motor-head-lift-prone": {
                "activity": "Tummy Time Fun",
                "description": "Place baby on tummy on a firm surface. Get down at eye level and talk, sing, or show colorful toys. Start with 3-5 minutes and increase gradually.",
                "materials": ["Play mat", "Colorful toys", "Small mirror"],
                "duration": 5,
            },
            "motor-head-steady": {
                "activity": "Supported Sitting Practice",
                "description": "Hold baby upright on your lap supporting the trunk. Let them practice holding their head steady while you talk and make faces.",
                "materials": ["Supportive pillow"],
                "duration": 5,
            },
            "motor-rolls-tummy-to-back": {
                "activity": "Rolling Encouragement",
                "description": "During tummy time, hold a toy to one side to encourage turning. Gently guide the rolling motion. Celebrate when they roll!",
                "materials": ["Favorite toy", "Play mat"],
                "duration": 10,
            },
            "motor-reaches-grasps-toy": {
                "activity": "Reach and Grab Game",
                "description": "Hold colorful toys within arm's reach and encourage baby to reach out and grab them. Try different textures.",
                "materials": ["Rattles", "Soft toys", "Textured objects"],
                "duration": 10,
            },
            "motor-sits-without-support": {
                "activity": "Sitting Practice with Support",
                "description": "Place baby in sitting position with pillows around for safety. Engage them with toys to encourage balance.",
                "materials": ["Pillows", "Boppy pillow", "Toys"],
                "duration": 10,
            },
            "motor-crawls": {
                "activity": "Crawling Obstacle Course",
                "description": "Place favorite toys just out of reach to motivate movement. Create a safe space with pillows to crawl over.",
                "materials": ["Pillows", "Favorite toys", "Tunnel toy"],
                "duration": 15,
            },
            "motor-pulls-to-stand": {
                "activity": "Stand-Up Play",
                "description": "Place toys on a low, sturdy table or couch. Encourage pulling up to reach them. Stay close for safety.",
                "materials": ["Low table", "Favorite toys"],
                "duration": 10,
            },
            "motor-walks-independently": {
                "activity": "Walking Practice",
                "description": "Hold both hands and walk together. Gradually reduce support to one hand, then let go briefly. Use push toys.",
                "materials": ["Push walker toy", "Soft shoes"],
                "duration": 15,
            },
            "motor-stacks-two-blocks": {
                "activity": "Block Stacking Fun",
                "description": "Show how to stack blocks and encourage imitation. Start with two blocks and celebrate success.",
                "materials": ["Soft blocks", "Stacking cups"],
                "duration": 10,
            },
            "motor-runs": {
                "activity": "Chase and Run",
                "description": "Play gentle chase games in a safe open space. Roll a ball and run after it together.",
                "materials": ["Soft ball", "Open space"],
                "duration": 15,
            },
            "motor-kicks-ball": {
                "activity": "Ball Kicking Game",
                "description": "Place a large, light ball in front of your child and demonstrate kicking. Hold hands for balance if needed.",
                "materials": ["Large soft ball"],
                "duration": 10,
            },
            "motor-jumps-both-feet": {
                "activity": "Jump Like a Frog",
                "description": "Show jumping with both feet. Practice on soft surfaces. Make it fun with animal sounds - jump like a frog or bunny!",
                "materials": ["Soft mat", "Mini trampoline (optional)"],
                "duration": 10,
            },
            "motor-scribbles": {
                "activity": "First Art Session",
                "description": "Tape paper to the table and offer large crayons. Show scribbling motions and let them explore freely.",
                "materials": ["Large crayons", "Paper", "Tape"],
                "duration": 15,
            },
            "motor-pedals-tricycle": {
                "activity": "Tricycle Practice",
                "description": "Place child on tricycle and help them understand the pedaling motion. Push gently to show cause and effect.",
                "materials": ["Tricycle or ride-on toy"],
                "duration": 15,
            },
            # Cognitive activities
            "cog-follows-moving-object": {
                "activity": "Visual Tracking Game",
                "description": "Slowly move a colorful toy side to side in front of baby's face. Use high-contrast black and white patterns for newborns.",
                "materials": ["High-contrast cards", "Colorful rattle"],
                "duration": 5,
            },
            "cog-object-permanence": {
                "activity": "Peek-a-Boo with Toys",
                "description": "Hide a toy under a blanket and ask 'Where did it go?' Let baby find it. Celebrate the discovery!",
                "materials": ["Small blanket", "Favorite toy"],
                "duration": 10,
            },
            "cog-cause-effect": {
                "activity": "Cause and Effect Discovery",
                "description": "Provide toys that respond to actions: press a button to hear music, shake a rattle to hear sound.",
                "materials": ["Musical toys", "Rattles", "Pop-up toys"],
                "duration": 10,
            },
            "cog-puts-in-container": {
                "activity": "Fill and Dump",
                "description": "Provide containers and small objects. Show how to put items in and dump them out. Great for learning!",
                "materials": ["Containers", "Blocks", "Balls"],
                "duration": 10,
            },
            "cog-simple-pretend-play": {
                "activity": "Tea Party Pretend Play",
                "description": "Set up a simple tea party with stuffed animals. Pretend to pour tea and feed the animals.",
                "materials": ["Play dishes", "Stuffed animals", "Play food"],
                "duration": 15,
            },
            "cog-simple-shape-sorter": {
                "activity": "Shape Sorting Fun",
                "description": "Start with a simple 3-shape sorter. Guide hands to match shapes. Name each shape as it goes in.",
                "materials": ["Shape sorter toy"],
                "duration": 10,
            },
            "cog-sorts-shapes-colors": {
                "activity": "Color and Shape Sorting",
                "description": "Sort objects by color into colored bowls. Sort shapes into groups. Make it a game!",
                "materials": ["Colored bowls", "Colored blocks", "Shape toys"],
                "duration": 15,
            },
            # Language activities
            "lang-coos": {
                "activity": "Conversation with Baby",
                "description": "Talk to baby frequently. When they coo, respond and wait for them to 'reply'. This teaches turn-taking in conversation.",
                "materials": [],
                "duration": 10,
            },
            "lang-babbles": {
                "activity": "Babble Back",
                "description": "When baby babbles, repeat the sounds back. Add new sounds. Sing simple songs with repetitive syllables.",
                "materials": [],
                "duration": 10,
            },
            "lang-responds-to-name": {
                "activity": "Name Game",
                "description": "Call your baby's name from different positions. When they turn, smile and praise them. Play from different rooms.",
                "materials": [],
                "duration": 5,
            },
            "lang-mama-dada-specific": {
                "activity": "Naming People",
                "description": "Point to family members and say their names. Use 'mama' and 'dada' consistently when referring to parents.",
                "materials": ["Family photos"],
                "duration": 10,
            },
            "lang-one-to-three-words": {
                "activity": "Word Building",
                "description": "Label everything throughout the day. Use simple, clear words. Read board books and name pictures.",
                "materials": ["Board books", "Picture cards"],
                "duration": 15,
            },
            "lang-two-word-phrases": {
                "activity": "Phrase Expansion",
                "description": "When child says one word, expand it: if they say 'ball', you say 'big ball' or 'throw ball'. Model two-word phrases.",
                "materials": ["Picture books", "Everyday objects"],
                "duration": 15,
            },
            "lang-ten-words": {
                "activity": "Daily Word Practice",
                "description": "Label items during routines: 'Here's your SHOE. Let's put on your SHOE.' Repeat key words often.",
                "materials": ["Picture books", "Flashcards"],
                "duration": 15,
            },
            "lang-follows-two-step": {
                "activity": "Two-Step Simon Says",
                "description": "Give fun two-step commands: 'Pick up the bear AND put it on the chair.' Make it a game!",
                "materials": ["Stuffed animals", "Household objects"],
                "duration": 10,
            },
            # Social activities
            "social-social-smile": {
                "activity": "Face Time Fun",
                "description": "Get close to baby's face and smile broadly. Make gentle expressions. Give baby time to smile back.",
                "materials": [],
                "duration": 5,
            },
            "social-peekaboo": {
                "activity": "Peek-a-Boo Games",
                "description": "Play peek-a-boo with your hands, a blanket, or hiding behind furniture. Vary the timing for surprises!",
                "materials": ["Light blanket"],
                "duration": 10,
            },
            "social-shows-affection": {
                "activity": "Affection Practice",
                "description": "Model giving hugs and kisses to stuffed animals. Ask child to 'give teddy a hug.' Praise affectionate behavior.",
                "materials": ["Stuffed animals", "Dolls"],
                "duration": 10,
            },
            "social-plays-alongside": {
                "activity": "Parallel Play Date",
                "description": "Arrange playtime with another child of similar age. Provide duplicate toys so they can play side by side.",
                "materials": ["Duplicate toys", "Play space"],
                "duration": 20,
            },
            "social-takes-turns": {
                "activity": "Turn-Taking Games",
                "description": "Roll a ball back and forth saying 'my turn, your turn.' Stack blocks taking turns. Play simple board games.",
                "materials": ["Ball", "Blocks", "Simple games"],
                "duration": 15,
            },
            "social-copies-adults": {
                "activity": "Follow the Leader",
                "description": "Do simple actions and encourage copying: clap hands, stomp feet, touch nose. Make it silly and fun!",
                "materials": [],
                "duration": 10,
            },
            "social-shows-concern": {
                "activity": "Feelings Talk",
                "description": "Name emotions in books and daily life. 'The baby is crying, she's sad.' Ask 'How does teddy feel?'",
                "materials": ["Feelings books", "Stuffed animals"],
                "duration": 10,
            },
        }
