from fastapi import Depends, Request, HTTPException, status
from typing import Annotated, Sequence
from cryptography.x509.oid import ExtensionOID, NameOID

from typing import TYPE_CHECKING

from pydantic import BaseModel
if TYPE_CHECKING:
    from cryptography.x509 import Certificate


def cert(request: Request) -> "Certificate":
    if (certificate := request.scope["ClientCertificate"]) is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Client did not provide a valid certificate")
    return certificate

def certCN(cert: Annotated["Certificate", Depends(cert)]) -> str:
    matches = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if len(matches) == 0:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, "Client Certificate Subject has no attribute CommonName")
    if len(matches) != 1:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, "Client Certificate Subject has multiple attributes CommonName")
    return str(matches[0].value)

def certSANs(cert: Annotated["Certificate", Depends(cert)]) -> Sequence[str]:
    return [ str(attribute.value) for attribute in cert.subject.get_attributes_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME) ]

class Names(BaseModel):
    CN: str
    SANs: Sequence[str]

def clientCertSubjectNames(CN: Annotated[str, Depends(certCN)],
                           SANs: Annotated[Sequence[str], Depends(certSANs)]) -> Names:
    return Names(CN=CN, SANs=SANs)
    