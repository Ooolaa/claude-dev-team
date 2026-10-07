import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/"


def test_superuser_transfers_an_item(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = crud.create_item(session=db, item_in=ItemCreate(title="t", description="d"), owner_id=create_random_user(db).id)
    new_owner = create_random_user(db)

    r = client.post(f"{URL}{item.id}/transfer", headers=superuser_token_headers, json={"owner_id": str(new_owner.id)})

    assert r.status_code == 200
    assert (r.json()["id"], r.json()["owner_id"], r.json()["title"], r.json()["description"]) == (
        str(item.id), str(new_owner.id), "t", "d"
    )
    db.refresh(item)
    assert item.owner_id == new_owner.id


def test_normal_user_cannot_transfer_even_their_own_item(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    me = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
    assert me is not None
    item = crud.create_item(session=db, item_in=ItemCreate(title="mine"), owner_id=me.id)
    other = create_random_user(db)

    r = client.post(f"{URL}{item.id}/transfer", headers=normal_user_token_headers, json={"owner_id": str(other.id)})

    assert r.status_code == 403
    db.refresh(item)
    assert item.owner_id == me.id


def test_transferring_a_missing_item_is_a_404(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    r = client.post(
        f"{URL}{uuid.uuid4()}/transfer", headers=superuser_token_headers, json={"owner_id": str(create_random_user(db).id)}
    )

    assert r.status_code == 404
