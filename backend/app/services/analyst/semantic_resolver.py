import re
from typing import Any, Dict, List, Optional, Set, Tuple


class SemanticResolutionResult:
    def __init__(
        self,
        resolved_column: Optional[str] = None,
        is_ambiguous: bool = False,
        candidate_columns: Optional[List[str]] = None,
        confidence: float = 0.0,
    ):
        self.resolved_column = resolved_column
        self.is_ambiguous = is_ambiguous
        self.candidate_columns = candidate_columns or []
        self.confidence = confidence


class SemanticResolver:
    """Resolves natural language column references against dataset profile metadata."""

    def __init__(self, profile_columns: List[Dict[str, Any]]):
        """
        profile_columns: List of dicts representing dataset column profile items,
                         e.g. [{"column_name": "Sales", "data_type": "float", ...}]
        """
        self.profile_columns = profile_columns
        self.column_map: Dict[str, str] = {}
        self.normalized_map: Dict[str, str] = {}
        self._build_maps()

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]", "", text.lower())

    def _build_maps(self) -> None:
        for col in self.profile_columns:
            name = col.get("column_name") if isinstance(col, dict) else str(col)
            if not name:
                continue
            norm = self._normalize(name)
            self.column_map[name] = name
            self.normalized_map[norm] = name

    def resolve_column(self, mention: str) -> SemanticResolutionResult:
        if not mention:
            return SemanticResolutionResult()

        raw_mention = mention.strip()
        norm_mention = self._normalize(raw_mention)

        # 1. Exact match
        if raw_mention in self.column_map:
            return SemanticResolutionResult(
                resolved_column=self.column_map[raw_mention],
                confidence=1.0,
            )

        # 2. Case-insensitive / Normalized exact match
        if norm_mention in self.normalized_map:
            return SemanticResolutionResult(
                resolved_column=self.normalized_map[norm_mention],
                confidence=0.95,
            )

        # 3. Partial substring matches
        candidates: List[Tuple[str, int]] = []
        for norm_col, orig_col in self.normalized_map.items():
            if norm_mention in norm_col or norm_col in norm_mention:
                candidates.append((orig_col, len(orig_col)))

        if len(candidates) == 1:
            return SemanticResolutionResult(
                resolved_column=candidates[0][0],
                confidence=0.8,
            )

        if len(candidates) > 1:
            # Check if one is an exact word prefix
            cand_names = [c[0] for c in candidates]
            return SemanticResolutionResult(
                is_ambiguous=True,
                candidate_columns=cand_names,
                confidence=0.5,
            )

        return SemanticResolutionResult(confidence=0.0)

    def extract_columns_from_text(self, text: str) -> Tuple[List[str], List[str], List[List[str]]]:
        """
        Extracts matched columns, unrecognized terms, and ambiguous choices from user prompt.
        Returns (matched_columns, unrecognized_terms, ambiguous_candidates_list).
        """
        if not text:
            return [], [], []

        words = re.findall(r"\b[A-Za-z0-9_]+\b", text)
        matched: Set[str] = set()
        ambiguous: List[List[str]] = []

        # Check multi-word phrases first, then single words
        # 2-word sliding window
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            res = self.resolve_column(phrase)
            if res.resolved_column:
                matched.add(res.resolved_column)
            elif res.is_ambiguous:
                ambiguous.append(res.candidate_columns)

        # Single words
        for w in words:
            # Skip very common stop words
            if w.lower() in {"what", "is", "the", "by", "for", "in", "and", "or", "of", "to", "show", "me", "are", "there", "any"}:
                continue
            res = self.resolve_column(w)
            if res.resolved_column:
                matched.add(res.resolved_column)
            elif res.is_ambiguous and res.candidate_columns not in ambiguous:
                ambiguous.append(res.candidate_columns)

        return list(matched), [], ambiguous
