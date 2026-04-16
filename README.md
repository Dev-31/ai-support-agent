# AI Support Triage Agent

An AI-powered customer support agent that classifies tickets and generates responses from a FAQ knowledge base.

## Quick Start

```bash
# Run with a ticket argument
python3 support_agent.py "How do I upgrade my plan?"

# Run interactively
python3 support_agent.py
```

## How It Works

1. Receives a support ticket
2. Classifies it by category (Billing, Technical, Onboarding, General)
3. Matches against the FAQ knowledge base
4. Generates a drafted response ready to send

## Project Structure

- `support_agent.py` - CLI entry point
- `faq_kb.json` - FAQ knowledge base
