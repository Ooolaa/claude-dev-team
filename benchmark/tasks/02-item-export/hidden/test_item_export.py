import csv
import io
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/export"


def rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def test_export_is_a_csv_download_with_the_agreed_columns(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(URL, headers=superuser_token_headers)

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert r.headers["content-disposition"] == 'attachment; filename="items.csv"'
    assert next(csv.reader(io.StringIO(r.text))) == ["id", "title", "description", "created_at"]


def test_export_has_every_own_item_and_no_one_elses(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    t = uuid.uuid4().hex[:12]
    me = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
    assert me is not None
    mine = [
        crud.create_item(session=db, item_in=ItemCreate(title=f"{t} {n}", description="a, \"quoted\"\nline"), owner_id=me.id)
        for n in range(120)
    ]
    bare = crud.create_item(session=db, item_in=ItemCreate(title=f"{t} bare"), owner_id=me.id)
    crud.create_item(session=db, item_in=ItemCreate(title=f"{t} theirs"), owner_id=create_random_user(db).id)

    r = client.get(URL, headers=normal_user_token_headers)

    assert r.status_code == 200
    exported = {row["id"]: row for row in rows(r.text) if row["title"].startswith(t)}
    assert set(exported) == {str(i.id) for i in [*mine, bare]}
    assert exported[str(mine[0].id)]["description"] == "a, \"quoted\"\nline"
    assert exported[str(bare.id)]["description"] == ""
    assert exported[str(bare.id)]["created_at"]


def test_superuser_export_includes_other_users_items(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    t = uuid.uuid4().hex[:12]
    item = crud.create_item(session=db, item_in=ItemCreate(title=t), owner_id=create_random_user(db).id)

    r = client.get(URL, headers=superuser_token_headers)

    assert r.status_code == 200
    assert str(item.id) in {row["id"] for row in rows(r.text)}
