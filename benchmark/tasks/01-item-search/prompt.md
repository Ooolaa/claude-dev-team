Add search to the items list endpoint.

`GET /api/v1/items/?q=<text>` should return only the items whose title contains `<text>`, ignoring case. Everything else about the endpoint stays as it is: normal users still see only their own items, superusers see all items, and `skip` and `limit` still page the results. `count` should be the total number of matching items, not just the ones on the current page. When `q` is left out, the endpoint behaves exactly as it does today.

We'll probably want the same kind of search on the users list later.
