import { useEffect, useMemo, useState } from "react";

import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ClipboardList,
  Clock3,
  FileText,
  HelpCircle,
  Laptop,
  Loader2,
  RefreshCw,
  Search,
  Send,
  Shield,
  Ticket,
  User,
  Users,
  Wifi,
  X,
  Zap,
} from "lucide-react";

import "./App.css";


const API_BASE = "http://127.0.0.1:8000";


/* ============================================================
   EMPLOYEES
============================================================ */

const EMPLOYEES = [
  {
    name: "Aditi Sharma",
    email: "aditi.sharma@veridian-corp.example",
    message:
      "My laptop won't turn on, completely dead, and it's about 3.5 years old.",
  },
  {
    name: "Vikram Chawla",
    email: "vikram.chawla@veridian-corp.example",
    message: "I need guest Wi-Fi tomorrow.",
  },
  {
    name: "Karan Mehta",
    email: "karan.mehta@veridian-corp.example",
    message: "I am locked out after 6 password attempts.",
  },
  {
    name: "Ritu Bhatia",
    email: "ritu.bhatia@veridian-corp.example",
    message:
      "I need approval to install a data-analysis tool that is not in the catalog.",
  },
  {
    name: "Sanjay Oberoi",
    email: "sanjay.oberoi@veridian-corp.example",
    message:
      "My VPN stopped working because my credentials expired.",
  },
  {
    name: "Meera Iyer",
    email: "meera.iyer@veridian-corp.example",
    message:
      "The printer on the 3rd floor shows a paper jam even though there is no jam.",
  },
  {
    name: "Farhan Ali",
    email: "farhan.ali@veridian-corp.example",
    message:
      "I work from home 4 days a week. How do I get a monitor?",
  },
  {
    name: "Ananya Reddy",
    email: "ananya.reddy@veridian-corp.example",
    message:
      "I received a suspected phishing email asking for my login details and forwarded it to teammates.",
  },
  {
    name: "Rohit Desai",
    email: "rohit.desai@veridian-corp.example",
    message:
      "My mailbox is full and I can't send emails.",
  },
  {
    name: "Kavya Pillai",
    email: "kavya.pillai@veridian-corp.example",
    message:
      "I need urgent admin access to the finance reporting server.",
  },
  {
    name: "Nikhil Bansal",
    email: "nikhil.bansal@veridian-corp.example",
    message:
      "We have a new contractor next week who needs VPN access.",
  },
  {
    name: "Sneha Kulkarni",
    email: "sneha.kulkarni@veridian-corp.example",
    message:
      "I cannot log into the expense tool because of invalid credentials.",
  },
  {
    name: "Aman Gupta",
    email: "aman.gupta@veridian-corp.example",
    message:
      "My laptop screen flickers. It is 2 years old and I might need a fix, not a replacement.",
  },
  {
    name: "Tanya Chopra",
    email: "tanya.chopra@veridian-corp.example",
    message:
      "I need approval to install a browser extension for productivity tracking.",
  },
  {
    name: "Rahul Menon",
    email: "rahul.menon@veridian-corp.example",
    message:
      "hey can you help, its not working",
  },
];


const EXAMPLES = [
  {
    title: "Laptop issue",
    icon: Laptop,
    text:
      "My laptop won't turn on, completely dead, and it's about 3.5 years old.",
  },
  {
    title: "Guest Wi-Fi",
    icon: Wifi,
    text: "I need guest Wi-Fi tomorrow.",
  },
  {
    title: "Password lockout",
    icon: Shield,
    text: "I am locked out after 6 password attempts.",
  },
  {
    title: "Phishing",
    icon: AlertTriangle,
    text:
      "I received a suspected phishing email asking for my login details.",
  },
  {
    title: "VPN",
    icon: Activity,
    text:
      "My VPN stopped working because my credentials expired.",
  },
  {
    title: "Software",
    icon: FileText,
    text:
      "I need approval to install software that is not in the catalog.",
  },
];


/* ============================================================
   HELPERS
============================================================ */

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}


function label(value) {
  if (!value) return "";

  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}


function formatDate(value) {
  if (!value) return "—";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return String(value);
  }
}


function getDecision(result) {
  if (
    result?.decision &&
    typeof result.decision === "object"
  ) {
    return result.decision;
  }

  return {
    decision:
      typeof result?.decision === "string"
        ? result.decision
        : "Further information may be required.",

    action:
      typeof result?.action === "string"
        ? result.action
        : "",

    requires_escalation:
      Boolean(result?.requires_escalation),

    requires_ticket:
      Boolean(result?.requires_ticket),
  };
}


function getPolicyId(policy) {
  return (
    policy?.kb_id ||
    policy?.policy_id ||
    policy?.id ||
    "POLICY"
  );
}


function getPolicyTitle(policy) {
  return (
    policy?.title ||
    policy?.name ||
    "Relevant Policy"
  );
}


function getPolicyContent(policy) {
  return (
    policy?.content ||
    policy?.description ||
    policy?.text ||
    "Policy information was retrieved."
  );
}


/* ============================================================
   STATUS BADGE
============================================================ */

function StatusBadge({ status }) {
  if (!status) {
    return (
      <span className="status neutral">
        Unknown
      </span>
    );
  }

  const value = String(status).toUpperCase();

  let type = "neutral";

  if (
    value.includes("RESOLVED") ||
    value.includes("CLOSED")
  ) {
    type = "success";
  } else if (
    value.includes("WAITING") ||
    value.includes("PENDING") ||
    value.includes("PROGRESS") ||
    value.includes("INVESTIGATING")
  ) {
    type = "warning";
  } else if (
    value.includes("ESCALAT") ||
    value.includes("REJECTED")
  ) {
    type = "danger";
  }

  return (
    <span className={`status ${type}`}>
      {status}
    </span>
  );
}


/* ============================================================
   ERROR PANEL
============================================================ */

