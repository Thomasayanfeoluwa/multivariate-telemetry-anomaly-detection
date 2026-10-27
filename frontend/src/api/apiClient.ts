/**
 * Typed fetch wrapper for the SWaT monitoring API.
 *
 * One method per backend endpoint. Uses native fetch (Node 20+).
 * Every method throws ApiError on non-2xx responses, carrying FastAPI's
 * `detail` string verbatim so callers can surface the same diagnostic
 * the backend produces (e.g. the exact NB13 Test-G feature-order error).
 *
 * Base URL: import.meta.env.VITE_API_BASE_URL, default http://127.0.0.1:8000.
 * Vite exposes only VITE_* vars to the client; anything else is not
 * reachable from the browser. Never put secrets in VITE_* vars.
 */

import type {
  HealthResponse,
  ModelInfoResponse,
  Partition,
  PredictRequest,
  PredictResponse,
  ReplayAdvanceResponse,
  ReplayResetResponse,
  ReplayStartRequest,
  ReplayStatus,
} from "../types/api";

const DEFAULT_BASE_URL = "http://127.0.0.1:8000";

function getBaseUrl(): string {
  // Vite injects import.meta.env at build time. Under non-Vite runners
  // (vitest, tsx probes, node --test) import.meta.env may be undefined;
  // fall back to the default so the module is loadable outside Vite too.
  const env = (import.meta as { env?: Record<string, string | undefined> }).env;
  const raw = (env?.VITE_API_BASE_URL ?? "").trim();
  return raw.length > 0 ? raw.replace(/\/+$/, "") : DEFAULT_BASE_URL;
}

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;
  readonly url: string;

  constructor(status: number, detail: string, url: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.url = url;
  }
}

interface FastApiErrorBody {
  detail?: unknown;
}

function extractDetail(body: unknown, status: number, fallback: string): string {
  // FastAPI validation errors are {detail: [{msg, loc, ...}]} (422)
  // and HTTPExceptions are {detail: "..."} (4xx/5xx).
  if (body && typeof body === "object") {
    const b = body as FastApiErrorBody;
    const d = b.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      const msgs = d
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            return String((item as { msg: unknown }).msg);
          }
          return String(item);
        })
        .filter((s) => s.length > 0);
      if (msgs.length > 0) return msgs.join("; ");
    }
  }
  return `HTTP ${status}: ${fallback}`;
}

async function request<T>(
  method: "GET" | "POST",
  path: string,
  body?: unknown,
): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  let response: Response;
  try {
    response = await fetch(url, {
      method,
      headers:
        body !== undefined
          ? { "Content-Type": "application/json", Accept: "application/json" }
          : { Accept: "application/json" },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    const reason = e instanceof Error ? e.message : String(e);
    throw new ApiError(0, `Network error contacting ${url}: ${reason}`, url);
  }

  let parsed: unknown = null;
  const text = await response.text();
  if (text.length > 0) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = null;
    }
  }

  if (!response.ok) {
    throw new ApiError(
      response.status,
      extractDetail(parsed, response.status, response.statusText || "error"),
      url,
    );
  }

  if (parsed === null) {
    throw new ApiError(
      response.status,
      "Empty response body from server.",
      url,
    );
  }
  return parsed as T;
}

// --- Public API ----------------------------------------------------------

export const api = {
  baseUrl(): string {
    return getBaseUrl();
  },

  health(): Promise<HealthResponse> {
    return request<HealthResponse>("GET", "/health");
  },

  modelInfo(): Promise<ModelInfoResponse> {
    return request<ModelInfoResponse>("GET", "/model-info");
  },

  predict(req: PredictRequest): Promise<PredictResponse> {
    return request<PredictResponse>("POST", "/predict", req);
  },

  replayStart(partition: Partition): Promise<ReplayResetResponse> {
    const payload: ReplayStartRequest = { partition };
    return request<ReplayResetResponse>("POST", "/replay/start", payload);
  },

  replayStatus(): Promise<ReplayStatus> {
    return request<ReplayStatus>("GET", "/replay/status");
  },

  replayAdvance(): Promise<ReplayAdvanceResponse> {
    return request<ReplayAdvanceResponse>("POST", "/replay/advance");
  },

  replayReset(): Promise<ReplayResetResponse> {
    return request<ReplayResetResponse>("POST", "/replay/reset");
  },
};