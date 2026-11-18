from app.services.semantic_search_service import search_knowledge


def search_company_knowledge(query: str) -> list[str]:
    """
    Search the company's knowledge base for relevant information.
    """
    results = search_knowledge(query)
    return results