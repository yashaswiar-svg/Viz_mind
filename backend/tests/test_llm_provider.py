import pytest
from app.services.llm.base_provider import LLMProvider, LLMProviderError
from app.services.llm.mock_provider import MockProvider
from app.services.llm.provider_factory import get_llm_provider


@pytest.mark.asyncio
async def test_mock_provider_completion():
    provider = MockProvider()
    prompt = "Candidate CAND_001 with evidence EVID_001 and EVID_002."
    sys_inst = "Grounding instructions."
    schema = {"title": "str"}

    res = await provider.generate_completion(prompt, sys_inst, schema)

    assert isinstance(res, dict)
    assert "title" in res
    assert "summary" in res
    assert "explanation" in res
    assert "claims" in res
    assert "limitations" in res
    assert len(res["claims"]) > 0
    assert "EVID_001" in res["claims"][0]["evidence_ids"]


def test_provider_factory_default():
    provider = get_llm_provider("mock")
    assert isinstance(provider, MockProvider)
