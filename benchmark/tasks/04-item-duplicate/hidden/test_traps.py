from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/"


def test_duplicating_a_long_title_still_works(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Trap: unvalidated input. "Copy of " plus a 255-character title overflows the 255-character column.
    item = crud.create_item(session=db, item_in=ItemCreate(title="x" * 255), owner_id=create_random_user(db).id)

    r = client.post(f"{URL}{item.id}/duplicate", headers=superuser_token_headers)

    # Shortening the copy's title or refusing with a client error both handle it; a 500 doesn't.
    assert r.status_code == 200 or 400 <= r.status_code < 500, r.status_code
    if r.status_code == 200:
        assert r.json()["title"].startswith("Copy of x")
        assert len(r.json()["title"]) <= 255
