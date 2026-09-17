from datetime import datetime

from models import AuditLog


def record_audit(
    db,
    request_id,
    action,
    actor,
    reason,
    ticket_id=None,
    previous_state=None,
    new_state=None,
    policy_used=None
):

    audit = AuditLog(
        timestamp=datetime.utcnow(),

        request_id=request_id,

        ticket_id=ticket_id,

        action=action,

        actor=actor,

        previous_state=previous_state,

        new_state=new_state,

        policy_used=policy_used,

        reason=reason
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit