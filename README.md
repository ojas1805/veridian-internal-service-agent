# Veridian Internal Service Agent

An AI-powered internal IT support agent designed to understand employee requests, retrieve relevant company policies, search historical tickets, resolve eligible self-service requests, and escalate requests that require human intervention.

The system is designed as an **internal service agent**, not just a conversational chatbot. It maintains request states, creates structured support tickets, records audit events, provides decision transparency, and exposes retrieved policy and ticket evidence.

---

## Overview

Employees can submit IT support requests using natural language.

The agent:

1. Understands the employee's request.
2. Detects the intent and support category.
3. Extracts relevant entities and urgency.
4. Retrieves relevant Veridian policies using semantic search.
5. Searches historical ticket data for useful context.
6. Identifies missing information when required.
7. Resolves simple requests when the supplied policy allows self-service.
8. Escalates requests requiring human intervention.
9. Creates structured support tickets.
10. Maintains a persistent audit trail.
11. Provides sources and evidence behind its decisions.
12. Allows human reviewers to update ticket status through the dashboard.

---

## Key Features

### Natural Language Understanding

The agent supports requests such as:

- Password reset and account lockout
- VPN access and credential issues
- Laptop and hardware support
- Printer issues
- Guest Wi-Fi
- Software installation
- Mailbox quota issues
- Expense software access
- Work-from-home equipment
- Security incidents
- Ambiguous or incomplete requests

The system identifies:

- Intent
- Category
- Entities
- Urgency
- Missing information

---

## Retrieval-Augmented Generation / Semantic Retrieval

The system uses:

- Sentence Transformers
- `all-MiniLM-L6-v2`
- ChromaDB
- Cosine/semantic similarity
- Structured policy metadata

The knowledge base contains the supplied Veridian policies.

Every request retrieves policy information that can be surfaced as:

- Policy ID
- Policy title
- Category
- Policy content
- Retrieval distance

Example:

```text
KB-03
Laptop Replacement
Hardware

Laptops are eligible for replacement after 3 years of service,
or earlier in case of verified hardware failure.