import type { Categories, FormValues, Prediction } from "./types";

const BASE: string = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail =
      typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail ?? res.statusText);
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const getCategories = () => request<Categories>("/categories");
export const getSample = () => request<FormValues>("/sample");
export const predict = (txn: FormValues) =>
  request<Prediction>("/predict", { method: "POST", body: JSON.stringify(txn) });