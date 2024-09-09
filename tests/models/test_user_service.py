import unittest
from unittest.mock import MagicMock
from tma.core.model.models.user import User
from tma.core.model.repository.user_repository import UserRepository
from tma.core.service.user.user_service import UserService

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(spec=UserRepository)
        self.service = UserService(self.mock_repository)

    def test_create_user_when_user_does_not_exist(self):
        session_id = '12345'
        self.mock_repository.get_user_by_session_id.return_value = None
        mock_user = User(session_id=session_id)

        self.mock_repository.add_user.side_effect = lambda user: setattr(user, 'id', 1)

        result = self.service.create_user(session_id)

        self.mock_repository.get_user_by_session_id.assert_called_once_with(session_id)
        self.mock_repository.add_user.assert_called_once()
        self.assertEqual(result.session_id, session_id)
        self.assertEqual(result.id, 1)

    def test_create_user_when_user_exists(self):
        session_id = '12345'
        existing_user = User(session_id=session_id)
        existing_user.id = 1
        self.mock_repository.get_user_by_session_id.return_value = existing_user

        result = self.service.create_user(session_id)

        self.mock_repository.get_user_by_session_id.assert_called_once_with(session_id)
        self.mock_repository.add_user.assert_not_called()
        self.assertEqual(result, existing_user)

    def test_get_user_by_session(self):
        session_id = '12345'
        mock_user = User(session_id=session_id)
        self.mock_repository.get_user_by_session_id.return_value = mock_user

        result = self.service.get_user_by_session(session_id)

        self.mock_repository.get_user_by_session_id.assert_called_once_with(session_id)
        self.assertEqual(result, mock_user)
