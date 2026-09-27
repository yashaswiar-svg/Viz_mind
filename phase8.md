# VIZMIND — PHASE 8 IMPLEMENTATION PROMPT

## AI Insight Engine — Explainable, Evidence-Grounded Data Analyst

You are implementing **Phase 8 of VizMind: Intelligent Data Visualization and Pattern Discovery**.

Read and inspect the ENTIRE existing Phase 1–7 implementation before making any changes.

The Phase 7 walkthrough confirms:

* Phase 1–7 are implemented.
* `pytest tests/ -v` → **67 passed, 23 skipped, 0 failed**
* `npm run build` → passed
* Alembic head → `007_add_phase7_anomaly_prediction_tables`
* Processed datasets are represented by the existing `Dataset` model using:

  * `dataset_kind = PROCESSED`
  * `parent_dataset_id`
* Phase 7 provides:

  * anomaly detection
  * anomaly severity/scoring
  * prediction
  * regression
  * classification
  * forecasting
  * baselines
  * model metrics
  * leakage protection
  * deterministic outputs
  * checksum/version validation
  * paginated prediction results

Your job is to implement **ONLY Phase 8**.

---

# 1. PHASE 8 OBJECTIVE

Build the **VizMind AI Insight Engine**.

The purpose of Phase 8 is to transform the verified outputs from Phases 3–7 into concise, useful, explainable insights for a human analyst.

The core pipeline becomes:

```text
Dataset
   ↓
Data Profile
   ↓
Preprocessing
   ↓
Visualization Intelligence
   ↓
Pattern Discovery
   ↓
Anomaly Detection
   ↓
Prediction
   ↓
Evidence Aggregation
   ↓
AI Insight Engine
   ↓
Evidence Validation
   ↓
Insight Ranking
   ↓
Persisted Insights
   ↓
Dashboard
```

The central product principle is:

> **VizMind does not ask the AI to analyze the raw dataset. VizMind computes the evidence first, then asks the AI to explain that evidence.**

The LLM must NEVER become the source of statistical truth.

---

# 2. STRICT PHASE 8 BOUNDARY

## Phase 8 MAY implement

* AI-generated explanations
* Evidence aggregation
* Insight generation
* Insight summarization
* Business-friendly wording
* Statistical explanation
* Anomaly explanation
* Prediction explanation
* Pattern explanation
* Visualization explanation
* Cross-module evidence synthesis
* Confidence/evidence metadata
* Insight ranking
* Duplicate insight removal
* LLM response validation
* Hallucination/evidence-grounding validation
* Prompt templates
* LLM provider abstraction
* LLM configuration
* AI insight persistence
* Insight API
* Insight dashboard
* Insight filtering
* Insight detail view
* Deterministic fallback explanations when LLM is unavailable

---

# 3. PHASE 8 MUST NOT IMPLEMENT

Do NOT implement or redesign:

* new anomaly detection algorithms
* new prediction algorithms
* new statistical tests
* clustering
* PCA
* deep learning
* AutoML
* new visualization algorithms
* natural-language dataset querying
* conversational analyst
* chatbot
* autonomous actions
* automated business decisions
* external API actions
* data cleaning
* preprocessing
* feature engineering
* model training beyond existing Phase 7
* changing Phase 3–7 statistical calculations
* replacing Python statistical calculations with an LLM
* LLM-generated numeric calculations
* raw dataset dumping into the LLM
* unrestricted raw-row prompting

Phase 8 is an **interpretation and explanation layer**, not another analysis engine.

Phase 9 will handle the **Natural-Language Analyst**.

Do NOT implement Phase 9 functionality.

---

# 4. FIRST STEP — INSPECT EXISTING PROJECT

Before writing code, inspect:

```text
backend/app/
backend/tests/
frontend/src/
backend/alembic/
README
architecture documentation
API documentation
configuration
existing schemas
existing repositories
existing services
existing exception handling
existing logging
```

Specifically inspect and reuse:

