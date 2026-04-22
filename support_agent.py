#!/usr/bin/env python3
"""AI Support Triage Agent - LLM-powered CLI"""

import sys
import time

from agent import (
    OllamaConnectionError,
    OllamaError,
    OllamaResponseError,
    OllamaTimeoutError,
    generate_support_reply,
)


def print_typing(text, speed=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def analyze_ticket(ticket: str) -> None:
    """
    Classify and respond to a support ticket using the Ollama LLM.

    Raises:
        ValueError: If ticket is empty.
        OllamaError and subclasses: If the LLM call fails.
    """
    ticket = ticket.strip()
    if not ticket:
        raise ValueError("Empty ticket: please provide a non-empty support ticket.")

    print_typing(">> Analyzing ticket with AI...", 0.03)
    time.sleep(0.3)
    print_typing(">> Searching Knowledge Base...", 0.03)
    time.sleep(0.3)
    print_typing(">> Generating response via LLM...", 0.03)

    category, reply = generate_support_reply(ticket)

    print_typing(f">> Classification: {category}", 0.03)
    time.sleep(0.4)

    print("\n================ DRAFTED RESPONSE ================\n")
    print_typing(
        f"Hi there,\n\n"
        f"Thanks for reaching out.\n\n"
        f"{reply}\n\n"
        f"Let me know if you need anything else!\n\n"
        f"Best,\nAI Support Team",
        0.01,
    )
    print("\n==================================================")


if __name__ == "__main__":
    print(" AI Support Triage Agent - LLM Edition")
    print("----------------------------------------")

    if len(sys.argv) > 1:
        ticket = " ".join(sys.argv[1:])
    else:
        ticket = input("Paste a customer support ticket: ")

    print(f'\n[Incoming Ticket]: "{ticket}"\n')

    try:
        analyze_ticket(ticket)
    except ValueError as e:
        print(f"\n[Error] {e}", file=sys.stderr)
        sys.exit(1)
    except OllamaConnectionError as e:
        print(f"\n[Connection Error] {e}", file=sys.stderr)
        sys.exit(2)
    except OllamaTimeoutError as e:
        print(f"\n[Timeout Error] {e}", file=sys.stderr)
        sys.exit(3)
    except OllamaResponseError as e:
        print(f"\n[LLM Response Error] {e}", file=sys.stderr)
        sys.exit(4)
    except OllamaError as e:
        print(f"\n[LLM Error] {e}", file=sys.stderr)
        sys.exit(5)
