Let users mark items as done.

Backend: items get a `done` flag. It can be set when creating an item (`POST /api/v1/items/`) and changed with the existing update (`PUT /api/v1/items/{id}`), and every endpoint that returns an item includes it. Add a database migration for the new column.

Frontend: on the Items page, add a checkbox to each row of the table so users can tick an item done, or untick it, without opening the edit dialog. Show the titles of done items struck through and dimmed. Keep it consistent with the rest of the app.
