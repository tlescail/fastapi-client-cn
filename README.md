# fastapi client cn

## ClientCnMiddleware

Injects the CommonName of the client's certificate inside the request's scope.

##### Example:

```python
from fastapi import FastAPI, Request
from fastapi_client_cn import ClientCnMiddleware

app = FastAPI()

app.add_middleware(ClientCnMiddleware)

@app.get('/')
async def test(request: Request):
    return request.scope['client_cn']
```