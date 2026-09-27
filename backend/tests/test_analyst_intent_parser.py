from app.services.analyst.intent_parser import IntentParser
from app.services.analyst.query_plan import AnalystIntent


def test_intent_parser_categories():
    parser = IntentParser()

    intent, _ = parser.parse_intent("What is the average sales by region?")
    assert intent in {AnalystIntent.DESCRIPTIVE_STATISTIC, AnalystIntent.GROUP_COMPARISON}

    intent, _ = parser.parse_intent("Show me the trend in monthly revenue")
    assert intent == AnalystIntent.TREND

    intent, _ = parser.parse_intent("Are there any unusual outliers?")
    assert intent == AnalystIntent.ANOMALY

    intent, _ = parser.parse_intent("What is the relationship between advertising and revenue?")
    assert intent == AnalystIntent.RELATIONSHIP

    intent, _ = parser.parse_intent("What AI insights did VizMind discover?")
    assert intent == AnalystIntent.INSIGHT


def test_intent_parser_unsupported_security():
    parser = IntentParser()

    intent, _ = parser.parse_intent("DROP TABLE users;--")
    assert intent == AnalystIntent.UNSUPPORTED

    intent, _ = parser.parse_intent("eval('import os; os.system(\"rm -rf /\")')")
    assert intent == AnalystIntent.UNSUPPORTED
