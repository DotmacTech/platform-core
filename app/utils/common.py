import json
from datetime import datetime
from typing import Any, Optional


def serialize_datetime(obj: Any) -> Any:
    """
    Serialize datetime objects to ISO format strings.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def json_dumps(obj: Any) -> str:
    """
    Serialize object to JSON string, handling datetime objects.
    """
    return json.dumps(obj, default=serialize_datetime)


def json_serializer(obj: Any) -> Any:
    """
    JSON serializer for objects not serializable by default json code.
    Used for Redis and other serialization needs.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def safe_parse_json(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string, returning default value if parsing fails.
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def get_client_ip(request) -> str:
    """
    Extract client IP address from request.
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # Get the client's IP (first in the list)
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse a datetime string into a datetime object.
    Supports ISO format and common date formats.
    Returns None if the input is None or invalid.
    """
    if not date_str:
        return None
    
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None
