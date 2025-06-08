from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory

from core.prompts import get_session_title_prompt, chat_prompt
from db.connection import get_connection

from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

CHAT_HISTORY_TABLE = os.getenv("CHAT_HISTORY_TABLE", "chat_history")

llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL)

def get_session_title_chain():
    return get_session_title_prompt() | llm

def get_chat_chain():
    return chat_prompt() | llm

def get_chat_chain_with_history(chat_history_table, connection):
    return RunnableWithMessageHistory(
        get_chat_chain(),
        lambda session_id: PostgresChatMessageHistory(
            chat_history_table,
            session_id,
            sync_connection=connection
        ),
        input_messages_key="user_input",
        history_messages_key="history"
    )