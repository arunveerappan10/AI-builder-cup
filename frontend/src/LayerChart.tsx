/**
 * UI-4 — the layer chart.
 *
 * Its own module so recharts can be code-split. The chart only exists after an
 * analysis has run, and recharts is 525 kB of the bundle - more than thirty
 * times everything else - so loading it up front would delay first paint for
 * a component nobody has asked for yet.
 */

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatMoney, formatPercent } from "./api";
import { Term } from "./components";
import type { TreatyOutcome } from "./types";

/** The layer chart. Burn per layer, with exhaustion marked by label and not
 * by colour alone. */
export default function LayerChart({ hero }: { hero: TreatyOutcome }) {
  const layers = hero.layers ?? [];
  if (!layers.length) {
    return (
      <section className="panel">
        <h2>Layer burn</h2>
        <p className="note">
          {hero.treaty_id} is a <Term>quota share</Term>, so it has no layers —
          it cedes a fixed percentage of the loss.
        </p>
      </section>
    );
  }

  const data = layers.map((layer) => ({
    name: `L${layer.layer_no}`,
    burn: Math.min(Number(layer.burn) * 100, 200),
    ceded: Number(layer.ceded),
    exhausted: layer.exhausted,
  }));

  return (
    <section className="panel">
      <h2>
        Layer burn &middot; {hero.treaty_id}
      </h2>
      <div style={{ width: "100%", height: 190 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 4, right: 12, bottom: 4, left: 0 }}>
            <CartesianGrid stroke="#2b3440" vertical={false} />
            <XAxis dataKey="name" stroke="#9fb0c3" tickLine={false} />
            <YAxis
              stroke="#9fb0c3"
              tickLine={false}
              unit="%"
              domain={[0, 100]}
              allowDataOverflow
            />
            <Tooltip
              contentStyle={{
                background: "#161b22",
                border: "1px solid #2b3440",
                borderRadius: 8,
                color: "#e8edf4",
              }}
              formatter={(value: number, key) =>
                key === "burn" ? [`${value.toFixed(1)}%`, "burn"] : [value, key]
              }
            />
            <Bar dataKey="burn" radius={[4, 4, 0, 0]}>
              {data.map((row) => (
                <Cell
                  key={row.name}
                  fill={row.exhausted ? "#ffb84d" : "#4da3ff"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* UI-12: the table is the accessible alternative to the chart, and it
          carries the numbers the chart only implies. */}
      <table style={{ marginTop: 10 }}>
        <caption className="note" style={{ captionSide: "bottom", textAlign: "left" }}>
          USD millions. <Term>burn</Term> above 100% means a reinstatement was
          drawn.
        </caption>
        <thead>
          <tr>
            <th>Layer</th>
            <th className="num">Ceded</th>
            <th className="num">Burn</th>
            <th className="num">Our loss</th>
            <th className="num">Our RIP</th>
            <th>State</th>
          </tr>
        </thead>
        <tbody>
          {layers.map((layer) => (
            <tr key={layer.layer_no}>
              <td>L{layer.layer_no}</td>
              <td className="num">{formatMoney(layer.ceded)}</td>
              <td className="num">{formatPercent(layer.burn)}</td>
              <td className="num">{formatMoney(layer.our_loss)}</td>
              <td className="num">{formatMoney(layer.our_rip)}</td>
              <td>
                {layer.exhausted ? (
                  <span className="pill exhausted">exhausted</span>
                ) : Number(layer.ceded) > 0 ? (
                  <span className="pill">part-burnt</span>
                ) : (
                  <span className="pill">untouched</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

