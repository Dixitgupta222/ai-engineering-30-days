from app.services.semantic_search_service import search_knowledge
from app.services.llm_service import generate_rag_answer
# def search_knowledge(keyword: str) -> bool:
#     with open("app/knowledge/company_knowledge.md", "r") as file:
#         content = file.read()

#     return keyword.lower() in content.lower()

def find_knowledge_section(keyword: str) -> str:
    with open("app/knowledge/company_knowledge.md", "r") as file:
        content = file.read()

    sections = content.split("\n## ")

    for section in sections:
        if keyword.lower() in section.lower():
            return section

    return "No matching section found"


def build_knowledge_prompt_with_context(
    customer_message: str,
    knowledge: str
) -> str:
    prompt = f"""
    You are a helpful company assistant.

    Use the company knowledge below to answer the customer.
    Do not make promises that the knowledge does not support.
    Never say or imply that you can contact, connect,
    forward requests to, or pass messages to company employees.
    You may recommend that customers contact the sales team,
    but do not offer to do it on their behalf.

    Your response must not offer to perform any action
    on behalf of the customer.

    Never end your response with a question asking
    whether you should contact, notify, forward, or
    connect the customer with anyone.

    If the customer needs a human representative,
    simply recommend that they contact the relevant team.

    Read all the company knowledge sections carefully.
    Your answer must address every relevant section.
    Do not ignore important conditions, warnings, or limitations.

    Do not treat a proposed service as confirmed feasibility.
    Clearly communicate any conditions that must be reviewed
    before confirming whether a project can be undertaken.

    If the customer mentions healthcare, hospitals, or
    medical projects, explicitly mention the required
    privacy, security, and regulatory review before
    confirming feasibility.

    Company knowledge:
    {knowledge}

    Customer message:
    {customer_message}
    """
    return prompt


def build_knowledge_prompt(customer_message: str) -> str:
    knowledge = find_knowledge_section(customer_message)

    return build_knowledge_prompt_with_context(
        customer_message,
        knowledge
    )


def identify_knowledge_category(customer_message: str) -> list[str]:
    message = customer_message.lower()
    categories = []

    if any(word in message for word in [
        "price", "pricing", "cost", "budget", "expensive"
    ]):
        categories.append("pricing")

    if any(word in message for word in [
        "chatbot", "virtual assistant", "build", "develop"
    ]):
        categories.append("product")

    if any(word in message for word in [
        "integration", "integrate", "salesforce", "software"
    ]):
        categories.append("technical")

    if any(word in message for word in [
        "healthcare", "medical", "hospital"
    ]):
        categories.append("healthcare")

    return categories


def answer_customer_with_knowledge(customer_message: str) -> str:
    categories = identify_knowledge_category(customer_message)

    knowledge = []

    if categories:
        for category in categories:
            category_knowledge = search_knowledge(
                customer_message,
                category=category,
                distance_threshold=1.2 if category in ["pricing", "healthcare"] else 0.8
            )
            knowledge.extend(category_knowledge)
    else:
        knowledge = search_knowledge(customer_message)

    if not knowledge:
        return "I don't have enough company information to answer that question."

    knowledge_context = "\n\n".join(knowledge)

    prompt = build_knowledge_prompt_with_context(
        customer_message,
        knowledge_context
    )

    # print(prompt)
    return generate_rag_answer(prompt)