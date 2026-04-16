#!/usr/bin/env python3
"""Stress tests for support_agent.py — edge cases, invalid inputs, error conditions."""
import json
import pytest
from unittest.mock import patch, mock_open

import support_agent

# ── Test fixtures ─────────────────────────────────────────────────────────────

VALID_KB = json.dumps({
    "faqs": [
        {"category": "billing",    "question": "Upgrade?",  "answer": "Billing answer."},
        {"category": "technical",  "question": "Sandbox?",  "answer": "Technical answer."},
        {"category": "onboarding", "question": "Invite?",   "answer": "Onboarding answer."},
    ]
})

EMPTY_FAQS_KB   = json.dumps({"faqs": []})
MISSING_KEY_KB  = json.dumps({"questions": []})   # wrong top-level key
INVALID_JSON    = "{ not valid json !!!"


def run_analyze(ticket, kb_data=VALID_KB):
    """Run analyze_ticket with all I/O mocked out. Returns the print_typing mock."""
    with patch("builtins.open", mock_open(read_data=kb_data)), \
         patch("support_agent.print_typing") as mock_pt, \
         patch("time.sleep"), \
         patch("builtins.print"):
        support_agent.analyze_ticket(ticket)
        return mock_pt


def typed_text(mock_pt):
    """Concatenate every string passed to print_typing for easy assertion."""
    return " ".join(str(args[0]) for args, _ in mock_pt.call_args_list)


# ── Edge-case inputs ──────────────────────────────────────────────────────────

class TestEdgeCaseInputs:
    def test_empty_string_raises(self):
        """Empty ticket should raise ValueError, not crash with a traceback."""
        with pytest.raises(ValueError, match="[Ee]mpty"):
            run_analyze("")

    def test_whitespace_only_raises(self):
        """Whitespace-only ticket should raise ValueError."""
        with pytest.raises(ValueError, match="[Ee]mpty"):
            run_analyze("   \t\n")

    def test_very_long_ticket(self):
        """50 000-character ticket should not crash."""
        run_analyze("upgrade " * 6250)

    def test_special_characters(self):
        """Punctuation and control characters should not crash."""
        run_analyze("!@#$%^&*()<>?/\\|\n\t---")

    def test_unicode_input(self):
        """Unicode text should not crash."""
        run_analyze("comment ça va? 你好 مرحبا")

    def test_multiline_ticket(self):
        """Multi-line ticket body should not crash."""
        run_analyze("Hello,\nI need help with billing.\nThanks.")

    def test_numbers_only(self):
        """Numeric-only ticket should not crash."""
        run_analyze("12345 6789")

    def test_single_character(self):
        """Single non-matching character should fall through to General Inquiry."""
        mock_pt = run_analyze("?")
        assert "General Inquiry" in typed_text(mock_pt)


# ── Classification logic ──────────────────────────────────────────────────────

class TestClassification:
    def test_sandbox_classifies_technical(self):
        mock_pt = run_analyze("my agent is stuck in sandbox mode")
        assert "Technical" in typed_text(mock_pt)

    def test_upgrade_classifies_billing(self):
        mock_pt = run_analyze("I want to upgrade my plan")
        assert "Billing" in typed_text(mock_pt)

    def test_billing_keyword_classifies_billing(self):
        mock_pt = run_analyze("I have a billing question")
        assert "Billing" in typed_text(mock_pt)

    def test_unknown_keyword_classifies_general(self):
        mock_pt = run_analyze("random unrelated question here")
        assert "General Inquiry" in typed_text(mock_pt)

    def test_technical_answer_in_response(self):
        mock_pt = run_analyze("sandbox issue")
        assert "Technical answer." in typed_text(mock_pt)

    def test_billing_answer_in_response(self):
        mock_pt = run_analyze("upgrade my account")
        assert "Billing answer." in typed_text(mock_pt)

    def test_case_insensitive_sandbox(self):
        mock_pt = run_analyze("SANDBOX ERROR")
        assert "Technical" in typed_text(mock_pt)

    def test_case_insensitive_billing(self):
        mock_pt = run_analyze("BILLING PROBLEM")
        assert "Billing" in typed_text(mock_pt)


# ── Knowledge-base error conditions ──────────────────────────────────────────

class TestKBErrors:
    def test_empty_faqs_technical_no_crash(self):
        """KB with empty faqs list — match is None — must not crash."""
        run_analyze("sandbox issue", EMPTY_FAQS_KB)

    def test_empty_faqs_billing_no_crash(self):
        """KB with empty faqs list — billing path — must not crash."""
        run_analyze("upgrade question", EMPTY_FAQS_KB)

    def test_empty_faqs_fallback_message(self):
        """When match is None, response must still include a fallback message."""
        mock_pt = run_analyze("sandbox issue", EMPTY_FAQS_KB)
        text = typed_text(mock_pt)
        # Must produce *some* drafted response body
        assert "Hi there" in text

    def test_missing_faqs_key_raises(self):
        """KB missing the 'faqs' key should raise KeyError."""
        with pytest.raises(KeyError):
            run_analyze("upgrade question", MISSING_KEY_KB)

    def test_invalid_json_raises(self):
        """Invalid JSON in KB should raise json.JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError):
            run_analyze("upgrade question", INVALID_JSON)

    def test_missing_kb_file_raises(self):
        """Missing KB file should raise FileNotFoundError."""
        with patch("builtins.open", side_effect=FileNotFoundError("No such file")), \
             patch("support_agent.print_typing"), \
             patch("time.sleep"), \
             patch("builtins.print"):
            with pytest.raises(FileNotFoundError):
                support_agent.analyze_ticket("upgrade question")
