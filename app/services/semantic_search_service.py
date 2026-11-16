
from pathlib import Path
import ollama
import chromadb

def load_knowledge_documents() -> list[str]:
    base_dir = Path(__file__).resolve().parents[2]

    knowledge_file = (
        base_dir / "app" / "knowledge" / "company_knowledge.md"
    )

    with open(knowledge_file, "r", encoding="utf-8") as file:
        content = file.read()

    sections = content.split("\n## ")

    documents = [
        section.strip()
        for section in sections
        if section.strip() and not section.startswith("# Company Knowledge Base")
    ]

    return documents

def generate_embeddings(documents: list[str]) -> list[list[float]]:
    response = ollama.embed(
        model="nomic-embed-text",
        input=documents
    )

    return response.embeddings


def get_chroma_client():
    base_dir = Path(__file__).resolve().parents[2]

    database_path = base_dir / "chroma_db"

    client = chromadb.PersistentClient(
        path=str(database_path)
    )

    return client


def get_knowledge_collection():
    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name="company_knowledge"
    )

    return collection


def store_knowledge_documents():
    collection = get_knowledge_collection()

    documents = load_knowledge_documents()

    embeddings = generate_embeddings(documents)

    ids = [f"doc{i + 1}" for i in range(len(documents))]

    metadatas = []

    for document in documents:
        heading = document.split("\n", 1)[0]

        if heading == "Product: AI Chatbot":
            category = "product"
        elif heading == "Pricing":
            category = "pricing"
        elif heading == "Integrations":
            category = "technical"
        elif heading == "Healthcare Projects":
            category = "healthcare"
        else:
            category = "general"

        metadatas.append({"category": category})

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return collection


def search_knowledge(
    query: str,
    n_results: int = 3,
    distance_threshold: float = 0.8,
    category: str | None = None
) -> list[str]:

    collection = get_knowledge_collection()

    if collection.count() == 0:
        return []

    response = ollama.embed(
        model="nomic-embed-text",
        input=query
    )

    query_embedding = response.embeddings[0]

    query_arguments = {
    "query_embeddings": [query_embedding],
    "n_results": min(n_results, collection.count())
    }

    if category is not None:
        query_arguments["where"] = {
            "category": category
        }

    results = collection.query(**query_arguments)

    relevant_documents = []

    for document, distance in zip(
        results["documents"][0],
        results["distances"][0]
    ):
        if distance < distance_threshold:
            relevant_documents.append(document)

    return relevant_documents
