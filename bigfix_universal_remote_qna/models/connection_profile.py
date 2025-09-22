from dataclasses import dataclass
from bigfix_universal_remote_qna.models.os_type import OSType


@dataclass
class ConnectionProfile:
    name: str
    host: str
    port: int = 22
    username: str = ""
    password: str = ""
    os: str = OSType.WINDOWS.value
    qna_path: str = ""