import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/"


# Whether done defaults to false is left to the broken-caller Trap, so these tests always send it.
def test_done_can_be_set_on_create(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    for done in (True, False):
        r = client.post(URL, headers=superuser_token_headers, json={"title": "t", "done": done})
        assert r.status_code == 200 and r.json()["done"] is done


def test_update_toggles_done_and_keeps_other_fields(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    item = client.post(URL, headers=superuser_token_headers, json={"title": "t", "description": "d", "done": False}).json()

    on = client.put(f"{URL}{item['id']}", headers=superuser_token_headers, json={"done": True})
    assert on.status_code == 200
    assert (on.json()["done"], on.json()["title"], on.json()["description"]) == (True, "t", "d")

    # An update that doesn't mention done leaves it alone.
    renamed = client.put(f"{URL}{item['id']}", headers=superuser_token_headers, json={"title": "t2"})
    assert renamed.json()["done"] is True

    off = client.put(f"{URL}{item['id']}", headers=superuser_token_headers, json={"done": False})
    assert off.json()["done"] is False


def test_list_and_read_include_done(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    t = uuid.uuid4().hex[:12]
    item = crud.create_item(session=db, item_in=ItemCreate(title=t, done=True), owner_id=create_random_user(db).id)

    one = client.get(f"{URL}{item.id}", headers=superuser_token_headers)
    listed = client.get(URL, headers=superuser_token_headers, params={"limit": 1000})

    assert one.json()["done"] is True
    assert [i["done"] for i in listed.json()["data"] if i["id"] == str(item.id)] == [True]


def test_normal_user_cannot_mark_someone_elses_item_done(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = crud.create_item(session=db, item_in=ItemCreate(title="theirs", done=False), owner_id=create_random_user(db).id)

    r = client.put(f"{URL}{item.id}", headers=normal_user_token_headers, json={"done": True})

    assert r.status_code == 403
    db.refresh(item)
    assert item.done is False
