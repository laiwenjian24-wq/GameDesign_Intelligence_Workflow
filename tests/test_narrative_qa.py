"""Tests for experimental Narrative QA answer generation."""

from src.llm.client import FakeLLMClient
from src.qa.narrative_qa import answer_from_full_context, answer_from_rag_context_pack


def _full_bundle_with_rin_canon():
    return {
        "question": "Rin是什么身份？",
        "instructions": [],
        "groups": {
            "canon": [
                {
                    "source_file": "story.md",
                    "status": "canon",
                    "asset_type": "character",
                    "text": "### Rin [Nexus-7 android]\nRin is a Nexus-7 android.",
                }
            ],
            "draft": [],
            "deprecated": [],
            "inspiration": [],
        },
        "source_list": [],
        "estimated_character_count": 0,
        "rough_token_estimate": 0,
    }


def _rag_pack_with_rin_canon():
    return {
        "canon_context": [
            {
                "source_file": "story.md",
                "status": "canon",
                "excerpt": "### Rin [Nexus-7 android]",
                "text": "Rin is a Nexus-7 android.",
                "metadata": {"section_title": "Rin [Nexus-7 android]"},
            }
        ],
        "draft_reference": [],
        "deprecated_warnings": [],
        "inspiration_context": [],
        "missing_evidence": [],
    }


def test_ask_rag_rin_identity_fake():
    report = answer_from_rag_context_pack(
        "Rin是什么身份？",
        _rag_pack_with_rin_canon(),
        FakeLLMClient(),
        provider="fake",
    )

    assert report["mode"] == "rag-context-pack"
    assert "Nexus-7 android" in report["answer"]["answer"]
    assert report["answer"]["confidence"] == "high"
    assert "story.md#Rin [Nexus-7 android]" in report["answer"]["canon_sources"]


def test_ask_full_rin_identity_fake():
    report = answer_from_full_context(
        "Rin是什么身份？",
        _full_bundle_with_rin_canon(),
        FakeLLMClient(),
        provider="fake",
    )

    assert report["mode"] == "full-context"
    assert "Nexus-7 android" in report["answer"]["answer"]
    assert report["answer"]["confidence"] == "high"
    assert report["answer"]["canon_sources"] == ["story.md"]


def test_ask_rag_requires_canon():
    report = answer_from_rag_context_pack(
        "Rin是什么身份？",
        {
            "canon_context": [],
            "draft_reference": [],
            "deprecated_warnings": [],
            "missing_evidence": ["No canon source selected."],
        },
        FakeLLMClient(),
        provider="fake",
    )

    assert report["answer"]["confidence"] == "low"
    assert "Insufficient canon evidence" in report["answer"]["answer"]
    assert report["answer"]["canon_sources"] == []
    assert "No canon source selected." in report["answer"]["missing_evidence"]


def test_deprecated_not_used_as_fact():
    report = answer_from_rag_context_pack(
        "Rin是什么身份？",
        {
            "canon_context": [],
            "draft_reference": [],
            "deprecated_warnings": [
                {
                    "source_file": "old.md",
                    "status": "deprecated",
                    "text": "Old draft says Rin has a different identity.",
                }
            ],
            "missing_evidence": [],
        },
        FakeLLMClient(),
        provider="fake",
    )

    assert report["answer"]["canon_sources"] == []
    assert "Insufficient canon evidence" in report["answer"]["answer"]
    assert "Draft, deprecated, and inspiration material cannot be used as current fact." in report["answer"]["limitations"]
