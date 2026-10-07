Let superusers hand an item over to another user.

Add `POST /api/v1/items/{id}/transfer` with a JSON body `{"owner_id": "<user id>"}`. It makes that user the item's owner and returns the updated item the way the other item endpoints do. Only superusers may transfer items; anyone else gets a 403, even for their own items. A missing item is a 404.

When someone leaves the team we'll also want to move all of their items to another user in one go, but that's the next ticket.
