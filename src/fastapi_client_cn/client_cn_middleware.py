from uvicorn.protocols.http.httptools_impl import HttpToolsProtocol
from typing import TYPE_CHECKING, Optional, Tuple, TypeAlias, Union, Dict


if TYPE_CHECKING:
    from asyncio import Transport
    from starlette.types import (
        ASGIApp,
        Scope,
        Receive,
        Send,
    )
    from ssl import SSLSocket
    _PCTRTT: TypeAlias = Tuple[Tuple[str, str], ...]
    _PCTRTTT: TypeAlias = Tuple[_PCTRTT, ...]
    _PeerCertValueType: TypeAlias = Union[str, _PCTRTTT, _PCTRTT]
    _PeerCertRetDictType: TypeAlias = Dict[str, _PeerCertValueType]

on_url_orig = HttpToolsProtocol.on_url

def on_url(self: HttpToolsProtocol, url: bytes):
    on_url_orig(self, url)
    self.scope['transport'] = self.transport # type: ignore

HttpToolsProtocol.on_url = on_url

class ClientCnMiddleware:

    def __init__(self, app: "ASGIApp"):
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope['type'] in ['http', 'websocket']:
            self._inject_cn(scope)
        return await self.app(scope, receive, send)

    def _inject_cn(self, scope: "Scope") -> None:
        scope['commonName'] = self._commonName(scope)

    def _commonName(self, scope: "Scope") -> Optional[str]:
        if (subject := self._subject(scope)) is None:
            return None
        if isinstance(subject, str):
            return None
        for item in [ entry[0] for entry in subject ]:
            if isinstance(item, str):
                continue
            if item[0] == 'commonName':
                return item[1]

    def _subject(self, scope: "Scope") -> Optional["_PeerCertValueType"]:
        if (perrcert := self._peercert(scope)) is None:
            return None
        return perrcert.get('subject')
    
    def _peercert(self, scope: "Scope") -> Optional["_PeerCertRetDictType"]:
        if (ssl_object := self._ssl_object(scope)) is None:
            return None
        return ssl_object.getpeercert()
        
    def _ssl_object(self, scope: "Scope") -> Optional["SSLSocket"]:
        if (transport := self._transport(scope)) is None:
            return None
        return transport.get_extra_info('ssl_object')
    
    def _transport(self, scope: "Scope") -> Optional["Transport"]:
        return scope['transport']