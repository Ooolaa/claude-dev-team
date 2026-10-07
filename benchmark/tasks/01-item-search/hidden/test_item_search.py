import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/"


def make_item(db: Session, title: str, owner_id: uuid.UUID) -> None:
    crud.create_item(session=db, item_in=ItemCreate(title=title), owner_id=owner_id)


def token() -> str:
    return uuid.uuid4().hex[:12]


def test_search_matches_title_ignoring_case(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    t = token()
    owner = create_random_user(db)
    make_item(db, f"Red {t} lamp", owner.id)
    make_item(db, f"blue {t.upper()} chair", owner.id)
    make_item(db, "unrelated", owner.id)

    r = client.get(URL, headers=superuser_token_headers, params={"q": t.upper()})

    assert r.status_code == 200
    titles = sorted(i["title"] for i in r.json()["data"])
    assert titles == sorted([f"Red {t} lamp", f"blue {t.upper()} chair"])
    assert r.json()["count"] == 2


def test_search_count_is_total_matches_not_page_size(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    t = token()
    owner = create_random_user(db)
    for n in range(3):
        make_item(db, f"{t} {n}", owner.id)

    r = client.get(URL, headers=superuser_token_headers, params={"q": t, "limit": 2})

    assert r.status_code == 200
    assert len(r.json()["data"]) == 2
    assert r.json()["count"] == 3


def test_search_keeps_normal_users_to_their_own_items(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    t = token()
    me = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
    assert me is not None
    make_item(db, f"mine {t}", me.id)
    make_item(db, f"theirs {t}", create_random_user(db).id)

    r = client.get(URL, headers=normal_user_token_headers, params={"q": t})

    assert r.status_code == 200
    assert [i["title"] for i in r.json()["data"]] == [f"mine {t}"]
    assert r.json()["count"] == 1
