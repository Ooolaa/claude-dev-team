Let users duplicate an item.

Add `POST /api/v1/items/{id}/duplicate`. It creates a new item owned by the caller, with the same description and the title `Copy of <original title>`, and returns it the way the other item endpoints do. Users can duplicate only items they could already read: normal users their own, superusers any. A missing item is a 404.

Next sprint we'll add a Duplicate button to the item menu on the Items page.
