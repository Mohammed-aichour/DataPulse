import React, { useEffect, useState } from "react";
import {
  Search,
  Filter,
  Users,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  Eye,
  X,
  GraduationCap,
  Home,
  BookOpen,
} from "lucide-react";
import { api } from "../services/api";
import { PaginatedStudents, StudentDetail, StudentListItem } from "../types";

export const StudentsPage: React.FC = () => {
  const [data, setData] = useState<PaginatedStudents | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [page, setPage] = useState<number>(1);
  const [search, setSearch] = useState<string>("");
  const [school, setSchool] = useState<string>("");
  const [course, setCourse] = useState<string>("");
  const [riskOnly, setRiskOnly] = useState<boolean>(false);

  // Detail Modal state
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);
  const [studentDetail, setStudentDetail] = useState<StudentDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const res = await api.getStudents({
        page,
        page_size: 12,
        search: search.trim() || undefined,
        school: school || undefined,
        course: course || undefined,
        risk_only: riskOnly,
      });
      setData(res);
    } catch (err) {
      console.error("Error fetching students:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [page, school, course, riskOnly]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchStudents();
  };

  const openStudentDetail = async (studentId: string) => {
    try {
      setSelectedStudentId(studentId);
      setLoadingDetail(true);
      const detail = await api.getStudentDetail(studentId);
      setStudentDetail(detail);
    } catch (err) {
      console.error("Error fetching student detail:", err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const closeDetail = () => {
    setSelectedStudentId(null);
    setStudentDetail(null);
  };

  const getTierBadge = (tier: string) => {
    switch (tier) {
      case "Excellent":
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
      case "Good":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "Satisfactory":
        return "bg-amber-100 text-amber-800 border-amber-200";
      default:
        return "bg-red-100 text-red-800 border-red-200";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Student Academic Directory
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Search and inspect individual academic profiles, enrollment histories, and early risk flags.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search student code (e.g. STU-0001)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
          />
        </form>

        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
          {/* School filter */}
          <select
            value={school}
            onChange={(e) => {
              setSchool(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
          >
            <option value="">All Schools</option>
            <option value="GP">Gabriel Pereira (GP)</option>
            <option value="MS">Mousinho da Silveira (MS)</option>
          </select>

          {/* Course filter */}
          <select
            value={course}
            onChange={(e) => {
              setCourse(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
          >
            <option value="">All Courses</option>
            <option value="MAT">Mathematics (MAT)</option>
            <option value="POR">Portuguese Language (POR)</option>
          </select>

          {/* Risk Toggle */}
          <button
            type="button"
            onClick={() => {
              setRiskOnly(!riskOnly);
              setPage(1);
            }}
            className={`px-3 py-2 text-xs font-semibold rounded-lg border transition-all inline-flex items-center gap-1.5 ${
              riskOnly
                ? "bg-amber-500 text-white border-amber-600 shadow-xs"
                : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
            }`}
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>At Risk Only</span>
          </button>
        </div>
      </div>

      {/* Students Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            <div className="h-6 w-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading student directory...
          </div>
        ) : !data || data.items.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">
            No students found matching the selected filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50/80 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200/80">
                <tr>
                  <th className="px-5 py-3.5">Student ID</th>
                  <th className="px-4 py-3.5">School & Sex</th>
                  <th className="px-4 py-3.5">Age / Residence</th>
                  <th className="px-4 py-3.5">Enrollments</th>
                  <th className="px-4 py-3.5">Final Grades (G3)</th>
                  <th className="px-4 py-3.5">Academic Status</th>
                  <th className="px-4 py-3.5">Performance Tier</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/60 font-medium">
                {data.items.map((s) => (
                  <tr key={s.student_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-slate-900 font-mono text-xs">
                      {s.student_id}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="font-semibold text-slate-800">{s.school}</span>
                      <span className="text-slate-400 text-xs ml-1.5">({s.sex === "F" ? "Female" : "Male"})</span>
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-600">
                      {s.age} yrs • {s.address === "U" ? "Urban" : "Rural"}
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex gap-1.5">
                        {s.courses.map((c) => (
                          <span
                            key={c}
                            className="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3.5 text-xs">
                      <div className="space-y-0.5">
                        {Object.entries(s.final_grades).map(([c, g]) => (
                          <div key={c} className="flex items-center gap-1.5">
                            <span className="font-semibold text-slate-500 text-[10px]">{c}:</span>
                            <span className={`font-bold ${g >= 10 ? "text-slate-800" : "text-red-600"}`}>
                              {g}/20
                            </span>
                          </div>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      {s.is_at_risk ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
                          <AlertTriangle className="h-3 w-3" />
                          At Risk
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle className="h-3 w-3" />
                          Good Standing
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${getTierBadge(s.performance_tier)}`}>
                        {s.performance_tier}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        onClick={() => openStudentDetail(s.student_id)}
                        className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors inline-flex items-center gap-1 text-xs font-semibold"
                        title="View Full Profile"
                      >
                        <Eye className="h-4 w-4" />
                        <span className="hidden sm:inline">Details</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination controls */}
        {data && (
          <div className="p-4 border-t border-slate-200/80 flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing {data.items.length > 0 ? (data.page - 1) * data.page_size + 1 : 0} to{" "}
              {Math.min(data.page * data.page_size, data.total)} of {data.total} students
            </span>
            <div className="flex items-center gap-1.5">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="px-3 py-1 font-semibold text-slate-800">
                Page {data.page} of {data.total_pages}
              </span>
              <button
                disabled={page >= data.total_pages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Student Detail Modal */}
      {selectedStudentId && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200">
            <div className="p-6 border-b border-slate-200 flex items-center justify-between sticky top-0 bg-white/95 backdrop-blur-xs z-10">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 font-bold font-mono">
                  {selectedStudentId.split("-")[1]}
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    Student Profile: {selectedStudentId}
                  </h2>
                  <p className="text-xs text-slate-500">
                    Comprehensive demographic, familial, and academic performance record
                  </p>
                </div>
              </div>
              <button
                onClick={closeDetail}
                className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {loadingDetail || !studentDetail ? (
                <div className="p-12 text-center text-slate-500">Loading student details...</div>
              ) : (
                <>
                  {/* Demographics Card */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                      Demographic & Household Background
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                      <div>
                        <p className="text-slate-400">School</p>
                        <p className="font-semibold text-slate-800">{studentDetail.school === "GP" ? "Gabriel Pereira" : "Mousinho da Silveira"}</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Gender / Age</p>
                        <p className="font-semibold text-slate-800">{studentDetail.sex === "F" ? "Female" : "Male"}, {studentDetail.age} yrs</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Address</p>
                        <p className="font-semibold text-slate-800">{studentDetail.address === "U" ? "Urban Area" : "Rural Area"}</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Family Size</p>
                        <p className="font-semibold text-slate-800">{studentDetail.famsize === "GT3" ? "> 3 members" : "≤ 3 members"}</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Mother Edu / Job</p>
                        <p className="font-semibold text-slate-800">Tier {studentDetail.medu}/4 • {studentDetail.mjob}</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Father Edu / Job</p>
                        <p className="font-semibold text-slate-800">Tier {studentDetail.fedu}/4 • {studentDetail.fjob}</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Guardian</p>
                        <p className="font-semibold text-slate-800 capitalize">{studentDetail.guardian}</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Home Internet</p>
                        <p className="font-semibold text-slate-800">{studentDetail.internet === "yes" ? "Yes (Connected)" : "No"}</p>
                      </div>
                    </div>
                  </div>

                  {/* Course Enrollments */}
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                      Academic Course Enrollments & Period Grades
                    </h3>
                    <div className="space-y-3">
                      {studentDetail.enrollments.map((enr) => (
                        <div
                          key={enr.record_id}
                          className="p-4 rounded-xl border border-slate-200 bg-white shadow-2xs"
                        >
                          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-sm text-slate-900">
                                {enr.course_code === "MAT" ? "Mathematics" : "Portuguese Language"}
                              </span>
                              <span className="text-xs px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-semibold font-mono">
                                {enr.record_id}
                              </span>
                            </div>
                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getTierBadge(enr.performance_tier)}`}>
                              {enr.performance_tier}
                            </span>
                          </div>

                          <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 mt-3 text-center text-xs">
                            <div>
                              <p className="text-slate-400 text-[10px] uppercase font-semibold">Period 1 (G1)</p>
                              <p className="text-sm font-bold text-slate-800">{enr.g1}/20</p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-[10px] uppercase font-semibold">Period 2 (G2)</p>
                              <p className="text-sm font-bold text-slate-800">{enr.g2}/20</p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-[10px] uppercase font-semibold">Final Grade (G3)</p>
                              <p className={`text-base font-extrabold ${enr.g3 >= 10 ? "text-emerald-600" : "text-red-600"}`}>
                                {enr.g3}/20
                              </p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-[10px] uppercase font-semibold">Study Time</p>
                              <p className="text-sm font-semibold text-slate-700">Tier {enr.studytime}/4</p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-[10px] uppercase font-semibold">Past Failures</p>
                              <p className={`text-sm font-semibold ${enr.failures > 0 ? "text-red-600" : "text-slate-700"}`}>
                                {enr.failures}
                              </p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-[10px] uppercase font-semibold">Absences</p>
                              <p className="text-sm font-semibold text-slate-700">{enr.absences} days</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
