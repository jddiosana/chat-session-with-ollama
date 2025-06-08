import pytest
from unittest.mock import patch, Mock
from app.services import chat

@pytest.fixture
def mock_session_id():
    return "test-session-id"

@pytest.fixture
def mock_db_cursor():
    cursor = Mock()
    cursor.fetchall.return_value = [("session1",), ("session2",)]
    return cursor

@pytest.fixture
def mock_db_connection(mock_db_cursor):
    connection = Mock()
    connection.cursor.return_value = mock_db_cursor
    return connection

def test_get_response_stream(mock_session_id):
    mock_chain = Mock()
    mock_chain.stream.return_value = ["Hi", " there", "!"]
    with patch("app.services.chat.CHAIN_WITH_HISTORY", mock_chain):
        result = list(chat.get_response_stream(mock_session_id, "Hello"))
        assert result == ["Hi", " there", "!"]
        mock_chain.stream.assert_called_once()

def test_get_chat_history(mock_session_id):
    mock_history = Mock()
    mock_history.messages = [
        Mock(type="human", content="Hello"),
        Mock(type="ai", content="Hi!")
    ]
    with patch("app.services.chat.get_session_history", return_value=mock_history):
        result = chat.get_chat_history(mock_session_id)
        assert result == [{"type": "human", "content": "Hello"}, {"type": "ai", "content": "Hi!"}]

def test_list_sessions():
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [("session1",), ("session2",)]
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.services.chat.SYNC_CONNECTION", mock_connection):
        result = chat.list_sessions()
        assert result == ["session1", "session2"]
        mock_cursor.execute.assert_called_once()

def test_delete_chat(mock_session_id):
    mock_history = Mock()
    with patch("app.services.chat.get_session_history", return_value=mock_history):
        chat.delete_chat(mock_session_id)
        mock_history.clear.assert_called_once()

def test_get_session_history(mock_session_id):
    with patch("app.services.chat.PostgresChatMessageHistory") as mock_cls:
        chat.get_session_history(mock_session_id)
        mock_cls.assert_called_once()
