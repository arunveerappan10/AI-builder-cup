"""CatSight API — API-1..5.

The browser calls this service directly on its `*.run.app` URL with CORS
(C-10). It is deliberately **not** behind a Firebase Hosting rewrite: that
path has a 60-second timeout and does not stream, and an analysis streams for
longer than that.

What is implemented here is the deterministic spine - the catalogue, the
treaties, and an analysis whose numbers come from the loss engine. No model
calls. The agent graph adds explanation and wording flags on top, emitting
more frames between the same SSE bookends, so the frontend contract does not
change when it lands.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.analysis import (
    EventNotFound,
    analyse,
    available_events,
    stream_analysis,
)
from app.config import Settings, settings
from ingest.seed_portfolio import build_portfolio

__all__ = ["app", "create_app"]

API_VERSION = "0.5.0-s4-spine"


class AnalysisRequest(BaseModel):
    """API-4's body. FR-GUARD: validated, with the query length bounded."""

    mode: str = Field(default="replay", pattern="^(replay|live)$")
    event_id: str | None = Field(default=None, max_length=64)
    event_query: str | None = Field(default=None, max_length=300)
    #: FR-MATCH: replay defaults to as-if, a historical event on the current
    #: book. `False` applies the treaty period test instead.
    as_if: bool = True


