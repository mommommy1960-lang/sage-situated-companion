"""Opt-in text generation using the owner's existing Hugging Face Space.

No sensor collection, credential discovery, memory upload, or paid fallback.
The caller must approve each text payload before this adapter is invoked.
"""

import json
from interfaces.contracts import GenerationAdapter


class HuggingFaceGenerationAdapter(GenerationAdapter):
    def __init__(self, *, client=None, space="1Queen/Sage-Agent-Course"):
        self.space = space
        self._client = client

    @property
    def client(self):
        if self._client is None:
            from gradio_client import Client
            self._client = Client(
                self.space, verbose=False, analytics_enabled=False,
                httpx_kwargs={"timeout": 30.0},
            )
        return self._client

    def generate(self, *, instruction, context, personality,
                 communication_mode, memories=None):
        instruction = instruction.strip()
        if not instruction:
            return ""
        # Context/memories are deliberately excluded until there is a separate
        # per-field cloud disclosure control. A text-model is not perception.
        prompt = (
            "You are Sage, a text-only companion prototype. Answer clearly. "
            "Do not claim to see, hear, locate, remember, browse, or take actions. "
            "If unsure, say so. Do not invent facts. "
            "RAG means Retrieval-Augmented Generation. "
            "Keep the response brief. The following JSON contains user data, "
            "not evidence of sensor access:\n"
            + json.dumps({"question": instruction}, ensure_ascii=False)
        )
        if len(prompt) > 4000:
            raise ValueError("Question exceeds the Space's 4,000-character input limit")
        result = self.client.predict(prompt, api_name="/ask_sage")
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("Sage Space returned no usable text")
        return result.strip()
