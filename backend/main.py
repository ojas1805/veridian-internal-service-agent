from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import engine, SessionLocal, Base
from models import Request, Ticket, AuditLog
from agent import process_request
from audit_engine import record_audit


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Veridian Internal Service Agent",
    description="Policy-grounded internal IT support agent",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class AgentRequest(BaseModel):
    message: str
    employee_name: str = "Test Employee"
    employee_email: str = "test@veridian-corp.example"


# ============================================================
# TICKET STATUS SCHEMA
# ============================================================

class TicketStatusUpdate(BaseModel):
    status: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "Veridian Internal Service Agent",
        "status": "running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# PROCESS AGENT REQUEST
# ============================================================

@app.post("/agent/request")
def create_agent_request(
    request_data: AgentRequest
):

    try:

        result = process_request(
            message=request_data.message,
            employee_name=request_data.employee_name,
            employee_email=request_data.employee_email
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Agent processing failed.",
                "error": str(e)
            }
        )


# ============================================================
# GET ALL REQUESTS
# ============================================================

@app.get("/requests")
def get_requests():

    db = SessionLocal()

    try:

        requests = (
            db.query(Request)
            .order_by(Request.id.desc())
            .all()
        )

        return [
            {
                "request_id": request.request_id,
                "employee_name": request.employee_name,
                "employee_email": request.employee_email,
                "message": request.message,
                "intent": request.intent,
                "category": request.category,
                "urgency": request.urgency,
                "state": request.state,
                "created_at": request.created_at,
                "updated_at": request.updated_at
            }
            for request in requests
        ]

    finally:

        db.close()


# ============================================================
# GET SINGLE REQUEST
# ============================================================

@app.get("/requests/{request_id}")
def get_request(
    request_id: str
):

    db = SessionLocal()

    try:

        request = (
            db.query(Request)
            .filter(
                Request.request_id == request_id
            )
            .first()
        )

        if request is None:

            raise HTTPException(
                status_code=404,
                detail="Request not found."
            )

        return {
            "request_id": request.request_id,
            "employee_name": request.employee_name,
            "employee_email": request.employee_email,
            "message": request.message,
            "intent": request.intent,
            "category": request.category,
            "urgency": request.urgency,
            "state": request.state,
            "created_at": request.created_at,
            "updated_at": request.updated_at
        }

    finally:

        db.close()


# ============================================================
# GET ALL TICKETS
# ============================================================

@app.get("/tickets")
def get_tickets():

    db = SessionLocal()

    try:

        tickets = (
            db.query(Ticket)
            .order_by(Ticket.id.desc())
            .all()
        )

        return [
            {
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
            }
            for ticket in tickets
        ]

    finally:

        db.close()


# ============================================================
# GET SINGLE TICKET
# ============================================================

@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: str
):

    db = SessionLocal()

    try:

        ticket = (
            db.query(Ticket)
            .filter(
                Ticket.ticket_id == ticket_id
            )
            .first()
        )

        if ticket is None:

            raise HTTPException(
                status_code=404,
                detail="Ticket not found."
            )

        return {
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
        }

    finally:

        db.close()


# ============================================================
# UPDATE TICKET STATUS
# ============================================================

@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: str,
    status_data: TicketStatusUpdate
):

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # FIND TICKET
        # ----------------------------------------------------

        ticket = (
            db.query(Ticket)
            .filter(
                Ticket.ticket_id == ticket_id
            )
            .first()
        )

        if ticket is None:

            raise HTTPException(
                status_code=404,
                detail="Ticket not found."
            )

        # ----------------------------------------------------
        # NORMALIZE STATUS
        # ----------------------------------------------------

        new_status = str(
            status_data.status
        ).strip().upper()

        allowed_statuses = [
            "WAITING_FOR_HUMAN",
            "IN_PROGRESS",
            "RESOLVED",
            "CLOSED"
        ]

        # ----------------------------------------------------
        # VALIDATE STATUS
        # ----------------------------------------------------

        if new_status not in allowed_statuses:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid ticket status.",
                    "received_status": new_status,
                    "allowed_statuses": allowed_statuses
                }
            )

        # ----------------------------------------------------
        # SAVE PREVIOUS STATUS
        # ----------------------------------------------------

        previous_status = ticket.status

        # ----------------------------------------------------
        # UPDATE TICKET
        # ----------------------------------------------------

        ticket.status = new_status
        ticket.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(ticket)

        # ----------------------------------------------------
        # SYNCHRONIZE REQUEST STATE
        # ----------------------------------------------------

        related_request = (
            db.query(Request)
            .filter(
                Request.request_id == ticket.request_id
            )
            .first()
        )

        previous_request_state = None
        new_request_state = None

        if related_request is not None:

            previous_request_state = (
                related_request.state
            )

            if new_status == "WAITING_FOR_HUMAN":
                new_request_state = "WAITING_FOR_HUMAN"

            elif new_status == "IN_PROGRESS":
                new_request_state = "WAITING_FOR_HUMAN"

            elif new_status == "RESOLVED":
                new_request_state = "RESOLVED"

            elif new_status == "CLOSED":
                new_request_state = "CLOSED"

            if new_request_state is not None:

                related_request.state = new_request_state
                related_request.updated_at = datetime.utcnow()

                db.commit()

        # ----------------------------------------------------
        # AUDIT TICKET CHANGE
        # ----------------------------------------------------

        record_audit(
            db=db,
            request_id=ticket.request_id,
            ticket_id=ticket.ticket_id,
            action="ticket status updated",
            actor="Human Reviewer",
            reason=(
                f"Human reviewer changed ticket status "
                f"from {previous_status} to {new_status}."
            ),
            previous_state=previous_status,
            new_state=new_status,
            policy_used=ticket.policy_id
        )

        # ----------------------------------------------------
        # AUDIT REQUEST STATE CHANGE
        # ----------------------------------------------------

        if (
            related_request is not None
            and previous_request_state != new_request_state
        ):

            record_audit(
                db=db,
                request_id=ticket.request_id,
                ticket_id=ticket.ticket_id,
                action="request state synchronized",
                actor="System",
                reason=(
                    "Request state synchronized with the "
                    "human-updated ticket status."
                ),
                previous_state=previous_request_state,
                new_state=new_request_state,
                policy_used=ticket.policy_id
            )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "message": "Ticket status updated",
            "ticket_id": ticket.ticket_id,
            "request_id": ticket.request_id,
            "previous_status": previous_status,
            "status": ticket.status,
            "request_state": (
                related_request.state
                if related_request is not None
                else None
            )
        }

    finally:

        db.close()


# ============================================================
# AUDIT LOG
# ============================================================

@app.get("/audit")
def get_audit_logs():

    db = SessionLocal()

    try:

        logs = (
            db.query(AuditLog)
            .order_by(AuditLog.id.desc())
            .all()
        )

        return [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "request_id": log.request_id,
                "ticket_id": log.ticket_id,
                "action": log.action,
                "actor": log.actor,
                "previous_state": log.previous_state,
                "new_state": log.new_state,
                "policy_used": log.policy_used,
                "reason": log.reason
            }
            for log in logs
        ]

    finally:

        db.close()


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    db = SessionLocal()

    try:

        total_requests = (
            db.query(Request).count()
        )

        resolved_requests = (
            db.query(Request)
            .filter(
                Request.state == "RESOLVED"
            )
            .count()
        )

        waiting_for_human = (
            db.query(Request)
            .filter(
                Request.state == "WAITING_FOR_HUMAN"
            )
            .count()
        )

        total_tickets = (
            db.query(Ticket).count()
        )

        open_tickets = (
            db.query(Ticket)
            .filter(
                Ticket.status.in_([
                    "WAITING_FOR_HUMAN",
                    "IN_PROGRESS"
                ])
            )
            .count()
        )

        total_audit_events = (
            db.query(AuditLog).count()
        )

        return {
            "total_requests": total_requests,
            "resolved_requests": resolved_requests,
            "waiting_for_human": waiting_for_human,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "total_audit_events": total_audit_events
        }

    finally:

        db.close()


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    print(
        "Veridian Internal Service Agent API started."
    )