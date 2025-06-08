import pytest
from unittest.mock import patch, Mock, AsyncMock
from app.services import chat_sessions

@pytest.fixture
def mock_session_id():
    return "11111111-1111-1111-1111-111111111111"

@pytest.fixture
def mock_title():
    return "My Session Title"

@pytest.fixture
def mock_llm_response():
    mock_response = Mock()
    mock_response.content = "Generated Title"
    return mock_response

@pytest.mark.asyncio
async def test_create_session_title(mock_session_id, mock_llm_response):
    with patch("app.services.chat_sessions.ChatOllama") as mock_llm_class, \
         patch("app.services.chat_sessions.get_session_title_prompt") as mock_prompt, \
         patch("app.services.chat_sessions.run_in_thread", new=AsyncMock()) as mock_run:

        # Simulate LLM instance
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm

        # Simulate prompt and chain
        mock_prompt_obj = Mock()
        mock_prompt.return_value = mock_prompt_obj

        mock_chain = Mock()
        mock_prompt_obj.__or__ = lambda self, other: mock_chain  # simulate prompt | llm

        mock_run.side_effect = [mock_llm_response, None]

        title = await chat_sessions.create_session_title(mock_session_id, "Hello")
        assert title == "Generated Title"


@pytest.mark.asyncio
async def test_rename_session(mock_session_id, mock_llm_response):
    with patch("app.services.chat_sessions.ChatOllama") as mock_llm_class, \
         patch("app.services.chat_sessions.get_session_title_prompt") as mock_prompt, \
         patch("app.services.chat_sessions.run_in_thread", new=AsyncMock()) as mock_run:

        # Simulate LLM instance
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm

        # Simulate prompt and chain
        mock_prompt_obj = Mock()
        mock_prompt.return_value = mock_prompt_obj

        mock_chain = Mock()
        mock_prompt_obj.__or__ = lambda self, other: mock_chain  # simulate prompt | llm

        mock_run.side_effect = [mock_llm_response, None]

        new_title = await chat_sessions.rename_session(mock_session_id, "Some messages")
        assert new_title == "Generated Title"


def test_store_title_in_db(mock_session_id, mock_title):
    with patch("app.services.chat_sessions.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        chat_sessions.store_title_in_db(mock_session_id, mock_title)

        mock_cursor.execute.assert_called_once()
        mock_conn.return_value.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

def test_update_title_in_db(mock_session_id, mock_title):
    with patch("app.services.chat_sessions.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        chat_sessions.update_title_in_db(mock_session_id, mock_title)

        mock_cursor.execute.assert_called_once()
        mock_conn.return_value.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

def test_get_title_from_db(mock_session_id, mock_title):
    with patch("app.services.chat_sessions.get_connection") as mock_conn:
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (mock_title,)
        mock_conn.return_value.cursor.return_value = mock_cursor

        title = chat_sessions.get_title_from_db(mock_session_id)
        assert title == mock_title

@pytest.mark.asyncio
async def test_get_session_title(mock_session_id, mock_title):
    with patch("app.services.chat_sessions.get_title_from_db", return_value=mock_title):
        title = await chat_sessions.get_session_title(mock_session_id)
        assert title == mock_title

@pytest.mark.asyncio
async def test_delete_session_title(mock_session_id):
    with patch("app.services.chat_sessions._delete_session_title_sync") as mock_del:
        await chat_sessions.delete_session_title(mock_session_id)
        mock_del.assert_called_once_with(mock_session_id)

def test_get_session_title_sync(mock_session_id, mock_title):
    with patch("app.services.chat_sessions.get_title_from_db", return_value=mock_title):
        title = chat_sessions.get_session_title_sync(mock_session_id)
        assert title == mock_title


