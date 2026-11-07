"""API client for Deal Intelligence Agent frontend.

Single source of truth for all backend communications conforming to CONTRACT.md:
- GET  /health
- GET  /deals
- POST /deals
- POST /deals/{id}/calls
- GET  /deals/{id}/brief?memory=on|off
- POST /deals/{id}/followup
- POST /deals/{id}/outcome
- GET  /playbook/insights
- POST /admin/seed

Never calls Hindsight or LLMs directly; strictly consumes backend REST endpoints.
Includes robust error handling for network outages, timeouts, and HTTP errors.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import requests

# Load environment configuration from frontend/.env if present
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")
DEFAULT_TIMEOUT = 15  # seconds


class DealAgentAPIException(Exception):
    """Base exception for backend API errors with user-friendly messages."""

    def __init__(self, message: str, status_code: Optional[int] = None, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail

    def __str__(self) -> str:
        if self.detail:
            return f"{self.message}: {self.detail}"
        return self.message


class BackendConnectionError(DealAgentAPIException):
    """Raised when the backend cannot be reached (e.g., server offline)."""
    pass


class BackendAPIError(DealAgentAPIException):
    """Raised when the backend returns a non-2xx HTTP status code."""
    pass


def _request(method: str, path: str, **kwargs) -> Any:
    """Execute an HTTP request against API_BASE with centralized error handling."""
    url = f"{API_BASE}{path}"
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)

    try:
        response = requests.request(method, url, **kwargs)
    except requests.exceptions.ConnectionError:
        raise BackendConnectionError(
            f"Cannot connect to backend server at {API_BASE}. Please verify that the backend is running."
        )
    except requests.exceptions.Timeout:
        raise BackendConnectionError(
            f"Request to backend timed out after {kwargs.get('timeout')} seconds."
        )
    except requests.exceptions.RequestException as exc:
        raise BackendConnectionError(f"Network error communicating with backend: {str(exc)}")

    if not response.ok:
        detail = None
        try:
            err_json = response.json()
            detail = err_json.get("detail") or err_json.get("message") or response.text
        except Exception:
            detail = response.text or response.reason

        raise BackendAPIError(
            message=f"Backend returned HTTP {response.status_code}",
            status_code=response.status_code,
            detail=detail,
        )

    try:
        return response.json()
    except Exception:
        return response.text


def check_health() -> bool:
    """Check backend service health (GET /health).

    Returns True if healthy, False if down or unreachable.
    """
    try:
        data = _request("GET", "/health", timeout=3)
        return isinstance(data, dict) and data.get("ok") is True
    except Exception:
        return False


def get_deals() -> List[Dict[str, Any]]:
    """Retrieve list of all deals (GET /deals).

    Returns list of dicts: [{deal_id, company, value, stage, calls_count, outcome}]
    """
    return _request("GET", "/deals")


def create_deal(company: str, value: float) -> Dict[str, Any]:
    """Create a new sales deal (POST /deals).

    Returns dict: {"deal_id": str}
    """
    payload = {"company": company, "value": float(value)}
    return _request("POST", "/deals", json=payload)


def add_call(
    deal_id: str,
    call_no: int,
    date: str,
    participants: List[str],
    transcript: str,
) -> Dict[str, Any]:
    """Add a call transcript to a deal (POST /deals/{id}/calls).

    Returns dict: {"retained": True}
    """
    payload = {
        "call_no": int(call_no),
        "date": date,
        "participants": participants,
        "transcript": transcript,
    }
    return _request("POST", f"/deals/{deal_id}/calls", json=payload)


def get_brief(deal_id: str, memory: str = "on") -> Dict[str, Any]:
    """Generate pre-call intelligence brief for a deal (GET /deals/{id}/brief).

    memory must be 'on' or 'off'.
    Returns dict: {brief, open_objections[], stakeholders[], promises[], recalled_facts[], memory_used, playbook_tips[]}
    """
    mem_param = "on" if memory.lower() == "on" else "off"
    return _request("GET", f"/deals/{deal_id}/brief", params={"memory": mem_param})


def get_followup(deal_id: str, memory: str = "on") -> Dict[str, Any]:
    """Draft personalized follow-up email (POST /deals/{id}/followup).

    memory must be 'on' or 'off'.
    Returns dict: {"email": str}
    """
    mem_param = "on" if memory.lower() == "on" else "off"
    return _request("POST", f"/deals/{deal_id}/followup", json={"memory": mem_param})


def set_deal_outcome(
    deal_id: str,
    result: str,
    objections_handled: Optional[List[str]] = None,
    notes: Optional[str] = "",
) -> Dict[str, Any]:
    """Record won/lost deal outcome (POST /deals/{id}/outcome).

    result must be 'won' or 'lost'.
    Returns dict: {"ok": True}
    """
    payload = {
        "result": result.lower(),
        "objections_handled": objections_handled or [],
        "notes": notes or "",
    }
    return _request("POST", f"/deals/{deal_id}/outcome", json=payload)


def get_playbook_insights() -> Dict[str, Any]:
    """Retrieve global playbook insights and mental models (GET /playbook/insights).

    Returns dict: {"insights": [...], "mental_models": [...]}
    """
    return _request("GET", "/playbook/insights")


def seed_demo_data() -> Dict[str, Any]:
    """Trigger backend seed data loading (POST /admin/seed).

    Returns dict: {"deals_loaded": int, "calls_retained": int}
    """
    return _request("POST", "/admin/seed")
