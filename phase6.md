# VIZMIND — PHASE 6 IMPLEMENTATION PROMPT

## Pattern Discovery Intelligence Engine

You are implementing **Phase 6 of VizMind: Intelligent Data Visualization and Pattern Discovery**.

Phase 1–5 are already implemented.

Before making any changes, inspect the COMPLETE existing Phase 1–5 implementation and integrate with it.

Do NOT assume filenames, class names, database schemas, API structures, or frontend components. Inspect the current repository first.

---

# 1. PHASE 6 OBJECTIVE

Implement:

> **Pattern Discovery Intelligence Engine**

The purpose of Phase 6 is to automatically discover meaningful, statistically supported patterns in a dataset.

Phase 5 answered:

> "What should we visualize?"

Phase 6 must answer:

> "What interesting relationships, trends, distributions, associations, and group differences are present in the data?"

The engine must use actual deterministic/statistical computation.

It must NOT use an LLM.

---

# 2. CORE PIPELINE

Implement this pipeline:

```text
Uploaded Dataset
       ↓
Phase 3 Profile
       ↓
Phase 4 Processed Dataset
       ↓
Pattern Discovery Engine
       ↓
Candidate Pattern Generation
       ↓
Statistical Computation
       ↓
Significance / Strength Evaluation
       ↓
Pattern Validation
       ↓
Deduplication
       ↓
Deterministic Ranking
       ↓
Pattern Results
       ↓
Pattern API
       ↓
Pattern Discovery Dashboard
```

The output should contain structured pattern records such as:

```text
Pattern:
"Sales and Profit show a positive linear association."

Evidence:
Pearson correlation = 0.78
Sample size = 1,245

Pattern type:
CORRELATION

Strength:
STRONG

Statistical significance:
p < 0.001
```

Another example:

```text
Pattern:
"Revenue differs across regions."

Pattern type:
GROUP_DIFFERENCE

Method:
ANOVA

Evidence:
F = ...
p = ...

Groups:
North, South, East, West
```

Another:

```text
Pattern:
"Monthly revenue shows an increasing trend."

Pattern type:
TIME_TREND

Evidence:
slope = ...
R² = ...
```

The wording may later be passed to the Phase 8 AI Insight Engine.

For Phase 6 itself, explanations must be deterministic and template-based.

---

# 3. STRICT PHASE 6 BOUNDARY

## IMPLEMENT ONLY

Phase 6 may implement:

* correlation analysis
* numeric relationship discovery
* categorical/numeric group comparison
* categorical association analysis
* time trend detection
* distribution summaries
* statistically supported relationship detection
* effect/strength measurements
* statistical significance where appropriate
* pattern candidate generation
* pattern validation
* pattern ranking
* pattern deduplication
* pattern persistence
* pattern APIs
* pattern dashboard
* deterministic explanations.

---

# 4. DO NOT IMPLEMENT

Do NOT implement:

### Anomaly detection

Do NOT implement:

* Isolation Forest
* Local Outlier Factor
* anomaly scoring
* automated outlier labeling
* anomaly alerts.

These belong to Phase 7.

### Prediction

Do NOT implement:

* forecasting
* regression prediction
* classification
* future prediction
* time-series forecasting.

These belong to Phase 7.

### AI / LLM

Do NOT implement:

* Gemini
* OpenAI
* Claude
* LLM calls
* AI-generated insights
* natural-language analyst
* conversational querying.

These belong to Phase 8/9.

### Clustering

Do NOT implement:

* K-Means
* DBSCAN
* hierarchical clustering
* PCA
* dimensionality reduction.

Unless explicitly required by a later phase, do not introduce them here.

---

# 5. FIRST STEP — INSPECT PHASE 1–5

Inspect:

```text
backend/app/
backend/tests/
backend/alembic/
frontend/src/
docs/
README.md
```

Specifically inspect:

### Phase 3

* DatasetProfile
* DatasetColumnProfile
* semantic types
* missingness
* cardinality
* numeric statistics
* datetime information.

### Phase 4

* Dataset source/processed relationship
* preprocessing job
* processed dataset
* processed checksum
* dataset loader.

### Phase 5

