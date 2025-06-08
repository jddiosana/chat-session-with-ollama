from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

def get_session_title_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that creates concise, descriptive titles for chat sessions. Create a title that captures the main topic or purpose of the conversation. \
        Create a short title (3-5 words) for a chat session that starts with the message given. Do not include any other text in your response. \
        If the message is vague -- no context or just a greeting, return 'New Chat'"),
        ("user", "{message}")
    ])

def get_system_prompt():
    system_prompt = """You are a helpful assistant that answers general questions from the user. Your goal is to provide quick, accurate, and helpful answers.\
    Make your answers short and concise while making sure to provide all the information the user is looking for.
    """
    return system_prompt

def chat_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{user_input}"),
    ])