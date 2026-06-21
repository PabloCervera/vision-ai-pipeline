

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

class QAChain:
    def __init__(self):
        self.qaChain = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

    def ask(self, question, events):
        """
        Responde a una pregunta basada en los eventos detectados.
        """
        formated_events = "\n".join([f"ID: {event['track_id']}, Alerta: {event['alert']}, Nivel de riesgo: {event['risk_level']}, Timestamp: {event['timestamp']}" for event in events])
                
        prompt = f"""Eres un asistente de un sistema de vigilancia inteligente. 
            Responde a la pregunta del usuario basándote ÚNICAMENTE en los siguientes eventos detectados.
            Si no hay información suficiente para responder, dilo claramente.

            Eventos:
            {formated_events}

            Pregunta: {question}
            """
        
        message = HumanMessage(content=prompt)
        response = self.qaChain.invoke([message])
        return response.content