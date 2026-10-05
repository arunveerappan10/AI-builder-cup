/**
 * The API contract, mirrored from `backend/app/analysis.py`.
 *
 * Money arrives as **strings**, not numbers, and stays that way until it is
 * formatted. The backend computes in Decimal precisely because binary float
 * gets the split case wrong - `7.85 - 0.525` is 7.324999999999999 - so
 * parsing it into a JS number here would reintroduce the error the whole
 * pipeline exists to avoid. Nothing in this app does arithmetic on money.
 */

export type Peril = "WS" | "EQ" | "FL" | "OTHER";

export interface EventSummary {
  event_id: string;
  name: string;
  peril: Peril;
  date: string;
  countries: string[];
  duration_h: number | null;
  regions: number;
}

export interface EventFact {
  text: string;
  source: string;
  url?: string | null;
}

export interface LayerResult {
  layer_no: number;
  ceded: string;
  our_loss: string;
  our_rip: string;
  /** Exceeds 1 when reinstatements are used - the layer chart's whole point. */
  burn: string;
  exhausted: boolean;
  reinstated: string;
}

export interface TreatyOutcome {
  treaty_id: string;
  cedent_id: string;
  cedent: string;
  type: "CAT_XL" | "QS";
  gross: string;
  regions: string[];
  our_net: string;
  ceded: string;
  layers?: LayerResult[];
  /** The full per-party view (MONEY_MOMENT 4.4), Cat XL only. */
  cedent_retention?: string;
  cedent_net_cost?: string;
  total_rip?: string;
  our_loss?: string;
  our_rip?: string;
  market_net?: string;
  capped?: boolean;
}

export interface Impact {
  event: {
    event_id: string;
    name: string;
    peril: Peril;
    start: string;
    end: string;
    duration_h: number | null;
    regions: number;
    facts: EventFact[];
    disclaimer?: string | null;
  };
  totals: {
    gross: string;
    ceded: string;
    our_net: string;
    treaties_matched: number;
    treaties_excluded: number;
  };
  as_if: boolean;
  treaties: TreatyOutcome[];
  excluded: { treaty_id: string; reason: string }[];
}

/** SSE frames (API-4). */
export type Frame =
  | { type: "stage"; agent: string; status: "started" | "completed" }
  | { type: "tool"; agent: string; name: string; summary: string }
  | { type: "partial"; agent: string; text: string }
  | { type: "result"; key: "event"; data: Impact["event"] }
  | { type: "result"; key: "impact"; data: Impact }
  | { type: "result"; key: string; data: unknown }
  | { type: "error"; message: string; retryable: boolean }
  | { type: "done"; analysis_id: string };

export interface Health {
  status: string;
  version: string;
  build: string;
  configured: boolean;
  models: { main: string; reason: string; embed: string; embed_dim: number };
  location: string;
  features: { courtroom: boolean; cached_replay_only: boolean };
  warnings: string[];
}
