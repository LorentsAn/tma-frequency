from tma.core.model.models.user import User
from tma.core.model.repository.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, session_id):
        user = self.user_repository.get_user_by_session_id(session_id)
        if not user:
            user = User(session_id=session_id)
            self.user_repository.add_user(user)
        return user

    def get_user_by_session(self, session_id):
        return self.user_repository.get_user_by_session_id(session_id)