function ErrorPanel({ error, onRetry }) {
  return (
    <div className="error-panel">

      <div className="error-icon">
        <AlertCircle size={20} />
      </div>

      <div className="error-content">

        <strong>
          The request could not be processed
        </strong>

        <p>
          The agent returned an error instead of
          a usable result. No unsupported action
          is being claimed as completed.
        </p>

        {error && (
          <details>
            <summary>
              Technical details
            </summary>

            <code>
              {error}
            </code>
          </details>
        )}

        <button
          type="button"
          className="secondary-button small"
          onClick={onRetry}
        >
          <RefreshCw size={15} />
          Try again
        </button>

      </div>

    </div>
  );
}


/* ============================================================
   AGENT RESULT
============================================================ */

function AgentResult({
  result,
  evidenceOpen,
  setEvidenceOpen,
}) {

  const policies = safeArray(
    result?.policies
  );

  const history = safeArray(
    result?.historical_tickets
  );

  const entities =
    result?.entities &&
    typeof result.entities === "object"
      ? result.entities
      : {};

  const understanding =
    result?.understanding &&
    typeof result.understanding === "object"
      ? result.understanding
      : {};

  const decision = getDecision(result);

  const ticket =
    result?.ticket &&
    typeof result.ticket === "object"
      ? result.ticket
      : null;

  const state =
    result?.state ||
    "UNDERSTANDING";

  const decisionText =
    String(
      decision?.decision || ""
    ).toLowerCase();

  const escalated =
    Boolean(decision?.requires_escalation) ||
    String(state)
      .toUpperCase()
      .includes("WAITING") ||
    decisionText.includes("escalat");

  const resolved =
    String(state).toUpperCase() === "RESOLVED" ||
    decisionText.includes("resolve");


  return (
    <div className="agent-result">

      <div className="result-heading">

        <div>
          <span className="eyebrow">
            AGENT RESPONSE
          </span>

          <h2>
            Request analysis
          </h2>

          <p>
            The agent analyzed the request using
            Veridian policy and available ticket
            context.
          </p>
        </div>


        <div
          className={
            resolved
              ? "result-status success"
              : escalated
              ? "result-status danger"
              : "result-status warning"
          }
        >
          {resolved ? (
            <CheckCircle2 size={16} />
          ) : escalated ? (
            <AlertTriangle size={16} />
          ) : (
            <HelpCircle size={16} />
          )}

          {resolved
            ? "Resolved"
            : escalated
            ? "Human review required"
            : "Needs information"}
        </div>

      </div>


      {/* LIFECYCLE */}

      <div className="lifecycle-card">

        <span className="card-label">
          REQUEST LIFECYCLE
        </span>

        <div className="lifecycle">

          {[
            "NEW",
            "UNDERSTANDING",
            state,
          ]
            .filter(
              (item, index, array) =>
                array.indexOf(item) === index
            )
            .map((item, index, array) => (
              <div
                className="lifecycle-item"
                key={`${item}-${index}`}
              >

                <div className="lifecycle-dot">
                  {index === array.length - 1 ? (
                    <Check size={12} />
                  ) : (
                    index + 1
                  )}
                </div>

                <span>
                  {label(item)}
                </span>

                {index < array.length - 1 && (
                  <ArrowRight size={13} />
                )}

              </div>
            ))}

        </div>

      </div>


      {/* RESULT CARDS */}

      <div className="result-grid">

        {/* ISSUE */}

        <div className="result-card full">

          <CardTitle
            icon={<ClipboardList size={17} />}
            title="Issue"
            subtitle="Original employee request"
          />

          <div className="issue-box">
            {result?.issue ||
              result?.message ||
              "No issue supplied."}
          </div>

        </div>


        {/* UNDERSTANDING */}

        <div className="result-card">

          <CardTitle
            icon={<Zap size={17} />}
            title="Agent Understanding"
            subtitle="What the agent detected"
          />

          <div className="field-list">

            <InfoRow
              label="Intent"
              value={
                understanding.intent ||
                result?.intent ||
                "Unknown"
              }
            />

            <InfoRow
              label="Category"
              value={
                understanding.category ||
                result?.category ||
                "Unknown"
              }
            />

            <InfoRow
              label="State"
              value={label(state)}
            />

          </div>


          {Object.keys(entities).length > 0 && (
            <div className="entity-section">

              <span className="mini-label">
                DETECTED DETAILS
              </span>

              {Object.entries(entities).map(
                ([key, value]) => (
                  <InfoRow
                    key={key}
                    label={label(key)}
                    value={String(value)}
                  />
                )
              )}

            </div>
          )}

        </div>


        {/* DECISION */}

        <div className="result-card">

          <CardTitle
            icon={<CheckCircle2 size={17} />}
            title="Decision"
            subtitle="Policy-driven outcome"
          />

          <div className="decision-text">
            {decision?.decision ||
              "Further information is required."}
          </div>


          {decision?.action && (
            <div className="action-box">

              <span>
                NEXT ACTION
              </span>

              <p>
                {decision.action}
              </p>

            </div>
          )}


          {decision?.requires_escalation && (
            <div className="escalation-box">

              <AlertTriangle size={17} />

              <div>

                <strong>
                  Human review required
                </strong>

                <span>
                  This request should be handled
                  through the reviewer workflow.
                </span>

              </div>

            </div>
          )}

        </div>


        {/* POLICY */}

        <div className="result-card full">

          <CardTitle
            icon={<Shield size={17} />}
            title="Relevant Policy"
            subtitle="Retrieved from the Veridian knowledge base"
          />

          {policies.length === 0 ? (
            <div className="no-data">
              <AlertCircle size={16} />

              No relevant policy was returned.
            </div>
          ) : (
            <div className="policy-list">

              {policies.map(
                (policy, index) => (
                  <div
                    className="policy-item"
                    key={`${getPolicyId(
                      policy
                    )}-${index}`}
                  >

                    <span className="policy-id">
                      {getPolicyId(policy)}
                    </span>

                    <div>

                      <strong>
                        {getPolicyTitle(policy)}
                      </strong>

                      <p>
                        {getPolicyContent(policy)}
                      </p>

                    </div>

                  </div>
                )
              )}

            </div>
          )}

        </div>


        {/* HISTORY */}

        <div className="result-card full">

          <CardTitle
            icon={<Clock3 size={17} />}
            title="Ticket History"
            subtitle="Relevant previous cases"
          />

          {history.length === 0 ? (
            <div className="no-data">
              <Clock3 size={16} />

              No relevant historical ticket
              was retrieved.
            </div>
          ) : (
            <div className="history-list">

              {history.map(
                (item, index) => (
                  <div
                    className="history-item"
                    key={
                      item?.ticket_id ||
                      `history-${index}`
                    }
                  >

                    <div>

                      <strong>
                        {item?.ticket_id ||
                          "Historical ticket"}
                      </strong>

                      <span>
                        {item?.issue_summary ||
                          item?.summary ||
                          item?.description ||
                          "Previous case"}
                      </span>

                    </div>

                    <StatusBadge
                      status={
                        item?.status ||
                        "Historical"
                      }
                    />

                  </div>
                )
              )}

            </div>
          )}

        </div>

      </div>


      {/* TICKET */}

      {ticket && (
        <div className="created-ticket">

          <div className="created-ticket-icon">
            <Ticket size={20} />
          </div>

          <div>

            <span>
              HUMAN REVIEW TICKET CREATED
            </span>

            <strong>
              {ticket.ticket_id}
            </strong>

          </div>

          <StatusBadge
            status={
              ticket.status ||
              "WAITING_FOR_HUMAN"
            }
          />

        </div>
      )}


      {/* EVIDENCE */}

      <div className="evidence-card">

        <button
          type="button"
          className="evidence-header"
          onClick={() =>
            setEvidenceOpen(
              !evidenceOpen
            )
          }
        >

          <div className="evidence-title">

            <Shield size={17} />

            <div>

              <strong>
                Sources & Evidence
              </strong>

              <span>
                Only sources actually returned
                by retrieval are shown.
              </span>

            </div>

          </div>

          {evidenceOpen ? (
            <ChevronUp size={18} />
          ) : (
            <ChevronDown size={18} />
          )}

        </button>


        {evidenceOpen && (
          <div className="evidence-body">

            {policies.map(
              (policy, index) => (
                <div
                  className="evidence-item"
                  key={`${getPolicyId(
                    policy
                  )}-${index}`}
                >

                  <span>
                    {getPolicyId(policy)}
                  </span>

                  <div>

                    <strong>
                      {getPolicyTitle(policy)}
                    </strong>

                    <p>
                      {getPolicyContent(policy)}
                    </p>

                  </div>

                </div>
              )
            )}


            {history.map(
              (item, index) => (
                <div
                  className="evidence-item"
                  key={
                    item?.ticket_id ||
                    `ticket-${index}`
                  }
                >

                  <span>
                    {item?.ticket_id ||
                      "TICKET"}
                  </span>

                  <div>

                    <strong>
                      Historical ticket
                    </strong>

                    <p>
                      {item?.issue_summary ||
                        item?.description ||
                        "Historical context"}
                    </p>

                  </div>

                </div>
              )
            )}


            {policies.length === 0 &&
              history.length === 0 && (
                <div className="no-data">
                  No evidence was retrieved.
                </div>
              )}

          </div>
        )}

      </div>

    </div>
  );
}


