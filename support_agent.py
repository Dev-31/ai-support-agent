#!/usr/bin/env python3
"""AI Support Triage Agent - MVP CLI"""
import sys
import json
import time

def print_typing(text, speed=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

import os

_KB_PATH = os.path.join(os.path.dirname(__file__), 'faq_kb.json')

def analyze_ticket(ticket):
    ticket = ticket.strip()
    if not ticket:
        raise ValueError("Empty ticket: please provide a non-empty support ticket.")

    with open(_KB_PATH, 'r') as f:
        kb = json.load(f)
    
    ticket_lower = ticket.lower()
    
    print_typing(">> Analyzing ticket...", 0.03)
    time.sleep(0.5)
    print_typing(">> Searching Knowledge Base...", 0.03)
    time.sleep(0.5)
    
    if "sandbox" in ticket_lower:
        category = "Technical"
        match = next((item for item in kb['faqs'] if item['category'] == 'technical'), None)
    elif "upgrade" in ticket_lower or "billing" in ticket_lower:
        category = "Billing"
        match = next((item for item in kb['faqs'] if item['category'] == 'billing'), None)
    else:
        category = "General Inquiry"
        match = {"answer": "I'll escalate this to our human support team for further review."}
    
    print_typing(f">> Classification: {category}", 0.03)
    time.sleep(0.5)
    
    print("\n================ DRAFTED RESPONSE ================\n")
    answer = match['answer'] if match else "Our support team will review this ticket and follow up shortly."
    print_typing(f"Hi there,\n\nThanks for reaching out about this.\n\n{answer}\n\nLet me know if you need anything else!\n\nBest,\nAI Support Team", 0.01)
    print("\n==================================================")

if __name__ == "__main__":
    print(" AI Support Triage Agent - MVP Ready")
    print("--------------------------------------")
    if len(sys.argv) > 1:
        ticket = sys.argv[1]
    else:
        ticket = input("Paste a customer support ticket: ")
    
    print(f"\n[Incoming Ticket]: \"{ticket}\"\n")
    analyze_ticket(ticket)
