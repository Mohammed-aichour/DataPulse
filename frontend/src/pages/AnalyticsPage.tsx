import React, { useEffect, useState } from "react";
import {
  BarChart3,
  TrendingUp,
  Download,
  Share2,
  FileSpreadsheet,
  CheckCircle2,
  Layers,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { api } from "../services/api";
import { CorrelationItem, FactorPerformance } from "../types";

export const AnalyticsPage: React.FC = () => {
  const [selectedFactor, setSelectedFactor] = useState<string>("studytime");
  const [factorData, setFactorData] = useState<FactorPerformance[]>([]);
  const [correlations, setCorrelations] = useState<CorrelationItem[]>([]);
  const [powerbiSpec, setPowerbiSpec] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const factorOptions = [
    { id: "studytime", label: "Weekly Study Time" },
    { id: "failures", label: "Past Academic Failures" },
    { id: "absences", label: "School Absence Tiers" },
    { id: "parent_edu", label: "Parental Educational Capital" },
    { id: "school", label: "School Institution" },
    { id: "sex", label: "Student Gender" },
    { id: "internet", label: "Home Internet Connectivity" },
  ];

  useEffect(() => {
    async function loadInitial() {
      try {
        setLoading(true);
        const [corrRes, pbiRes] = await Promise.all([
          api.getCorrelations(),
          api.getPowerBiSpec(),
        ]);
        setCorrelations(corrRes);
        setPowerbiSpec(pbiRes);
      } catch (err) {
        console.error("Error loading analytics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  useEffect(() => {
    async function loadFactor() {
      try {
        const res = await api.getPerformanceByFactor(selectedFactor);
        setFactorData(res);
      } catch (err) {
        console.error("Error loading factor performance:", err);
      }
    }
    loadFactor();
  }, [selectedFactor]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Advanced Institutional Analytics
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Multi-variable exploratory breakdown, correlation structures, and enterprise Power BI reporting integration.
        </p>
      </div>

      {/* Factor Performance Explorer */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Factor Performance Impact Explorer
            </h2>
            <p className="text-xs text-slate-500">
              Compare grade averages and passing percentages grouped by contextual variables
            </p>
          </div>

          <div className="flex flex-wrap gap-1.5 p-1 bg-slate-100 rounded-lg">
            {factorOptions.map((opt) => (
              <button
                key={opt.id}
                onClick={() => setSelectedFactor(opt.id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                  selectedFactor === opt.id
                    ? "bg-white text-indigo-700 shadow-2xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Chart */}
        <div className="h-80 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={factorData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="factor_group" stroke="#64748b" fontSize={12} />
              <YAxis yAxisId="grade" domain={[0, 20]} stroke="#475569" fontSize={11} label={{ value: "Grade / 20", angle: -90, position: "insideLeft", fontSize: 10 }} />
              <YAxis yAxisId="pct" orientation="right" domain={[0, 100]} stroke="#059669" fontSize={11} label={{ value: "Pass Rate %", angle: 90, position: "insideRight", fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  border: "none",
                  borderRadius: "8px",
                  color: "#fff",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "12px" }} />
              <Bar yAxisId="grade" dataKey="avg_grade" name="Average Final Grade (0-20)" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="pct" dataKey="pass_rate_pct" name="Course Pass Rate (%)" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Factor Table Summary */}
        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 uppercase text-[10px] font-bold text-slate-400 border-y border-slate-200">
              <tr>
                <th className="px-4 py-2.5">Category Group</th>
                <th className="px-4 py-2.5">Cohort Size</th>
                <th className="px-4 py-2.5">Avg Final Grade</th>
                <th className="px-4 py-2.5">Passing Rate</th>
                <th className="px-4 py-2.5">At Risk Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {factorData.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50/50">
                  <td className="px-4 py-2.5 font-bold text-slate-800">{row.factor_group}</td>
                  <td className="px-4 py-2.5">{row.student_count} records</td>
                  <td className="px-4 py-2.5 font-bold text-indigo-700">{row.avg_grade} / 20</td>
                  <td className="px-4 py-2.5 text-emerald-600 font-bold">{row.pass_rate_pct}%</td>
                  <td className="px-4 py-2.5 text-red-600 font-bold">{row.risk_rate_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Feature Correlation Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Empirical Correlation Ranking (Target: Final Grade G3)
          </h2>
          <p className="text-xs text-slate-500">
            Pearson linear correlation coefficients computed directly against student final performance
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {correlations.map((c) => (
            <div
              key={c.feature}
              className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 flex items-center justify-between hover:bg-slate-50 transition-colors"
            >
              <div>
                <p className="font-bold text-xs text-slate-800">{c.label}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                      c.impact === "Positive"
                        ? "bg-emerald-100 text-emerald-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {c.impact} ({c.magnitude})
                  </span>
                </div>
              </div>
              <div className="text-right">
                <span className={`text-base font-extrabold font-mono ${c.correlation >= 0 ? "text-indigo-600" : "text-amber-600"}`}>
                  {c.correlation > 0 ? `+${c.correlation}` : c.correlation}
                </span>
                <p className="text-[10px] text-slate-400">r coefficient</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Power BI Integration & CSV Export Panel */}
      <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white p-6 rounded-xl shadow-lg border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <BarChart3 className="h-4 w-4" />
              </span>
              <h2 className="text-lg font-bold">Power BI Enterprise Integration</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Connect external Business Intelligence suites, download star-schema datasets, or import analytical SQL views.
            </p>
          </div>

          {/* CSV Export Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <a
              href={api.getCsvExportUrl("students")}
              download
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold border border-white/10 transition-colors"
            >
              <FileSpreadsheet className="h-3.5 w-3.5 text-sky-400" />
              <span>Export Students CSV</span>
            </a>
            <a
              href={api.getCsvExportUrl("academic_records")}
              download
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-xs transition-colors"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export Enrollments CSV</span>
            </a>
            <a
              href={api.getCsvExportUrl("courses")}
              download
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold border border-white/10 transition-colors"
            >
              <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
              <span>Export Courses CSV</span>
            </a>
          </div>
        </div>

        {/* Star-Schema & DAX Specification */}
        {powerbiSpec && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
            <div className="space-y-3 bg-slate-800/40 p-4 rounded-xl border border-slate-700/50">
              <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
                <Layers className="h-4 w-4 text-indigo-400" />
                Recommended Star-Schema Architecture
              </h3>
              <p className="text-slate-300">
                <strong>Fact Table:</strong> {powerbiSpec.star_schema?.fact_table}
              </p>
              <div className="space-y-1">
                <p className="font-semibold text-slate-400">Dimension Tables:</p>
                {powerbiSpec.star_schema?.dimension_tables?.map((d: string, i: number) => (
                  <p key={i} className="text-slate-300 pl-2 border-l border-slate-700">
                    • {d}
                  </p>
                ))}
              </div>
            </div>

            <div className="space-y-3 bg-slate-800/40 p-4 rounded-xl border border-slate-700/50">
              <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-amber-400" />
                Certified DAX KPI Measures
              </h3>
              <div className="space-y-2 overflow-y-auto max-h-48 pr-1">
                {powerbiSpec.recommended_dax_measures?.map((m: any, i: number) => (
                  <div key={i} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                    <p className="font-bold text-amber-300">{m.name}</p>
                    <code className="block mt-1 p-1 bg-black/40 rounded text-[11px] text-indigo-200 font-mono">
                      {m.dax}
                    </code>
                    <p className="text-[10px] text-slate-400 mt-1">{m.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
