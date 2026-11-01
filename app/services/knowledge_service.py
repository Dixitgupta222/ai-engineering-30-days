def search_knowledge(keyword: str) -> bool:
    with open("app/knowledge/company_knowledge.md", "r") as file:
        content = file.read()

    return keyword.lower() in content.lower()

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



def answer_customer_with_knowledge(customer_message: str) -> str:
    message = customer_message.lower()

    if "healthcare" in message:
        keyword = "healthcare"
    elif "pricing" in message or "price" in message or "cost" in message:
        keyword = "pricing"
    elif "chatbot" in message:
        keyword = "AI Chatbot"
    elif "integration" in message:
        keyword = "Integrations"
    else:
        keyword = customer_message

    knowledge = find_knowledge_section(keyword)

    if knowledge == "No matching section found":
        return "I don't have enough company information to answer that question."

    return build_knowledge_prompt_with_context(
        customer_message,
        knowledge
    )