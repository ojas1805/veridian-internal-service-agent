import json
import re
from datetime import datetime

from database import SessionLocal
from models import Request
from retrieval import search_knowledge, search_ticket_history
from audit_engine import record_audit
from ticket_engine import create_ticket


# ============================================================
# REQUEST ID
# ============================================================

def generate_request_id(db):
    latest_request = (
        db.query(Request)
        .order_by(Request.id.desc())
        .first()
    )

    if latest_request is None:
        return "REQ-01"

    try:
        number = int(latest_request.request_id.split("-")[1])
        return f"REQ-{number + 1:02d}"
    except Exception:
        return f"REQ-{latest_request.id + 1:02d}"


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(message):
    text = message.lower().strip()

    # Security
    if any(word in text for word in [
        "phishing",
        "phish",
        "malware",
        "unauthorized access",
        "suspicious email",
        "suspicious link",
        "login link",
        "security incident"
    ]):
        return "security_incident", "Security"

    # VPN
    if any(word in text for word in [
        "vpn",
        "virtual private network"
    ]):
        return "vpn_access", "Network Access"

    # Password
    if any(word in text for word in [
        "password",
        "locked out",
        "login password",
        "forgot password",
        "failed attempts"
    ]):
        return "password_reset", "Account Access"

    # Printer
    if any(word in text for word in [
        "printer",
        "printing",
        "print job",
        "paper jam",
        "print spooler"
    ]):
        return "printer_issue", "Hardware"

    # Mailbox
    if any(word in text for word in [
        "mailbox",
        "mailbox full",
        "email quota",
        "email storage",
        "mail storage",
        "cannot send email",
        "can't send email"
    ]):
        return "mailbox_quota", "Email"

    # Guest Wi-Fi
    if any(word in text for word in [
        "guest wifi",
        "guest wi-fi",
        "guest wireless",
        "visitor wifi",
        "visitor wi-fi"
    ]):
        return "guest_wifi", "Network Access"

    # Expense software
    if any(word in text for word in [
        "expense software",
        "expense tool",
        "expense system",
        "expense app"
    ]):
        return "expense_access", "Finance Software"

    # Home office equipment
    if any(word in text for word in [
        "home office",
        "work from home",
        "working from home",
        "wfh",
        "monitor at home",
        "chair at home"
    ]):
        return "home_office_equipment", "Equipment"

    # Software installation
    if any(word in text for word in [
        "install software",
        "install an app",
        "software installation",
        "browser extension",
        "productivity tool",
        "application installation",
        "install a tool"
    ]):
        return "software_installation", "Software"

    # Laptop
    if any(word in text for word in [
        "laptop",
        "computer",
        "screen flicker",
        "screen is flickering",
        "device won't turn on",
        "device wont turn on",
        "laptop won't turn on",
        "laptop wont turn on",
        "hardware failure"
    ]):
        return "laptop_support", "Hardware"

    # Unknown
    return "unknown", "General Support"


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def extract_entities(message):
    text = message.lower()

    entities = {}

    # Employee type
    if "contractor" in text:
        entities["employee_type"] = "contractor"
    elif "full-time" in text or "full time" in text:
        entities["employee_type"] = "full_time"

    # Password attempts
    attempt_patterns = [
        r"(\d+)\s*(?:password\s*)?(?:failed\s*)?attempts?",
        r"after\s+(\d+)\s*(?:failed\s*)?attempts?",
        r"(\d+)\s*times"
    ]

    for pattern in attempt_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                entities["password_attempts"] = int(match.group(1))
                break
            except ValueError:
                pass

    # Laptop/device age
    age_patterns = [
        r"(\d+(?:\.\d+)?)\s*years?\s*old",
        r"(\d+(?:\.\d+)?)\s*years?\s*of\s*(?:service|use)",
        r"about\s*(\d+(?:\.\d+)?)\s*years?"
    ]

    for pattern in age_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                entities["device_age_years"] = float(match.group(1))
                break
            except ValueError:
                pass

    # Remote work days
    remote_patterns = [
        r"(\d+)\s*days?\s*(?:a|per)\s*week",
        r"remote.*?(\d+)\s*days?",
        r"work.*?home.*?(\d+)\s*days?"
    ]

    for pattern in remote_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                entities["remote_days_per_week"] = int(match.group(1))
                break
            except ValueError:
                pass

    # Guest request
    if "guest" in text and ("wifi" in text or "wi-fi" in text):
        entities["guest_request"] = True

    # Non-catalog software
    if any(phrase in text for phrase in [
        "not in the catalog",
        "not in catalog",
        "non-catalog",
        "non catalog",
        "outside the catalog"
    ]):
        entities["catalog_status"] = "non_catalog"

    # Security risk
    if any(word in text for word in [
        "phishing",
        "phish",
        "malware",
        "unauthorized access",
        "suspicious email",
        "suspicious link"
    ]):
        entities["security_risk"] = True

    # Hardware failure
    if any(phrase in text for phrase in [
        "hardware failure",
        "hardware failed",
        "verified hardware failure",
        "completely dead",
        "won't turn on",
        "wont turn on"
    ]):
        entities["hardware_failure"] = True

    # Urgency
    if any(word in text for word in [
        "urgent",
        "urgently",
        "immediately",
        "asap",
        "critical"
    ]):
        entities["urgency"] = "high"
    else:
        entities["urgency"] = "normal"

    return entities


