from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, MessagesState, START
from langchain_anthropic import ChatAnthropic
from app.tools import get_card_fee, get_transfer_limit

load_dotenv()

llm = ChatAnthropic(model="claude-haiku-4-5", max_tokens=300)
llm_with_tools = llm.bind_tools([get_card_fee, get_transfer_limit])

def call_model(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(MessagesState)                        # 1
graph.add_node("model", call_model)                      # 2
graph.add_node("tools", ToolNode([get_card_fee, get_transfer_limit]))    # 3
graph.add_edge(START, "model")                           # 4
graph.add_conditional_edges("model", tools_condition)    # 5
graph.add_edge("tools", "model")                         # 6
agent = graph.compile()

if __name__ == "__main__":
    questions = [
        "What is the monthly fee for a credit card?",
        "What is the daily limit for transfers to other banks?",
        "What's the weather tomorrow?",
    ]
    for question in questions:
        result = agent.invoke({"messages": [("user", question)]})
        print("=" * 60)
        for m in result["messages"]:
            print(type(m).__name__, "|", m.text, "|", getattr(m, "tool_calls", ""))