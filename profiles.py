"""
Simple JSON-file store for user profiles and watchlist tickers.
Each profile has: id, name, tickers (list of symbols to track).
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

_STORE_PATH = Path(__file__).resolve().parent / "data" / "profiles.json"


def _ensure_store() -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _STORE_PATH.exists():
        _STORE_PATH.write_text("[]", encoding="utf-8")


def _load() -> list[dict[str, Any]]:
    _ensure_store()
    raw = _STORE_PATH.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def _save(profiles: list[dict[str, Any]]) -> None:
    _ensure_store()
    _STORE_PATH.write_text(json.dumps(profiles, indent=2), encoding="utf-8")


def list_profiles() -> list[dict[str, Any]]:
    """Return all profiles (id, name, tickers)."""
    data = _load()
    return [{"id": p["id"], "name": p["name"], "tickers": p.get("tickers", [])} for p in data]


def get_profile(profile_id: str) -> dict[str, Any] | None:
    """Return a single profile by id or None."""
    for p in _load():
        if p.get("id") == profile_id:
            return {"id": p["id"], "name": p["name"], "tickers": p.get("tickers", [])}
    return None


def create_profile(name: str) -> dict[str, Any]:
    """Create a new profile with empty watchlist. Returns the new profile."""
    name = (name or "").strip() or "Unnamed profile"
    profiles = _load()
    profile = {"id": str(uuid.uuid4()), "name": name, "tickers": []}
    profiles.append(profile)
    _save(profiles)
    return {"id": profile["id"], "name": profile["name"], "tickers": profile["tickers"]}


def update_profile_tickers(
    profile_id: str,
    add_tickers: list[str] | None = None,
    remove_tickers: list[str] | None = None,
) -> dict[str, Any] | None:
    """Add and/or remove tickers from a profile. Returns updated profile or None if not found."""
    add_tickers = add_tickers or []
    remove_tickers = remove_tickers or []
    profiles = _load()
    for p in profiles:
        if p.get("id") != profile_id:
            continue
        tickers: list[str] = list(p.get("tickers", []))
        for t in add_tickers:
            t = (t or "").strip().upper()
            if t and t not in tickers:
                tickers.append(t)
        for t in remove_tickers:
            t = (t or "").strip().upper()
            if t in tickers:
                tickers.remove(t)
        p["tickers"] = tickers
        _save(profiles)
        return {"id": p["id"], "name": p["name"], "tickers": p["tickers"]}
    return None


def delete_profile(profile_id: str) -> bool:
    """Remove a profile. Returns True if deleted."""
    profiles = _load()
    for i, p in enumerate(profiles):
        if p.get("id") == profile_id:
            profiles.pop(i)
            _save(profiles)
            return True
    return False