/* ============================================================
   CARD TITLE
============================================================ */

function CardTitle({
  icon,
  title,
  subtitle,
}) {
  return (
    <div className="card-title">

      <div className="card-title-icon">
        {icon}
      </div>

      <div>

        <h3>
          {title}
        </h3>

        <span>
          {subtitle}
        </span>

      </div>

    </div>
  );
}


/* ============================================================
   INFO ROW
============================================================ */

function InfoRow({
  label: rowLabel,
  value,
}) {
  return (
    <div className="info-row">

      <span>
        {rowLabel}
      </span>

      <strong>
        {value || "—"}
      </strong>

    </div>
  );
}


/* ============================================================
   MAIN APP
============================================================ */

export default function App() {

  const [employee, setEmployee] =
    useState(EMPLOYEES[0]);

  const [message, setMessage] =
    useState(EMPLOYEES[0].message);

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [evidenceOpen, setEvidenceOpen] =
    useState(true);


  const [summary, setSummary] =
    useState(null);

  const [tickets, setTickets] =
    useState([]);

  const [requests, setRequests] =
    useState([]);

  const [auditLogs, setAuditLogs] =
    useState([]);

  const [demoRequests, setDemoRequests] =
    useState([]);

  const [demoTickets, setDemoTickets] =
    useState([]);


  const [selectedTicket, setSelectedTicket] =
    useState(null);

  const [ticketSearch, setTicketSearch] =
    useState("");

  const [activeSection, setActiveSection] =
    useState("employee");

  const [refreshing, setRefreshing] =
    useState(false);


  /* ==========================================================
     LOAD DASHBOARD
  ========================================================== */

  async function loadDashboardData() {

    const endpoints = [
      {
        key: "summary",
        url: `${API_BASE}/dashboard/summary`,
      },
      {
        key: "tickets",
        url: `${API_BASE}/tickets`,
      },
      {
        key: "requests",
        url: `${API_BASE}/requests`,
      },
      {
        key: "audit",
        url: `${API_BASE}/audit`,
      },
      {
        key: "demoRequests",
        url: `${API_BASE}/demo/requests`,
      },
      {
        key: "demoTickets",
        url: `${API_BASE}/demo/tickets`,
      },
    ];


    const results =
      await Promise.allSettled(
        endpoints.map(
          async (endpoint) => {

            const response =
              await fetch(
                endpoint.url
              );

            if (!response.ok) {
              throw new Error(
                `${endpoint.key}: HTTP ${response.status}`
              );
            }

            return {
              key: endpoint.key,
              data:
                await response.json(),
            };
          }
        )
      );


    results.forEach((item) => {

      if (
        item.status !== "fulfilled"
      ) {
        return;
      }

      const {
        key,
        data,
      } = item.value;


      if (key === "summary") {
        setSummary(data);
      }

      if (key === "tickets") {
        setTickets(
          Array.isArray(data)
            ? data
            : []
        );
      }

      if (key === "requests") {
        setRequests(
          Array.isArray(data)
            ? data
            : []
        );
      }

      if (key === "audit") {
        setAuditLogs(
          Array.isArray(data)
            ? data
            : []
        );
      }

      if (key === "demoRequests") {
        setDemoRequests(
          Array.isArray(data)
            ? data
            : []
        );
      }

      if (key === "demoTickets") {
        setDemoTickets(
          Array.isArray(data)
            ? data
            : []
        );
      }

    });
  }


  useEffect(() => {
    loadDashboardData();
  }, []);


  /* ==========================================================
     EMPLOYEE
  ========================================================== */

  function handleEmployeeChange(event) {

    const selected =
      EMPLOYEES.find(
        (item) =>
          item.name ===
          event.target.value
      );

    if (!selected) {
      return;
    }

    setEmployee(selected);
    setMessage(selected.message);
    setResult(null);
    setError("");
  }


  /* ==========================================================
     EXAMPLE
  ========================================================== */

  function selectExample(example) {

    setMessage(example.text);
    setResult(null);
    setError("");

    navigateTo("employee");
  }


  /* ==========================================================
     SUBMIT
  ========================================================== */

  async function handleSubmit(event) {

    if (event) {
      event.preventDefault();
    }

    const text =
      message.trim();


    if (!text) {

      setError(
        "Please describe your IT issue before submitting."
      );

      return;
    }


    setLoading(true);
    setError("");
    setResult(null);


    try {

      const response =
        await fetch(
          `${API_BASE}/agent/request`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              message: text,
              employee_name:
                employee.name,
              employee_email:
                employee.email,
            }),
          }
        );


      let data = null;

      try {
        data =
          await response.json();
      } catch {
        data = null;
      }


      if (!response.ok) {

        let messageText =
          "The agent could not process this request.";

        if (
          typeof data?.detail ===
          "string"
        ) {
          messageText =
            data.detail;
        } else if (
          data?.detail?.message
        ) {
          messageText =
            data.detail.message;
        } else if (
          data?.message
        ) {
          messageText =
            data.message;
        }

        throw new Error(
          messageText
        );
      }


      if (!data) {
        throw new Error(
          "The agent returned an empty response."
        );
      }


      /*
        Normalize the response so that
        unexpected/missing fields cannot
        crash the React interface.
      */

      const safeResult = {
        ...data,

        issue:
          data.issue ||
          data.message ||
          text,

        state:
          data.state ||
          "UNDERSTANDING",

        policies:
          safeArray(data.policies),

        historical_tickets:
          safeArray(
            data.historical_tickets
          ),

        entities:
          data.entities &&
          typeof data.entities ===
            "object"
            ? data.entities
            : {},

        decision:
          data.decision ||
          {
            decision:
              "Further information is required.",
            action:
              "Please provide more information about the issue.",
            requires_escalation:
              false,
            requires_ticket:
              false,
          },
      };


      setResult(
        safeResult
      );


      /*
        Dashboard refresh must NEVER
        remove a successful employee
        response.
      */

      try {
        await loadDashboardData();
      } catch (dashboardError) {
        console.warn(
          "Dashboard refresh failed:",
          dashboardError
        );
      }

    } catch (err) {

      console.error(
        "Agent request failed:",
        err
      );

      setError(
        err?.message ||
          "Something went wrong while processing the request."
      );

    } finally {

      setLoading(false);

    }
  }


  function retryRequest() {
    setError("");
    handleSubmit();
  }


  /* ==========================================================
     TICKET UPDATE
  ========================================================== */

  async function updateTicketStatus(
    ticketId,
    status
  ) {

    try {

      const response =
        await fetch(
          `${API_BASE}/tickets/${ticketId}/status`,
          {
            method: "PATCH",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              status,
            }),
          }
        );


      let data = null;

      try {
        data =
          await response.json();
      } catch {
        data = null;
      }


      if (!response.ok) {
        throw new Error(
          data?.detail?.message ||
            data?.detail ||
            "Unable to update ticket."
        );
      }


      await loadDashboardData();


      setSelectedTicket(
        (current) => {

          if (
            !current ||
            current.ticket_id !==
              ticketId
          ) {
            return current;
          }

          return {
            ...current,
            status,
          };
        }
      );

    } catch (err) {

      console.error(
        "Ticket update failed:",
        err
      );

      window.alert(
        err?.message ||
          "Unable to update ticket."
      );
    }
  }


  /* ==========================================================
     TICKET FILTER
  ========================================================== */

  const filteredTickets =
    useMemo(() => {

      const query =
        ticketSearch
          .trim()
          .toLowerCase();


      if (!query) {
        return tickets;
      }


      return tickets.filter(
        (ticket) => {

          const values = [
            ticket?.ticket_id,
            ticket?.request_id,
            ticket?.employee_name,
            ticket?.issue_summary,
            ticket?.category,
            ticket?.assigned_team,
          ];


          return values.some(
            (value) =>
              String(
                value || ""
              )
                .toLowerCase()
                .includes(query)
          );
        }
      );

    }, [
      tickets,
      ticketSearch,
    ]);


  /* ==========================================================
     NAVIGATION
  ========================================================== */

  function navigateTo(section) {

    setActiveSection(section);


    const map = {
      employee:
        "employee-agent",
      dashboard:
        "reviewer-dashboard",
      tickets:
        "ticket-queue",
      requests:
        "requests-section",
      audit:
        "audit-panel",
    };


    const targetId =
      map[section];


    if (!targetId) {
      return;
    }


    setTimeout(() => {

      const element =
        document.getElementById(
          targetId
        );


      if (!element) {
        console.warn(
          "Navigation target not found:",
          targetId
        );

        return;
      }


      element.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

    }, 50);
  }


  /* ==========================================================
     METRICS
  ========================================================== */

  const liveRequests =
    summary?.total_requests ??
    requests.length;

  const resolved =
    summary?.resolved_requests ??
    requests.filter(
      (item) =>
        item?.state ===
        "RESOLVED"
    ).length;

  const waiting =
    summary?.waiting_for_human ??
    requests.filter(
      (item) =>
        item?.state ===
        "WAITING_FOR_HUMAN"
    ).length;

  const liveTickets =
    summary?.total_tickets ??
    tickets.length;

  const openTickets =
    summary?.open_tickets ??
    tickets.filter(
      (item) =>
        item?.status ===
          "WAITING_FOR_HUMAN" ||
        item?.status ===
          "IN_PROGRESS"
    ).length;

  const auditCount =
    summary?.total_audit_events ??
    auditLogs.length;


  /* ==========================================================
     RENDER
  ========================================================== */

  return (
    <div className="app">

      {/* ======================================================
         SIDEBAR
      ====================================================== */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-logo">
            V
          </div>

          <div>
            <strong>
              Veridian
            </strong>

            <span>
              Internal Service Agent
            </span>
          </div>

        </div>


        <div className="workspace-label">
          WORKSPACE
        </div>


        <nav className="sidebar-nav">

          <SidebarButton
            active={
              activeSection ===
              "employee"
            }
            icon={
              <Send size={17} />
            }
            text="Employee Agent"
            onClick={() =>
              navigateTo(
                "employee"
              )
            }
          />


          <SidebarButton
            active={
              activeSection ===
              "dashboard"
            }
            icon={
              <Activity size={17} />
            }
            text="Reviewer Dashboard"
            onClick={() =>
              navigateTo(
                "dashboard"
              )
            }
          />


          <SidebarButton
            active={
              activeSection ===
              "tickets"
            }
            icon={
              <Ticket size={17} />
            }
            text="Ticket Queue"
            badge={
              openTickets > 0
                ? openTickets
                : null
            }
            onClick={() =>
              navigateTo(
                "tickets"
              )
            }
          />


          <SidebarButton
            active={
              activeSection ===
              "requests"
            }
            icon={
              <ClipboardList
                size={17}
              />
            }
            text="Requests"
            onClick={() =>
              navigateTo(
                "requests"
              )
            }
          />


          <SidebarButton
            active={
              activeSection ===
              "audit"
            }
            icon={
              <Shield size={17} />
            }
            text="Audit Trail"
            onClick={() =>
              navigateTo(
                "audit"
              )
            }
          />

        </nav>


        <div className="sidebar-bottom">

          <div className="system-status">

            <span className="online-dot"></span>

            <div>

              <strong>
                System operational
              </strong>

              <span>
                Agent API connected
              </span>

            </div>

          </div>

          <small>
            Veridian Agent v1.0
          </small>

        </div>

      </aside>


      {/* ======================================================
         MAIN
      ====================================================== */}

      <main className="main">

        {/* TOP BAR */}

        <header className="topbar">

          <div className="breadcrumbs">

            <button
              type="button"
              onClick={() =>
                navigateTo(
                  "employee"
                )
              }
            >
              Internal IT Support
            </button>

            <span>
              /
            </span>

            <button
              type="button"
              className="current"
              onClick={() =>
                navigateTo(
                  "employee"
                )
              }
            >
              Employee Agent
            </button>

          </div>


          <div className="topbar-actions">

            <div className="connection">

              <span className="online-dot"></span>

              Connected

            </div>

            <button
              type="button"
              className="refresh-button"
              onClick={
                async () => {
                  setRefreshing(true);

                  try {
                    await loadDashboardData();
                  } finally {
                    setRefreshing(false);
                  }
                }
              }
              title="Refresh dashboard"
            >
              <RefreshCw
                size={16}
                className={
                  refreshing
                    ? "spin"
                    : ""
                }
              />
            </button>

          </div>

        </header>


        {/* ====================================================
           EMPLOYEE AGENT
        ==================================================== */}

        <section
          id="employee-agent"
          className="section"
        >

          <div className="hero">

            <div>

              <span className="eyebrow">
                VERIDIAN CORP
              </span>

              <h1>
                How can we help?
              </h1>

              <p>
                Describe your IT issue in your
                own words. The agent will understand
                the request, retrieve relevant policy,
                check available context and determine
                the appropriate next step.
              </p>

            </div>


            <div className="ai-badge">

              <div className="ai-badge-icon">
                <Zap size={17} />
              </div>

              <div>

                <strong>
                  Policy-grounded AI
                </strong>

                <span>
                  Human review when required
                </span>

              </div>

            </div>

          </div>


          {/* REQUEST FORM */}

          <div className="request-panel">

            <div className="employee-header">

              <div>

                <span className="field-label">
                  EMPLOYEE
                </span>

                <div className="employee-select">

                  <User size={17} />

                  <select
                    value={
                      employee.name
                    }
                    onChange={
                      handleEmployeeChange
                    }
                  >

                    {EMPLOYEES.map(
                      (item) => (
                        <option
                          key={
                            item.email
                          }
                          value={
                            item.name
                          }
                        >
                          {item.name}
                        </option>
                      )
                    )}

                  </select>

                </div>

              </div>


              <span className="employee-email">
                {employee.email}
              </span>

            </div>


            <form
              className="request-form"
              onSubmit={
                handleSubmit
              }
            >

              <label
                htmlFor="issue"
                className="field-label"
              >
                DESCRIBE YOUR ISSUE
              </label>


              <div className="textarea-wrapper">

                <textarea
                  id="issue"
                  value={message}
                  onChange={(event) =>
                    setMessage(
                      event.target.value
                    )
                  }
                  disabled={loading}
                  rows={7}
                  placeholder="Example: My VPN stopped working and says my credentials have expired."
                />

                <div className="textarea-footer">

                  <span>
                    {message.length} characters
                  </span>

                  <span>
                    Natural-language requests supported
                  </span>

                </div>

              </div>


              {error && (
                <ErrorPanel
                  error={error}
                  onRetry={
                    retryRequest
                  }
                />
              )}


              <div className="form-actions">

                <div className="grounding-note">

                  <Shield size={14} />

                  <span>
                    Policy and ticket context
                    are used to ground the response.
                  </span>

                </div>


                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    loading ||
                    !message.trim()
                  }
                >

                  {loading ? (
                    <>
                      <Loader2
                        size={16}
                        className="spin"
                      />

                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Send size={16} />

                      Analyze Request
                    </>
                  )}

                </button>

              </div>

            </form>

          </div>


          {/* EXAMPLES */}

          <div className="examples">

            <div className="examples-heading">

              <strong>
                Try an example
              </strong>

              <span>
                Or type your own issue above
              </span>

            </div>


            <div className="example-grid">

              {EXAMPLES.map(
                (example) => {

                  const Icon =
                    example.icon;

                  return (
                    <button
                      type="button"
                      className="example-card"
                      key={
                        example.title
                      }
                      onClick={() =>
                        selectExample(
                          example
                        )
                      }
                    >

                      <div className="example-icon">
                        <Icon size={16} />
                      </div>

                      <div>

                        <strong>
                          {example.title}
                        </strong>

                        <span>
                          {example.text}
                        </span>

                      </div>

                    </button>
                  );
                }
              )}

            </div>

          </div>


          {/* RESULT */}

          {result && (
            <AgentResult
              result={result}
              evidenceOpen={
                evidenceOpen
              }
              setEvidenceOpen={
                setEvidenceOpen
              }
            />
          )}

        </section>


        {/* ====================================================
           REVIEWER DASHBOARD
        ==================================================== */}

        <section
          id="reviewer-dashboard"
          className="section section-border"
        >

          <SectionHeader
            eyebrow="REVIEWER"
            title="Reviewer Dashboard"
            description="Monitor live requests, human-review tickets, assignment records and audit activity."
            action={
              <button
                type="button"
                className="secondary-button"
                onClick={
                  async () => {
                    setRefreshing(true);

                    try {
                      await loadDashboardData();
                    } finally {
                      setRefreshing(false);
                    }
                  }
                }
              >
                <RefreshCw
                  size={15}
                  className={
                    refreshing
                      ? "spin"
                      : ""
                  }
                />

                Refresh
              </button>
            }
          />


          <div className="metrics">

            <Metric
              icon={
                <ClipboardList
                  size={18}
                />
              }
              label="Live Requests"
              value={liveRequests}
            />

            <Metric
              icon={
                <CheckCircle2
                  size={18}
                />
              }
              label="Resolved"
              value={resolved}
              type="success"
            />

            <Metric
              icon={
                <Users size={18} />
              }
              label="Waiting for Human"
              value={waiting}
              type="warning"
            />

            <Metric
              icon={
                <Ticket size={18} />
              }
              label="Live Tickets"
              value={liveTickets}
            />

            <Metric
              icon={
                <Clock3 size={18} />
              }
              label="Open Tickets"
              value={openTickets}
              type="warning"
            />

            <Metric
              icon={
                <Shield size={18} />
              }
              label="Audit Events"
              value={auditCount}
            />

          </div>


          <div className="assignment-summary">

            <div>
              <span>
                Assignment Requests
              </span>

              <strong>
                {demoRequests.length}
              </strong>
            </div>

            <div>
              <span>
                Assignment Tickets
              </span>

              <strong>
                {demoTickets.length}
              </strong>
            </div>

            <div>
              <span>
                Active Assignment Tickets
              </span>

              <strong>
                {
                  demoTickets.filter(
                    (item) =>
                      item?.active === true
                  ).length
                }
              </strong>
            </div>

            <div className="assignment-note">

              <FileText size={16} />

              <span>
                Assignment records are shown
                separately from live agent-created
                records.
              </span>

            </div>

          </div>

        </section>


        {/* ====================================================
           TICKET QUEUE
        ==================================================== */}

        <section
          id="ticket-queue"
          className="section section-border"
        >

          <SectionHeader
            eyebrow="HUMAN REVIEW"
            title="Ticket Queue"
            description="Escalated requests that require human handling."
          />


          <div className="queue-toolbar">

            <div className="search-box">

              <Search size={16} />

              <input
                value={
                  ticketSearch
                }
                onChange={(event) =>
                  setTicketSearch(
                    event.target.value
                  )
                }
                placeholder="Search ticket, employee, category..."
              />

              {ticketSearch && (
                <button
                  type="button"
                  onClick={() =>
                    setTicketSearch("")
                  }
                >
                  <X size={14} />
                </button>
              )}

            </div>


            <span className="queue-count">

              {
                filteredTickets.filter(
                  (ticket) =>
                    ticket.status !==
                      "RESOLVED" &&
                    ticket.status !==
                      "CLOSED"
                ).length
              }{" "}
              open

            </span>

          </div>


          <div className="ticket-layout">

            {/* LEFT: TICKETS */}

            <div className="ticket-list">

              {filteredTickets.length === 0 ? (
                <div className="empty-state">

                  <Ticket size={28} />

                  <strong>
                    No tickets found
                  </strong>

                  <span>
                    Escalated requests will
                    appear here.
                  </span>

                </div>
              ) : (
                filteredTickets.map(
                  (ticket) => (

                    <button
                      type="button"
                      key={
                        ticket.ticket_id
                      }
                      className={
                        selectedTicket?.ticket_id ===
                        ticket.ticket_id
                          ? "ticket-card selected"
                          : "ticket-card"
                      }
                      onClick={() => {

                        console.log(
                          "Opening ticket:",
                          ticket.ticket_id
                        );

                        setSelectedTicket(
                          ticket
                        );

                      }}
                    >

                      <div className="ticket-top">

                        <strong>
                          {ticket.ticket_id}
                        </strong>

                        <StatusBadge
                          status={
                            ticket.status
                          }
                        />

                      </div>


                      <div className="ticket-title">

                        {ticket.issue_summary ||
                          "Untitled ticket"}

                      </div>


                      <div className="ticket-meta">

                        <span>
                          {ticket.employee_name ||
                            "Unknown employee"}
                        </span>

                        <span>
                          {ticket.category ||
                            "Unknown category"}
                        </span>

                      </div>


                      <div className="review-link">

                        <span>
                          Review ticket
                        </span>

                        <ArrowRight
                          size={14}
                        />

                      </div>

                    </button>

                  )
                )
              )}

            </div>


            {/* RIGHT: DETAIL */}

            <TicketDetail
              ticket={
                selectedTicket
              }
              updateStatus={
                updateTicketStatus
              }
            />

          </div>


          {/* ASSIGNMENT TICKETS */}

          <div className="subsection">

            <SectionHeader
              eyebrow="ASSIGNMENT DATA"
              title="Existing Ticket Queue"
              description="Historical and active tickets supplied with the assignment."
            />


            <div className="assignment-ticket-grid">

              {demoTickets.map(
                (ticket) => (
                  <div
                    className="assignment-ticket"
                    key={
                      ticket.ticket_id
                    }
                  >

                    <div className="ticket-top">

                      <strong>
                        {ticket.ticket_id}
                      </strong>

                      <StatusBadge
                        status={
                          ticket.status
                        }
                      />

                    </div>

                    <div className="ticket-title">
                      {ticket.issue_summary}
                    </div>

                    <div className="ticket-meta">

                      <span>
                        {ticket.employee_name}
                      </span>

                      <span>
                        {ticket.active
                          ? "Active"
                          : "Historical"}
                      </span>

                    </div>

                  </div>
                )
              )}

            </div>

          </div>

        </section>


        {/* ====================================================
           REQUESTS
        ==================================================== */}

        <section
          id="requests-section"
          className="section section-border"
        >

          <SectionHeader
            eyebrow="REQUESTS"
            title="Employee Requests"
            description="Requests processed by the live agent."
          />


          <div className="table-card">

            <div className="table-scroll">

              <table>

                <thead>

                  <tr>
                    <th>
                      Request
                    </th>

                    <th>
                      Employee
                    </th>

                    <th>
                      Issue
                    </th>

                    <th>
                      Category
                    </th>

                    <th>
                      State
                    </th>

                    <th>
                      Created
                    </th>
                  </tr>

                </thead>


                <tbody>

                  {requests.length === 0 ? (
                    <tr>
                      <td
                        colSpan="6"
                        className="table-empty"
                      >
                        No live requests yet.
                      </td>
                    </tr>
                  ) : (
                    requests.map(
                      (request) => (
                        <tr
                          key={
                            request.request_id
                          }
                        >

                          <td>
                            <strong>
                              {
                                request.request_id
                              }
                            </strong>
                          </td>

                          <td>
                            {
                              request.employee_name ||
                              "—"
                            }
                          </td>

                          <td className="issue-cell">
                            {
                              request.message ||
                              "—"
                            }
                          </td>

                          <td>
                            {
                              request.category ||
                              "—"
                            }
                          </td>

                          <td>
                            <StatusBadge
                              status={
                                request.state
                              }
                            />
                          </td>

                          <td>
                            {
                              formatDate(
                                request.created_at
                              )
                            }
                          </td>

                        </tr>
                      )
                    )
                  )}

                </tbody>

              </table>

            </div>

          </div>


          {/* DEMO REQUESTS */}

          <div className="subsection">

            <SectionHeader
              eyebrow="ASSIGNMENT DATA"
              title="Demo Requests"
              description="Employee requests supplied with the assignment."
            />


            <div className="demo-grid">

              {demoRequests.map(
                (request) => (
                  <div
                    className="demo-card"
                    key={
                      request.request_id
                    }
                  >

                    <div className="demo-top">

                      <strong>
                        {request.request_id}
                      </strong>

                      <span>
                        {request.status}
                      </span>

                    </div>

                    <h4>
                      {request.employee_name}
                    </h4>

                    <p>
                      {request.message}
                    </p>

                  </div>
                )
              )}

            </div>

          </div>

        </section>


        {/* ====================================================
           AUDIT
        ==================================================== */}

        <section
          id="audit-panel"
          className="section section-border"
        >

          <SectionHeader
            eyebrow="GOVERNANCE"
            title="Audit Trail"
            description="Persistent record of AI-agent and human-reviewer actions."
          />


          <div className="audit-card">

            {auditLogs.length === 0 ? (
              <div className="empty-state">

                <Shield size={28} />

                <strong>
                  No audit events
                </strong>

                <span>
                  Agent actions will appear here.
                </span>

              </div>
            ) : (
              <div className="audit-list">

                {auditLogs.map(
                  (log) => (
                    <div
                      className="audit-item"
                      key={
                        log.id
                      }
                    >

                      <div className="audit-icon">
                        <Activity
                          size={15}
                        />
                      </div>


                      <div className="audit-content">

                        <div className="audit-heading">

                          <strong>
                            {log.action}
                          </strong>

                          <span>
                            {formatDate(
                              log.timestamp
                            )}
                          </span>

                        </div>


                        <div className="audit-tags">

                          {log.request_id && (
                            <span>
                              Request:{" "}
                              {
                                log.request_id
                              }
                            </span>
                          )}

                          {log.ticket_id && (
                            <span>
                              Ticket:{" "}
                              {
                                log.ticket_id
                              }
                            </span>
                          )}

                          {log.actor && (
                            <span>
                              Actor:{" "}
                              {
                                log.actor
                              }
                            </span>
                          )}

                          {log.policy_used && (
                            <span>
                              Policy:{" "}
                              {
                                log.policy_used
                              }
                            </span>
                          )}

                        </div>


                        {log.reason && (
                          <p>
                            {log.reason}
                          </p>
                        )}


                        {(log.previous_state ||
                          log.new_state) && (
                          <div className="transition">

                            <span>
                              {
                                log.previous_state ||
                                "—"
                              }
                            </span>

                            <ArrowRight
                              size={12}
                            />

                            <span>
                              {
                                log.new_state ||
                                "—"
                              }
                            </span>

                          </div>
                        )}

                      </div>

                    </div>
                  )
                )}

              </div>
            )}

          </div>

        </section>


        {/* FOOTER */}

        <footer className="footer">

          <div>

            <strong>
              Veridian Internal Service Agent
            </strong>

            <span>
              Policy-grounded internal IT support
            </span>

          </div>

          <span>
            Human-in-the-loop • Auditable
          </span>

        </footer>

      </main>

    </div>
  );
}


