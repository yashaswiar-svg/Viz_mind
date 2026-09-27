import json
from typing import Any, Dict, List
from app.services.insight_candidate_generator import InsightCandidate


class InsightPromptBuilder:
    """Constructs strict grounding prompts for LLM explanation generation."""

    def build_system_instruction(self) -> str:
        return (
            "You are VizMind's AI Explanation Layer. Your role is strictly to explain pre-computed analytical evidence.\n"
            "CRITICAL RULES:\n"
            "1. GROUNDING ONLY: Use ONLY the provided analytical evidence metrics and evidence IDs. Do NOT invent new facts or statistics.\n"
            "2. NO STATISTICAL CALCULATIONS: Do not calculate new statistics, probabilities, or p-values. Explain the provided numbers.\n"
            "3. NO RAW DATA: Rely exclusively on the provided pre-computed statistical summaries. Never request or refer to raw CSV rows.\n"
            "4. NO CAUSALITY CLAIMS: Correlation does NOT imply causation. Never state that variable X caused, led to, or resulted in Y unless a causal experiment design is explicitly stated in evidence.\n"
            "5. NO FUTURE CERTAINTY: Predictions and forecasts are statistical model estimates, not guarantees. Never state that an outcome is guaranteed or will definitely happen.\n"
            "6. MANDATORY EVIDENCE CITATIONS: Every factual claim in your output MUST include an array of valid evidence IDs (e.g. ['EVID_001']) from the supplied candidate evidence.\n"
            "7. NO AUTONOMOUS DECISIONS: Do not recommend autonomous business decisions (e.g. 'fire vendor', 'raise prices 20%'). Inform the user about findings.\n"
            "8. OUTPUT FORMAT: Respond ONLY with a valid JSON object dictionary matching the specified JSON schema."
        )

    def build_user_prompt(self, candidate: InsightCandidate) -> Tuple[str, Dict[str, Any]]:
        evid_payload = [item.to_dict() for item in candidate.evidence_items]

        schema = {
            "title": "Concise headline title summarizing the insight (string)",
            "summary": "1-2 sentence executive summary of the grounded finding (string)",
            "explanation": "Detailed natural language narrative explaining what the computed evidence metrics mean (string)",
            "claims": [
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": "Factual claim statement supported by evidence (string)",
                    "evidence_ids": ["EVID_001"],
                }
            ],
            "limitations": [
                "Specific analytical limitation statement (e.g. Correlation does not establish causation) (string)"
            ],
        }

        prompt_str = (
            f"Candidate ID: {candidate.candidate_id}\n"
            f"Insight Type: {candidate.insight_type}\n"
            f"Title Template: {candidate.title_template}\n"
            f"Target Columns: {json.dumps(candidate.target_columns)}\n\n"
            f"ANALYTICAL EVIDENCE PACKAGE:\n"
            f"{json.dumps(evid_payload, indent=2)}\n\n"
            f"REQUIRED OUTPUT JSON SCHEMA:\n"
            f"{json.dumps(schema, indent=2)}\n\n"
            f"Generate an explainable narrative grounded strictly in the evidence items above. "
            f"Ensure every claim references at least one evidence ID."
        )

        return prompt_str, schema