* VisualizationRun
* VisualizationRecommendation
* visualization planner
* visualization scoring
* chart specification
* chart data builder
* visualization repository
* frontend visualization components.

Reuse existing infrastructure wherever possible.

Do not duplicate dataset loading, profile loading, checksum validation, or processed dataset resolution.

---

# 6. DATASET VERSION RULE

Pattern discovery must operate on the same kind of immutable processed dataset used by Phase 5.

Expected pipeline:

```text
Source Dataset
      ↓
Profile
      ↓
Preprocessing
      ↓
Processed Dataset
      ↓
Pattern Discovery
```

If a valid processed dataset does not exist:

```text
PREPROCESSING_REQUIRED
```

Do not automatically preprocess.

Pattern discovery must never modify:

* source dataset
* processed dataset.

---

# 7. VERSION INTEGRITY

Every pattern discovery run must be tied to:

* dataset ID
* processed dataset ID
* profile ID
* processed checksum.

Before running:

```text
profile.dataset_id == dataset_id

processed_dataset.parent_dataset_id == dataset_id

processed dataset exists

processed dataset is valid

stored processed checksum == current processed checksum
```

If validation fails:

```text
PATTERN_DATASET_VERSION_MISMATCH
```

Do not silently analyze a different dataset version.

---

# 8. PATTERN TYPES

Implement the following core pattern types.

```text
CORRELATION
GROUP_DIFFERENCE
CATEGORICAL_ASSOCIATION
TIME_TREND
DISTRIBUTION
```

Do not add excessive pattern categories.

---

# 9. PATTERN TYPE 1 — NUMERIC CORRELATION

Discover relationships between eligible numeric variables.

Example:

```text
Sales ↔ Profit
Age ↔ Income
Temperature ↔ Demand
```

Use:

### Pearson correlation

Appropriate for linear numeric relationships.

Calculate:

```text
r
p-value
n
```

### Spearman correlation

Use where rank/monotonic relationships are appropriate.

The implementation may calculate both when useful, but avoid unnecessary duplication.

At minimum support Pearson.

---

# 10. CORRELATION FILTERS

Do not calculate every numeric pair if the dataset has many numeric columns.

Use configurable:

```text
MAX_CORRELATION_COLUMNS
MAX_CORRELATION_PAIRS
```

Example:

```text
MAX_CORRELATION_COLUMNS = 30
MAX_CORRELATION_PAIRS = 100
```

Candidate pairs should be selected deterministically.

Exclude:

* constant columns
* all-null columns
* identifier-like columns
* binary IDs
* columns with insufficient valid observations.

---

# 11. CORRELATION THRESHOLDS

Use configurable thresholds.

Suggested:

```text
ABS_CORRELATION_MIN = 0.30
```

Interpretation:

```text
0.00–0.29 → weak / usually ignore
0.30–0.49 → moderate
0.50–0.69 → moderately strong
0.70–1.00 → strong
```

Do not call correlation "causal".

The result must explicitly state:

> Correlation does not imply causation.

---

# 12. CORRELATION SIGNIFICANCE

Calculate a p-value where appropriate.

Store:

```text
correlation
absolute_correlation
p_value
sample_size
method
```

Use a configurable significance threshold:

```text
P_VALUE_THRESHOLD = 0.05
```

However, do NOT rely on p-value alone.

Large datasets can produce statistically significant but practically weak correlations.

A candidate should generally require:

```text
absolute correlation >= minimum threshold
```

and then report significance separately.

---

# 13. MULTIPLE COMPARISONS

When many numeric pairs are tested, multiple-comparison effects matter.

Implement a deterministic correction if practical.

Preferred:

```text
Benjamini-Hochberg false discovery rate correction
```

Store:

```text
raw_p_value
adjusted_p_value
```

Use:

```text
FDR_ALPHA = 0.05
```

for significance classification.

If implementation complexity becomes excessive, at minimum document the limitation rather than pretending uncorrected p-values represent independent hypothesis testing.

---

# 14. CORRELATION PATTERN OUTPUT

Example:

```json
{
  "pattern_type": "CORRELATION",
  "columns": ["sales", "profit"],
  "method": "pearson",
  "statistics": {
    "correlation": 0.78,
    "absolute_correlation": 0.78,
    "p_value": 0.0001,
    "adjusted_p_value": 0.0003,
    "sample_size": 1245
  },
  "strength": "STRONG",
  "direction": "POSITIVE",
  "significant": true
}
```

