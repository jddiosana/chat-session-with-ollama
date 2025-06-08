from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import psycopg
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from db.connection import get_connection
from core.prompts import get_session_title_prompt

from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

SESSION_TITLES_TABLE = os.getenv("SESSION_TITLES_TABLE", "session_titles")

# Create a thread pool for running synchronous operations
thread_pool = ThreadPoolExecutor()

async def run_in_thread(func, *args, **kwargs):
    """Run a synchronous function in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(thread_pool, lambda: func(*args, **kwargs))

def init_session_titles_table():
    """Initialize the session_titles table if it doesn't exist."""
    sync_connection = get_connection()
    cursor = sync_connection.cursor()
    
    # Create table if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {SESSION_TITLES_TABLE} (
            session_id UUID PRIMARY KEY,
            title TEXT NOT NULL
        )
    """)
    
    sync_connection.commit()
    cursor.close()
    sync_connection.close()

async def create_session_title(session_id: str, first_message: str) -> str:
    """Generate a title for a chat session based on the first message."""
    # Initialize LLM
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
    
    # Create prompt template
    prompt = get_session_title_prompt()
    
    # Generate title
    chain = prompt | llm
    response = await run_in_thread(chain.invoke, {"message": first_message})
    title = response.content.strip()
    
    # Store title in database
    await run_in_thread(store_title_in_db, session_id, title)
    return title

def store_title_in_db(session_id: str, title: str):
    """Store title in database (synchronous function)."""
    sync_connection = get_connection()
    cursor = sync_connection.cursor()
    
    cursor.execute(
        f"INSERT INTO {SESSION_TITLES_TABLE} (session_id, title) VALUES (%s, %s) ON CONFLICT (session_id) DO UPDATE SET title = %s",
        (session_id, title, title)
    )
    
    sync_connection.commit()
    cursor.close()
    sync_connection.close()

async def rename_session(session_id: str, messages: str) -> str:
    """Rename a session."""
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL)

    prompt = get_session_title_prompt()

    chain = prompt | llm
    response = await run_in_thread(chain.invoke, {"message": messages})
    new_title = response.content.strip()

    await run_in_thread(update_title_in_db, session_id, new_title)
    return new_title

def update_title_in_db(session_id: str, new_title: str):
    """Update title in database (synchronous function)."""
    sync_connection = get_connection()
    cursor = sync_connection.cursor()
    
    cursor.execute(f"UPDATE {SESSION_TITLES_TABLE} SET title = %s WHERE session_id = %s", (new_title, session_id))
    sync_connection.commit()
    cursor.close()
    sync_connection.close()

async def get_session_title(session_id: str) -> str:
    """Retrieve the title for a given session."""
    return await run_in_thread(get_title_from_db, session_id)

def get_title_from_db(session_id: str) -> str:
    """Get title from database (synchronous function)."""
    sync_connection = get_connection()
    cursor = sync_connection.cursor()
    
    cursor.execute(f"SELECT title FROM {SESSION_TITLES_TABLE} WHERE session_id = %s", (session_id,))
    result = cursor.fetchone()
    
    cursor.close()
    sync_connection.close()
    
    return result[0] if result else None

async def delete_session_title(session_id: str):
    """Delete session title from database asynchronously."""
    await run_in_thread(_delete_session_title_sync, session_id)
        
def _delete_session_title_sync(session_id: str):
    """Delete session title from database (synchronous function)."""
    sync_connection = get_connection()
    cursor = sync_connection.cursor()
    
    cursor.execute(f"DELETE FROM {SESSION_TITLES_TABLE} WHERE session_id = %s", (session_id,))
    sync_connection.commit()
    cursor.close()
    sync_connection.close()

def get_session_title_sync(session_id: str) -> str:
    """Synchronous version of get_session_title."""
    return get_title_from_db(session_id)

# Initialize the table when the module is imported
init_session_titles_table()

