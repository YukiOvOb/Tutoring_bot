from __future__ import annotations

"""Simple chooser helpers.

Provides parse_intent(text) -> str and to_choice_number(intent_label) -> int.
"""

from typing import Final


def parse_intent(text: str) -> str:
    normalized = text.strip().lower()
    if normalized in (
        "1",
        "咨询",
        "consult",
        "consultation",
        "tutoring consultation",
        "tutoringconsultation",
    ):
        return "consultation"
    if normalized in (
        "2",
        "免费",
        "free",
        "free material",
        "free materials",
        "free chinese materials",
    ):
        return "free_material"
    if normalized == "备考":
        return "exam_prep"
    if normalized == "自己兴趣":
        return "interest"
    return text


def to_choice_number(intent_label: str) -> int:
    if intent_label == "consultation":
        return 1
    if intent_label == "free_material":
        return 2
    return 0