/* ============================================================
   SIDEBAR BUTTON
============================================================ */

function SidebarButton({
  active,
  icon,
  text,
  badge,
  onClick,
}) {
  return (
    <button
      type="button"
      className={
        active
          ? "sidebar-button active"
          : "sidebar-button"
      }
      onClick={onClick}
    >

      {icon}

      <span>
        {text}
      </span>

      {badge && (
        <small>
          {badge}
        </small>
      )}

    </button>
  );
}


/* ============================================================
   SECTION HEADER
============================================================ */

function SectionHeader({
  eyebrow,
  title,
  description,
  action,
}) {
  return (
    <div className="section-header">

      <div>

        <span className="eyebrow">
          {eyebrow}
        </span>

        <h2>
          {title}
        </h2>

        <p>
          {description}
        </p>

      </div>

      {action && (
        <div>
          {action}
        </div>
      )}

    </div>
  );
}


/* ============================================================
   METRIC
============================================================ */

function Metric({
  icon,
  label: metricLabel,
  value,
  type = "",
}) {
  return (
    <div className="metric">

      <div
        className={`metric-icon ${type}`}
      >
        {icon}
      </div>

      <div>

        <span>
          {metricLabel}
        </span>

        <strong>
          {value}
        </strong>

      </div>

    </div>
  );
}


