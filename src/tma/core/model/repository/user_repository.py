from sqlalchemy.orm import Session

from tma.core.model.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_user(self, user):
        try:
            self.session.add(user)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def get_user_by_id(self, user_id):
        try:
            user = self.session.query(User).filter(User.user_id == user_id).first()
            return user
        finally:
            self.session.close()

    def get_user_by_session_id(self, session_id):
        try:
            user = self.session.query(User).filter(User.session_id == session_id).first()
            return user
        finally:
            self.session.close()
