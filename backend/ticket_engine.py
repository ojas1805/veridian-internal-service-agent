from datetime import datetime

from models import Ticket


def generate_ticket_id(db):

    latest_ticket = (
        db.query(Ticket)
        .order_by(Ticket.id.desc())
        .first()
    )

    if latest_ticket is None:
        return "TK-1052"

    number = int(
        latest_ticket.ticket_id.split("-")[1]
    )

    return f"TK-{number + 1}"


def create_ticket(
    db,
    request_id,
    employee_name,
    employee_email,
    issue_summary,
    category,
    description,
    priority,
    assigned_team,
    ai_recommendation,
    policy_id,
    evidence
):

    ticket_id = generate_ticket_id(db)

    ticket = Ticket(

        ticket_id=ticket_id,

        request_id=request_id,

        employee_name=employee_name,

        employee_email=employee_email,

        issue_summary=issue_summary,

        category=category,

        description=description,

        priority=priority,

        assigned_team=assigned_team,

        status="WAITING_FOR_HUMAN",

        ai_recommendation=ai_recommendation,

        policy_id=policy_id,

        evidence=evidence,

        created_at=datetime.utcnow(),

        updated_at=datetime.utcnow()
    )

    db.add(ticket)

    db.commit()

    db.refresh(ticket)

    return ticket