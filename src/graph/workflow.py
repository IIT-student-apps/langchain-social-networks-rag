# graph/workflow.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from src.agents.chat_analyst import chat_analyst
from src.agents.comment_analyst import comment_analyst
from src.agents.profile_analyst import profile_analyst
from src.graph.orchestrator import orchestrator_chain
from src.agents.post_analyst import post_analyst
load_dotenv()
class AgentState(TypedDict):
    user_query: str
    plan: dict
    results: List[str]
    final_answer: str

def orchestrator_node(state):
    try:
        plan = orchestrator_chain.invoke({"user_query": state["user_query"]})
        # Защита от пустого JSON
        agents = plan.get("agents", [])
        reason = plan.get("reason", "Не указано")
        print(f"Оркестратор выбрал: {agents}, причина: {reason}")
        return {"plan": {"agents": agents, "reason": reason}, "results": []}
    except Exception as e:
        print(f"Оркестратор упал: {e}")
        return {"plan": {"agents": ["chat_analyst", "comment_analyst", "profile_analyst", "post_analyst"], "reason": "fallback"}, "results": []}


async def run_agents(state):
    results = state["results"]
    agents = state["plan"].get("agents", [])

    for agent_name in agents:
        try:
            if agent_name == "chat_analyst":
                agent = chat_analyst
            elif agent_name == "comment_analyst":
                agent = comment_analyst
            elif agent_name == "profile_analyst":
                agent = profile_analyst
            elif agent_name == "post_analyst":
                agent = post_analyst
            else:
                continue
            
            
            print(f"Вызов агента {agent_name} с input: {state['user_query']}")
            result = await agent.ainvoke({
                "input": state["user_query"],
                
                "agent_scratchpad": []
            })
            print(f"Результат: {result}")

            
            messages = result.get("messages", [])
            output = next(
                (m.content for m in reversed(messages) if isinstance(m, AIMessage) and m.content),
                f"Агент {agent_name} не вернул ответ."
            )
            results.append(output)
        except Exception as e:
            results.append(f"Ошибка в {agent_name}: {str(e)}")

    return {"results": results}


def compile_results(state):
    if not state["results"]:
        return {"final_answer": "Нет данных для анализа."}
    
    final = "\n\n".join([f"Агент {i+1}:\n{r}" for i, r in enumerate(state["results"])])
    return {"final_answer": final}


workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("run_agents", run_agents)
workflow.add_node("compile", compile_results)

workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", "run_agents")
workflow.add_edge("run_agents", "compile")
workflow.add_edge("compile", END)

app = workflow.compile()