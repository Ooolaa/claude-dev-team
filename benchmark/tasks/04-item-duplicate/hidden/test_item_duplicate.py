import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/"


def test_duplicate_copies_the_item_for_the_caller(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    me = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
    assert me is not None
    t = uuid.uuid4().hex[:12]
    item = crud.create_item(session=db, item_in=ItemCreate(title=t, description="d"), owner_id=me.id)

    r = client.post(f"{URL}{item.id}/duplicate", headers=normal_user_token_headers)

    assert r.status_code == 200
    copy = r.json()
    assert copy["id"] != str(item.id)
    assert (copy["title"], copy["description"], copy["owner_id"]) == (f"Copy of {t}", "d", str(me.id))
    # The copy is a real item, and the original is untouched.
    assert client.get(f"{URL}{copy['id']}", headers=normal_user_token_headers).json()["title"] == f"Copy of {t}"
    assert client.get(f"{URL}{item.id}", headers=normal_user_token_headers).json()["title"] == t


def test_superuser_can_duplicate_anyones_item_and_owns_the_copy(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = crud.create_item(session=db, item_in=ItemCreate(title="theirs"), owner_id=create_random_user(db).id)
    me = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert me is not None

    r = client.post(f"{URL}{item.id}/duplicate", headers=superuser_token_headers)

    assert r.status_code == 200
    assert r.json()["owner_id"] == str(me.id)
    assert r.json()["description"] is None


def test_normal_user_cannot_duplicate_someone_elses_item(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = crud.create_item(session=db, item_in=ItemCreate(title="theirs"), owner_id=create_random_user(db).id)

    r = client.post(f"{URL}{item.id}/duplicate", headers=normal_user_token_headers)

    assert r.status_code == 403


def test_duplicating_a_missing_item_is_a_404(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(f"{URL}{uuid.uuid4()}/duplicate", headers=superuser_token_headers)

    assert r.status_code == 404
