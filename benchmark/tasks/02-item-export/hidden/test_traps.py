import csv
import io
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import ItemCreate

URL = f"{settings.API_V1_STR}/items/export"


def test_formula_cells_are_neutralised(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    # Trap: unvalidated input. A cell starting with = + - @ runs as a formula in Excel and Sheets.
    t = uuid.uuid4().hex[:8]
    me = crud.get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
    assert me is not None
    payloads = [f'=HYPERLINK("http://x.test/{t}")', f"+{t}+1", f"-{t}+1", f"@SUM({t})"]
    for p in payloads:
        crud.create_item(session=db, item_in=ItemCreate(title=p, description=p), owner_id=me.id)

    r = client.get(URL, headers=normal_user_token_headers)

    assert r.status_code == 200
    cells = [c for row in csv.DictReader(io.StringIO(r.text)) for c in (row["title"], row["description"]) if t in c]
    assert len(cells) == 2 * len(payloads)
    for cell in cells:
        assert cell[0] not in "=+-@", cell
        assert any(p in cell for p in payloads), cell
