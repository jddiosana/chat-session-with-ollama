from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_postgres import PostgresChatMessageHistory

import psycopg
import uuid

from services.chat_sessions import get_session_title
from core.chains import get_chat_chain_with_history
from db.connection import get_connection

from dotenv import load_dotenv
import os

load_dotenv()

CHAT_HISTORY_TABLE = os.getenv("CHAT_HISTORY_TABLE", "chat_history")

DB_NAME = os.getenv("DB_NAME", "chat-history")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")

IS_TESTING = os.getenv("IS_TESTING", "0") == "1"

if not IS_TESTING:
    SYNC_CONNECTION = get_connection()
    PostgresChatMessageHistory.create_tables(
        SYNC_CONNECTION,
        CHAT_HISTORY_TABLE
    )
    CHAIN_WITH_HISTORY = get_chat_chain_with_history(CHAT_HISTORY_TABLE, SYNC_CONNECTION)
else:
    SYNC_CONNECTION = None
    CHAIN_WITH_HISTORY = None

def get_session_history(session_id):
    return PostgresChatMessageHistory(
        CHAT_HISTORY_TABLE,
        session_id,
        sync_connection=SYNC_CONNECTION
    )

def get_response_stream(session_id, user_input):
    response = CHAIN_WITH_HISTORY.stream({"user_input": user_input}, config={"configurable": {"session_id": session_id}})
    for chunk in response:
        yield chunk

def get_chat_history(session_id):
    chat_history = get_session_history(session_id)
    return [
        {"type": msg.type, "content": msg.content}
        for msg in chat_history.messages
    ] 

def list_sessions():
    cursor = SYNC_CONNECTION.cursor()
    # get distinct sessions with the 
    cursor.execute("""
        WITH latest_messages AS (
            SELECT session_id, MAX(created_at) as last_activity
            FROM chat_history
            GROUP BY session_id
        )
        SELECT session_id 
        FROM latest_messages 
        ORDER BY last_activity ASC
    """)
    return [row[0] for row in cursor.fetchall()]

def delete_chat(session_id):
    chat_history = get_session_history(session_id)
    chat_history.clear()