class _RateLimiter:
    """FR-GUARD's per-IP hourly limit and the global daily cap.

    In-process and therefore per-instance, which is honest about what it is: a
    cost guard against a popular link, not a security control. Cloud Run runs
    at most 3 instances (C-12), so the effective ceiling is 3x the configured
    limit - stated here rather than discovered from a bill.
    """

    def __init__(self, per_hour: int, daily_cap: int) -> None:
        self.per_hour = per_hour
        self.daily_cap = daily_cap
        self._by_ip: dict[str, deque[float]] = {}
        self._day: deque[float] = deque()

    def check(self, ip: str, *, now: float | None = None) -> tuple[bool, str]:
        now = now if now is not None else time.time()

        while self._day and now - self._day[0] > 86_400:
            self._day.popleft()
        if len(self._day) >= self.daily_cap:
            return False, (
                "The daily analysis cap has been reached. Cached replays are "
                "still available, and the cap resets 24 hours after the first "
                "run of the day."
            )

        seen = self._by_ip.setdefault(ip, deque())
        while seen and now - seen[0] > 3_600:
            seen.popleft()
        if len(seen) >= self.per_hour:
            wait = int((3_600 - (now - seen[0])) // 60) + 1
            return False, (
                f"You have run {self.per_hour} analyses in the last hour. "
                f"Try again in about {wait} minute(s), or open a cached replay."
            )

        seen.append(now)
        self._day.append(now)
        return True, ""


def create_app(config: Settings | None = None) -> FastAPI:
    config = config if config is not None else settings
    api = FastAPI(
        title="CatSight API",
        version=API_VERSION,
        description=(
            "Treaty-level catastrophe impact with a machine-verified citation "
            "for every wording claim."
        ),
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Admin-Token"],
    )

    limiter = _RateLimiter(config.rate_limit_per_hour, config.daily_analysis_cap)
    api.state.config = config
    api.state.limiter = limiter
    # Built once: 24 treaties and 592 exposures are deterministic, and
    # rebuilding them per request would dominate the response time.
    api.state.portfolio = None

    def portfolio():
        if api.state.portfolio is None:
            api.state.portfolio = build_portfolio()
        return api.state.portfolio

    # ----------------------------------------------------------------- API-1 #

    @api.get("/healthz")
    def healthz() -> dict[str, Any]:
        """Liveness plus enough configuration to diagnose a bad deploy.

        Answers even when the project is unset: "up but unconfigured" is a
        far more useful signal than a service that refuses to boot.
        """
        return {
            "status": "ok",
            "version": API_VERSION,
            "build": config.build_label,
            "configured": config.configured,
            "models": {
                "main": config.model_main,
                "reason": config.model_reason,
                "embed": config.embed_model,
                "embed_dim": config.embed_dim,
            },
            "location": config.location,
            "features": {
                "courtroom": config.courtroom_enabled,
                "cached_replay_only": config.cached_replay_only,
            },
            "warnings": list(config.warnings),
        }

    # ----------------------------------------------------------------- API-2 #

    @api.get("/api/events")
    def events() -> dict[str, Any]:
        return {"events": available_events(config.data_dir)}

    # ----------------------------------------------------------------- API-3 #

    @api.get("/api/treaties")
    def treaties() -> dict[str, Any]:
        book = portfolio()
        names = {c.cedent_id: c.name for c in book.cedents}
        return {
            "treaties": [
                {
                    "treaty_id": t.treaty_id,
                    "cedent_id": t.cedent_id,
                    "cedent": names.get(t.cedent_id, t.cedent_id),
                    "type": t.type,
                    "perils": list(t.perils),
                    "territory": {
                        "include": list(t.territory.get("include", ())),
                        "exclude": list(t.territory.get("exclude", ())),
                    },
                    "inception": t.inception,
                    "expiry": t.expiry,
                    "currency": t.currency,
                    "hours_clause": dict(t.hours_clause),
                    "layers": len(t.layers),
                    "has_wording": bool(t.wording_id),
                    "wording_id": t.wording_id,
                }
                for t in book.treaties
            ]
        }

    @api.get("/api/treaties/{treaty_id}")
    def treaty_detail(treaty_id: str) -> dict[str, Any]:
        book = portfolio()
        try:
            found = book.treaty(treaty_id)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"no treaty {treaty_id}")
        return {
            "treaty_id": found.treaty_id,
            "cedent": book.cedent(found.cedent_id).name,
            "type": found.type,
            "perils": list(found.perils),
            "territory": {
                "include": list(found.territory.get("include", ())),
                "exclude": list(found.territory.get("exclude", ())),
            },
            "inception": found.inception,
            "expiry": found.expiry,
            "currency": found.currency,
            "hours_clause": dict(found.hours_clause),
            "exclusions": list(found.exclusions),
            "layers": [
                {
                    "layer_no": layer.layer_no,
                    "retention": layer.retention,
                    "limit": layer.limit,
                    "premium": layer.premium,
                    "our_share": layer.our_share,
                    "reinstatements": dict(layer.reinstatements),
                }
                for layer in found.layers
            ],
            "qs": dict(found.qs) if found.qs else None,
            "wording_id": found.wording_id,
            "endorsement": found.endorsement,
            "extraction": found.extraction,
        }

    # ----------------------------------------------------------------- API-4 #

    @api.post("/api/analyses")
    def create_analysis(body: AnalysisRequest, request: Request) -> StreamingResponse:
        """SSE stream. The client uses `fetch()` with a ReadableStream, not
        `EventSource`, because EventSource cannot POST."""
        if body.mode == "live":
            raise HTTPException(
                status_code=501,
                detail=(
                    "Live mode is not implemented yet. Pick a replay event "
                    "from GET /api/events."
                ),
            )
        event_id = body.event_id or "jebi-2018"

        client_ip = request.client.host if request.client else "unknown"
        allowed, message = api.state.limiter.check(client_ip)
        if not allowed:
            # FR-GUARD-5: never a bare 429. Say what happened and what to do.
            raise HTTPException(
                status_code=429,
                detail={"message": message, "cached_available": True},
            )

        return StreamingResponse(
            stream_analysis(
                event_id,
                portfolio=portfolio(),
                data_dir=config.data_dir,
                as_if=body.as_if,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                # Cloud Run buffers responses without this, which turns a
                # stream into one block at the end and defeats the point.
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    # ----------------------------------------------------------------- API-5 #

    @api.get("/api/analyses/{analysis_id}")
    def get_analysis(analysis_id: str) -> dict[str, Any]:
        """The full analysis document.

        A replay analysis is addressable as `replay-{event_id}` and is
        **recomputed rather than stored**: the deterministic pipeline returns
        the same figures every time, so persistence would add a cache to
        invalidate for no gain. That stops being true once the agents add
        prose and an analyst can record a Courtroom position, which is when
        this reads from Firestore instead.
        """
        prefix = "replay-"
        if not analysis_id.startswith(prefix):
            raise HTTPException(
                status_code=404,
                detail="only replay analyses exist so far, as replay-{event_id}",
            )
        event_id = analysis_id[len(prefix) :]
        try:
            result = analyse(
                event_id, portfolio=portfolio(), data_dir=config.data_dir
            )
        except EventNotFound:
            raise HTTPException(status_code=404, detail=f"no event {event_id}")
        return {"analysis_id": analysis_id, **result.to_json()}

    return api


app = create_app()
