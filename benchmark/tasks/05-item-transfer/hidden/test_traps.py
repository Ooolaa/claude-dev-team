import re
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.main import app
from app.models import ItemCreate
from tests.utils.user import create_random_user

URL = f"{settings.API_V1_STR}/items/"

# Every endpoint in the pinned template, outside the dev-only /private routes; path parameter names ignored.
TEMPLATE_ENDPOINTS = {
    ("get", "/items/"), ("post", "/items/"),
    ("get", "/items/{}"), ("put", "/items/{}"), ("delete", "/items/{}"),
    ("post", "/login/access-token"), ("post", "/login/test-token"),
    ("post", "/password-recovery/{}"), ("post", "/reset-password/"),
    ("post", "/password-recovery-html-content/{}"),
    ("get", "/users/"), ("post", "/users/"),
    ("get", "/users/me"), ("patch", "/users/me"), ("delete", "/users/me"),
    ("patch", "/users/me/password"), ("post", "/users/signup"),
    ("get", "/users/{}"), ("patch", "/users/{}"), ("delete", "/users/{}"),
    ("post", "/utils/test-email/"), ("get", "/utils/health-check/"),
}


def test_unknown_owner_is_a_client_error(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Trap: unvalidated input. An owner_id that matches no user violates the foreign key: a 500 if unchecked.
    owner = create_random_user(db)
    item = crud.create_item(session=db, item_in=ItemCreate(title="t"), owner_id=owner.id)

    r = client.post(f"{URL}{item.id}/transfer", headers=superuser_token_headers, json={"owner_id": str(uuid.uuid4())})

    assert 400 <= r.status_code < 500, r.status_code
    db.refresh(item)
    assert item.owner_id == owner.id


def test_only_the_transfer_endpoint_is_new() -> None:
    # Trap: scope-creep bait. Moving all of a user's items at once is the next ticket.
    endpoints = {
        (method, re.sub(r"\{[^}]*\}", "{}", path.removeprefix(settings.API_V1_STR)))
        for path, ops in app.openapi()["paths"].items()
        for method in ops
        if not path.startswith(f"{settings.API_V1_STR}/private/")
    }
    assert endpoints - TEMPLATE_ENDPOINTS == {("post", "/items/{}/transfer")}
