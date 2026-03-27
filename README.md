# ClientCertificateMiddleware

Injects the x509 Certificate of the client inside the request's scope.
Provides dependables to access parts of said certificate.

##### Example:

```python
from fastapi import FastAPI, Depends
from typing import Annotated
from client_certificate_middleware import ClientCertificateMiddleware, clientCertificateSubjectCN

app = FastAPI()

app.add_middleware(ClientCertificateMiddleware)

@app.get('/cn')
async def cn(cn: Annotated[str, Depends(clientCertificateSubjectCN)]):
    return cn
```