# ClientCertificateMiddleware

Injects the x509 Certificate of the client inside the request's scope.
Provides dependables to access parts of said certificate.

##### Example:

```python
from fastapi import FastAPI, Depends
from typing import Annotated
from client_certificate_middleware import ClientCertificateMiddleware
from client_certificate_middleware.dependency import certCN

app = FastAPI()

# add the middleware
app.add_middleware(ClientCertificateMiddleware)

# use depedables
@app.get('/cn')
async def cn(cn: Annotated[str, Depends(certCN)]) -> str:
    return cn
```