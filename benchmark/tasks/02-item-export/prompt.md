Let users download their items as a CSV file.

Add `GET /api/v1/items/export`. It returns the same items the items list would show the caller (normal users only their own, superusers all of them), every one of them with no paging, as CSV with a header row and the columns `id`, `title`, `description`, `created_at`. An item with no description gets an empty cell. Send it as `text/csv` with `Content-Disposition: attachment; filename="items.csv"` so the browser downloads it.

Most of our users open the file in Excel or Google Sheets.
