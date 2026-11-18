from app.tools.lead_tools import analyze_customer_lead
from unittest.mock import Mock
from app.services.agent_service import execute_tool
from app.services import agent_service

def test_analyze_customer_lead():
    result = analyze_customer_lead(
        message="We urgently need an AI chatbot demo with a budget",
        company_size=600
    )

    assert result["score"] == 100
    assert result["priority"] == "high"
    assert result["recommendation"] == "Assign to enterprise sales"
    assert result["contact"] == "Contact immediately"

def test_execute_lead_analysis_tool():
    tool_call = Mock()
    tool_call.function.name = "analyze_customer_lead"
    tool_call.function.arguments = {
        "message": "We need an urgent AI chatbot demo",
        "company_size": 600
    }

    result = execute_tool(tool_call)

    assert result["priority"] == "high"
    assert result["recommendation"] == "Assign to enterprise sales"


from unittest.mock import patch

def test_execute_knowledge_search_tool():
    tool_call = Mock()
    tool_call.function.name = "search_company_knowledge"
    tool_call.function.arguments = {
        "query": "AI chatbot pricing"
    }

    with patch(
        "app.services.agent_service.search_company_knowledge",
        return_value=["Pricing depends on project scope."]
    ) as mock_search:

        result = execute_tool(tool_call)

    mock_search.assert_called_once_with(query="AI chatbot pricing")
    assert result == ["Pricing depends on project scope."]

def test_execute_unknown_tool():
    tool_call = Mock()
    tool_call.function.name = "unknown_tool"
    tool_call.function.arguments = {}

    result = execute_tool(tool_call)

    assert result == "Unknown tool requested"

def test_run_agent_returns_final_response():
    mock_response = Mock()
    mock_response.message.tool_calls = None
    mock_response.message.content = "Hello! How can I help you?"

    with patch(
        "app.services.agent_service.ollama.chat",
        return_value=mock_response
    ) as mock_chat:

        result = agent_service.run_agent("Hello")

    assert result == "Hello! How can I help you?"
    mock_chat.assert_called_once()

def test_run_agent_executes_lead_tool():
    tool_call = Mock()
    tool_call.function.name = "analyze_customer_lead"
    tool_call.function.arguments = {
        "message": "We need an urgent AI chatbot demo",
        "company_size": 600
    }

    tool_response = Mock()
    tool_response.message.tool_calls = [tool_call]

    final_response = Mock()
    final_response.message.tool_calls = None
    final_response.message.content = "This is a high-priority lead."

    with patch(
        "app.services.agent_service.ollama.chat",
        side_effect=[tool_response, final_response]
    ) as mock_chat:

        with patch(
            "app.services.agent_service.execute_tool",
            return_value={
                "score": 100,
                "priority": "high",
                "recommendation": "Assign to enterprise sales",
                "contact": "Contact immediately"
            }
        ) as mock_execute:

            result = agent_service.run_agent("We need an urgent AI chatbot demo")

    assert result == "This is a high-priority lead."
    mock_execute.assert_called_once_with(tool_call)
    assert mock_chat.call_count == 2

def test_run_agent_executes_multiple_tools():
    knowledge_call = Mock()
    knowledge_call.function.name = "search_company_knowledge"
    knowledge_call.function.arguments = {"query": "AI chatbot pricing"}

    lead_call = Mock()
    lead_call.function.name = "analyze_customer_lead"
    lead_call.function.arguments = {
        "message": "We need an AI chatbot",
        "company_size": 600
    }

    tool_response = Mock()
    tool_response.message.tool_calls = [
        knowledge_call,
        lead_call
    ]

    final_response = Mock()
    final_response.message.tool_calls = None
    final_response.message.content = "Combined answer."

    with patch(
        "app.services.agent_service.ollama.chat",
        side_effect=[tool_response, final_response]
    ):

        with patch(
            "app.services.agent_service.execute_tool",
            side_effect=[
                ["Pricing depends on project scope."],
                {"score": 90, "priority": "high"}
            ]
        ) as mock_execute:

            result = agent_service.run_agent("Evaluate my chatbot project.")

    assert result == "Combined answer."
    assert mock_execute.call_count == 2