```text
dataset_loader.py
visualization_service.py
visualization_repository.py
pattern_discovery_service.py
pattern_discovery_repository.py
anomaly_detection_service.py
anomaly_detection_repository.py
prediction_service.py
prediction_repository.py
Dataset model
DatasetProfile model
PatternDiscoveryRun
PatternResult
AnomalyDetectionRun
AnomalyResult
PredictionRun
PredictionResult
existing checksum/version validation
existing API error handling
existing logging
existing configuration system
```

Do NOT create duplicate versions of existing infrastructure.

---

# 5. ARCHITECTURAL PRINCIPLE

Implement:

```text
COMPUTATION LAYER
        ↓
Evidence
        ↓
EVIDENCE CONTRACT
        ↓
LLM EXPLANATION LAYER
        ↓
VALIDATION
        ↓
INSIGHT
```

The LLM should receive structured evidence such as:

```json
{
  "pattern_type": "CORRELATION",
  "columns": ["sales", "advertising_spend"],
  "correlation": 0.72,
  "p_value": 0.001,
  "sample_size": 250,
  "strength": "STRONG",
  "significant": true
}
```

NOT:

```text
Here is the entire CSV.
Analyze it and tell me what is interesting.
```

The first approach is mandatory.

---

# 6. EVIDENCE CONTRACT

Create a centralized evidence representation.

Suggested file:

```text
backend/app/services/insight_evidence.py
```

Create structured evidence objects for:

### Dataset evidence

```text
dataset_profile
quality_score
quality_level
row_count
column_count
missing_percentage
duplicate_percentage
```

### Visualization evidence

```text
visualization_type
columns
aggregation
score
reason
```

### Pattern evidence

```text
pattern_type
columns
method
statistics
sample_size
p_value
adjusted_p_value
effect_size
strength
significant
description
```

### Anomaly evidence

```text
column
observation_reference
anomaly_score
severity
methods_detected
statistical_evidence
```

### Prediction evidence

```text
problem_type
target
model
baseline
features
train_rows
validation_rows
test_rows
metrics
baseline_metrics
model_improvement
```

Never expose unnecessary raw data.

---

# 7. EVIDENCE AGGREGATION ENGINE

Create:

```text
backend/app/services/insight_evidence_service.py
```

Responsibilities:

1. Retrieve relevant outputs from previous phases.
2. Validate dataset/version relationships.
3. Construct normalized evidence.
4. Remove redundant evidence.
5. Limit evidence size.
6. Rank evidence candidates.
7. Create an LLM-safe evidence package.

Suggested pipeline:

```text
Profile
   ↓
Visualization Results
   ↓
Pattern Results
   ↓
Anomaly Results
   ↓
Prediction Results
   ↓
Evidence Normalization
   ↓
Evidence Ranking
   ↓
Evidence Package
```

Do not send unlimited results.

Add configurable limits such as:

```text
MAX_PROFILE_EVIDENCE = 20
MAX_VISUALIZATION_EVIDENCE = 10
MAX_PATTERN_EVIDENCE = 15
MAX_ANOMALY_EVIDENCE = 20
MAX_PREDICTION_EVIDENCE = 10
MAX_TOTAL_EVIDENCE_ITEMS = 50
```

---

# 8. INSIGHT TYPES

Create a controlled enum.

Suggested:

```text
DATA_QUALITY
TREND
CORRELATION
GROUP_DIFFERENCE
CATEGORICAL_ASSOCIATION
DISTRIBUTION
ANOMALY
PREDICTION
FORECAST
VISUALIZATION
CROSS_MODULE
```

Do NOT allow arbitrary insight types.

---

# 9. INSIGHT STRUCTURE

Create a structured insight model.

Suggested fields:

```text
id
dataset_id
processed_dataset_id
insight_type
title
summary
explanation
importance
evidence_strength
confidence
columns
source_type
source_ids
statistics
recommendation
limitations
status
created_at
updated_at
```

Important distinction:

### Evidence strength

How strong is the underlying computed evidence?

### Confidence

How confidently can VizMind communicate the interpretation?

Do not use confidence as fake statistical probability.

Do NOT generate:

```text
95% confident this business decision will succeed
```

unless such a probability is actually supported by a valid statistical/modeling method.

---

# 10. INSIGHT STATUS

Use controlled statuses:

```text
GENERATED
VALIDATED
REJECTED
FALLBACK
```

