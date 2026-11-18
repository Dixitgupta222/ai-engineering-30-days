import ollama

from app.tools.knowledge_tools import search_company_knowledge
from app.tools.lead_tools import analyze_customer_lead

knowledge_tool = {
    "type": "function",
    "function": {
        "name": "search_company_knowledge",
        "description": "Search the company knowledge base for information about products, pricing, integrations, and healthcare projects.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The customer's question to search for."
                }
            },
            "required": ["query"]
        }
    }
}

lead_analysis_tool = {
    "type": "function",
    "function": {
        "name": "analyze_customer_lead",
        "description": "Analyze a potential customer lead and determine its score, priority, and recommended action.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The customer's message or project requirements."
                },
                "company_size": {
                    "type": "integer",
                    "description": "The number of employees in the customer's company."
                }
            },
            "required": ["message", "company_size"]
        }
    }
}

def run_agent(user_message: str):
    messages = [
        {
            "role": "system",
            "content": """
            You are a helpful company sales assistant.

            For questions about company products, pricing,
            integrations, services, or project requirements,
            use the search_company_knowledge tool.

            For greetings and general conversation,
            respond directly without using tools.

            Never invent company prices, packages,
            integrations, or capabilities.

            If company knowledge does not provide an exact price,
            explain that pricing depends on project requirements
            and recommend contacting the sales team.

            Do not claim that you can contact employees,
            provide quotes, or take actions on behalf of customers.

            Use retrieved company knowledge as the source
            of truth for company-specific answers.

            For questions involving lead qualification, customer potential,
            company size, lead score, or priority, use the
            analyze_customer_lead tool.

            When a customer message contains both company knowledge questions
            and lead qualification requirements, use both tools.

            Use the customer message and company size as inputs
            for lead analysis.

            STRICT KNOWLEDGE AND HALLUCINATION PREVENTION RULES:

            1. Only describe company products, services, integrations,
            pricing, and capabilities when supported by retrieved
            company knowledge.

            2. Never use general industry knowledge to claim that
            our company supports a particular integration or feature.

            3. If an integration is mentioned but not confirmed in
            company knowledge, clearly state that engineering
            confirmation is required.

            4. Never invent partner names, platforms, packages,
            prices, or technical capabilities.

            5. If the retrieved information is insufficient,
            honestly explain that the information is not confirmed.

            6. For healthcare projects, always mention that privacy,
            security, and regulatory requirements need review
            before feasibility can be confirmed.
            """
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = ollama.chat(
        model="llama3.2:3b",
        messages=messages,
        tools=[knowledge_tool, lead_analysis_tool]
    )

    tool_rounds = 0
    while response.message.tool_calls and tool_rounds < 5:
        tool_rounds += 1
        messages.append(response.message)
        for tool_call in response.message.tool_calls:
            try:
                result = execute_tool(tool_call)
            except Exception as error:
                result = f"Tool execution failed: {str(error)}"

            messages.append({
                "role": "tool",
                "tool_name": tool_call.function.name,
                "content": str(result)
            })

        response = ollama.chat(
            model="llama3.2:3b",
            messages=messages,
            tools=[knowledge_tool, lead_analysis_tool]
         )

    if response.message.tool_calls:
        return "I couldn't complete your request within the available processing steps. Please try simplifying your question."
    is_healthcare_query = any(
        word in user_message.lower()
        for word in ["healthcare", "hospital", "medical"]
    )
    if is_healthcare_query:
        required_warning = (
            "Healthcare-related projects require a review of privacy, "
            "security, and regulatory requirements before feasibility "
            "can be confirmed."
        )

        response_content = response.message.content

        if not all(
            term in response_content.lower()
            for term in ["privacy", "security", "regulatory"]
        ):
            response_content += "\n\n" + required_warning

        return response_content

    return response.message.content

def execute_tool(tool_call):
    function_name = tool_call.function.name
    arguments = tool_call.function.arguments

    if function_name == "search_company_knowledge":
        return search_company_knowledge(**arguments)

    if function_name == "analyze_customer_lead":
        return analyze_customer_lead(**arguments)

    return "Unknown tool requested"