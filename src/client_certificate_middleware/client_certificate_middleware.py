from uvicorn.protocols.http.httptools_impl import HttpToolsProtocol as HttpToolsProtocol
from typing import (
    TYPE_CHECKING,
    Optional as Optional,
)
from cryptography.x509 import load_der_x509_certificate as load_der_x509_certificate

if TYPE_CHECKING:
    from asyncio import Transport as Transport
    from cryptography.x509 import Certificate as Certificate
    from starlette.types import (
        ASGIApp as ASGIApp,
        Scope as Scope,
        Receive as Receive,
        Send as Send,
    )
    from ssl import SSLSocket as SSLSocket

on_url_orig = HttpToolsProtocol.on_url

def on_url(self: HttpToolsProtocol, url: bytes):
    on_url_orig(self, url)
    self.scope['state']['transport'] = self.transport # pyright: ignore[reportTypedDictNotRequiredAccess]

HttpToolsProtocol.on_url = on_url

class ClientCertificateMiddleware:

    def __init__(self, app: "ASGIApp"):
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope['type'] in ['http', 'websocket']:
            scope['ClientCertificate'] = self.__getCertificate(scope)
        return await self.app(scope, receive, send)

    def __getCertificate(self, scope: "Scope") -> Optional["Certificate"]:
        if (peercert := self.__getpeercert(scope)) is None:
            return None
        return load_der_x509_certificate(peercert)

    def __getpeercert(self, scope: "Scope") -> Optional[bytes]:
        if (ssl_socket := self.__getSSLSocket(scope)) is None:
            return None
        try:
            return ssl_socket.getpeercert(True)
        except ValueError:
            return None
        
    def __getSSLSocket(self, scope: "Scope") -> Optional["SSLSocket"]:
        if (transport := self.__gettransport(scope)) is None:
            return None
        return transport.get_extra_info('ssl_object')
    
    def __gettransport(self, scope: "Scope") -> Optional["Transport"]:
        return scope['state']['transport']