Only `VALIDATED` insights should normally be displayed as AI-generated insights.

Fallback deterministic explanations may use:

```text
FALLBACK
```

when the LLM is unavailable.

---

# 11. INSIGHT IMPORTANCE

Use deterministic importance levels:

```text
LOW
MEDIUM
HIGH
```

Do NOT allow the LLM to arbitrarily determine importance.

Importance must be derived from structured evidence.

For example:

* statistical significance
* effect size
* anomaly severity
* prediction improvement over baseline
* data quality impact
* evidence consistency across modules

Create:

```text
backend/app/services/insight_scoring.py
```

The scoring system must be deterministic.

Do not use an LLM to assign numeric importance.

---

# 12. EVIDENCE RANKING

Rank evidence before sending it to the LLM.

Example factors:

```text
statistical significance
effect size
sample size
anomaly severity
prediction improvement
visualization relevance
data quality impact
cross-module agreement
```

Do NOT simply rank based on p-value.

A tiny effect with a huge sample should not automatically become the most important insight.

Keep the ranking transparent.

---

# 13. CROSS-MODULE EVIDENCE

One of VizMind's differentiators should be connecting evidence from different engines.

Example:

```text
Pattern Discovery:
Sales increased over time.

Visualization:
Sales line chart shows a consistent upward trend.

Prediction:
Model predicts continued growth.

AI Insight:
Sales show a historically increasing trend, and the prediction model indicates that this pattern may continue under the modeled conditions.
```

Another example:

```text
Pattern:
Customer segment A has significantly higher average revenue.

Visualization:
Revenue distribution differs between segments.

Anomaly:
Several unusually high transactions occur in segment A.

AI Insight:
Segment A has higher typical revenue, but a small number of unusually large transactions contribute disproportionately to the upper end of the distribution.
```

The LLM may synthesize these only when all claims are supported by evidence.

---

# 14. CRITICAL CLAIM RULE

Every generated claim must be traceable to evidence.

For example:

```text
Claim:
"Sales increased over the observed period."

Evidence:
pattern_result_id = 123
pattern_type = TIME_TREND
slope = ...
r2 = ...
```

Create an internal claim/evidence mapping.

Suggested structure:

```text
Insight
 ├── Evidence 1
 ├── Evidence 2
 ├── Evidence 3
 └── Claim validation
```

Do not create unsupported statements.

---

# 15. LLM PROVIDER ABSTRACTION

Create:

```text
backend/app/services/llm/
```

Suggested:

```text
base.py
provider.py
gemini_provider.py
openai_provider.py
mock_provider.py
```

Use an interface such as:

```text
LLMProvider
    generate_structured_insight(...)
```

The rest of VizMind must NOT depend directly on Gemini/OpenAI-specific code.

---

# 16. PROVIDER CONFIGURATION

Extend existing configuration carefully.

Suggested:

```text
LLM_PROVIDER=mock
LLM_MODEL=
LLM_API_KEY=
LLM_TIMEOUT_SECONDS=30
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0
LLM_ENABLED=false
```

Default:

```text
LLM_PROVIDER=mock
LLM_ENABLED=false
```

This is important because the application and tests must work without an external API key.

Never hard-code API keys.

Never commit secrets.

---

# 17. MOCK PROVIDER

Create a deterministic mock provider.

It must allow:

```text
pytest
```

to run without internet access or API keys.

The mock provider should generate predictable structured output.

Example:

```json
{
  "title": "Strong relationship between advertising spend and sales",
  "summary": "Sales and advertising spend show a strong positive correlation in the analyzed data.",
  "explanation": "...",
  "limitations": "Correlation does not establish causation."
}
```

Do not make tests depend on a live LLM.

---

# 18. PROMPT ENGINE

Create:

```text
backend/app/services/insight_prompt_builder.py
```

The prompt must clearly tell the model:

```text
You are an analytical explanation assistant.

Use ONLY the supplied evidence.

Do not invent statistics.

Do not calculate new statistics.

Do not infer unsupported causes.

Do not claim correlation means causation.

Do not make business decisions.

Do not invent future outcomes.

If evidence is insufficient, state that clearly.

Explain findings in simple professional language.

Every factual claim must be supported by supplied evidence.
```

