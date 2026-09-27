import json
import re
from typing import Any, Dict, List
from app.services.llm.base_provider import LLMProvider, LLMResponseFormatError


class MockProvider(LLMProvider):
    """Deterministic mock provider returning structured schema-compliant output without network requests."""

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:

        # Extract evidence IDs from prompt text (e.g. EVID_001, EVID_002)
        found_evids = re.findall(r"EVID_\d+", prompt)
        unique_evids = list(dict.fromkeys(found_evids)) if found_evids else ["EVID_001"]

        # Extract title or candidate info if present
        title_match = re.search(r'"title_template":\s*"([^"]+)"', prompt)
        title = title_match.group(1) if title_match else "Statistical Evidence Analysis"

        cand_type_match = re.search(r'"insight_type":\s*"([^"]+)"', prompt)
        itype = cand_type_match.group(1) if cand_type_match else "ANALYTICAL"

        summary = f"The {itype.lower().replace('_', ' ')} candidate was evaluated against grounded analytical evidence ({', '.join(unique_evids)})."
        explanation = (
            f"VizMind analytical engines computed statistical evidence supporting this explanation. "
            f"Specific metrics recorded under evidence IDs {', '.join(unique_evids)} establish the quantitative foundation for this insight."
        )

        claims = [
            {
                "claim_id": "CLAIM_001",
                "claim_text": f"Grounded analytical evidence ({', '.join(unique_evids)}) supports the evaluated {itype.lower().replace('_', ' ')} finding.",
                "evidence_ids": unique_evids,
            }
        ]

        limitations = [
            "Analytical evidence reflects computed sample metrics.",
            "Correlation does not establish causation.",
        ]

        output = {
            "title": title,
            "summary": summary,
            "explanation": explanation,
            "claims": claims,
            "limitations": limitations,
        }

        return output