# ============================================================
# MISSING INFORMATION
# ============================================================

def check_missing_information(intent, entities, message):
    text = message.lower()

    # Completely vague request
    if intent == "unknown":
        return {
            "needs_information": True,
            "question": (
                "Could you tell me what is not working and which "
                "device, application, or service is affected?"
            )
        }

    # Laptop replacement
    if intent == "laptop_support":

        replacement_requested = any(word in text for word in [
            "replacement",
            "replace",
            "new laptop",
            "new computer"
        ])

        if replacement_requested:

            has_age = "device_age_years" in entities
            has_failure = entities.get("hardware_failure", False)

            if not has_age and not has_failure:
                return {
                    "needs_information": True,
                    "question": (
                        "How old is the laptop, and has a hardware "
                        "failure been verified?"
                    )
                }

    return {
        "needs_information": False,
        "question": None
    }


# ============================================================
# POLICY HELPERS
# ============================================================

def policy_contains(policy, phrases):
    content = policy.get("content", "").lower()

    return any(
        phrase.lower() in content
        for phrase in phrases
    )


def find_policy(policies, kb_id):
    for policy in policies:
        if policy.get("kb_id") == kb_id:
            return policy

    return None


def get_policy_ids(policies):
    """
    IMPORTANT:
    policies must remain a list of dictionaries.
    Do not pass format_search_results() here because
    that function returns display strings.
    """

    ids = []

    for policy in policies:
        if not isinstance(policy, dict):
            continue

        kb_id = policy.get("kb_id")

        if kb_id and kb_id not in ids:
            ids.append(kb_id)

    return ids


def format_policy_for_evidence(policy):
    if not isinstance(policy, dict):
        return str(policy)

    return {
        "kb_id": policy.get("kb_id"),
        "title": policy.get("title"),
        "category": policy.get("category"),
        "content": policy.get("content"),
        "distance": policy.get("distance")
    }


def format_policies_for_display(policies):
    formatted = []

    for policy in policies:
        if not isinstance(policy, dict):
            continue

        formatted.append(
            {
                "kb_id": policy.get("kb_id"),
                "title": policy.get("title"),
                "category": policy.get("category"),
                "content": policy.get("content"),
                "distance": policy.get("distance")
            }
        )

    return formatted


# ============================================================
# POLICY DECISION ENGINE
# ============================================================

