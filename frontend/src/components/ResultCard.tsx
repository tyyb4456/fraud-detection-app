import { pretty } from "../fields";
import type { Prediction } from "../types";

export default function ResultCard({ result }: { result: Prediction }) {
  const pct = result.fraud_probability * 100;
  const max = Math.max(...result.top_reasons.map((r) => Math.abs(r.impact)), 0.001);

  return (
    <div className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/50 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Fraud probability</p>
          <p className="text-4xl font-bold text-slate-100">{pct.toFixed(1)}%</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-sm font-semibold ${
          result.flagged ? "bg-rose-500/20 text-rose-300" : "bg-emerald-500/20 text-emerald-300"}`}>
          {result.flagged ? "FLAGGED" : "LOOKS OK"}
        </span>
      </div>

      <div>
        <div className="relative h-3 rounded-full bg-slate-800">
          <div className={`h-3 rounded-full ${result.flagged ? "bg-rose-500" : "bg-emerald-500"}`}
               style={{ width: `${Math.min(pct, 100)}%` }} />
          <div className="absolute -top-1 h-5 w-0.5 bg-white"
               style={{ left: `${result.threshold * 100}%` }} title="decision threshold" />
        </div>
        <p className="mt-1 text-xs text-slate-500">
          White marker = decision threshold ({(result.threshold * 100).toFixed(1)}%)
        </p>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">Why this score</h3>
        <div className="space-y-3">
          {result.top_reasons.map((r) => (
            <div key={r.feature}>
              <div className="mb-1 flex justify-between text-xs">
                <span className="text-slate-300">{pretty(r.feature)} = {String(r.value)}</span>
                <span className={r.impact >= 0 ? "text-rose-300" : "text-emerald-300"}>
                  {r.impact >= 0 ? "+" : ""}{r.impact}
                </span>
              </div>
              <div className="relative h-4 rounded bg-slate-800">
                <div className="absolute inset-y-0 left-1/2 w-px bg-slate-600" />
                <div className={`absolute inset-y-0 rounded ${
                       r.impact >= 0 ? "left-1/2 bg-rose-500" : "right-1/2 bg-emerald-500"}`}
                     style={{ width: `${(Math.abs(r.impact) / max) * 50}%` }} />
              </div>
            </div>
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-500">
          Red pushes toward fraud, green toward legit (log-odds contribution).
        </p>
      </div>
    </div>
  );
}