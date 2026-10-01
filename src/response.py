from dataclasses import dataclass, field

@dataclass
class Response:
    body: str = ""
    status: int = 200
    content_type: str = "text/html; charset=utf-8"
    location: str | None = None      
    headers: dict = field(default_factory=dict)

    @classmethod
    def html(cls, page: str, status: int = 200) -> Response:
        return cls(body=page, status=status)
    
    @classmethod
    def redirect(cls, location: str) -> Response: 
        return cls(status=302, location=location, headers={"Location": location}) 