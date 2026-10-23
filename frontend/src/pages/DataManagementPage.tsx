import React, { useEffect, useState } from "react";
import {
  Database,
  Play,
  RotateCw,
  CheckCircle2,
  AlertCircle,
  FileCheck,
  ShieldCheck,
  Clock,
  Layers,
  HardDrive,
  Hash,
} from "lucide-react";
import { api } from "../services/api";
import { PipelineHistoryItem, PipelineStatus } from "../types";

export const DataManagementPage: React.FC = () => {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [history, setHistory] = useState<PipelineHistoryItem[]>([]);
  const [qualitySummary, setQualitySummary] = useState<any>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  const loadPipelineData = async () => {
    try {
      const [statusRes, historyRes, qualityRes] = await Promise.all([
        api.getPipelineStatus(),
        api.getPipelineHistory(),
        api.getDataQuality(),
      ]);
      setStatus(statusRes);
      setHistory(historyRes);
      setQualitySummary(qualityRes);
    } catch (err) {
      console.error("Error loading pipeline data:", err);
    }
  };

  useEffect(() => {
    loadPipelineData();
  }, []);

  const handleRunPipeline = async () => {
    try {
      setRunning(true);
      setRunMessage("Executing ETL extraction, schema validation, database upsert, and model retraining...");
      const res = await api.runPipeline();
      setRunMessage(
        `Pipeline finished successfully in ${res.duration_seconds}s! Processed ${res.records_processed} records with Quality Score ${res.quality_score}%.`
      );
      await loadPipelineData();
    } catch (err: any) {
      setRunMessage(`Pipeline failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Data Engineering & ETL Orchestration
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Automated data lifecycle management: Extraction, Pydantic validation, relational loading, and model persistence.
        </p>
      </div>

      {/* Pipeline Trigger Hero Card */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-50 text-indigo-700">
              <Database className="h-5 w-5" />
            </span>
            <h2 className="text-base font-bold text-slate-900">
              End-to-End Pipeline Execution Engine
            </h2>
          </div>
          <p className="text-xs text-slate-500 max-w-xl">
            Triggers the full pipeline: downloads raw UCI files, verifies cryptographic checksums, runs multi-tier validation, updates normalized relational tables, and retrains both classification and regression models.
          </p>
        </div>

        <button
          onClick={handleRunPipeline}
          disabled={running}
          className="w-full md:w-auto px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-sm shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-50 shrink-0"
        >
          {running ? (
            <>
              <RotateCw className="h-4 w-4 animate-spin" />
              <span>Executing Pipeline...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Run Master Pipeline Now</span>
            </>
          )}
        </button>
      </div>

      {runMessage && (
        <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-900 text-xs flex items-center gap-2.5">
          <CheckCircle2 className="h-4 w-4 text-indigo-600 shrink-0" />
          <span>{runMessage}</span>
        </div>
      )}

      {/* Database Entity Stats */}
      {status && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 text-center">
            <p className="text-xs uppercase font-bold text-slate-400">Total Students</p>
            <p className="text-2xl font-bold text-slate-900 mt-1">
              {status.database_counts.students}
            </p>
            <p className="text-[11px] text-slate-500">Unique entities</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 text-center">
            <p className="text-xs uppercase font-bold text-slate-400">Academic Records</p>
            <p className="text-2xl font-bold text-slate-900 mt-1">
              {status.database_counts.academic_records}
            </p>
            <p className="text-[11px] text-slate-500">Course enrollments</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 text-center">
            <p className="text-xs uppercase font-bold text-slate-400">Active Courses</p>
            <p className="text-2xl font-bold text-slate-900 mt-1">
              {status.database_counts.courses}
            </p>
            <p className="text-[11px] text-slate-500">MAT & POR</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 text-center">
            <p className="text-xs uppercase font-bold text-slate-400">Quality Score</p>
            <p className="text-2xl font-bold text-emerald-600 mt-1">
              {status.latest_run.quality_score}%
            </p>
            <p className="text-[11px] text-slate-500">Validation score</p>
          </div>
        </div>
      )}

      {/* Data Ingestion & Provenance Card */}
      {qualitySummary && (
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              Verified Ingestion Provenance & Checksums
            </h2>
            <p className="text-xs text-slate-500">
              Raw data files registered with SHA-256 cryptographic hashes for end-to-end data integrity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {qualitySummary.imports?.map((imp: any, i: number) => (
              <div
                key={i}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 font-mono text-sm">{imp.file_name}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                    {imp.status}
                  </span>
                </div>
                <p className="text-slate-500">{imp.source_name}</p>
                <div className="pt-2 border-t border-slate-200/80 flex items-center justify-between text-slate-600">
                  <span>Records: <strong>{imp.row_count}</strong></span>
                  <span>Synthetic: <strong>{imp.is_synthetic ? "Yes" : "False (Genuine UCI)"}</strong></span>
                </div>
                <div className="p-1.5 rounded bg-white border border-slate-200 font-mono text-[10px] text-slate-500 truncate">
                  SHA256: {imp.checksum}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pipeline Execution History Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200/80 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Pipeline Execution Audit Log</h2>
            <p className="text-xs text-slate-500">Historical trace of automated ETL and ML training triggers</p>
          </div>
          <span className="text-xs text-slate-500 font-medium">Last 20 Runs</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 uppercase text-[10px] font-bold text-slate-400 border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Run ID</th>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Records Processed</th>
                <th className="px-4 py-3">Duration</th>
                <th className="px-4 py-3">Quality Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {history.map((h) => (
                <tr key={h.id} className="hover:bg-slate-50/50">
                  <td className="px-5 py-3 font-mono font-bold text-slate-800">#{h.id}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {new Date(h.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800">
                      <CheckCircle2 className="h-3 w-3" />
                      {h.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-bold text-slate-800">{h.records_processed} records</td>
                  <td className="px-4 py-3 text-slate-600">{h.duration_seconds}s</td>
                  <td className="px-4 py-3 font-bold text-emerald-600">{h.quality_score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