---

# 15. PATTERN TYPE 2 — GROUP DIFFERENCE

Discover whether a numeric variable differs meaningfully between categorical groups.

Example:

```text
Revenue by Region
Profit by Product Category
Salary by Department
```

For two groups:

Use an appropriate test such as:

```text
Welch's t-test
```

For more than two groups:

Use:

```text
One-way ANOVA
```

However, do not blindly apply ANOVA when assumptions are clearly inappropriate.

Where practical, use robust alternatives such as:

```text
Mann-Whitney U
Kruskal-Wallis
```

depending on group count and data characteristics.

The method used must be stored.

---

# 16. GROUP DIFFERENCE REQUIREMENTS

Only consider categorical variables with manageable cardinality.

Suggested:

```text
MIN_GROUP_SIZE = 10
MAX_GROUPS_FOR_TEST = 20
```

Exclude:

* identifier-like categorical columns
* extremely high-cardinality columns
* groups with insufficient observations.

Never generate a statistical comparison from groups with only one or two observations.

---

# 17. EFFECT SIZE

Do not rely only on p-values.

Where appropriate calculate effect size.

Examples:

### Two groups

```text
Cohen's d
```

### More than two groups

```text
eta squared
```

or another appropriate effect-size measure.

Store:

```text
effect_size
effect_size_type
```

This is important because:

> statistical significance does not necessarily mean practical significance.

---

# 18. GROUP DIFFERENCE OUTPUT

Example:

```json
{
  "pattern_type": "GROUP_DIFFERENCE",
  "dimension": "region",
  "measure": "revenue",
  "method": "ANOVA",
  "statistics": {
    "f_statistic": 12.43,
    "p_value": 0.0002,
    "adjusted_p_value": 0.001,
    "effect_size": 0.08,
    "effect_size_type": "eta_squared"
  },
  "groups": 4,
  "significant": true
}
```

---

# 19. MULTIPLE GROUP COMPARISONS

Do NOT automatically claim:

```text
North is significantly different from South
```

from an overall ANOVA.

ANOVA only indicates that at least one group differs.

If pairwise comparison is implemented, use an appropriate multiple-comparison correction such as:

```text
Tukey HSD
```

and store the pairwise results.

Otherwise report only the overall group difference.

---

# 20. PATTERN TYPE 3 — CATEGORICAL ASSOCIATION

Discover relationships between two categorical variables.

Examples:

```text
Gender ↔ Subscription
Region ↔ Product Category
Payment Type ↔ Customer Segment
```

Use:

```text
Chi-square test of independence
```

Calculate:

```text
chi_square
p_value
degrees_of_freedom
sample_size
```

Also calculate an effect-size measure such as:

```text
Cramér's V
```

---

# 21. CATEGORICAL ASSOCIATION VALIDATION

Only analyze suitable categorical columns.

Do not use:

* unique identifiers
* extremely high-cardinality fields
* free text
* columns with too many sparse categories.

Check expected cell frequencies.

If Chi-square assumptions are not suitable, either:

* skip the candidate
* or use a clearly supported alternative.

Do not blindly produce invalid statistical results.

---

# 22. CATEGORICAL ASSOCIATION OUTPUT

Example:

```json
{
  "pattern_type": "CATEGORICAL_ASSOCIATION",
  "columns": ["region", "subscription"],
  "method": "chi_square",
  "statistics": {
    "chi_square": 28.42,
    "p_value": 0.00001,
    "adjusted_p_value": 0.00003,
    "degrees_of_freedom": 3,
    "sample_size": 1245,
    "cramers_v": 0.15
  },
  "significant": true
}
```

---

# 23. PATTERN TYPE 4 — TIME TREND

Discover basic temporal trends.

This is NOT forecasting.

For suitable:

```text
datetime + numeric
```

analyze historical trend.

Possible methods:

### Linear trend

Calculate:

```text
slope
intercept
R²
```

### Trend direction

Classify:

```text
INCREASING
DECREASING
STABLE
```

based on deterministic thresholds.

---

# 24. TIME TREND REQUIREMENTS