The prompt should contain:

```text
ROLE
TASK
EVIDENCE
OUTPUT SCHEMA
RULES
LIMITATIONS
```

---

# 19. STRUCTURED LLM OUTPUT

The LLM must return structured JSON.

Example:

```json
{
  "title": "...",
  "summary": "...",
  "explanation": "...",
  "limitations": [
    "Correlation does not establish causation."
  ],
  "evidence_references": [
    "pattern:123"
  ]
}
```

Do NOT accept arbitrary prose as the primary response format.

Validate JSON schema using Pydantic.

---

# 20. LLM OUTPUT VALIDATION

Create:

```text
backend/app/services/insight_validator.py
```

Validation must check:

### Schema validation

Required fields exist.

### Evidence-reference validation

Every referenced evidence ID exists.

### Numeric claim validation

If the LLM says:

```text
correlation = 0.72
```

verify that `0.72` exists in the supplied evidence within an acceptable formatting tolerance.

### Unsupported claim detection

Reject or flag statements that introduce unsupported facts.

### Causality protection

Reject claims such as:

```text
X causes Y
```

when only correlation evidence exists.

### Future certainty protection

Reject:

```text
Sales will increase.
```

Prefer:

```text
The model predicts an increase under the evaluated conditions.
```

### Recommendation protection

Do not let the LLM produce high-impact autonomous business decisions.

For example, avoid:

```text
Immediately stop advertising.
```

Instead:

```text
The analysis suggests reviewing advertising efficiency alongside the observed relationship.
```

---

# 21. HALLUCINATION / GROUNDING STRATEGY

Do NOT attempt to solve hallucination through another unrestricted LLM.

Use deterministic validation wherever possible.

Implement:

```text
Evidence → Prompt → Structured Response → Validator → Validated Insight
```

If validation fails:

```text
LLM output
   ↓
Validation failed
   ↓
Discard output
   ↓
Generate deterministic fallback explanation
```

Never display an unvalidated AI insight as verified.

---

# 22. DETERMINISTIC FALLBACK ENGINE

Create:

```text
backend/app/services/insight_fallback.py
```

This is important for:

* no API key
* provider failure
* timeout
* malformed response
* evidence validation failure
* offline development
* tests

Generate template-based explanations from computed statistics.

Examples:

### Correlation

```text
{column_a} and {column_b} show a {strength} {direction} relationship
based on a correlation of {correlation} across {sample_size} observations.
This relationship does not establish causation.
```

### Trend

```text
{column} shows an {increasing/decreasing/stable} historical trend
with R² = {r2} across {sample_size} observations.
```

### Anomaly

```text
{column} contains observations classified as {severity} anomalies
based on {methods}.
```

### Prediction

```text
The {model} model achieved {metric} on the held-out test set,
compared with {baseline} for the baseline model.
```

Fallback text must only use known evidence.

---

# 23. DATABASE DESIGN

Create:

```text
InsightRun
Insight
InsightEvidence
```

Migration:

```text
008_add_phase8_insight_tables.py
```

The migration must follow migration `007`.

---

# 24. InsightRun MODEL

Suggested fields:

```text
id
dataset_id
processed_dataset_id
profile_id
status
started_at
completed_at
insight_count
evidence_count
llm_provider
llm_model
fallback_used
error_message
created_at
updated_at
```

Do not store API keys.

Do not store raw prompts containing sensitive/raw dataset values.

---

# 25. Insight MODEL

Suggested:

```text
id
run_id
dataset_id
processed_dataset_id
insight_type
title
summary
explanation
importance
evidence_strength
confidence
columns
statistics
limitations
source_type
source_ids
status
created_at
updated_at
```

Use JSONB where structured variable data is appropriate.

Do not store complete raw dataset rows.

---

# 26. InsightEvidence MODEL

Suggested:

```text
id
insight_id
source_type
source_id
evidence_type
evidence_data
created_at
```

`evidence_data` must contain only the minimal structured evidence necessary to reproduce/explain the insight.

Do not store complete raw datasets.

---

# 27. DATABASE INTEGRITY

Use foreign keys.

Use appropriate indexes.

