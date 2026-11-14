import type { Dispatch, SetStateAction } from "react";
import { NUMERIC, CATS, BOOLS } from "../fields";
import type { Categories, FormValues } from "../types";

const input =
  "w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none";

interface Props {
  values: FormValues;
  setValues: Dispatch<SetStateAction<FormValues>>;
  categories: Categories;
  onSubmit: () => void;
  onLoadSample: () => void;
  loading: boolean;
}

export default function TransactionForm({
  values, setValues, categories, onSubmit, onLoadSample, loading,
}: Props) {
  const set = (k: string, v: string | number | boolean) =>
    setValues((prev) => ({ ...prev, [k]: v }));

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); onSubmit(); }}
      className="space-y-6 rounded-xl border border-slate-800 bg-slate-900/50 p-5"
    >
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">Numbers</h2>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          {NUMERIC.map(([k, label]) => (
            <label key={k} className="text-xs text-slate-400">
              {label}
              <input type="number" step="any" className={input}
                     value={String(values[k] ?? "")}
                     onChange={(e) => set(k, e.target.value)} />
            </label>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">Categories</h2>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          {CATS.map(([k, label]) => (
            <label key={k} className="text-xs text-slate-400">
              {label}
              <select className={input} value={String(values[k] ?? "")}
                      onChange={(e) => set(k, e.target.value)}>
                {(categories[k] ?? []).map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </label>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">Flags</h2>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
          {BOOLS.map(([k, label]) => (
            <label key={k} className="flex items-center gap-2 text-sm text-slate-300">
              <input type="checkbox" className="h-4 w-4 accent-indigo-500"
                     checked={Boolean(values[k])}
                     onChange={(e) => set(k, e.target.checked)} />
              {label}
            </label>
          ))}
        </div>
      </section>

      <div className="flex gap-3">
        <button type="submit" disabled={loading}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50">
          {loading ? "Scoring..." : "Score transaction"}
        </button>
        <button type="button" onClick={onLoadSample}
                className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800">
          Load sample fraud row
        </button>
      </div>
    </form>
  );
}