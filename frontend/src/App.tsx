/**
 * UI-1..8 — the demo path.
 *
 * One click runs the hero event. Everything else on the page is secondary to
 * that: a judge with ninety seconds should not have to choose anything.
 */

import { Suspense, lazy, useCallback, useEffect, useRef, useState } from "react";

import { BUILD_LABEL, fetchEvents, fetchHealth, runAnalysis } from "./api";
import {
  EventPanel,
  ExcludedPanel,
  MoneyMoment,
  Term,
  TreatyTable,
  TrustPanel,
} from "./components";

// recharts is most of the bundle and the chart cannot appear until an
// analysis has produced layers, so it loads on demand.
const LayerChart = lazy(() => import("./LayerChart"));
import type { EventSummary, Frame, Health, Impact } from "./types";

const HERO_EVENT = "jebi-2018";
/** Sakura's programme is the worked example in DOMAIN_PRIMER section 4, so it
 * is the one whose figures a judge can check against the deck. */
const HERO_TREATY = "T-001";

type Stage = { agent: string; done: boolean };

export default function App() {
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selected, setSelected] = useState(HERO_EVENT);
  const [health, setHealth] = useState<Health | null>(null);

  const [running, setRunning] = useState(false);
  const [stages, setStages] = useState<Stage[]>([]);
  const [impact, setImpact] = useState<Impact | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abort = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchEvents(controller.signal)
      .then((payload) => setEvents(payload.events))
      .catch(() => {
        /* the catalogue is a convenience; the hero button works without it */
      });
    fetchHealth(controller.signal)
      .then(setHealth)
      .catch(() => setHealth(null));
    return () => controller.abort();
  }, []);

  // Abort an in-flight analysis if the component goes away, so a navigation
  // does not leave a stream running against the backend.
  useEffect(() => () => abort.current?.abort(), []);

  const run = useCallback(
    async (eventId: string) => {
      abort.current?.abort();
      const controller = new AbortController();
      abort.current = controller;

      setRunning(true);
      setError(null);
      setImpact(null);
      setStages([]);

      try {
        for await (const frame of runAnalysis({ event_id: eventId }, controller.signal)) {
          apply(frame, { setStages, setImpact, setError });
        }
      } catch (caught) {
        if ((caught as Error)?.name !== "AbortError") {
          setError(
            caught instanceof Error
              ? `${caught.message} — is the API running?`
              : "The analysis could not be started.",
          );
        }
      } finally {
        setRunning(false);
      }
    },
    [],
  );

  const hero =
    impact?.treaties.find((t) => t.treaty_id === HERO_TREATY) ?? impact?.treaties[0];

  return (
    <div className="wrap">
      <header className="top">
        <h1>CatSight</h1>
        <span className="tag">
          Treaty-level catastrophe impact for reinsurers
        </span>
        <span className="spacer" />
        <span className="build">
          build {BUILD_LABEL}
          {health ? ` · api ${health.version}` : ""}
        </span>
      </header>

      <div className="lede">
        <p>
          After a typhoon or earthquake, a reinsurer needs three answers before
          the market does: <strong>which treaties responded</strong>,{" "}
          <strong>roughly what each layer pays</strong>, and{" "}
          <strong>which clauses change that answer</strong>. CatSight produces
          all three from the actual wordings.
        </p>
        <p>
          Every figure below is computed by a deterministic loss engine — not by
          a language model — so you can check the arithmetic.
        </p>

        <div className="controls">
          <button
            className="primary"
            onClick={() => run(selected)}
            disabled={running}
            aria-busy={running}
          >
            {running ? "Running…" : `Run demo: ${labelFor(events, selected)}`}
          </button>

          <label htmlFor="event" style={{ color: "var(--ink-dim)", fontSize: 14 }}>
            Event
          </label>
          <select
            id="event"
            value={selected}
            disabled={running}
            onChange={(e) => setSelected(e.target.value)}
          >
            {(events.length ? events : [fallbackEvent()]).map((event) => (
              <option key={event.event_id} value={event.event_id}>
                {event.name} ({event.date}) · {event.peril}
              </option>
            ))}
          </select>
        </div>

        {stages.length > 0 && (
          <ul className="stages" aria-live="polite">
            {stages.map((stage) => (
              <li key={stage.agent} className={stage.done ? "done" : "running"}>
                {stage.agent.replace(/_/g, " ")} {stage.done ? "✓" : "…"}
              </li>
            ))}
          </ul>
        )}
      </div>

      {error && (
        <div className="banner error" role="alert">
          {error}
        </div>
      )}

      {health && !health.configured && (
        <div className="banner info">
          The API is running without a Google Cloud project configured. Every
          number on this page still works — the loss engine needs no model — but
          clause analysis will be unavailable.
        </div>
      )}

      {impact && hero && (
        <>
          <EventPanel impact={impact} />
          <MoneyMoment hero={hero} />
          <div className="grid">
            <Suspense
              fallback={
                <section className="panel">
                  <h2>Layer burn</h2>
                  <p className="note" style={{ marginTop: 0 }}>
                    Loading chart&hellip;
                  </p>
                </section>
              }
            >
              <LayerChart hero={hero} />
            </Suspense>
            <TrustPanel />
          </div>
          <TreatyTable impact={impact} heroId={hero.treaty_id} />
          <ExcludedPanel impact={impact} />
        </>
      )}

      {!impact && !running && !error && (
        <section className="panel">
          <h2>Ready</h2>
          <p className="note" style={{ marginTop: 0 }}>
            Press <strong>Run demo</strong>. The hero event is Typhoon Jebi
            (2018), priced against the portfolio in force today — the{" "}
            <Term>as-if</Term> basis.
          </p>
        </section>
      )}

      <footer className="foot">
        Synthetic portfolio and synthetic treaty wordings. Cedent names are
        fictional. Hazard from NOAA IBTrACS and USGS ShakeMap; damage ratios
        from published vulnerability curves. Indicative first view, not a
        catastrophe-model output.
      </footer>
    </div>
  );
}

function apply(
  frame: Frame,
  set: {
    setStages: React.Dispatch<React.SetStateAction<Stage[]>>;
    setImpact: (impact: Impact) => void;
    setError: (message: string) => void;
  },
) {
  switch (frame.type) {
    case "stage":
      set.setStages((current) => {
        const done = frame.status === "completed";
        const existing = current.find((s) => s.agent === frame.agent);
        if (!existing) return [...current, { agent: frame.agent, done }];
        return current.map((s) => (s.agent === frame.agent ? { ...s, done } : s));
      });
      break;
    case "result":
      if (frame.key === "impact") set.setImpact(frame.data as Impact);
      break;
    case "error":
      set.setError(frame.message);
      break;
    default:
      // `tool`, `partial` and `done` carry no state this page renders yet.
      break;
  }
}

function labelFor(events: EventSummary[], id: string): string {
  const found = events.find((e) => e.event_id === id);
  return found ? `${found.name} ${found.date.slice(0, 4)}` : "Typhoon Jebi 2018";
}

function fallbackEvent(): EventSummary {
  return {
    event_id: HERO_EVENT,
    name: "Typhoon Jebi",
    peril: "WS",
    date: "2018-09-04",
    countries: ["JPN"],
    duration_h: 9,
    regions: 34,
  };
}
