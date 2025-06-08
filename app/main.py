import streamlit as st
from services.chat import get_response_stream, get_chat_history, list_sessions, delete_chat
from services.chat_sessions import create_session_title, get_session_title, get_session_title_sync, rename_session, delete_session_title
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

# initialize thread pool for async operations
thread_pool = ThreadPoolExecutor()

def run_async(coro):
    """Run an async function in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def create_new_session():
    st.session_state["session_id"] = None
    st.session_state["history"] = []

async def delete_session(session_id): # delete session history and session title on the backend asynchronously
    delete_chat(session_id)
    if session_id == st.session_state["session_id"]:
        st.session_state["session_id"] = None
    st.session_state["history"] = [] 
    await delete_session_title(session_id)

async def update_session_title(session_id: str, messages: str):
    """Update session title asynchronously."""
    new_title = await rename_session(session_id, messages)
    if new_title:
        return new_title
    return None

# session management
if "sessions" not in st.session_state:
    st.session_state["sessions"] = [str(session_id) for session_id in list_sessions()]

# default session_id is None
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None

st.set_page_config(
    page_title="Ollama Chatbot",
)

with st.sidebar:
        
    # create new session button
    st.button("New Chat", on_click=create_new_session, use_container_width=True)
    
    st.divider()
    
    st.header("Chat History")

    # list session history
    for session in st.session_state["sessions"]:
        session_title_col, delete_col = st.columns([4, 1])
        with session_title_col:
            session_title = get_session_title_sync(session) or f"New Chat" # get session title or default to "New Chat" if no title yet

            if session == st.session_state["session_id"]:
                st.button(
                    session_title,
                    key=f"session_{session}",
                    use_container_width=True,
                    type="primary" # emphasize the current session
                )
            else:
                if st.button(
                    session_title,
                    key=f"session_{session}",
                    use_container_width=True
                ):
                    st.session_state["session_id"] = session 
                    st.session_state["history"] = []
                    st.rerun()
        with delete_col: # delete session button
            if st.button("🗑️", key=f"delete_{session}", use_container_width=True):
                st.session_state["sessions"].remove(session)
                run_async(delete_session(session))
                st.rerun()

# Main chat area

session_id = st.session_state["session_id"]

if session_id is None: # default no session selected
    st.title("Hi! How can I help you today?")
else: # if session selected, show session title
    session_title = get_session_title_sync(session_id)
    if "session_title" in st.session_state:
        st.title(st.session_state["session_title"])
    else:
        st.title(session_title if session_title else f"New Chat")

if "history" not in st.session_state:
    st.session_state["history"] = []

# fetch history from db
if session_id is not None:
    st.session_state["history"] = get_chat_history(session_id)

# display chat history
for msg in st.session_state["history"]:
    if msg["type"] == "human":
        with st.chat_message("user"):   
            st.markdown(f"{msg['content']}")
    elif msg["type"] == "ai" or msg["type"] == "AIMessageChunk":
        with st.chat_message("assistant"):
            st.markdown(f"{msg['content']}")

# user input
user_input = st.chat_input("Type your message here...", key="user_input")
if user_input and user_input != "":
    with st.chat_message("user"):
        st.markdown(f"{user_input}")
    with st.chat_message("assistant"):
        if session_id is None:  # if this is a new chat, create a new session
            session_id = str(uuid.uuid4())
            st.session_state["session_id"] = session_id
            st.session_state["sessions"] = [session_id] + st.session_state["sessions"] # add new session to the top of the list
            thread_pool.submit(run_async, create_session_title(session_id, user_input)) # create session title asynchronously
            st.write_stream(get_response_stream(session_id, user_input))
            st.rerun()
        else:
            st.write_stream(get_response_stream(session_id, user_input))
            if get_session_title_sync(session_id) == "New Chat": # rename session after getting more information from the session
                message_history = get_chat_history(session_id)
                messages = "\n".join(f"{msg['type']}: {msg['content']}" for msg in message_history[-4:]) 
                new_title = run_async(update_session_title(session_id, messages))
                if new_title:
                    st.session_state["session_title"] = new_title
            st.rerun()  # refresh the UI to update sidebar and title