def test_run_agent_handles_multiple_rounds():
    first_tool = Mock()
    first_tool.function.name = "search_company_knowledge"
    first_tool.function.arguments = {"query": "AI chatbot integrations"}

    second_tool = Mock()
    second_tool.function.name = "analyze_customer_lead"
    second_tool.function.arguments = {
        "message": "We need an AI chatbot",
        "company_size": 600
    }

    first_response = Mock()
    first_response.message.tool_calls = [first_tool]

    second_response = Mock()
    second_response.message.tool_calls = [second_tool]

    final_response = Mock()
    final_response.message.tool_calls = None
    final_response.message.content = "Final combined answer."

    with patch(
        "app.services.agent_service.ollama.chat",
        side_effect=[
            first_response,
            second_response,
            final_response
        ]
    ) as mock_chat:

        with patch(
            "app.services.agent_service.execute_tool",
            side_effect=[
                ["Integration confirmation required."],
                {"score": 90, "priority": "high"}
            ]
        ) as mock_execute:

            result = agent_service.run_agent("Evaluate my hospital chatbot project.")

    assert "Final combined answer." in result
    assert "privacy" in result.lower()
    assert "security" in result.lower()
    assert "regulatory" in result.lower()
    assert mock_execute.call_count == 2
    assert mock_chat.call_count == 3

def test_run_agent_stops_after_five_rounds():
    tool_call = Mock()
    tool_call.function.name = "unknown_tool"
    tool_call.function.arguments = {}

    tool_response = Mock()
    tool_response.message.tool_calls = [tool_call]

    with patch(
        "app.services.agent_service.ollama.chat",
        return_value=tool_response
    ) as mock_chat:

        with patch(
            "app.services.agent_service.execute_tool",
            return_value="Unknown tool requested"
        ) as mock_execute:

            result = agent_service.run_agent("Test tool limit")

    assert mock_execute.call_count == 5
    assert mock_chat.call_count == 6

def test_run_agent_returns_fallback_after_five_rounds():
    tool_call = Mock()
    tool_call.function.name = "unknown_tool"
    tool_call.function.arguments = {}

    tool_response = Mock()
    tool_response.message.tool_calls = [tool_call]

    with patch(
        "app.services.agent_service.ollama.chat",
        return_value=tool_response
    ):

        with patch(
            "app.services.agent_service.execute_tool",
            return_value="Unknown tool requested"
        ):

            result = agent_service.run_agent("Test tool limit")

    assert result == (
        "I couldn't complete your request within the available "
        "processing steps. Please try simplifying your question."
    )

def test_run_agent_handles_tool_execution_error():
    tool_call = Mock()
    tool_call.function.name = "unknown_tool"
    tool_call.function.arguments = {}

    tool_response = Mock()
    tool_response.message.tool_calls = [tool_call]

    final_response = Mock()
    final_response.message.tool_calls = None
    final_response.message.content = "I encountered a tool error."

    with patch(
        "app.services.agent_service.ollama.chat",
        side_effect=[tool_response, final_response]
    ) as mock_chat:

        with patch(
            "app.services.agent_service.execute_tool",
            side_effect=RuntimeError("Database unavailable")
        ) as mock_execute:

            result = agent_service.run_agent("Test error handling")

    assert result == "I encountered a tool error."
    mock_execute.assert_called_once_with(tool_call)

    tool_messages = mock_chat.call_args_list[1].kwargs["messages"]
    assert tool_messages[-1]["content"] == (
        "Tool execution failed: Database unavailable"
    )

def test_run_agent_adds_healthcare_warning():
    mock_response = Mock()
    mock_response.message.tool_calls = None
    mock_response.message.content = "We can discuss your hospital chatbot project."

    with patch(
        "app.services.agent_service.ollama.chat",
        return_value=mock_response
    ):
        result = agent_service.run_agent(
            "We need a medical chatbot."
        )

    assert "privacy" in result.lower()
    assert "security" in result.lower()
    assert "regulatory" in result.lower()
    assert "feasibility" in result.lower()
    