def apply_policy(
    intent,
    category,
    entities,
    message,
    policies,
    historical_tickets
):

    policy_ids = get_policy_ids(policies)

    # --------------------------------------------------------
    # GUEST WI-FI
    # --------------------------------------------------------

    if intent == "guest_wifi":

        policy = find_policy(policies, "KB-07")

        if policy:
            return {
                "decision": "Direct Resolution",
                "action": (
                    "Use the front-desk kiosk to generate guest "
                    "Wi-Fi credentials. The credentials are valid "
                    "for 24 hours."
                ),
                "requires_ticket": False,
                "assigned_team": None,
                "priority": "NORMAL",
                "recommendation": (
                    "Direct the employee to the front-desk kiosk "
                    "to generate guest Wi-Fi credentials."
                ),
                "reason": (
                    "KB-07 states that any employee can generate "
                    "guest Wi-Fi credentials at the front-desk "
                    "kiosk and no IT ticket is required."
                )
            }

    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    if intent == "password_reset":

        attempts = entities.get("password_attempts")

        if attempts is not None and attempts > 5:

            return {
                "decision": "Escalate to IT",
                "action": (
                    "The employee needs IT assistance to manually "
                    "unlock the account."
                ),
                "requires_ticket": True,
                "assigned_team": "IT",
                "priority": "HIGH",
                "recommendation": (
                    "Escalate to IT for manual account unlock."
                ),
                "reason": (
                    "KB-01 states that employees can reset their "
                    "own password, but after 5 failed attempts "
                    "IT must manually unlock the account."
                )
            }

        return {
            "decision": "Direct Resolution",
            "action": (
                "Use the employee self-service password reset portal."
            ),
            "requires_ticket": False,
            "assigned_team": None,
            "priority": "NORMAL",
            "recommendation": (
                "Direct the employee to the self-service password "
                "reset portal."
            ),
            "reason": (
                "KB-01 allows employees to reset their own password "
                "through the self-service portal."
            )
        }

    # --------------------------------------------------------
    # SECURITY INCIDENT
    # --------------------------------------------------------

    if intent == "security_incident":

        return {
            "decision": "Escalate to Security",
            "action": (
                "Report the suspected security incident immediately "
                "to security@veridian-corp.example and do not forward "
                "the suspicious message to other employees."
            ),
            "requires_ticket": True,
            "assigned_team": "Security",
            "priority": "HIGH",
            "recommendation": (
                "Escalate the suspected security incident to Security "
                "immediately."
            ),
            "reason": (
                "KB-09 requires suspected phishing, malware, or "
                "unauthorized access to be reported immediately."
            )
        }

    # --------------------------------------------------------
    # VPN
    # --------------------------------------------------------

    if intent == "vpn_access":

        if entities.get("employee_type") == "contractor":

            return {
                "decision": "Escalate for Approval",
                "action": (
                    "Contractor VPN access requires manager approval "
                    "through the access request form."
                ),
                "requires_ticket": True,
                "assigned_team": "IT",
                "priority": "NORMAL",
                "recommendation": (
                    "Route the VPN access request through the required "
                    "manager approval process."
                ),
                "reason": (
                    "KB-02 states that contractors require manager "
                    "approval through the access request form."
                )
            }

        return {
            "decision": "Direct Resolution",
            "action": (
                "Full-time employees receive VPN access automatically. "
                "VPN credentials expire every 90 days and must be "
                "renewed by the employee."
            ),
            "requires_ticket": False,
            "assigned_team": None,
            "priority": "NORMAL",
            "recommendation": (
                "Check whether the employee's VPN credentials have "
                "expired and renew them if required."
            ),
            "reason": (
                "KB-02 specifies automatic VPN access for full-time "
                "employees and 90-day credential renewal."
            )
        }

    # --------------------------------------------------------
    # SOFTWARE INSTALLATION
    # --------------------------------------------------------

    if intent == "software_installation":

        if entities.get("catalog_status") == "non_catalog":

            return {
                "decision": "Escalate to IT Security",
                "action": (
                    "The software or browser extension requires "
                    "IT Security review before installation."
                ),
                "requires_ticket": True,
                "assigned_team": "IT Security",
                "priority": "NORMAL",
                "recommendation": (
                    "Submit the non-catalog software request for "
                    "IT Security review."
                ),
                "reason": (
                    "KB-04 states that non-catalog software requires "
                    "IT Security review and indicates a 3–5 business "
                    "day review period."
                )
            }

        return {
            "decision": "Direct Resolution",
            "action": (
                "Standard software in the approved catalog can be "
                "self-installed."
            ),
            "requires_ticket": False,
            "assigned_team": None,
            "priority": "NORMAL",
            "recommendation": (
                "Use the approved software catalog for "
                "self-installation."
            ),
            "reason": (
                "KB-04 allows standard software in the approved "
                "catalog to be self-installed."
            )
        }

    # --------------------------------------------------------
    # PRINTER
    # --------------------------------------------------------

    if intent == "printer_issue":

        return {
            "decision": "Troubleshooting Required",
            "action": (
                "First check the print queue and restart the print "
                "spooler. If the problem persists, log a ticket with "
                "the printer asset tag."
            ),
            "requires_ticket": True,
            "assigned_team": "IT",
            "priority": "NORMAL",
            "recommendation": (
                "Perform the KB-05 troubleshooting steps. If the "
                "problem persists, create an IT ticket containing "
                "the printer asset tag."
            ),
            "reason": (
                "KB-05 specifies checking the queue and restarting "
                "the print spooler before logging a ticket."
            )
        }

    # --------------------------------------------------------
    # MAILBOX
    # --------------------------------------------------------

    if intent == "mailbox_quota":

        return {
            "decision": "Policy Guidance",
            "action": (
                "The default mailbox quota is 25GB. Archive old mail "
                "when nearing the quota. Increases beyond 25GB require "
                "manager approval and are capped at 50GB."
            ),
            "requires_ticket": True,
            "assigned_team": "IT",
            "priority": "NORMAL",
            "recommendation": (
                "Have the employee archive old mail first. If a quota "
                "increase is needed, follow the manager approval "
                "requirement."
            ),
            "reason": (
                "KB-06 defines the 25GB default quota and approval "
                "requirement for increases."
            )
        }

    # --------------------------------------------------------
    # EXPENSE SOFTWARE
    # --------------------------------------------------------

    if intent == "expense_access":

        return {
            "decision": "Escalate to Finance",
            "action": (
                "Expense software access is granted by Finance, "
                "not IT. IT can assist with login or technical issues "
                "once an account exists."
            ),
            "requires_ticket": True,
            "assigned_team": "Finance",
            "priority": "NORMAL",
            "recommendation": (
                "Route access provisioning to Finance. If the account "
                "already exists and the problem is technical, IT can "
                "assist with the login issue."
            ),
            "reason": (
                "KB-08 assigns expense software access to Finance."
            )
        }

    # --------------------------------------------------------
    # HOME OFFICE
    # --------------------------------------------------------

    if intent == "home_office_equipment":

        remote_days = entities.get("remote_days_per_week")

        if remote_days is not None and remote_days > 3:

            return {
                "decision": "Approval Required",
                "action": (
                    "The employee is eligible for the one-time home "
                    "office equipment allowance, subject to manager "
                    "sign-off and Finance processing."
                ),
                "requires_ticket": True,
                "assigned_team": "Finance",
                "priority": "NORMAL",
                "recommendation": (
                    "Proceed with manager sign-off and Finance "
                    "processing. IT handles equipment shipping only "
                    "after approval."
                ),
                "reason": (
                    "KB-10 states that employees working remotely "
                    "more than 3 days per week are eligible, with "
                    "manager sign-off and Finance processing required."
                )
            }

        return {
            "decision": "Needs Information",
            "action": (
                "The supplied policy requires confirmation that the "
                "employee works remotely more than 3 days per week."
            ),
            "requires_ticket": False,
            "assigned_team": None,
            "priority": "NORMAL",
            "recommendation": (
                "Ask how many days per week the employee works remotely."
            ),
            "reason": (
                "KB-10 eligibility depends on working remotely more "
                "than 3 days per week."
            )
        }

    # --------------------------------------------------------
    # LAPTOP / HARDWARE
    # --------------------------------------------------------

    if intent == "laptop_support":

        text = message.lower()

        replacement_requested = any(word in text for word in [
            "replacement",
            "replace",
            "new laptop",
            "new computer"
        ])

        age = entities.get("device_age_years")
        hardware_failure = entities.get(
            "hardware_failure",
            False
        )

        if replacement_requested:

            # Laptop replacement policy
            kb03 = find_policy(policies, "KB-03")

            # Asset management policy
            asset01 = find_policy(policies, "ASSET-01")

            # Verified hardware failure can qualify for early replacement
            if hardware_failure:

                return {
                    "decision": "Escalate for Replacement Review",
                    "action": (
                        "The supplied policy allows replacement earlier "
                        "than 3 years when a hardware failure is verified. "
                        "The Asset Management Policy also applies to "
                        "company hardware and requires Finance sign-off "
                        "plus IT approval for early replacement outside "
                        "the 4-year refresh cycle."
                    ),
                    "requires_ticket": True,
                    "assigned_team": "IT",
                    "priority": "NORMAL",
                    "recommendation": (
                        "Create a ticket for laptop replacement review "
                        "and include the verified hardware failure. "
                        "Because Asset Management is also relevant, the "
                        "early-replacement approval requirements must be "
                        "reviewed."
                    ),
                    "reason": (
                        "KB-03 permits earlier replacement for verified "
                        "hardware failure. ASSET-01 separately states that "
                        "early replacement outside the 4-year refresh "
                        "cycle requires Finance sign-off in addition "
                        "to IT approval."
                    )
                }

            # Age >= 3 years
            if age is not None and age >= 3:

                return {
                    "decision": "Escalate for Replacement Review",
                    "action": (
                        "The laptop meets the 3-year service threshold "
                        "in KB-03. The supplied Asset Management Policy "
                        "also states that company hardware follows a "
                        "4-year refresh cycle, so the applicable "
                        "replacement/approval requirements should be "
                        "reviewed."
                    ),
                    "requires_ticket": True,
                    "assigned_team": "IT",
                    "priority": "NORMAL",
                    "recommendation": (
                        "Create a replacement-review ticket. Include "
                        "the laptop age and retrieve both KB-03 and "
                        "ASSET-01 as supporting policy sources."
                    ),
                    "reason": (
                        "KB-03 states that laptops are eligible for "
                        "replacement after 3 years. ASSET-01 separately "
                        "defines the 4-year refresh cycle and early "
                        "replacement approval requirements."
                    )
                }

            # Under 3 years and no verified failure
            if age is not None and age < 3:

                return {
                    "decision": "Needs Human Review",
                    "action": (
                        "The laptop is under 3 years old and no verified "
                        "hardware failure was provided. The supplied "
                        "policy does not establish automatic replacement "
                        "eligibility in this situation."
                    ),
                    "requires_ticket": True,
                    "assigned_team": "IT",
                    "priority": "NORMAL",
                    "recommendation": (
                        "Escalate to IT for assessment rather than "
                        "claiming that replacement is approved."
                    ),
                    "reason": (
                        "KB-03 specifies replacement after 3 years or "
                        "earlier with verified hardware failure."
                    )
                }

        # General laptop problem, not replacement
        return {
            "decision": "Needs Human Review",
            "action": (
                "The supplied policies do not provide enough information "
                "to resolve this hardware issue automatically."
            ),
            "requires_ticket": True,
            "assigned_team": "IT",
            "priority": "NORMAL",
            "recommendation": (
                "Create an IT support ticket for hardware investigation."
            ),
            "reason": (
                "The supplied knowledge base does not define a complete "
                "self-service resolution for this hardware problem."
            )
        }

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return {
        "decision": "Escalate for Clarification",
        "action": (
            "The request is too vague to determine the affected "
            "service or applicable policy."
        ),
        "requires_ticket": True,
        "assigned_team": "IT",
        "priority": "NORMAL",
        "recommendation": (
            "Request clarification about the affected device, "
            "application, or service."
        ),
        "reason": (
            "The employee request does not contain enough information "
            "to identify an applicable policy."
        )
    }


