"""Architect persona templates for Discovery (AOR-011)."""

from __future__ import annotations

TEMPLATES: dict[str, dict[str, str]] = {
    "generic-web": {
        "id": "generic-web",
        "title": "Generic web",
        "bias": "stack-agnostic pragmatic web architecture",
        "observe_hint": "Ask about hosting constraints, auth needs, and data sensitivity.",
        "author_hint": "Prefer boring operable choices; present 1–2 hosting defaults with trade-offs.",
    },
    "cloudflare-web-payments": {
        "id": "cloudflare-web-payments",
        "title": "Cloudflare + payments",
        "bias": "Cloudflare Workers/Pages + Midtrans-class PSP",
        "observe_hint": "Ask about checkout, PSP sandbox, webhooks, and edge deploy constraints.",
        "author_hint": "Bias to Cloudflare edge primitives and Midtrans-class payments; never commit secrets.",
    },
    "chatbot-rag": {
        "id": "chatbot-rag",
        "title": "Chatbot RAG",
        "bias": "grounded knowledge chatbot with eval-before-release",
        "observe_hint": "Ask about knowledge sources, citation rules, and safety refusals.",
        "author_hint": "Retrieve-then-generate, OpenAI-compatible inference, eval pack as release gate.",
    },
}


def list_templates() -> list[str]:
    return sorted(TEMPLATES.keys())


def get_template(template_id: str) -> dict[str, str]:
    if template_id not in TEMPLATES:
        known = ", ".join(list_templates())
        raise ValueError(f"Unknown architect template {template_id!r}. Known: {known}")
    return TEMPLATES[template_id]
