import React, { useEffect, useState } from "react";
import {
  Users,
  GraduationCap,
  Award,
  AlertTriangle,
  Database,
  ArrowUpRight,
  TrendingUp,
  BookOpen,
  Calendar,
  CheckCircle2,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  AreaChart,
  Area,
} from "recharts";
import { api, API_BASE_URL } from "../services/api";
import { CoursePerformance, GradeDistributionBin, OverviewKPIs } from "../types";

export const DashboardPage: React.FC = () => {
  const [kpis, setKpis] = useState<OverviewKPIs | null>(null);
  const [courses, setCourses] = useState<CoursePerformance[]>([]);
  const [distribution, setDistribution] = useState<GradeDistributionBin[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [kpiRes, courseRes, distRes] = await Promise.all([
          api.getOverviewKPIs(),
          api.getCourses(),
          api.getGradeDistribution(),
        ]);
        setKpis(kpiRes);
        setCourses(courseRes);
        setDistribution(distRes);
        setError(null);
      } catch (err: any) {
        console.error("Dashboard data load error:", err);
        setError(err.message || "Failed to load dashboard metrics");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3 text-slate-500">
        <div className="h-8 w-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium">Aggregating live institutional metrics...</p>
      </div>
    );
  }

  if (error || !kpis) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-red-700">
        <h3 className="font-bold text-base">Backend Connection Notice</h3>
        <p className="text-sm mt-1">{error}</p>
        <p className="text-xs text-red-600 mt-2">
          Make sure the FastAPI backend is running and reachable ({API_BASE_URL}), and the database has been loaded.
        </p>
      </div>
    );
  }

  const kpiCards = [
    {
      label: "Total Unique Students",
      value: kpis.total_students.toLocaleString(),
      subtext: "Deduplicated across courses",
      icon: Users,
      color: "text-blue-600 bg-blue-50 border-blue-200",
    },
    {
      label: "Course Enrollments",
      value: kpis.total_enrollments.toLocaleString(),
      subtext: "Mathematics & Portuguese",
      icon: GraduationCap,
      color: "text-indigo-600 bg-indigo-50 border-indigo-200",
    },
    {
      label: "Academic Pass Rate",
      value: `${kpis.pass_rate_pct}%`,
      subtext: "Score ≥ 10/20 threshold",
      icon: Award,
      color: "text-emerald-600 bg-emerald-50 border-emerald-200",
    },
    {
      label: "Average Final Grade",
      value: `${kpis.avg_final_grade} / 20`,
      subtext: "Institutional scale (0-20)",
      icon: TrendingUp,
      color: "text-purple-600 bg-purple-50 border-purple-200",
    },
    {
      label: "Academic Risk Count",
      value: kpis.risk_count.toLocaleString(),
      subtext: `${kpis.risk_rate_pct}% needing support`,
      icon: AlertTriangle,
      color: "text-amber-600 bg-amber-50 border-amber-200",
    },
    {
      label: "Data Quality Score",
      value: `${kpis.data_quality_score}%`,
      subtext: "Validated & schema-conformant",
      icon: CheckCircle2,
      color: "text-teal-600 bg-teal-50 border-teal-200",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Executive Academic Dashboard
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Real-time descriptive and predictive performance analytics across university departments.
          </p>
        </div>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-600 shadow-2xs">
          <Calendar className="h-3.5 w-3.5 text-slate-400" />
          <span>Last Pipeline Run: {kpis.last_pipeline_run ? new Date(kpis.last_pipeline_run).toLocaleDateString() : "Active"}</span>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {kpiCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  {card.label}
                </span>
                <div className={`p-2 rounded-lg border ${card.color}`}>
                  <Icon className="h-4 w-4" />
                </div>
              </div>
              <div className="mt-3">
                <span className="text-2xl font-bold text-slate-900 tracking-tight">
                  {card.value}
                </span>
                <p className="text-xs text-slate-500 mt-1">{card.subtext}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Grade Distribution Multi-Period */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Grade Progression & Distribution Across Evaluation Periods
              </h2>
              <p className="text-xs text-slate-500">
                Tracking cohort migration across 8 standard score bands (0-20 scale)
              </p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 font-medium">
              G1 vs G2 vs Final (G3)
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="grade_range" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    border: "none",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "12px",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
                <Bar dataKey="period_1" name="Period 1 (G1)" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="period_2" name="Period 2 (G2)" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="final_g3" name="Final Grade (G3)" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Course Comparative Highlights */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Departmental Breakdown
            </h2>
            <p className="text-xs text-slate-500 mb-4">
              Direct comparison between STEM and Humanities cohorts
            </p>

            <div className="space-y-4">
              {courses.map((c) => (
                <div
                  key={c.course_code}
                  className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-bold text-sm text-slate-800">
                        {c.course_name}
                      </span>
                      <p className="text-xs text-slate-500">
                        {c.enrollments} Students Enrolled
                      </p>
                    </div>
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-700">
                      {c.course_code}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-200/80 text-center">
                    <div>
                      <p className="text-[10px] uppercase font-semibold text-slate-400">Avg Grade</p>
                      <p className="text-sm font-bold text-slate-800">{c.avg_g3}/20</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase font-semibold text-slate-400">Pass Rate</p>
                      <p className="text-sm font-bold text-emerald-600">{c.pass_rate_pct}%</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase font-semibold text-slate-400">Absences</p>
                      <p className="text-sm font-bold text-slate-700">{c.avg_absences} d</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 p-3.5 rounded-lg bg-indigo-50/70 border border-indigo-100 text-xs text-indigo-800 flex items-start gap-2.5">
            <BookOpen className="h-4 w-4 text-indigo-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Curriculum Key Insight</p>
              <p className="text-indigo-700/90 mt-0.5">
                Portuguese language cohorts demonstrate a higher pass rate (84.9%) than Mathematics (67.1%), reflecting standard secondary STEM difficulty curves.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