Require:

* valid datetime column
* numeric measure
* sufficient time points
* non-constant measure.

Suggested:

```text
MIN_TIME_POINTS = 8
```

Aggregate time data when necessary.

Reuse Phase 5 temporal aggregation logic where appropriate rather than duplicating it.

---

# 25. TREND STRENGTH

Do not call a trend meaningful solely because slope is non-zero.

Use:

* R²
* slope
* number of periods
* significance where appropriate.

Possible thresholds:

```text
MIN_TREND_R2 = 0.30
```

Make configurable.

---

# 26. TIME TREND OUTPUT

Example:

```json
{
  "pattern_type": "TIME_TREND",
  "time_column": "order_date",
  "measure": "revenue",
  "direction": "INCREASING",
  "statistics": {
    "slope": 1250.4,
    "r_squared": 0.67,
    "sample_size": 36
  }
}
```

Important:

Do not say:

> Revenue will continue increasing.

Only state:

> Revenue showed an increasing historical trend over the analyzed period.

Forecasting belongs to Phase 7.

---

# 27. PATTERN TYPE 5 — DISTRIBUTION

Generate useful distribution summaries for eligible numeric columns.

Possible statistics:

```text
mean
median
std
min
max
Q1
Q3
IQR
skewness
sample_size
```

This is descriptive analysis.

Do NOT turn this into anomaly detection.

Do not label extreme observations as anomalies.

---

# 28. DISTRIBUTION PATTERN OUTPUT

Example:

```json
{
  "pattern_type": "DISTRIBUTION",
  "column": "revenue",
  "statistics": {
    "mean": 12450,
    "median": 9800,
    "std": 5400,
    "q1": 6200,
    "q3": 15100,
    "iqr": 8900,
    "skewness": 1.42,
    "sample_size": 1245
  }
}
```

A template explanation may say:

> Revenue has a right-skewed distribution.

Do not call the high values anomalies.

---

# 29. STATISTICAL ENGINE

Create a dedicated module/service.

Suggested:

```text
backend/app/services/pattern_statistics.py
```

Use appropriate scientific Python libraries already available or add only necessary dependencies.

Potential libraries:

```text
pandas
numpy
scipy
statsmodels
```

Inspect current requirements first.

Do not add large ML libraries unnecessarily.

---

# 30. PATTERN PLANNER

Create:

```text
pattern_discovery_planner.py
```

Responsibilities:

* identify eligible columns
* generate candidate pattern tests
* enforce candidate limits
* avoid identifiers
* avoid unsuitable columns
* avoid impossible tests.

---

# 31. PATTERN SCORING

Create:

```text
pattern_scoring.py
```

Every discovered pattern receives a deterministic relevance score.

Suggested factors:

```text
effect magnitude
statistical significance
sample size
data quality
pattern reliability
practical strength
redundancy
```

Do NOT use p-value alone.

For example:

A correlation of:

```text
r = 0.05
p < 0.001
```

should not outrank:

```text
r = 0.75
p < 0.001
```

simply because both are statistically significant.

---

# 32. SIGNIFICANCE VS STRENGTH

Keep these concepts separate.

Each pattern should have:

```text
strength
significance
effect_size
sample_size
```

Example:

```text
Strength: STRONG
Statistically significant: YES
```

or:

```text
Strength: WEAK
Statistically significant: YES
```

Do not collapse these into one misleading metric.

---

# 33. MULTIPLE TESTING

Many patterns may be tested simultaneously.

For families of statistical tests:

Use Benjamini-Hochberg FDR correction where practical.

Store:

```text
raw_p_value
adjusted_p_value
```

The system should clearly indicate whether significance is based on:

```text
raw p-value
```

or:

```text
adjusted p-value
```

Prefer adjusted p-values for large candidate sets.

---

# 34. SAMPLE SIZE REQUIREMENTS

Every statistical pattern should record:

```text
sample_size
```

Use minimum sample requirements.

Examples:

```text
MIN_CORRELATION_N = 10
MIN_GROUP_SIZE = 10
MIN_TIME_POINTS = 8
```

These must be configurable.

If insufficient data exists:

```text
do not generate the pattern
```

Do not fabricate statistical significance.

---