Use cascade deletion where appropriate.

Deleting a Dataset must not leave orphan:

```text
InsightRun
Insight
InsightEvidence
```

records.

Ensure processed dataset relationships follow the existing Phase 4/7 architecture.

---

# 28. CHECKSUM / VERSION INTEGRITY

Phase 8 must inherit the version-integrity principle from Phases 4–7.

Before insight generation:

```text
validate source dataset
validate processed dataset
validate profile
validate processed checksum
validate referenced Phase 5/6/7 results
```

If the processed dataset changed:

```text
INSIGHT_DATASET_VERSION_MISMATCH
```

must be returned.

Never generate insights from stale analytical results.

---

# 29. INSIGHT GENERATION SERVICE

Create:

```text
backend/app/services/insight_service.py
```

Pipeline:

```text
validate dataset
        ↓
resolve processed dataset
        ↓
validate checksum
        ↓
retrieve Phase 3 profile
        ↓
retrieve Phase 5 visualization evidence
        ↓
retrieve Phase 6 patterns
        ↓
retrieve Phase 7 anomalies
        ↓
retrieve Phase 7 predictions
        ↓
build evidence package
        ↓
rank evidence
        ↓
create deterministic insight candidates
        ↓
send bounded evidence to LLM
        ↓
validate LLM response
        ↓
fallback if necessary
        ↓
score insight
        ↓
deduplicate
        ↓
persist
        ↓
return results
```

---

# 30. DO NOT SEND ALL RESULTS TO THE LLM

Use evidence selection.

For example:

```text
Top 5 strongest patterns
Top 5 important anomalies
Top 3 prediction results
Top 3 visualizations
Top 3 quality issues
```

Then apply:

```text
MAX_TOTAL_EVIDENCE_ITEMS
```

This keeps prompts small, predictable and cost-controlled.

---

# 31. INSIGHT DEDUPLICATION

The same fact may appear in:

* visualization
* pattern discovery
* anomaly detection
* prediction

Do not generate four nearly identical insights.

Create:

```text
insight_deduplication.py
```

Use deterministic fingerprints based on:

```text
insight_type
columns
source_ids
normalized semantic key
```

Keep cross-module synthesis where it adds meaningful information.

---

# 32. INSIGHT LIMIT

Add:

```text
MAX_INSIGHTS_PER_RUN = 15
```

Do not flood the dashboard.

Prefer a small number of evidence-rich insights.

---

# 33. API

Create:

```text
POST /api/v1/datasets/{dataset_id}/insights
GET  /api/v1/datasets/{dataset_id}/insights
GET  /api/v1/datasets/{dataset_id}/insights/{insight_id}
GET  /api/v1/datasets/{dataset_id}/insights/runs/{run_id}
```

Optional:

```text
GET /api/v1/datasets/{dataset_id}/insights/summary
```

---

# 34. API BEHAVIOR

### POST

Runs insight generation.

It must:

* validate preprocessing
* validate version/checksum
* collect evidence
* generate insights
* persist run
* return summary

### GET

Must NOT automatically generate insights.

It only retrieves persisted insights.

### GET individual

Return:

* title
* summary
* explanation
* evidence
* statistics
* limitations
* importance
* confidence
* source references

Never expose:

* API key
* filesystem path
* raw dataset
* internal secrets

---

# 35. ERROR CODES

Add appropriate errors such as:

```text
PREPROCESSING_REQUIRED
INSIGHT_DATASET_VERSION_MISMATCH
INSIGHT_RUN_NOT_FOUND
INSIGHT_NOT_FOUND
NO_ANALYTICAL_EVIDENCE
INSIGHT_GENERATION_FAILED
LLM_PROVIDER_UNAVAILABLE
LLM_TIMEOUT
LLM_INVALID_RESPONSE
INSIGHT_VALIDATION_FAILED
```

Reuse the project's existing exception architecture.

---

# 36. FRONTEND

Create:

```text
InsightView.jsx
InsightSummary.jsx
InsightCard.jsx
InsightEvidence.jsx
InsightDetail.jsx
```

Integrate into the existing dataset workflow.

Suggested flow:

