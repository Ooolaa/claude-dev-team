import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/"


def test_like_wildcards_in_query_are_literal(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Trap: unvalidated input. Passing q straight into LIKE/ILIKE makes % and _ wildcards.
    t = uuid.uuid4().hex[:12]
    owner = create_random_user(db)
    for title in (f"{t}%off", f"{t}xoff", f"{t}_new", f"{t}xnew"):
        crud.create_item(session=db, item_in=ItemCreate(title=title), owner_id=owner.id)

    for q, expected in ((f"{t}%", f"{t}%off"), (f"{t}_", f"{t}_new")):
        r = client.get(URL, headers=superuser_token_headers, params={"q": q})
        assert r.status_code == 200
        assert [i["title"] for i in r.json()["data"]] == [expected]