# 35. MISSING DATA HANDLING

Statistical calculations must use valid observations.

For correlation:

```text
pairwise complete observations
```

For group comparisons:

```text
valid numeric observations within each group
```

For categorical association:

```text
valid categorical pairs
```

Record:

```text
sample_size
missing_excluded
```

where useful.

Never modify the dataset.

---

# 36. CONSTANT VARIABLES

Exclude:

```text
constant numeric
constant categorical
all-null
```

from relationship tests.

They cannot provide meaningful relationships.

---

# 37. IDENTIFIER PROTECTION

Do not analyze:

```text
customer_id
transaction_id
order_id
UUID
email
phone
```

as meaningful analytical variables.

Reuse Phase 5 identifier detection where possible.

Avoid duplicate implementations.

---

# 38. CANDIDATE EXPLOSION CONTROL

This is critical.

Do NOT perform uncontrolled combinations.

Example:

```text
100 numeric columns
→ 4,950 correlation pairs
```

may be excessive.

Set limits:

```text
MAX_CORRELATION_COLUMNS = 30
MAX_CORRELATION_PAIRS = 100

MAX_GROUP_COMPARISONS = 50

MAX_CATEGORICAL_ASSOCIATIONS = 50

MAX_TIME_TRENDS = 10

MAX_DISTRIBUTION_PATTERNS = 10

MAX_TOTAL_PATTERNS = 30
```

These are configurable.

Final output must not exceed:

```text
MAX_TOTAL_PATTERNS
```

Do not fabricate patterns to reach the limit.

---

# 39. PATTERN DEDUPLICATION

Remove equivalent patterns.

For correlation:

```text
Sales ↔ Profit
```

is identical to:

```text
Profit ↔ Sales
```

Store only one.

For categorical association:

```text
Region ↔ Subscription
```

must not duplicate:

```text
Subscription ↔ Region
```

For group difference:

Avoid generating duplicate dimension/measure combinations.

---

# 40. PATTERN RESULT MODEL

Create:

```text
PatternDiscoveryRun
```

with:

```text
id
dataset_id
processed_dataset_id
profile_id
processed_checksum
status
started_at
completed_at
pattern_count
error_message
created_at
updated_at
```

Statuses:

```text
PENDING
RUNNING
COMPLETED
FAILED
```

---

# 41. PATTERN RECORD

Create:

```text
PatternResult
```

Fields:

```text
id
run_id
dataset_id
processed_dataset_id
pattern_type
rank
score
title
description
columns
statistics
significant
strength
sample_size
raw_p_value
adjusted_p_value
effect_size
method
created_at
updated_at
```

Use JSONB for flexible statistical metadata where appropriate.

Do not store arbitrary raw dataset values.

---

# 42. DATABASE RELATIONSHIP

Use:

```text
Dataset
   ↓
Processed Dataset
   ↓
PatternDiscoveryRun
   ↓
PatternResult
```

Pattern results must always be tied to the exact processed dataset version.

---

# 43. REPOSITORY

Create:

```text
pattern_discovery_repository.py
```

Methods:

```text
create_run()
update_run()
get_run()
get_latest_run()
save_patterns()
get_patterns()
get_pattern()
```

Use transactional persistence.

If generation fails:

```text
run.status = FAILED
```

and do not leave partial completed results.

---

# 44. API

Implement:

### Generate patterns

```http
POST /api/v1/datasets/{dataset_id}/patterns
```

Process:

```text
validate dataset
↓
verify profile
↓
verify processed dataset
↓
verify checksum
↓
create run
↓
load processed data
↓
generate candidates
↓
calculate statistics
↓
correct multiple testing
↓
validate
↓
score
↓
deduplicate
↓
rank
↓
persist
↓
complete run
```

---

### Get patterns

```http
GET /api/v1/datasets/{dataset_id}/patterns
```

Must not automatically run discovery.

Return the latest valid run.

---

### Get individual pattern

```http
GET /api/v1/datasets/{dataset_id}/patterns/{pattern_id}
```

Return the structured result.

---

# 45. API SCHEMAS

Create:

```text
PatternDiscoveryRunResponse
PatternResultResponse
PatternStatisticsResponse
PatternSummaryResponse
```

