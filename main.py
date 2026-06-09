
from asyncio import graph

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

graph.add_edge("planner", "implement")
graph.add_edge("implement", "review")
graph.add_edge("review", "decision")

graph.add_conditional_edges(
    "decision",
    router,
    {
        "implement": "implement",
        "report": "report"
    }
)