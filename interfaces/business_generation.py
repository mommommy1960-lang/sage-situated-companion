"""Approved-fact lookup adapter around Sage's existing GenerationAdapter contract.

No network, provider credentials, action execution, or memory disclosure.
"""
import json
import re
from pathlib import Path
from interfaces.contracts import GenerationAdapter


def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


class BusinessFAQGenerationAdapter(GenerationAdapter):
    def __init__(self, profile_id="civic"):
        path = Path(__file__).resolve().parents[1] / "apps/business_ambassador/data.json"
        profiles = json.loads(path.read_text())["profiles"]
        self.profile = next((p for p in profiles if p["id"] == profile_id), None)
        if self.profile is None:
            raise ValueError("Unknown approved business profile")

    def generate(self, *, instruction, context, personality, communication_mode, memories=None):
        if not isinstance(instruction, str) or not instruction.strip() or len(instruction) > 500:
            raise ValueError("Enter a question of 1–500 characters")
        key = normalize(instruction)
        matches = [f for f in self.profile["faqs"] if any(normalize(a) == key for a in [f["question"], *f["aliases"]])]
        if len(matches) != 1:
            return "I don’t have an approved answer to that question. A person should help rather than having me guess."
        fact = matches[0]
        return f'{fact["answer"]}\nSource: {fact["sourceLabel"]}'