Use strict Pydantic validation.

Avoid leaking internal database implementation details.

---

# 46. FRONTEND

Create:

```text
PatternDiscoveryView.jsx
PatternCard.jsx
PatternSummary.jsx
PatternStatistics.jsx
```

Reuse the existing Phase 5 visualization components where useful.

---

# 47. USER FLOW

The overall flow should become:

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
```

Add a button:

```text
Discover Patterns
```

after preprocessing or visualization.

Do not require Phase 5 visualization generation to run first.

Phase 6 may reuse the same processed dataset directly.

---

# 48. PATTERN DASHBOARD

Display:

```text
Pattern Discovery
```

with summary:

```text
Patterns found: 14
Significant patterns: 9
Strong patterns: 4
```

Then pattern cards.

Example:

```text
┌─────────────────────────────────────┐
│ Strong Positive Correlation         │
│                                     │
│ Sales ↔ Profit                      │
│                                     │
│ Pearson r: 0.78                     │
│ p-value: <0.001                     │
│ n: 1,245                            │
│                                     │
│ Strong positive relationship.       │
│ Correlation does not imply causation│
└─────────────────────────────────────┘
```

---

# 49. PATTERN TYPES IN UI

Use clear labels:

```text
Correlation
Group Difference
Categorical Association
Time Trend
Distribution
```

Do not use vague AI-style labels such as:

```text
Amazing Insight
Hidden Secret
Powerful Discovery
```

Keep the presentation analytical and professional.

---

# 50. STATISTICAL DISCLAIMERS IN UI

Where relevant, display:

### Correlation

> Correlation does not imply causation.

### Historical trend

> This describes the observed historical data and is not a forecast.

### Statistical significance

> Statistical significance does not necessarily imply practical importance.

This is especially important for responsible interpretation.

---

# 51. OPTIONAL VISUAL LINK

If Phase 5 already provides a visualization recommendation related to a discovered pattern, optionally link to it.

Example:

```text
Related visualization:
Sales vs Profit scatter plot
```

Do NOT generate new visualization logic inside Phase 6.

Reuse Phase 5.

---

# 52. PERFORMANCE

Do not load excessive data into the frontend.

Pattern computations happen server-side.

Frontend receives only:

* pattern metadata
* statistical summaries
* limited supporting values where necessary.

Never send entire datasets just to explain a pattern.

---

# 53. SECURITY

Do not expose:

* raw data
* filesystem paths
* database credentials
* arbitrary statistical expressions
* arbitrary Python
* arbitrary SQL.

All statistical operations must come from server-defined functions.

---

# 54. LOGGING

Add structured events:

```text
pattern_discovery_started
pattern_candidates_generated
correlation_analysis_completed
group_analysis_completed
categorical_association_completed
time_trend_analysis_completed
distribution_analysis_completed
pattern_scoring_completed
pattern_discovery_completed
pattern_discovery_failed
```

Include:

```text
request_id
dataset_id
processed_dataset_id
pattern_run_id
```

Do not log raw rows.

---

# 55. ERROR HANDLING

Use existing error framework.

Possible errors:

```text
DATASET_NOT_FOUND
PROFILE_REQUIRED
PREPROCESSING_REQUIRED
PROCESSED_DATASET_NOT_FOUND
PATTERN_DISCOVERY_NOT_FOUND
PATTERN_DATASET_VERSION_MISMATCH
INSUFFICIENT_DATA
PATTERN_DISCOVERY_FAILED
INVALID_PATTERN_REQUEST
```

---

# 56. TESTING — STATISTICS

Create tests for:

## Correlation

Test:

* strong positive
* strong negative
* weak relationship
* constant column
* missing values
* insufficient sample
* deterministic result.

## Group differences

Test:

* two groups
* multiple groups
* insufficient group size
* unequal group sizes
* non-significant groups
* significant groups
* effect size.

## Categorical association

Test:

* associated categories
* independent categories
* sparse contingency tables
* invalid/high-cardinality columns.

## Time trend

Test:

* increasing trend
* decreasing trend
* stable series
* insufficient time points
* missing dates
* duplicate timestamps.

## Distribution

Test:

* normal-ish data
* skewed data
* constant data
* missing values.

---

# 57. MULTIPLE TESTING TESTS

Verify Benjamini-Hochberg correction where implemented.

Test:

```text
raw_p_value
adjusted_p_value
```

and ensure adjusted p-values are valid.

Do not report raw p-values as corrected values.

---

# 58. DETERMINISM TEST

Run the same dataset twice.

Verify:

```text
pattern types identical
statistics identical within floating-point tolerance
scores identical
ranking identical
```

Pattern discovery must be reproducible.

---

# 59. PERSISTENCE TESTS

Verify:

```text
PatternDiscoveryRun created
PatternResult records created
processed_dataset_id correct
processed_checksum correct
rank stored
score stored
statistics stored
pattern type stored
```

Failed runs must not appear as successful runs.

---

# 60. VERSION INTEGRITY TEST

Before discovery:

```text
processed_checksum_before
```

After discovery:

```text
processed_checksum_after
```

must remain identical.

Also verify source checksum remains unchanged.

---

# 61. DELETE/CASCADE TEST

Verify:

```text
Dataset
 ↓
