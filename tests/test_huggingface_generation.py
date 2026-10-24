from types import SimpleNamespace
import pytest
from interfaces.huggingface_generation import HuggingFaceGenerationAdapter


def test_payload_excludes_private_context_and_memory():
    calls = []
    adapter = HuggingFaceGenerationAdapter(client=SimpleNamespace(
        predict=lambda *args, **kwargs: calls.append((args, kwargs)) or " Answer "))
    result = adapter.generate(instruction="Explain RAG", context={"location": "SECRET GPS"},
        personality={"preferred_address": "PRIVATE NAME"}, communication_mode="normal",
        memories=[SimpleNamespace(content="SECRET MEMORY")])
    assert result == "Answer"
    payload = calls[0][0][0]
    assert "Explain RAG" in payload
    assert "SECRET" not in payload and "PRIVATE NAME" not in payload
    assert calls[0][1] == {"api_name": "/ask_sage"}


@pytest.mark.parametrize("response", [None, "", [], {"text": "answer"}])
def test_invalid_output_is_not_presented_as_success(response):
    adapter = HuggingFaceGenerationAdapter(client=SimpleNamespace(predict=lambda *a, **k: response))
    with pytest.raises(RuntimeError):
        adapter.generate(instruction="Hi", context={}, personality={}, communication_mode="normal")


def test_empty_and_oversized_input_never_calls_service():
    def forbidden(*a, **k):
        pytest.fail("unexpected remote call")
    adapter = HuggingFaceGenerationAdapter(client=SimpleNamespace(predict=forbidden))
    args = dict(context={}, personality={}, communication_mode="normal")
    assert adapter.generate(instruction="  ", **args) == ""
    with pytest.raises(ValueError):
        adapter.generate(instruction="x" * 4000, **args)
