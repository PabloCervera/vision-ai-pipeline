"""
Este módulo define un agente de alerta que analiza la escena, evalúa el nivel de riesgo y genera alertas en función de la información obtenida. Utiliza un modelo de lenguaje para describir la escena y determinar el nivel de riesgo,
 y luego decide si enviar una alerta o ignorar la situación.
"""

from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from scene_analyzer import SceneAnalyzer

class AgentState(TypedDict):
    frame: object
    static_objects: list
    scene_description: str
    risk_level: str
    alert_message: str


analyzer = SceneAnalyzer()
load_dotenv()
llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

def analyze_scene(state: AgentState) -> dict:
    """
    Analiza la escena utilizando un modelo de lenguaje para generar una descripción.
    """

    description = analyzer.analyze(state["frame"], f"Se han detectado {len(state['static_objects'])} objetos estáticos.")
    return {"scene_description": description}

def decide_risk(state: AgentState) -> dict:
    """
    Analiza el nivel de riesgo basado en la descripción de la escena y el número de objetos estáticos.
    """
    prompt = (
        f"Basándote en esta descripción de escena, evalúa el nivel de riesgo. "
        f"Responde ÚNICAMENTE con una de estas tres palabras: low, medium, high. "
        f"Descripción: {state['scene_description']}"
    )
    message = HumanMessage(content=[
            {"type": "text", "text": prompt},
        ])
    risk_level = llm.invoke([message])
    return {"risk_level": risk_level.content.strip().lower()}

def send_alert(state: AgentState) -> dict:
    """
    Genera un mensaje de alerta basado en el nivel de riesgo.
    """
    alert_message = f"Alerta nivel {state['risk_level']}: {state['scene_description']}"    
    return {"alert_message": alert_message}

def ignore(state: AgentState) -> dict:
    """
    Acción de ignorar, no realiza ninguna operación.
    """
    return {}


graph = StateGraph(AgentState)

# Añadir nodos
graph.add_node("analyze_scene", analyze_scene)
graph.add_node("decide_risk", decide_risk)
graph.add_node("send_alert", send_alert)
graph.add_node("ignore", ignore)

# Punto de entrada
graph.set_entry_point("analyze_scene")

# Aristas fijas
graph.add_edge("analyze_scene", "decide_risk")

# Arista condicional: según risk_level va a send_alert o ignore
graph.add_conditional_edges(
    "decide_risk",
    lambda state: state["risk_level"] if state["risk_level"] in ["high", "medium"] else "low",
    {"high": "send_alert", "medium": "send_alert", "low": "ignore"}
)

graph.add_edge("send_alert", END)
graph.add_edge("ignore", END)

agent = graph.compile()