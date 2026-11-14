import { useEffect, useState } from "react";
import { getCategories, getSample, predict } from "./api";
import { NUMERIC } from "./fields";
import TransactionForm from "./components/TransactionForm";
import ResultCard from "./components/ResultCard";
import type { Categories, FormValues, Prediction } from "./types";

const msg = (e: unknown) => (e instanceof Error ? e.message : String(e));

export default function App() {
  const [categories, setCategories] = useState<Categories>({});
  const [values, setValues] = useState<FormValues>({});
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([getCategories(), getSample()])
      .then(([c, s]) => { setCategories(c); setValues(s); })
      .catch((e) => setError(`Cannot reach the API: ${msg(e)}`));
  }, []);

  const loadSample = () => getSample().then(setValues).catch((e) => setError(msg(e)));

  const submit = async () => {
    setError(""); setLoading(true);
    try {
      const payload: FormValues = { ...values };
      for (const [k] of NUMERIC) {
        const n = Number(values[k]);
        if (values[k] === "" || Number.isNaN(n)) throw new Error(`Enter a valid number for ${k}`);
        payload[k] = n;
      }
      setResult(await predict(payload));
    } catch (e) {
      setError(msg(e)); setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-4">
        <h1 className="text-xl font-semibold">Fraud Scoring</h1>
        <p className="text-sm text-slate-400">Score a transaction and see what drove the decision.</p>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 p-6 lg:grid-cols-[1.4fr_1fr]">
        <TransactionForm values={values} setValues={setValues} categories={categories}
                         onSubmit={submit} onLoadSample={loadSample} loading={loading} />
        <div className="space-y-4">
          {error && (
            <div className="rounded-lg border border-rose-800 bg-rose-950/50 p-3 text-sm text-rose-200">
              {error}
            </div>
          )}
          {result ? (
            <ResultCard result={result} />
          ) : (
            <div className="rounded-xl border border-dashed border-slate-800 p-8 text-center text-sm text-slate-500">
              Fill in the form and press "Score transaction".
            </div>
          )}
        </div>
      </main>
    </div>
  );
}