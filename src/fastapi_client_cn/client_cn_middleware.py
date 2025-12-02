from uvicorn.protocols.http.httptools_impl import HttpToolsProtocol
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
from logging import getLogger


if TYPE_CHECKING:
    from asyncio import Transport
    from starlette.types import (
        ASGIApp,
        Scope,
        Receive,
        Send,
    )
    from ssl import SSLSocket

on_url_orig = HttpToolsProtocol.on_url

def on_url(self: HttpToolsProtocol, url):
    on_url_orig(self, url)
    self.scope['transport'] = self.transport

HttpToolsProtocol.on_url = on_url

class ClientCnMiddleware:

    def __init__(self, app: "ASGIApp", scope_entry: str = "client_cn"):
        self.app = app
        self.scope_entry = scope_entry

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope['type'] in ['http', 'websocket']:
            self._inject_cn(scope)
        return await self.app(scope, receive, send)

    def _inject_cn(self, scope: "Scope") -> None:
        try:
            scope[self.scope_entry] = self.get_common_name(scope)
        except Exception as e:
            getLogger(self.__class__.__qualname__).exception(e)
    
    def get_common_name(self, scope: "Scope") -> Optional[str]:
        if (subject := self.get_subject(scope)) != None:
            for item in [ item[0] for item in subject ]:
                print(item)
                if item[0] == "commonName":
                    return item[1]

    def get_subject(self, scope: "Scope") -> Optional[Tuple[Any]]:
        if (peer_cert := self.get_peer_cert(scope)) != None:
            return peer_cert.get('subject')

    def get_peer_cert(self, scope: "Scope") -> Optional[Dict[str, Any]]:
        if (ssl_socket := self.get_ssl_socket(scope)) != None:
            return ssl_socket.getpeercert(False)
        
    def get_ssl_socket(self, scope: "Scope") -> Optional["SSLSocket"]:
        if (transport := self.get_transport(scope)) != None:
            return transport.get_extra_info('ssl_object')
         
    def get_transport(self, scope: "Scope") -> Optional["Transport"]:
        return scope['transport']