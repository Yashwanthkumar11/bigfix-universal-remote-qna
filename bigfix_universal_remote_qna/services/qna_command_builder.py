from bigfix_universal_remote_qna.models.os_type import OSType


class QnACommandBuilder:
    """Builds QnA commands for different operating systems"""
    
    @staticmethod
    def build_command(query: str, qna_path: str, os_type: str) -> str:
        """Build QnA command based on OS type"""
        if os_type == OSType.WINDOWS.value:
            escaped_query = query.replace('"', '\\"')
            return f'echo {escaped_query} | "{qna_path}"'
        else:
            escaped_query = query.replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
            return f'echo "{escaped_query}" | "{qna_path}"'
