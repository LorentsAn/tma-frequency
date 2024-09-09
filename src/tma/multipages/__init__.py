import sys
from pathlib import Path

import redis

import solara

from tma.core.database import create_database, drop_database
from tma.core.model.repository import user_repo
from tma.core.service.services.user_service import UserService
from tma.core.settings import settings

root_path = str(Path(__file__).resolve().parents[1])

if root_path not in sys.path:
    sys.path.append(root_path)

# redis_db = redis.from_url(settings.redis_dsn, encoding="utf-8", decode_responses=True)

# todo delete
create_database()


@solara.component
def Page():
    session_id = solara.get_session_id()

    user_service = UserService(user_repo)

    # Add a new user
    user_service.create_user(session_id)
# @solara.component
# def Layout(children):
#     return solara.AppLayout(children=children, color=None)
