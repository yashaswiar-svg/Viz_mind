import re
from typing import Tuple
from app.services.analyst.query_plan import AnalystIntent


class IntentParser:
    """Classifies user natural language questions into structured analyst intents."""

    UNSUPPORTED_PATTERNS = [
        r"\b(delete|drop|truncate|alter|insert|update|create|exec|eval|system|subprocess|shell|rm|sudo|chmod)\b",
        r";\s*--",
    ]

    INTENT_TRIGGERS = [
        (AnalystIntent.ANOMALY, [r"\banomal(y|ies)\b", r"\boutlier(s)?\b", r"\bunusual\b", r"\bstrange\b", r"\bunexpected\b"]),
        (AnalystIntent.PREDICTION, [r"\bpredict(ion|ive)?\b", r"\bforecast(ing)?\b", r"\bmodel\b", r"\baccuracy\b", r"\br2\b", r"\brmse\b"]),
        (AnalystIntent.PATTERN, [r"\bpattern(s)?\b", r"\bcluster(s)?\b", r"\bsegment(s)?\b", r"\bassociation(s)?\b"]),
        (AnalystIntent.INSIGHT, [r"\binsight(s)?\b", r"\bdiscover(ed|ies)?\b", r"\bkey finding(s)?\b", r"\btakeaway(s)?\b"]),
        (AnalystIntent.VISUALIZATION, [r"\bvisualiz(e|ation)\b", r"\bchart\b", r"\bplot\b", r"\bgraph\b"]),
        (AnalystIntent.TREND, [r"\btrend(s)?\b", r"\bover time\b", r"\bmonthly\b", r"\byearly\b", r"\bdaily\b", r"\btimeline\b", r"\bgrowth\b"]),
        (AnalystIntent.RELATIONSHIP, [r"\bcorrelat(e|ion)\b", r"\brelationship\b", r"\bdepend(s)?\b", r"\bversus\b", r"\bvs\.?\b"]),
        (AnalystIntent.TOP_BOTTOM, [r"\btop\b", r"\bhighest\b", r"\bbest\b", r"\bworst\b", r"\blowest\b", r"\bbottom\b", r"\bmost\b", r"\bleast\b"]),
        (AnalystIntent.GROUP_COMPARISON, [r"\bgroup(ed)? by\b", r"\bbreakdown\b", r"\bcompare\b", r"\bper\b", r"\bby\b"]),
        (AnalystIntent.FILTERED_ANALYSIS, [r"\bwhere\b", r"\bfilter(ed)?\b", r"\bonly\b", r"\bfor\b"]),
        (AnalystIntent.DESCRIPTIVE_STATISTIC, [r"\baverage\b", r"\bmean\b", r"\bsum\b", r"\btotal\b", r"\bmedian\b", r"\bmin\b", r"\bmax\b", r"\bcount\b", r"\bstat(s|istics)?\b"]),
        (AnalystIntent.DATASET_OVERVIEW, [r"\boverview\b", r"\bsummary\b", r"\bprofile\b", r"\bstructure\b", r"\bcolumn(s)?\b", r"\bshape\b"]),
    ]

    def parse_intent(self, question: str) -> Tuple[AnalystIntent, float]:
        if not question or not question.strip():
            return AnalystIntent.UNSUPPORTED, 0.0

        q_lower = question.strip().lower()

        # Check for dangerous / unsupported system requests
        for pat in self.UNSUPPORTED_PATTERNS:
            if re.search(pat, q_lower):
                return AnalystIntent.UNSUPPORTED, 1.0

        # Check follow-up indicators
        if q_lower.startswith(("what about", "how about", "and for", "and in", "what of")):
            return AnalystIntent.FOLLOW_UP, 0.9

        # Check intent triggers in priority order
        for intent, patterns in self.INTENT_TRIGGERS:
            for pat in patterns:
                if re.search(pat, q_lower):
                    return intent, 0.85

        # Fallback to DESCRIPTIVE_STATISTIC or DATASET_OVERVIEW if generic
        if "?" in q_lower or len(q_lower.split()) > 2:
            return AnalystIntent.DESCRIPTIVE_STATISTIC, 0.5

        return AnalystIntent.DATASET_OVERVIEW, 0.4
