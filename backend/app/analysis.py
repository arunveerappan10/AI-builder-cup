"""The analysis pipeline — FR-MATCH and FR-LOSS, end to end, deterministically.

This is the spine of an analysis: an event, the treaties it touches, and what
each one pays. It is built entirely on tested modules - `hazard`,
`vulnerability`, `loss_engine`, `seed_portfolio` - and **makes no model calls
at all.**

That is a deliberate ordering choice, not a shortcut. The numbers are the part
a reinsurer would be fired for getting wrong, and they come from arithmetic
that a judge can re-derive. The agents add explanation, wording flags and the
Courtroom *on top of* this; they never produce a figure. So this layer must
work, be deployable and be demonstrable before any agent exists - and once it
does, a quota failure degrades the demo's prose rather than its answer.

## Matching is conservative (FR-MATCH)

A treaty responds when **all** of these hold:

  * the event's peril is a covered peril;
  * at least one affected region is inside the territory - by country code,
    with region-level exclusions subtracted (W3's Okinawa carve-out);
  * and **only when `as_if=False`**, the event falls inside the treaty period.

## As-if is the default, and it is not a shortcut

Replay mode defaults to `as_if=True`: a historical event applied to the book
in force today. That is standard practice - the question a reinsurer asks is
"what would Jebi cost us on this year's portfolio", not "what did it cost the
2018 portfolio", which is already settled and paid.

It also has to be the default here for the demo to say anything at all: the
replay events are 2013-2024 and the synthetic book runs 2025-2027, so a
literal period test excludes all 24 treaties. Running with `as_if=False`
exercises the period rule instead, and the book carries one deliberately
expired treaty so that path has something to exclude. The UI must show which
mode produced a figure (UI-9); an as-if number presented as a historical one
would be misleading.

Anything unmatched is reported with a reason rather than silently dropped. An
analyst's first question about a programme that did not respond is "why not",
and "it was not in the list" is not an answer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from catsight_agent.tools.loss_engine import (
    CatXLResult,
    ExposureSlice,
    Layer,
    QuotaShare,
    QuotaShareResult,
    apply_cat_xl,
    apply_quota_share,
    gross_loss,
    quantise,
)
from catsight_agent.tools.vulnerability import VulnerabilityModel
from ingest.seed_portfolio import Portfolio, Treaty, build_portfolio

__all__ = [
    "EventNotFound",
    "MatchDecision",
    "TreatyOutcome",
    "AnalysisResult",
    "available_events",
    "load_event",
    "match_treaties",
    "analyse",
    "stream_analysis",
]


class EventNotFound(LookupError):
    """No replay fixture for that event id."""


# --------------------------------------------------------------------------- #
# Events
# --------------------------------------------------------------------------- #


def _events_dir(data_dir: Path | str = "data") -> Path:
    return Path(data_dir) / "events"


def available_events(data_dir: Path | str = "data") -> list[dict[str, Any]]:
    """API-2's replay catalogue. Sorted by date, newest last."""
    catalogue = []
    for path in sorted(_events_dir(data_dir).glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        countries = sorted({r.get("country") for r in payload.get("regions", []) if r.get("country")})
        catalogue.append(
            {
                "event_id": payload["event_id"],
                "name": payload["name"],
                "peril": payload["peril"],
                "date": payload["start"][:10],
                "countries": countries,
                "duration_h": payload.get("duration_h"),
                "regions": len(payload.get("regions", [])),
            }
        )
    return sorted(catalogue, key=lambda row: row["date"])


def load_event(event_id: str, data_dir: Path | str = "data") -> dict[str, Any]:
    path = _events_dir(data_dir) / f"{event_id}.json"
    if not path.exists():
        raise EventNotFound(event_id)
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Matching
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class MatchDecision:
    """Why a treaty did or did not respond. Both cases carry a reason."""

    treaty_id: str
    cedent_id: str
    matched: bool
    reason: str
    regions: tuple[str, ...] = ()


def _event_date(event: dict[str, Any]) -> str:
    return str(event["start"])[:10]


def _affected(event: dict[str, Any]) -> list[dict[str, Any]]:
    """Regions with a non-zero intensity. A region sampled at zero is in the
    file for completeness but is not affected."""
    out = []
    for region in event.get("regions", []):
        values = (region.get("intensity") or {}).values()
        if any(float(v) > 0 for v in values):
            out.append(region)
    return out


def match_treaties(
    portfolio: Portfolio, event: dict[str, Any], *, as_if: bool = True
) -> tuple[MatchDecision, ...]:
    """FR-MATCH. One decision per treaty, matched or not, always with a reason."""
    peril = event["peril"]
    on = _event_date(event)
    affected = _affected(event)
    countries = {r.get("country") for r in affected}

    decisions: list[MatchDecision] = []
    for treaty in portfolio.treaties:
        if peril not in treaty.perils:
            decisions.append(
                MatchDecision(
                    treaty.treaty_id,
                    treaty.cedent_id,
                    False,
                    f"{peril} is not a covered peril (covers {', '.join(treaty.perils)})",
                )
            )
            continue

        if not as_if and not (treaty.inception <= on <= treaty.expiry):
            decisions.append(
                MatchDecision(
                    treaty.treaty_id,
                    treaty.cedent_id,
                    False,
                    f"event date {on} is outside the period "
                    f"{treaty.inception} to {treaty.expiry}",
                )
            )
            continue

        include = set(treaty.territory.get("include", ()))
        exclude = set(treaty.territory.get("exclude", ()))
        if not (include & countries):
            decisions.append(
                MatchDecision(
                    treaty.treaty_id,
                    treaty.cedent_id,
                    False,
                    f"no affected region in territory ({', '.join(sorted(include))})",
                )
            )
            continue

        in_scope = tuple(
            r["code"]
            for r in affected
            if r.get("country") in include and r["code"] not in exclude
        )
        if not in_scope:
            # Every affected region in the covered country is carved out - W3's
            # Okinawa exclusion is exactly this case, and it must read as a
            # territorial exclusion rather than "no exposure".
            carved = sorted(exclude & {r["code"] for r in affected})
            decisions.append(
                MatchDecision(
                    treaty.treaty_id,
                    treaty.cedent_id,
                    False,
                    f"every affected region is territorially excluded ({', '.join(carved)})",
                    (),
                )
            )
            continue

        decisions.append(
            MatchDecision(
                treaty.treaty_id,
                treaty.cedent_id,
                True,
                f"{len(in_scope)} affected region(s) in territory",
                in_scope,
            )
        )
    return tuple(decisions)


# --------------------------------------------------------------------------- #
# Pricing
# --------------------------------------------------------------------------- #


def _damage_ratios(
    event: dict[str, Any], model: VulnerabilityModel
) -> dict[str, float]:
    """Region code to damage ratio, from the event's sampled intensities."""
    peril = event["peril"]
    key = "wind_ms" if peril == "WS" else "mmi"
    ratios: dict[str, float] = {}
    for region in event.get("regions", []):
        intensity = (region.get("intensity") or {}).get(key)
        if intensity is None:
            continue
        ratios[region["code"]] = model.damage_ratio(
            float(intensity), peril, region.get("country") or "JPN"
        )
    return ratios


def _layers_of(treaty: Treaty) -> list[Layer]:
    return [
        Layer(
            layer_no=layer.layer_no,
            retention=layer.retention,
            limit=layer.limit,
            premium=layer.premium,
            our_share=layer.our_share,
            reinstatements=int(layer.reinstatements.get("count", 0)),
            reinstatement_rate=Decimal(str(layer.reinstatements.get("rate", 1.0))),
        )
        for layer in treaty.layers
    ]


@dataclass
class TreatyOutcome:
    """One treaty's result, with the inputs that produced it."""

    treaty_id: str
    cedent_id: str
    cedent_name: str
    type: str
    gross: Decimal
    regions: tuple[str, ...]
    cat_xl: CatXLResult | None = None
    quota_share: QuotaShareResult | None = None

    @property
    def our_net(self) -> Decimal:
        if self.cat_xl is not None:
            return self.cat_xl.our_net
        if self.quota_share is not None:
            # No reinstatement premium on a proportional treaty, so net is loss.
            return self.quota_share.our_loss
        return Decimal(0)

    @property
    def ceded(self) -> Decimal:
        if self.cat_xl is not None:
            return self.cat_xl.total_ceded
        if self.quota_share is not None:
            return self.quota_share.ceded
        return Decimal(0)

    def to_json(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "treaty_id": self.treaty_id,
            "cedent_id": self.cedent_id,
            "cedent": self.cedent_name,
            "type": self.type,
            "gross": str(quantise(self.gross)),
            "regions": list(self.regions),
            "our_net": str(quantise(self.our_net)),
            "ceded": str(quantise(self.ceded)),
        }
        if self.cat_xl is not None:
            payload["layers"] = [
                {
                    "layer_no": lr.layer_no,
                    "ceded": str(quantise(lr.ceded)),
                    "our_loss": str(quantise(lr.our_loss)),
                    "our_rip": str(quantise(lr.our_rip)),
                    # The engine's own verdicts, not recomputed here. `burn`
                    # exceeds 1 when reinstatements are used, which is the
                    # layer chart's whole point (UI-4).
                    "burn": str(quantise(lr.burn, 4)),
                    "exhausted": lr.exhausted,
                    "reinstated": str(quantise(lr.reinstated)),
                }
                for lr in self.cat_xl.layers
            ]
            payload["cedent_retention"] = str(quantise(self.cat_xl.cedent_retention))
            payload["our_rip"] = str(quantise(self.cat_xl.our_rip))
            payload["market_net"] = str(quantise(self.cat_xl.market_net))
        if self.quota_share is not None:
            payload["capped"] = self.quota_share.capped
        return payload


@dataclass
class AnalysisResult:
    event: dict[str, Any]
    outcomes: list[TreatyOutcome] = field(default_factory=list)
    decisions: tuple[MatchDecision, ...] = ()
    #: True when the period test was skipped - a historical event on the
    #: current book. Carried into the payload so the UI can label it.
    as_if: bool = True

    @property
    def matched(self) -> int:
        return sum(1 for d in self.decisions if d.matched)

    @property
    def excluded(self) -> int:
        return sum(1 for d in self.decisions if not d.matched)

    @property
    def our_net_total(self) -> Decimal:
        return sum((o.our_net for o in self.outcomes), Decimal(0))

    @property
    def gross_total(self) -> Decimal:
        return sum((o.gross for o in self.outcomes), Decimal(0))

    @property
    def ceded_total(self) -> Decimal:
        return sum((o.ceded for o in self.outcomes), Decimal(0))

    def to_json(self) -> dict[str, Any]:
        return {
            "event": {
                "event_id": self.event["event_id"],
                "name": self.event["name"],
                "peril": self.event["peril"],
                "start": self.event["start"],
                "end": self.event["end"],
                "duration_h": self.event.get("duration_h"),
                "regions": len(self.event.get("regions", [])),
                "facts": self.event.get("facts", []),
                "disclaimer": self.event.get("disclaimer"),
            },
            "totals": {
                "gross": str(quantise(self.gross_total)),
                "ceded": str(quantise(self.ceded_total)),
                "our_net": str(quantise(self.our_net_total)),
                "treaties_matched": self.matched,
                "treaties_excluded": self.excluded,
            },
            "as_if": self.as_if,
            "treaties": [o.to_json() for o in self.outcomes],
            "excluded": [
                {"treaty_id": d.treaty_id, "reason": d.reason}
                for d in self.decisions
                if not d.matched
            ],
        }


def analyse(
    event_id: str,
    *,
    portfolio: Portfolio | None = None,
    model: VulnerabilityModel | None = None,
    data_dir: Path | str = "data",
    as_if: bool = True,
) -> AnalysisResult:
    """Run the deterministic half of an analysis for one replay event."""
    event = load_event(event_id, data_dir)
    portfolio = portfolio if portfolio is not None else build_portfolio()
    model = model if model is not None else VulnerabilityModel.load()

    decisions = match_treaties(portfolio, event, as_if=as_if)
    ratios = _damage_ratios(event, model)
    result = AnalysisResult(event=event, decisions=decisions, as_if=as_if)

    for decision in decisions:
        if not decision.matched:
            continue
        treaty = portfolio.treaty(decision.treaty_id)
        slices = [
            ExposureSlice(e.region_code, e.peril, e.tsi_usd)
            for e in portfolio.exposures_for(treaty.cedent_id, event["peril"])
            if e.region_code in decision.regions
        ]
        gross = gross_loss(slices, ratios)

        outcome = TreatyOutcome(
            treaty_id=treaty.treaty_id,
            cedent_id=treaty.cedent_id,
            cedent_name=portfolio.cedent(treaty.cedent_id).name,
            type=treaty.type,
            gross=gross,
            regions=decision.regions,
        )
        if treaty.type == "CAT_XL" and treaty.layers:
            outcome.cat_xl = apply_cat_xl([gross], _layers_of(treaty))
        elif treaty.qs:
            outcome.quota_share = apply_quota_share(
                gross,
                QuotaShare(
                    cession_pct=Decimal(str(treaty.qs["cession_pct"])),
                    our_share=Decimal(str(treaty.qs.get("our_share", 0))),
                    event_limit=(
                        Decimal(str(treaty.qs["event_limit"]))
                        if treaty.qs.get("event_limit")
                        else None
                    ),
                ),
            )
        result.outcomes.append(outcome)

    # Largest net exposure first: the first question is always "where are we
    # most on the hook", not "which treaty id sorts first".
    result.outcomes.sort(key=lambda o: o.our_net, reverse=True)
    return result


# --------------------------------------------------------------------------- #
# SSE (API-4)
# --------------------------------------------------------------------------- #


def _sse(payload: dict[str, Any]) -> str:
    """One SSE frame. `data: {json}\\n\\n`, per API-4."""
    return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"


def stream_analysis(
    event_id: str,
    *,
    portfolio: Portfolio | None = None,
    model: VulnerabilityModel | None = None,
    data_dir: Path | str = "data",
    as_if: bool = True,
) -> Iterator[str]:
    """API-4's event stream for the deterministic pipeline.

    The frame types are the ones the final agent graph will emit, so the
    frontend is written against the real contract now and does not change when
    the agents land - only more frames arrive between the same bookends.
    """
    stages = ("event_intel", "exposure_analyst")
    try:
        yield _sse({"type": "stage", "agent": stages[0], "status": "started"})
        event = load_event(event_id, data_dir)
        yield _sse(
            {
                "type": "result",
                "key": "event",
                "data": {
                    "event_id": event["event_id"],
                    "name": event["name"],
                    "peril": event["peril"],
                    "duration_h": event.get("duration_h"),
                    "regions": len(event.get("regions", [])),
                    "facts": event.get("facts", []),
                },
            }
        )
        yield _sse({"type": "stage", "agent": stages[0], "status": "completed"})

        yield _sse({"type": "stage", "agent": stages[1], "status": "started"})
        result = analyse(
            event_id,
            portfolio=portfolio,
            model=model,
            data_dir=data_dir,
            as_if=as_if,
        )
        yield _sse(
            {
                "type": "tool",
                "agent": stages[1],
                "name": "match_treaties",
                "summary": f"{result.matched} matched, {result.excluded} excluded",
            }
        )
        yield _sse(
            {"type": "result", "key": "impact", "data": result.to_json()}
        )
        yield _sse({"type": "stage", "agent": stages[1], "status": "completed"})
        yield _sse({"type": "done", "analysis_id": f"replay-{event_id}"})
    except EventNotFound:
        yield _sse(
            {
                "type": "error",
                "message": f"No replay fixture for {event_id!r}.",
                "retryable": False,
            }
        )
    except Exception as exc:  # noqa: BLE001 - the stream must end cleanly
        # A half-finished SSE stream looks like a hung browser. An error frame
        # followed by `done` lets the UI say what went wrong.
        yield _sse(
            {"type": "error", "message": f"{type(exc).__name__}: {exc}", "retryable": True}
        )