# ============================================================
# REQUEST DATABASE
# ============================================================

def save_request(
    db,
    message,
    employee_name,
    employee_email,
    intent,
    category,
    urgency,
    state
):

    request_id = generate_request_id(db)

    request = Request(
        request_id=request_id,
        employee_name=employee_name,
        employee_email=employee_email,
        message=message,
        intent=intent,
        category=category,
        urgency=urgency,
        state=state,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


# ============================================================
# EVIDENCE BUILDER
# ============================================================

def build_evidence(
    policies,
    historical_tickets,
    entities
):

    return {
        "knowledge_base": [
            format_policy_for_evidence(policy)
            for policy in policies
            if isinstance(policy, dict)
        ],
        "historical_tickets": historical_tickets,
        "extracted_entities": entities
    }


# ============================================================
# MAIN AGENT
# ============================================================

def process_request(
    message,
    employee_name="Test Employee",
    employee_email="test@veridian-corp.example"
):

    db = SessionLocal()

    try:

        # ====================================================
        # 1. UNDERSTANDING
        # ====================================================

        understanding = detect_intent(message)

        intent = understanding[0]
        category = understanding[1]

        entities = extract_entities(message)
        urgency = entities.get("urgency", "normal")

        # ====================================================
        # 2. CREATE REQUEST
        # ====================================================

        request = save_request(
            db=db,
            message=message,
            employee_name=employee_name,
            employee_email=employee_email,
            intent=intent,
            category=category,
            urgency=urgency,
            state="UNDERSTANDING"
        )

        request_id = request.request_id

        # ====================================================
        # AUDIT: REQUEST RECEIVED
        # ====================================================

        record_audit(
            db=db,
            request_id=request_id,
            action="request received",
            actor="AI Agent",
            previous_state=None,
            new_state="NEW",
            reason="Employee request received."
        )

        # ====================================================
        # AUDIT: INTENT
        # ====================================================

        record_audit(
            db=db,
            request_id=request_id,
            action="intent detected",
            actor="AI Agent",
            previous_state="NEW",
            new_state="UNDERSTANDING",
            reason=(
                f"Detected intent={intent}, "
                f"category={category}, "
                f"urgency={urgency}."
            )
        )

        # ====================================================
        # 3. RETRIEVE POLICY
        # ====================================================

        policy_results = search_knowledge(
            message,
            top_k=5
        )

        # IMPORTANT:
        # Keep policy_results as dictionaries.
        # Do NOT call format_search_results() here.
        policies = policy_results

        policy_ids = get_policy_ids(policies)

        record_audit(
            db=db,
            request_id=request_id,
            action="policy retrieved",
            actor="AI Agent",
            previous_state="UNDERSTANDING",
            new_state="UNDERSTANDING",
            policy_used=", ".join(policy_ids),
            reason=(
                f"Retrieved {len(policies)} relevant "
                f"knowledge-base source(s)."
            )
        )

        # ====================================================
        # 4. SEARCH TICKET HISTORY
        # ====================================================

        historical_tickets = search_ticket_history(
            message,
            top_k=3
        )

        record_audit(
            db=db,
            request_id=request_id,
            action="ticket history searched",
            actor="AI Agent",
            previous_state="UNDERSTANDING",
            new_state="UNDERSTANDING",
            policy_used=", ".join(policy_ids),
            reason=(
                f"Retrieved {len(historical_tickets)} "
                f"historical ticket(s) for context."
            )
        )

        # ====================================================
        # 5. CHECK MISSING INFORMATION
        # ====================================================

        missing = check_missing_information(
            intent,
            entities,
            message
        )

        if missing["needs_information"]:

            previous_state = request.state

            request.state = "NEEDS_INFORMATION"
            request.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(request)

            record_audit(
                db=db,
                request_id=request_id,
                action="follow-up required",
                actor="AI Agent",
                previous_state=previous_state,
                new_state="NEEDS_INFORMATION",
                policy_used=", ".join(policy_ids),
                reason=missing["question"]
            )

            evidence = build_evidence(
                policies,
                historical_tickets,
                entities
            )

            return {
                "request_id": request_id,
                "state": "NEEDS_INFORMATION",
                "intent": intent,
                "category": category,
                "urgency": urgency,
                "entities": entities,
                "message": message,
                "follow_up_question": missing["question"],
                "decision": "Needs Information",
                "action": "Waiting for employee clarification.",
                "escalation": False,
                "ticket": None,
                "policy_ids": policy_ids,
                "policies": format_policies_for_display(policies),
                "historical_tickets": historical_tickets,
                "evidence": evidence
            }

        # ====================================================
        # 6. APPLY POLICY
        # ====================================================

        decision = apply_policy(
            intent=intent,
            category=category,
            entities=entities,
            message=message,
            policies=policies,
            historical_tickets=historical_tickets
        )

        # ====================================================
        # 7. DECISION AUDIT
        # ====================================================

        record_audit(
            db=db,
            request_id=request_id,
            action="policy decision made",
            actor="AI Agent",
            previous_state="UNDERSTANDING",
            new_state="UNDERSTANDING",
            policy_used=", ".join(policy_ids),
            reason=decision.get(
                "reason",
                "Policy-based decision generated."
            )
        )

        # ====================================================
        # 8. DIRECT RESOLUTION
        # ====================================================

        if not decision.get("requires_ticket", False):

            previous_state = request.state

            request.state = "RESOLVED"
            request.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(request)

            record_audit(
                db=db,
                request_id=request_id,
                action="request resolved",
                actor="AI Agent",
                previous_state=previous_state,
                new_state="RESOLVED",
                policy_used=", ".join(policy_ids),
                reason=decision.get(
                    "reason",
                    "Request resolved using supplied policy."
                )
            )

            evidence = build_evidence(
                policies,
                historical_tickets,
                entities
            )

            return {
                "request_id": request_id,
                "state": "RESOLVED",
                "intent": intent,
                "category": category,
                "urgency": urgency,
                "entities": entities,
                "message": message,
                "follow_up_question": None,
                "decision": decision.get("decision"),
                "action": decision.get("action"),
                "escalation": False,
                "ticket": None,
                "policy_ids": policy_ids,
                "policies": format_policies_for_display(policies),
                "historical_tickets": historical_tickets,
                "evidence": evidence
            }

        # ====================================================
        # 9. ESCALATION REQUIRED
        # ====================================================

        previous_state = request.state

        request.state = "ESCALATION_REQUIRED"
        request.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(request)

        record_audit(
            db=db,
            request_id=request_id,
            action="escalation required",
            actor="AI Agent",
            previous_state=previous_state,
            new_state="ESCALATION_REQUIRED",
            policy_used=", ".join(policy_ids),
            reason=decision.get(
                "reason",
                "Human intervention required."
            )
        )

        # ====================================================
        # 10. BUILD TICKET
        # ====================================================

        evidence = build_evidence(
            policies,
            historical_tickets,
            entities
        )

        issue_summary = message[:200]

        description = (
            f"Employee request: {message}\n\n"
            f"Detected intent: {intent}\n"
            f"Category: {category}\n"
            f"Urgency: {urgency}\n"
            f"Extracted entities: {json.dumps(entities)}\n\n"
            f"AI decision: {decision.get('decision')}\n"
            f"AI action/recommendation: "
            f"{decision.get('recommendation')}\n\n"
            f"Reason: {decision.get('reason')}"
        )

        ticket = create_ticket(
            db=db,
            request_id=request_id,
            employee_name=employee_name,
            employee_email=employee_email,
            issue_summary=issue_summary,
            category=category,
            description=description,
            priority=decision.get(
                "priority",
                "NORMAL"
            ),
            assigned_team=decision.get(
                "assigned_team",
                "IT"
            ),
            ai_recommendation=decision.get(
                "recommendation",
                ""
            ),
            policy_id=", ".join(policy_ids),
            evidence=json.dumps(
                evidence,
                indent=2,
                default=str
            )
        )

        # ====================================================
        # 11. TICKET CREATED
        # ====================================================

        record_audit(
            db=db,
            request_id=request_id,
            ticket_id=ticket.ticket_id,
            action="ticket created",
            actor="AI Agent",
            previous_state="ESCALATION_REQUIRED",
            new_state="TICKET_CREATED",
            policy_used=", ".join(policy_ids),
            reason=(
                f"Created ticket {ticket.ticket_id} "
                f"for human review."
            )
        )

        # ====================================================
        # 12. WAITING FOR HUMAN
        # ====================================================

        previous_state = request.state

        request.state = "WAITING_FOR_HUMAN"
        request.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(request)

        record_audit(
            db=db,
            request_id=request_id,
            ticket_id=ticket.ticket_id,
            action="waiting for human",
            actor="AI Agent",
            previous_state=previous_state,
            new_state="WAITING_FOR_HUMAN",
            policy_used=", ".join(policy_ids),
            reason=(
                "Ticket created and assigned for human review."
            )
        )

        # ====================================================
        # 13. RETURN COMPLETE RESPONSE
        # ====================================================

        return {
            "request_id": request_id,
            "state": "WAITING_FOR_HUMAN",
            "intent": intent,
            "category": category,
            "urgency": urgency,
            "entities": entities,
            "message": message,
            "follow_up_question": None,
            "decision": decision.get("decision"),
            "action": decision.get("action"),
            "escalation": True,
            "ticket": {
                "ticket_id": ticket.ticket_id,
                "request_id": ticket.request_id,
                "employee_name": ticket.employee_name,
                "employee_email": ticket.employee_email,
                "issue_summary": ticket.issue_summary,
                "category": ticket.category,
                "description": ticket.description,
                "priority": ticket.priority,
                "assigned_team": ticket.assigned_team,
                "status": ticket.status,
                "ai_recommendation": ticket.ai_recommendation,
                "policy_id": ticket.policy_id,
                "evidence": ticket.evidence,
                "created_at": ticket.created_at,
                "updated_at": ticket.updated_at
            },
            "policy_ids": policy_ids,
            "policies": format_policies_for_display(policies),
            "historical_tickets": historical_tickets,
            "evidence": evidence
        }

    except Exception as e:

        db.rollback()

        raise e

    finally:

        db.close()