PatternDiscoveryRun
 ↓
PatternResult
```

does not leave orphan records after dataset deletion according to the existing Phase 4 deletion architecture.

---

# 62. END-TO-END TEST

Perform:

```text
Upload
 ↓
Profile
 ↓
Preprocess
 ↓
Generate Visualizations
 ↓
Discover Patterns
 ↓
Retrieve Pattern Results
 ↓
Open Pattern Details
 ↓
Verify Source Checksum
 ↓
Verify Processed Checksum
```

Phase 5 visualization generation should remain functional.

---

# 63. REGRESSION TESTING

Run all existing tests:

```bash
cd backend
python -m pytest tests/ -v
```

Phase 1–5 functionality must continue working.

Especially verify:

* upload
* dataset listing
* profile
* preprocessing
* processed dataset
* visualization generation
* chart data
* source integrity
* frontend build.

---

# 64. FRONTEND BUILD

Run:

```bash
cd frontend
npm run build
```

The production build must succeed.

---

# 65. DATABASE VERIFICATION

Run:

```bash
cd backend
alembic upgrade head
alembic current
```

Verify the new migration is applied successfully.

Do not modify previous migrations.

---

# 66. DOCUMENTATION

Update:

```text
README.md
docs/architecture.md
docs/api.md
docs/development.md
docs/roadmap.md
```

Document:

* Pattern Discovery architecture
* supported pattern types
* statistical methods
* significance thresholds
* effect-size methods
* multiple testing correction
* candidate limits
* ranking
* version integrity
* limitations.

Clearly state:

> Phase 6 discovers statistically supported patterns. It does not detect anomalies, make predictions, or generate AI explanations.

---

# 67. IMPORTANT STATISTICAL PRINCIPLES

The implementation must follow these principles:

### Correlation ≠ causation

Never state causal conclusions.

### Statistical significance ≠ practical significance

Always consider effect size.

### Large sample ≠ automatically important relationship

Do not rank only by p-value.

### Historical trend ≠ forecast

Do not make future claims.

### Group difference ≠ every pair differs

Overall ANOVA only indicates that at least one group may differ.

### Missing data affects results

Record valid sample sizes.

### Multiple tests require caution

Use FDR correction where appropriate.

---

# 68. CODE QUALITY

Follow existing project architecture.

Requirements:

* type hints
* small reusable functions
* deterministic calculations
* service/repository separation
* Pydantic validation
* structured logging
* meaningful exceptions
* no route-level statistical logic
* no frontend statistical calculations for authoritative results
* no duplicated dataset loading
* no duplicated identifier detection.

Keep statistical functions independently testable.

---

# 69. RECOMMENDED FILE STRUCTURE

Adapt to the existing repository, but conceptually:

```text
backend/app/
├── db/
│   ├── models/
│   │   ├── pattern_discovery_run.py
│   │   └── pattern_result.py
│   └── repositories/
│       └── pattern_discovery_repository.py
│
├── services/
│   ├── pattern_discovery_service.py
│   ├── pattern_discovery_planner.py
│   ├── pattern_statistics.py
│   ├── pattern_scoring.py
│   └── pattern_validator.py
│
├── schemas/
│   └── patterns.py
│
└── api/
    └── routes/
        └── patterns.py
