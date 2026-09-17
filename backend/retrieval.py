import json
import os

import chromadb
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "veridian_knowledge"
KNOWLEDGE_FILE = "data/knowledge_base.json"


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded.")


# ============================================================
# CHROMA DATABASE
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():

    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# INDEX KNOWLEDGE BASE
# ============================================================

def index_knowledge_base():

    knowledge_base = load_knowledge_base()

    existing = collection.count()

    if existing > 0:
        return

    documents = []
    ids = []
    metadatas = []

    for policy in knowledge_base:

        kb_id = policy.get("kb_id")

        title = policy.get(
            "title",
            ""
        )

        category = policy.get(
            "category",
            ""
        )

        content = policy.get(
            "content",
            ""
        )

        document = (
            f"Policy ID: {kb_id}\n"
            f"Title: {title}\n"
            f"Category: {category}\n"
            f"Content: {content}"
        )

        documents.append(document)
        ids.append(kb_id)

        metadatas.append({
            "kb_id": kb_id,
            "title": title,
            "category": category
        })

    embeddings = model.encode(
        documents
    ).tolist()

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )


# Make sure the KB is indexed
index_knowledge_base()


# ============================================================
# KNOWLEDGE SEARCH
# ============================================================

def search_knowledge(
    query,
    top_k=3
):

    query_embedding = model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=[
            "metadatas",
            "documents",
            "distances"
        ]
    )

    policies = []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i in range(len(ids)):

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        document = (
            documents[i]
            if i < len(documents)
            else ""
        )

        distance = (
            distances[i]
            if i < len(distances)
            else None
        )

        policies.append({
            "kb_id": metadata.get(
                "kb_id",
                ids[i]
            ),
            "title": metadata.get(
                "title",
                ""
            ),
            "category": metadata.get(
                "category",
                ""
            ),
            "content": document,
            "distance": distance
        })

    return policies


# ============================================================
# FORMAT POLICY RESULTS
# ============================================================

def format_search_results(results):

    if not results:
        return "No relevant policy sources were retrieved."

    formatted = []

    for result in results:

        formatted.append(
            f"KB ID: {result.get('kb_id')}\n"
            f"Title: {result.get('title')}\n"
            f"Category: {result.get('category')}\n"
            f"Content: {result.get('content')}\n"
            f"Relevance distance: {result.get('distance')}"
        )

    return "\n\n".join(formatted)


# ============================================================
# LOAD HISTORICAL TICKETS
# ============================================================

def load_tickets():

    ticket_file = "data/tickets.json"

    if not os.path.exists(ticket_file):
        return []

    with open(
        ticket_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# SEARCH HISTORICAL TICKETS
# ============================================================

def search_ticket_history(
    query,
    top_k=3
):

    tickets = load_tickets()

    if not tickets:
        return []

    ticket_texts = []

    for ticket in tickets:

        text = " ".join([
            str(ticket.get("issue_summary", "")),
            str(ticket.get("category", "")),
            str(ticket.get("employee", "")),
            str(ticket.get("status", "")),
            str(ticket.get("policy_id", ""))
        ])

        ticket_texts.append(text)

    ticket_embeddings = model.encode(
        ticket_texts
    )

    query_embedding = model.encode(
        [query]
    )

    similarities = cosine_similarity(
        query_embedding,
        ticket_embeddings
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        ticket = tickets[index]

        results.append({
            "ticket_id": ticket.get(
                "ticket_id"
            ),
            "employee": ticket.get(
                "employee"
            ),
            "issue_summary": ticket.get(
                "issue_summary"
            ),
            "category": ticket.get(
                "category"
            ),
            "status": ticket.get(
                "status"
            ),
            "policy_id": ticket.get(
                "policy_id"
            ),
            "similarity": float(
                similarities[index]
            )
        })

    return results


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("\nKnowledge search test:\n")

    results = search_knowledge(
        "My VPN credentials expired.",
        top_k=3
    )

    for result in results:
        print(result)

    print("\nFormatted results:\n")

    print(
        format_search_results(results)
    )

    print("\nHistorical ticket search:\n")

    tickets = search_ticket_history(
        "My VPN credentials expired.",
        top_k=3
    )

    for ticket in tickets:
        print(ticket)