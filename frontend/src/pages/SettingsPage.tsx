import React, { useEffect, useState } from "react";
import {
  Settings,
  Server,
  Database,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
  BookOpen,
  GraduationCap,
  Sparkles,
  RefreshCw,
} from "lucide-react";
import { api } from "../services/api";
import { HealthInfo } from "../types";

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [pingLatency, setPingLatency] = useState<number | null>(null);
  const [checking, setChecking] = useState<boolean>(false);

  const checkHealth = async () => {
    try {
      setChecking(true);
      const start = performance.now();
      const res = await api.getHealth();
      const latency = Math.round(performance.now() - start);
      setHealth(res);
      setPingLatency(latency);
    } catch (err) {
      console.error("Health check error:", err);
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Platform Configuration & System Architecture
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Backend operational telemetry, environment diagnostics, and institutional project metadata.
        </p>
      </div>

      {/* Live Health Diagnostic Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Server className="h-4 w-4 text-indigo-600" />
              Live API Health & Diagnostic Telemetry
            </h2>
            <p className="text-xs text-slate-500">
              Real-time connection verification against FastAPI backend runtime
            </p>
          </div>

          <button
            onClick={checkHealth}
            disabled={checking}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 inline-flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${checking ? "animate-spin" : ""}`} />
            <span>Test Connection</span>
          </button>
        </div>

        {health && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-slate-400 text-[10px] uppercase font-semibold">API Server</span>
              <p className="font-bold text-emerald-600 flex items-center gap-1 mt-0.5">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {health.status}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-slate-400 text-[10px] uppercase font-semibold">Database Engine</span>
              <p className="font-bold text-slate-800 flex items-center gap-1 mt-0.5">
                <Database className="h-3.5 w-3.5 text-indigo-600" />
                {health.database}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-slate-400 text-[10px] uppercase font-semibold">ML Inference</span>
              <p className="font-bold text-slate-800 flex items-center gap-1 mt-0.5">
                <ShieldCheck className="h-3.5 w-3.5 text-indigo-600" />
                {health.ml_models}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
              <span className="text-slate-400 text-[10px] uppercase font-semibold">Ping Latency</span>
              <p className="font-bold text-slate-800 font-mono mt-0.5">
                {pingLatency !== null ? `${pingLatency} ms` : "—"}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Institutional Project Attribution */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-sky-400 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <GraduationCap className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Universiapolis International University of Agadir (UIA)
            </h2>
            <p className="text-xs text-slate-500">
              Computer Engineering Academic Portfolio & Engineering Excellence
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-2">
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2">
            <h3 className="font-bold text-slate-800 text-sm">Author Information</h3>
            <p className="text-slate-600">
              <strong>Student:</strong> Mohamed
            </p>
            <p className="text-slate-600">
              <strong>Program:</strong> 2nd-Year Computer Engineering
            </p>
            <p className="text-slate-600">
              <strong>Institution:</strong> Universiapolis International University of Agadir (Morocco)
            </p>
            <p className="text-slate-600">
              <strong>Domain:</strong> Full-Stack Data Science, Analytics Engineering & DevOps
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2">
            <h3 className="font-bold text-slate-800 text-sm">Technical Stack Summary</h3>
            <p className="text-slate-600">
              <strong>Backend:</strong> Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
            </p>
            <p className="text-slate-600">
              <strong>Machine Learning:</strong> Scikit-Learn (Gradient Boosting, Random Forest, Ridge), Joblib
            </p>
            <p className="text-slate-600">
              <strong>Frontend:</strong> React 19, TypeScript, Vite, Tailwind CSS, Recharts, Lucide
            </p>
            <p className="text-slate-600">
              <strong>DevOps:</strong> Docker, Docker Compose, PostgreSQL 16, GitHub Actions CI
            </p>
          </div>
        </div>
      </div>

      {/* Developer API Documentation Links */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-3">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-indigo-600" />
          API & Schema Documentation
        </h2>
        <div className="flex flex-wrap gap-3 pt-1">
          <a
            href="http://localhost:8000/api/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 text-xs font-semibold border border-indigo-200 transition-colors"
          >
            <span>Interactive OpenAPI Swagger Docs</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          <a
            href="http://localhost:8000/api/redoc"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-50 text-slate-700 hover:bg-slate-100 text-xs font-semibold border border-slate-200 transition-colors"
          >
            <span>ReDoc API Documentation</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          <a
            href="http://localhost:8000/api/export/powerbi-spec"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-50 text-slate-700 hover:bg-slate-100 text-xs font-semibold border border-slate-200 transition-colors"
          >
            <span>Power BI JSON Schema Spec</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
};
