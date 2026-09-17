from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from database import Base


# ============================================================
# REQUEST
# ============================================================

class Request(Base):

    __tablename__ = "requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    request_id = Column(
        String,
        unique=True,
        index=True
    )

    employee_name = Column(
        String
    )

    employee_email = Column(
        String
    )

    message = Column(
        Text
    )

    intent = Column(
        String,
        nullable=True
    )

    category = Column(
        String,
        nullable=True
    )

    urgency = Column(
        String,
        nullable=True
    )

    state = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ============================================================
# TICKET
# ============================================================

class Ticket(Base):

    __tablename__ = "tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_id = Column(
        String,
        unique=True,
        index=True
    )

    request_id = Column(
        String
    )

    employee_name = Column(
        String
    )

    employee_email = Column(
        String
    )

    issue_summary = Column(
        Text
    )

    category = Column(
        String
    )

    description = Column(
        Text
    )

    priority = Column(
        String,
        nullable=True
    )

    assigned_team = Column(
        String
    )

    status = Column(
        String
    )

    ai_recommendation = Column(
        Text
    )

    policy_id = Column(
        String
    )

    evidence = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    request_id = Column(
        String,
        nullable=True
    )

    ticket_id = Column(
        String,
        nullable=True
    )

    action = Column(
        String
    )

    actor = Column(
        String
    )

    previous_state = Column(
        String,
        nullable=True
    )

    new_state = Column(
        String,
        nullable=True
    )

    policy_used = Column(
        String,
        nullable=True
    )

    reason = Column(
        Text
    )