/* ============================================================
   TICKET DETAIL
============================================================ */

function TicketDetail({
  ticket,
  updateStatus,
}) {

  if (!ticket) {
    return (
      <div className="ticket-detail empty">

        <div className="empty-ticket-icon">
          <Ticket size={28} />
        </div>

        <h3>
          Select a ticket
        </h3>

        <p>
          Click any ticket on the left.
          Its complete review information
          will appear here.
        </p>

      </div>
    );
  }


  return (
    <div className="ticket-detail">

      {/* HEADER */}

      <div className="ticket-detail-header">

        <div>

          <span className="eyebrow">
            HUMAN REVIEW
          </span>

          <h3>
            {ticket.ticket_id}
          </h3>

        </div>

        <StatusBadge
          status={ticket.status}
        />

      </div>


      {/* DETAILS */}

      <div className="detail-grid">

        <Detail
          label="Employee"
          value={
            ticket.employee_name
          }
        />

        <Detail
          label="Request ID"
          value={
            ticket.request_id
          }
        />

        <Detail
          label="Category"
          value={
            ticket.category
          }
        />

        <Detail
          label="Assigned Team"
          value={
            ticket.assigned_team ||
            "Human Review"
          }
        />

      </div>


      <DetailBlock
        label="Issue Summary"
        value={
          ticket.issue_summary ||
          "No issue summary available."
        }
      />


      <DetailBlock
        label="Description"
        value={
          ticket.description ||
          "No description available."
        }
      />


      <DetailBlock
        label="Priority"
        value={
          ticket.priority ||
          "Not specified by the source."
        }
      />


      {/* AI RECOMMENDATION */}

      <div className="recommendation">

        <div className="recommendation-title">

          <Zap size={16} />

          AI Recommendation

        </div>

        <p>
          {ticket.ai_recommendation ||
            "No AI recommendation recorded."}
        </p>

      </div>


      {/* POLICY */}

      <div className="ticket-policy">

        <Shield size={16} />

        <span>
          Relevant Policy
        </span>

        <strong>
          {ticket.policy_id ||
            "Not specified"}
        </strong>

      </div>


      {/* EVIDENCE */}

      <div className="ticket-evidence">

        <div className="ticket-evidence-title">

          <FileText size={15} />

          Evidence

        </div>

        <p>
          {ticket.evidence ||
            "No evidence recorded."}
        </p>

      </div>


      {/* REVIEW */}

      <div className="review-box">

        <div>

          <strong>
            Human review
          </strong>

          <span>
            Review the policy and evidence
            before changing the ticket state.
          </span>

        </div>


        <div className="review-buttons">

          <button
            type="button"
            onClick={() =>
              updateStatus(
                ticket.ticket_id,
                "IN_PROGRESS"
              )
            }
          >
            <Clock3 size={14} />
            In Progress
          </button>


          <button
            type="button"
            onClick={() =>
              updateStatus(
                ticket.ticket_id,
                "RESOLVED"
              )
            }
          >
            <Check size={14} />
            Resolve
          </button>


          <button
            type="button"
            onClick={() =>
              updateStatus(
                ticket.ticket_id,
                "CLOSED"
              )
            }
          >
            <CheckCircle2 size={14} />
            Close
          </button>

        </div>

      </div>

    </div>
  );
}


/* ============================================================
   DETAIL
============================================================ */

function Detail({
  label: detailLabel,
  value,
}) {
  return (
    <div className="detail">

      <span>
        {detailLabel}
      </span>

      <strong>
        {value || "—"}
      </strong>

    </div>
  );
}


/* ============================================================
   DETAIL BLOCK
============================================================ */

function DetailBlock({
  label: blockLabel,
  value,
}) {
  return (
    <div className="detail-block">

      <span>
        {blockLabel}
      </span>

      <p>
        {value}
      </p>

    </div>
  );
}