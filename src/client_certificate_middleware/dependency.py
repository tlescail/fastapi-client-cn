from fastapi import (
    Depends as Depends,
    Request as Request,
)
from typing import (
    Annotated as Annotated,
    Optional as Optional,
)
from ssl import SSLCertVerificationError as SSLCertVerificationError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cryptography.x509 import (
        Certificate as Certificate,
        Name as Name,
    )


def clientCertificate(request: Request) -> "Certificate":
    certificate: Optional["Certificate"] = request.scope["ClientCertificate"]
    if certificate is None:
        raise SSLCertVerificationError()
    return certificate

def clientCertificateSubject(certificate: Annotated["Certificate", Depends(clientCertificate)]) -> "Name":
    return certificate.subject

def clientCertificateSubjectCN(subject: Annotated["Name", Depends(clientCertificateSubject)]) -> str:
    for attribute in subject: # pyright: ignore[reportUnknownVariableType]
        if attribute.rfc4514_attribute_name == 'CN':
            return attribute.value # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    raise KeyError('CN undefined in Certificate Subject')