```text
Dataset
  ↓
Profile
  ↓
Preprocess
  ↓
Visualize
  ↓
Discover Patterns
  ↓
Detect Anomalies
  ↓
Predict
  ↓
Generate AI Insights
```

---

# 37. INSIGHT DASHBOARD

Display:

### Header

```text
AI Data Insights
```

### Summary

```text
Total insights
High importance
Medium importance
Low importance
Evidence sources
AI/Fallback mode
```

### Insight card

Each card should show:

```text
[Insight Type]

Title

Short summary

Importance

Evidence strength

Related columns

Source modules

View evidence
```

---

# 38. INSIGHT DETAIL VIEW

Show:

```text
Title
Summary
Detailed explanation
Why this matters
Evidence
Statistics
Source analysis
Limitations
Generation mode
```

Example:

```text
Why this insight was generated

Pattern Discovery
Correlation = 0.72
p-value = 0.001
n = 250

Visualization
Scatter plot recommendation score = 91

Limitations
Correlation does not establish causation.
```

This transparency is important for VizMind.

---

# 39. AI/FALLBACK INDICATOR

Clearly distinguish:

```text
AI Generated
```

from:

```text
Deterministic Explanation
```

If the LLM was unavailable, do not pretend the fallback text was generated by AI.

---

# 40. NO RAW DATA DISPLAY

Phase 8 UI must NOT display:

* complete CSV
* raw file paths
* API keys
* internal database identifiers unnecessarily
* sensitive raw rows

Only show aggregated evidence.

---

# 41. LOADING / FAILURE STATES

Frontend must support:

```text
Not Generated
Generating
Completed
Fallback Mode
Failed
No Evidence
```

Do not show a blank screen.

---

# 42. CONFIGURATION

Add centralized configuration:

```text
INSIGHT_ENABLED=true/false

LLM_ENABLED=false
LLM_PROVIDER=mock
LLM_MODEL=
LLM_API_KEY=

LLM_TIMEOUT_SECONDS=30
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0

MAX_TOTAL_EVIDENCE_ITEMS=50
MAX_INSIGHTS_PER_RUN=15
```

Use environment variables.

Never hard-code credentials.

---

# 43. SECURITY

Do not send raw datasets to the LLM.

Do not send:

* entire CSV files
* complete database rows
* filesystem paths
* credentials
* tokens
* internal secrets

Only send structured analytical evidence.

If the provider is external, document that structured analytical evidence is transmitted to the configured provider.

---

# 44. PRIVACY

Implement a clear data-minimization principle.

The LLM should receive:

```text
statistics
aggregations
pattern metadata
model metrics
anomaly metadata
column names when necessary
```

not:

```text
raw observations
```

unless a future phase explicitly requires it.

Phase 8 does NOT require raw-row prompting.

---

# 45. OBSERVABILITY

Add logs:

```text
insight_generation_started
insight_evidence_collected
insight_candidates_created
llm_generation_started
llm_generation_completed
llm_generation_failed
insight_validation_completed
insight_fallback_used
insight_persisted
insight_generation_completed
insight_generation_failed
```

Include:

```text
request_id
dataset_id
processed_dataset_id
insight_run_id
provider
model
evidence_count
insight_count
duration
fallback_used
```

Never log:

* API keys
* prompts containing sensitive data
* raw dataset rows
* full LLM responses if they could contain sensitive data

---

# 46. TESTING

Create comprehensive Phase 8 tests.

## Evidence tests

```text
test_insight_evidence.py
```

Test:

* profile evidence
* visualization evidence
* pattern evidence
* anomaly evidence
* prediction evidence
* evidence limits
* deterministic ordering
* no raw rows
* evidence normalization

## Scoring tests

```text
test_insight_scoring.py
```

Test:

* importance
* evidence strength
* deterministic ranking
* significance handling
* effect size handling
* anomaly severity
* prediction improvement

## Prompt tests

```text
test_insight_prompt_builder.py
```

Test:

* required instructions
* evidence included
* no raw data
* output schema
* causality restriction

## Mock LLM tests

```text
test_llm_provider.py
```

Test:

* deterministic mock response
* provider interface
* timeout/failure behavior

## Validator tests

```text
test_insight_validator.py
```

Test:

* valid output
* malformed JSON
* missing evidence reference
* unsupported statistic
* causality claim
* unsupported future claim
* fabricated numbers
* missing required fields

## Fallback tests

```text
test_insight_fallback.py
```

Test all supported insight types.

## Service tests

```text
test_insight_service.py
```

Test:

* evidence collection
* LLM generation
* validation
* fallback
* deduplication
* persistence
* limits
* failure handling

## API tests

```text
test_insight_api.py
```

Test:

* POST
* GET
* GET detail
* run retrieval
* dataset not found
* preprocessing required
* checksum mismatch
* no evidence
* provider failure
* fallback

---

# 47. DETERMINISM

With:

```text
LLM_PROVIDER=mock
```

the same evidence must produce the same result.

Test:

```text
same dataset
same checksum
same evidence
same configuration
        ↓
same insight ranking
same fallback output
```

For live LLM providers, deterministic output cannot be guaranteed, so tests must not depend on exact live-model wording.

---

# 48. VERSION INTEGRITY TEST

Test:

```text
dataset
 ↓
profile
 ↓
preprocess
 ↓
phase 5–7 analysis
 ↓
modify processed dataset
 ↓
generate insights
```

Expected:

```text
INSIGHT_DATASET_VERSION_MISMATCH
```

No stale insights should be generated.

---

# 49. CASCADE TEST

Test:

```text
Dataset
 ↓
InsightRun
 ↓
Insight
 ↓
InsightEvidence
```

Delete dataset.

Verify:

```text
InsightRun deleted
Insight deleted
InsightEvidence deleted
```

No orphan records.

---

# 50. FAILURE CLEANUP

If LLM generation fails:

```text
Run status = FAILED
```

or, if deterministic fallback succeeds:

```text
Run status = COMPLETED
fallback_used = true
```

Do not leave partial insight records.

Use coordinated DB transaction handling.

Do not claim filesystem/database atomicity.

---

# 51. PHASE 8 REGRESSION TESTING

After implementation:

```bash
cd backend
python -m pytest tests/ -v
```

Expected:

* Phase 1–7 tests continue passing.
* Phase 8 tests pass.
* Database-dependent tests must clearly distinguish:

  * PASSED
  * SKIPPED
  * FAILED

Do NOT report skipped PostgreSQL tests as passed.

---

# 52. FRONTEND VERIFICATION

Run:

```bash
cd frontend
npm run build
```

The production build must succeed.

Check:

* no JSX errors
* no broken imports
* no console-breaking runtime errors
* insight dashboard loads
* API failure states work
* fallback mode is visible
* existing Phase 1–7 pages still work

---

# 53. DATABASE VERIFICATION

Run:

```bash
cd backend

python -m alembic upgrade head
python -m alembic current
python -m alembic heads
```

Expected:

```text
008_add_phase8_insight_tables
```

Migration must be linear after:

```text
007_add_phase7_anomaly_prediction_tables
```

Do not modify previous migrations unless absolutely necessary.

---

# 54. END-TO-END VERIFICATION

Perform the complete workflow:

```text
Upload dataset
      ↓
Profile
      ↓
Preprocess
      ↓
Generate visualizations
      ↓
Discover patterns
      ↓
Detect anomalies
      ↓
Run prediction
      ↓
Generate AI insights
      ↓
Retrieve insights
      ↓
Open insight details
      ↓
Inspect evidence
      ↓
Verify source checksum unchanged
      ↓
Verify processed checksum unchanged
      ↓
Delete dataset
      ↓
Verify insight records deleted
```

Test both:

### AI mode

When a configured provider is available.

### Fallback mode

With:

```text
LLM_PROVIDER=mock
```

or disabled external LLM.

---

# 55. DOCUMENTATION

Update:

```text
README.md
architecture documentation
API documentation
development documentation
roadmap
```

Document:

### Phase 8 purpose

AI explanation layer.

### Evidence architecture

How Phase 3–7 outputs become evidence.

### LLM architecture

Provider abstraction.

### Security

No raw dataset transmission.

### Validation

How hallucination/unsupported claims are rejected.

### Fallback

How deterministic explanations work.

### Limitations

Clearly document:

* LLM responses are probabilistic.
* Validation reduces unsupported claims but does not guarantee perfect semantic correctness.
* Correlation does not imply causation.
* Prediction does not guarantee future outcomes.
* Forecasts depend on historical patterns and model assumptions.
* AI explanations do not replace statistical evidence.

---

# 56. IMPORTANT PRODUCT PRINCIPLE

VizMind should communicate:

> **The numbers come from the analytical engines. The AI explains what those numbers mean.**

Never:

> "The AI analyzed your dataset and discovered this."

Prefer:

> "VizMind detected a statistically significant relationship and generated an explanation based on the computed evidence."

This distinction should be reflected in the UI and documentation.

---

# 57. PERFORMANCE

Avoid:

* loading the entire dataset multiple times unnecessarily
* sending large prompts
* repeated database queries
* repeated LLM calls for identical evidence

Reuse existing repositories/services.

Where appropriate:

```text
retrieve evidence once
normalize once
generate insight candidates
```

Do not introduce premature distributed infrastructure.

---

# 58. NO AUTONOMOUS DECISION MAKING

The AI Insight Engine may say:

```text
The analysis suggests reviewing...
```

It must not autonomously:

```text
change prices
send emails
delete records
approve transactions
reject customers
execute business actions
```

Phase 8 is explanatory only.

---

# 59. CODE QUALITY

Follow existing project conventions.

Use:

* type hints
* Pydantic schemas
* SQLAlchemy 2.x
* async patterns already established
* centralized exceptions
* centralized configuration
* structured logging
* repository/service separation
* small testable functions

Do not duplicate existing utilities.

Do not introduce unnecessary dependencies.

Before adding an external dependency, inspect whether an existing project dependency already solves the requirement.

---

# 60. STRICT PHASE BOUNDARY

Do NOT implement Phase 9.

Do NOT build:

```text
chatbot
natural language query parser
conversational memory
multi-turn analyst
text-to-SQL
```

Those belong to Phase 9.

Phase 8 ends with:

```text
Evidence
→ AI Explanation
→ Validation
→ Insight Persistence
→ Insight Dashboard
```

---

# 61. FINAL COMPLETION REPORT

When implementation is complete, provide a concise but complete report containing:

## Implementation

* files created
* files modified
* services created
* database models
* migration

## AI architecture

* evidence pipeline
* provider abstraction
* prompt strategy
* validation
* fallback

## Security

* raw data protection
* secret protection
* data minimization

## Insight system

* insight types
* ranking
* deduplication
* limits

## APIs

List every endpoint.

## Frontend

List all new components and workflow integration.

## Testing

Report separately:

```text
Phase 1 tests:
PASSED / SKIPPED / FAILED

Phase 2:
...

Phase 7:
...

Phase 8:
...

Total:
PASSED = ?
SKIPPED = ?
FAILED = ?
```

Do NOT count skipped tests as passed.

## Build

Report:

```text
npm run build = PASS/FAIL
```

## Migration

Report:

```text
alembic upgrade head = PASS/FAIL
alembic current = ...
alembic heads = ...
```

## E2E

Report:

```text
upload → profile → preprocess → visualization → patterns
→ anomaly → prediction → AI insights
```

## Integrity

Confirm:

```text
source checksum unchanged
processed checksum unchanged
no stale evidence accepted
no orphan insight records
```

## Phase boundary

Explicitly confirm:

> Phase 9 — Natural-Language Analyst was NOT implemented.

---

# 62. IMPLEMENTATION RULE

Work incrementally.

Before coding:

1. Inspect Phase 1–7.
2. Identify reusable components.
3. Identify any mismatch between this plan and the actual repository.
4. Do not blindly overwrite existing code.
5. Preserve all existing functionality.

Then implement Phase 8.

After each major component:

```text
implement
→ test
→ inspect
→ fix
→ continue
```

At the end:

```text
pytest
npm run build
alembic verification
E2E verification
```

Do not stop at "code compiles."

---

# 63. FINAL STOP CONDITION

Once Phase 8 is implemented and verified:

STOP.

Do NOT implement Phase 9.

Do NOT add additional features outside Phase 8.

Wait for the next instruction.