```

Frontend:

```text
frontend/src/
├── components/
│   ├── PatternDiscoveryView.jsx
│   ├── PatternCard.jsx
│   ├── PatternSummary.jsx
│   └── PatternStatistics.jsx
│
└── services/
    └── api.js
```

Use existing naming conventions if different.

---

# 70. FINAL ACCEPTANCE CHECKLIST

Phase 6 is complete only when:

## Pattern Engine

* [ ] numeric correlation implemented
* [ ] group difference analysis implemented
* [ ] categorical association implemented
* [ ] time trend implemented
* [ ] distribution analysis implemented
* [ ] effect sizes implemented where appropriate
* [ ] p-values calculated where appropriate
* [ ] multiple-testing correction implemented/documented
* [ ] sample-size checks implemented
* [ ] identifier protection implemented
* [ ] candidate limits implemented
* [ ] deterministic scoring implemented
* [ ] pattern deduplication implemented.

## Database

* [ ] PatternDiscoveryRun
* [ ] PatternResult
* [ ] migration
* [ ] foreign keys
* [ ] indexes
* [ ] processed dataset reference
* [ ] checksum
* [ ] failure handling
* [ ] delete behavior.

## APIs

* [ ] POST patterns
* [ ] GET patterns
* [ ] GET individual pattern
* [ ] validation
* [ ] structured errors.

## Frontend

* [ ] Pattern Discovery button
* [ ] Pattern dashboard
* [ ] Pattern cards
* [ ] statistics display
* [ ] significance display
* [ ] strength display
* [ ] loading state
* [ ] empty state
* [ ] error state
* [ ] appropriate statistical disclaimers.

## Testing

* [ ] correlation tests
* [ ] group comparison tests
* [ ] categorical association tests
* [ ] time trend tests
* [ ] distribution tests
* [ ] multiple-testing tests
* [ ] deterministic tests
* [ ] persistence tests
* [ ] checksum tests
* [ ] cascade tests
* [ ] API tests
* [ ] Phase 1–5 regression tests.

## Verification

* [ ] pytest passes
* [ ] frontend build passes
* [ ] migration passes
* [ ] end-to-end workflow passes
* [ ] source checksum unchanged
* [ ] processed checksum unchanged.

---

# 71. FINAL REPORT

After implementation provide:

## 1. Files created

List every new file.

## 2. Files modified

List every modified file.

## 3. Database changes

Explain:

* new tables
* relationships
* migration
* indexes.

## 4. Statistical methods

List:

* correlation method
* group comparison method
* categorical association method
* trend method
* distribution statistics
* effect-size methods
* multiple-testing correction.

## 5. Pattern limits

Report configured limits.

## 6. API endpoints

List every Phase 6 endpoint.

## 7. Frontend

Explain Pattern Discovery dashboard.

## 8. Tests

Report exact results:

```text
X passed
Y failed
Z skipped
```

Do not simply state "tests passed."

## 9. Build

Report exact frontend build result.

## 10. End-to-end verification

Report:

```text
Upload
→ Profile
→ Preprocess
→ Visualize
→ Discover Patterns
→ Retrieve Results
```

## 11. Known limitations

Clearly identify anything intentionally deferred.

---

# 72. STRICT STOP CONDITION

After Phase 6 is fully implemented and verified:

**STOP.**

Do NOT implement Phase 7.

Do not add:

* anomaly detection
* outlier detection engine
* Isolation Forest
* LOF
* forecasting
* prediction
* classification
* regression prediction
* clustering
* PCA
* LLM
* Gemini
* OpenAI
* AI-generated insights
* natural-language analyst.

Phase 6 ends at:

```text
Dataset
   ↓
Profile
   ↓
Preprocess
   ↓
Visualize
   ↓
Pattern Discovery
   ↓
Statistical Evidence
   ↓
Ranked Pattern Results
   ↓
Pattern Dashboard
```

The next phase will separately handle:

```text
Phase 7
Anomaly Detection + Prediction
```

Do not implement any Phase 7 functionality now.

Update the roadmap to mark Phase 6 complete only after all acceptance criteria and regression tests pass.

Then **STOP and WAIT for the next instruction.**
