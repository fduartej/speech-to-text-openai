import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT=os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
SQL_DATABASE = os.getenv("SQL_DATABASE")

from langchain.utilities import SQLDatabase  
from langchain.chains import create_sql_query_chain
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

# Define BaseCache
class BaseCache(BaseModel):
    pass

# Define Callbacks if not available
class Callbacks(BaseModel):
    pass

# Ensure SQLDatabaseChain is fully defined
SQLDatabaseChain.model_rebuild()

import streamlit as st

@st.cache_resource
def get_chain():
    print("Creating chain")
    db = SQLDatabase.from_uri(SQL_DATABASE)
    llm = ChatOpenAI(temperature=0, verbose=True)
    
    chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
    return chain

def create_history(messages):
    history = ChatMessageHistory()
    for message in messages:
        if message["role"] == "user":
            history.add_user_message(message["content"])
        else:
            history.add_ai_message(message["content"])
    return history

def invoke_chain(question, messages):
    # Simple heuristic to detect casual messages
    casual_phrases = ["hola", "buenos días", "cómo estás", "gracias", "adiós"]
    if any(phrase in question.lower() for phrase in casual_phrases):
        # Responder de manera genérica sin realizar una consulta SQL
        return "¡Hola! ¿En qué puedo ayudarte hoy?"

    # Continuar con la lógica existente para consultas SQL
    chain = get_chain()
    history = create_history(messages)
    response = chain.invoke({"query": question, "top_k": 3, "messages": history.messages})
    
    # Limpiar la consulta SQL generada
    # sql_query = response.get('SQLQuery', 'No SQL Query found')
    # sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    # Imprimir la consulta SQL generada
    print(f"Generated SQL Query: {response.get('SQLQuery', 'No SQL Query found')}")
  
    for key, value in response.items():
        print(f"{key}: {value}")
    history.add_user_message(question)
    answer = response["result"]
    history.add_ai_message(answer)
    return answer

def invoke_chainold(question,messages):
    chain = get_chain()
    history = create_history(messages)
    response = chain.invoke({"query": question,"top_k":3,"messages":history.messages})
     # Imprimir la consulta SQL generada
    print(f"Generated SQL Query: {response.get('SQLQuery', 'No SQL Query found')}")
  
    for key, value in response.items():
        print(f"{key}: {value}")
    history.add_user_message(question)
    answer = response["result"]
    history.add_ai_message(answer)
    return answer