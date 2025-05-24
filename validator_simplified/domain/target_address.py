class TargetAddress:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
    
    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"
    
    def __str__(self) -> str:
        return self.url 