from src.llm.client import LLMClient


def test_llm_generate():
    llm = LLMClient()

    response = llm.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say something you want (around 100 words)."
    )

    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    