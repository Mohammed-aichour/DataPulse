import React, { useEffect, useState } from "react";
import {
  BrainCircuit,
  Award,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  Sparkles,
  ShieldAlert,
  Info,
  Clock,
  Layers,
} from "lucide-react";
import { api } from "../services/api";
import { ModelEvaluation, PredictionRequest, PredictionResponse } from "../types";

export const MachineLearningPage: React.FC = () => {
  const [evaluation, setEvaluation] = useState<ModelEvaluation | null>(null);
  const [activeScenario, setActiveScenario] = useState<string>("scenario_c");

  // Prediction form state
  const [formData, setFormData] = useState<PredictionRequest>({
    course_code: "MAT",
    school: "GP",
    sex: "F",
    age: 17,
    address: "U",
    famsize: "GT3",
    Pstatus: "T",
    Medu: 3,
    Fedu: 3,
    Mjob: "services",
    Fjob: "services",
    reason: "course",
    guardian: "mother",
    traveltime: 1,
    studytime: 2,
    failures: 0,
    schoolsup: "no",
    famsup: "yes",
    paid: "no",
    activities: "yes",
    nursery: "yes",
    higher: "yes",
    internet: "yes",
    romantic: "no",
    famrel: 4,
    freetime: 3,
    goout: 3,
    Dalc: 1,
    Walc: 1,
    health: 4,
    absences: 2,
    G1: 12,
    G2: 13,
    scenario: "scenario_c",
  });

  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [predicting, setPredicting] = useState<boolean>(false);
  const [predictError, setPredictError] = useState<string | null>(null);

  useEffect(() => {
    async function loadModelData() {
      try {
        const res = await api.getModelEvaluation();
        setEvaluation(res);
      } catch (err) {
        console.error("Error loading ML evaluation:", err);
      }
    }
    loadModelData();
  }, []);

  const handleScenarioChange = (scKey: string) => {
    setActiveScenario(scKey);
    setFormData((prev) => ({
      ...prev,
      scenario: scKey,
    }));
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setPredicting(true);
      setPredictError(null);
      const res = await api.predict({
        ...formData,
        scenario: activeScenario,
        G1: activeScenario === "scenario_a" ? null : formData.G1,
        G2: activeScenario === "scenario_a" || activeScenario === "scenario_b" ? null : formData.G2,
      });
      setPrediction(res);
    } catch (err: any) {
      console.error("Prediction error:", err);
      setPredictError(err.message || "Failed to execute predictive inference");
    } finally {
      setPredicting(false);
    }
  };

  const presetHighAchiever = () => {
    setFormData((prev) => ({
      ...prev,
      course_code: "MAT",
      studytime: 3,
      failures: 0,
      absences: 1,
      G1: 16,
      G2: 17,
      higher: "yes",
      Walc: 1,
    }));
  };

  const presetAtRisk = () => {
    setFormData((prev) => ({
      ...prev,
      course_code: "MAT",
      studytime: 1,
      failures: 2,
      absences: 14,
      G1: 6,
      G2: 7,
      higher: "no",
      Walc: 4,
    }));
  };

  const scenarioMeta = [
    {
      id: "scenario_a",
      label: "Scenario A: Early Intake",
      subtext: "Pre-Grades (Anti-Target Leakage)",
      badge: "Intake Horizon (Wk 0-4)",
      badgeColor: "bg-emerald-50 text-emerald-700 border-emerald-200",
    },
    {
      id: "scenario_b",
      label: "Scenario B: Mid-Term",
      subtext: "Post-Period 1 (with G1)",
      badge: "Mid-Term Horizon (Month 3)",
      badgeColor: "bg-blue-50 text-blue-700 border-blue-200",
    },
    {
      id: "scenario_c",
      label: "Scenario C: Late-Stage",
      subtext: "Post-Period 2 (with G1 & G2)",
      badge: "Final Horizon (Month 7)",
      badgeColor: "bg-purple-50 text-purple-700 border-purple-200",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Predictive Intelligence & Multi-Horizon Machine Learning
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Scientifically sound, anti-target leakage predictive pipelines segmented across the student academic lifecycle.
        </p>
      </div>

      {/* Scenario Selection Tabs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {scenarioMeta.map((sc) => (
          <button
            key={sc.id}
            type="button"
            onClick={() => handleScenarioChange(sc.id)}
            className={`p-4 rounded-xl text-left border transition-all ${
              activeScenario === sc.id
                ? "bg-white border-indigo-600 ring-2 ring-indigo-500/20 shadow-sm"
                : "bg-white/80 border-slate-200 hover:bg-white text-slate-600"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${sc.badgeColor}`}>
                {sc.badge}
              </span>
              {activeScenario === sc.id && (
                <CheckCircle2 className="h-4 w-4 text-indigo-600" />
              )}
            </div>
            <p className="font-bold text-sm text-slate-900">{sc.label}</p>
            <p className="text-xs text-slate-500 mt-0.5">{sc.subtext}</p>
          </button>
        ))}
      </div>

      {/* Multi-Scenario Benchmark Comparison */}
      {evaluation && evaluation.scenarios && (
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <BrainCircuit className="h-4 w-4 text-indigo-600" />
                Multi-Horizon Benchmark Performance (Stratified 5-Fold Cross-Validation)
              </h2>
              <p className="text-xs text-slate-500">
                Audited metrics demonstrating authentic predictive lift as the academic year progresses
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100">
              {evaluation.framework}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 uppercase text-[10px] font-bold text-slate-400 border-y border-slate-200">
                <tr>
                  <th className="px-4 py-2.5">Evaluation Horizon</th>
                  <th className="px-4 py-2.5">Grades Used</th>
                  <th className="px-4 py-2.5">Best Classifier</th>
                  <th className="px-4 py-2.5">Test ROC-AUC</th>
                  <th className="px-4 py-2.5">5-Fold CV ROC-AUC</th>
                  <th className="px-4 py-2.5">Best Regressor</th>
                  <th className="px-4 py-2.5">MAE (Grade pts)</th>
                  <th className="px-4 py-2.5">R² Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {Object.entries(evaluation.scenarios).map(([scKey, sc]) => {
                  const bestClf = sc.best_classifier;
                  const clfData = sc.classification[bestClf];
                  const bestReg = sc.best_regressor;
                  const regData = sc.regression[bestReg];
                  const isCurrent = activeScenario === scKey;

                  const gradeStatus =
                    scKey === "scenario_a"
                      ? "Zero (Pre-Grades)"
                      : scKey === "scenario_b"
                      ? "G1 (Period 1)"
                      : "G1, G2 & Delta";

                  return (
                    <tr key={scKey} className={isCurrent ? "bg-indigo-50/50 font-semibold" : "hover:bg-slate-50/50"}>
                      <td className="px-4 py-3 font-bold text-slate-900 flex items-center gap-2">
                        {isCurrent && <Award className="h-3.5 w-3.5 text-indigo-600 shrink-0" />}
                        <span>{sc.scenario_name.split("—")[0]}</span>
                      </td>
                      <td className="px-4 py-3 text-slate-700">{gradeStatus}</td>
                      <td className="px-4 py-3 font-bold text-slate-800">{bestClf}</td>
                      <td className="px-4 py-3 font-bold text-indigo-700">{clfData.roc_auc.toFixed(3)}</td>
                      <td className="px-4 py-3 text-emerald-600">
                        {clfData.cv_roc_auc_mean ? clfData.cv_roc_auc_mean.toFixed(3) : "—"}
                      </td>
                      <td className="px-4 py-3 text-slate-700">{bestReg}</td>
                      <td className="px-4 py-3 text-slate-800 font-mono">{regData.mae.toFixed(2)} pts</td>
                      <td className="px-4 py-3 font-bold text-indigo-700 font-mono">{regData.r2.toFixed(3)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Interactive Prediction Simulation Engine */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Inputs */}
        <div className="lg:col-span-7 bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sliders className="h-4 w-4 text-indigo-600" />
                Live Student Risk Simulation
              </h2>
              <p className="text-xs text-slate-500">
                Testing inference for: <strong className="text-indigo-700">{scenarioMeta.find(s => s.id === activeScenario)?.label}</strong>
              </p>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={presetHighAchiever}
                className="px-2.5 py-1 text-xs font-semibold rounded bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition-colors"
              >
                Preset: Top Student
              </button>
              <button
                type="button"
                onClick={presetAtRisk}
                className="px-2.5 py-1 text-xs font-semibold rounded bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 transition-colors"
              >
                Preset: At Risk
              </button>
            </div>
          </div>

          <form onSubmit={handlePredict} className="space-y-4 text-xs">
            {/* Grades Section with Anti-Leakage notice */}
            <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800 flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5 text-indigo-600" />
                  Periodic Examination Marks
                </span>
                {activeScenario === "scenario_a" && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                    Excluded in Scenario A to prevent target leakage
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* G1 */}
                <div className={activeScenario === "scenario_a" ? "opacity-40 pointer-events-none" : ""}>
                  <div className="flex justify-between font-semibold text-slate-700 mb-1">
                    <span>Period 1 Grade (G1)</span>
                    <span className="font-bold text-indigo-600">{formData.G1 ?? 0} / 20</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="20"
                    disabled={activeScenario === "scenario_a"}
                    value={formData.G1 ?? 10}
                    onChange={(e) => setFormData({ ...formData, G1: parseInt(e.target.value) })}
                    className="w-full accent-indigo-600"
                  />
                </div>

                {/* G2 */}
                <div className={activeScenario !== "scenario_c" ? "opacity-40 pointer-events-none" : ""}>
                  <div className="flex justify-between font-semibold text-slate-700 mb-1">
                    <span>Period 2 Grade (G2)</span>
                    <span className="font-bold text-indigo-600">{formData.G2 ?? 0} / 20</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="20"
                    disabled={activeScenario !== "scenario_c"}
                    value={formData.G2 ?? 10}
                    onChange={(e) => setFormData({ ...formData, G2: parseInt(e.target.value) })}
                    className="w-full accent-indigo-600"
                  />
                </div>
              </div>
            </div>

            {/* Behavioral & Contextual Features */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Course Domain</label>
                <select
                  value={formData.course_code}
                  onChange={(e) => setFormData({ ...formData, course_code: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-medium"
                >
                  <option value="MAT">Mathematics (MAT)</option>
                  <option value="POR">Portuguese Language (POR)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Weekly Study Time: {formData.studytime === 1 ? "< 2 hrs" : formData.studytime === 2 ? "2-5 hrs" : formData.studytime === 3 ? "5-10 hrs" : "> 10 hrs"}
                </label>
                <input
                  type="range"
                  min="1"
                  max="4"
                  value={formData.studytime}
                  onChange={(e) => setFormData({ ...formData, studytime: parseInt(e.target.value) })}
                  className="w-full accent-indigo-600"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Past Academic Failures: {formData.failures}
                </label>
                <input
                  type="range"
                  min="0"
                  max="3"
                  value={formData.failures}
                  onChange={(e) => setFormData({ ...formData, failures: parseInt(e.target.value) })}
                  className="w-full accent-red-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  School Absences: {formData.absences} days
                </label>
                <input
                  type="range"
                  min="0"
                  max="40"
                  value={formData.absences}
                  onChange={(e) => setFormData({ ...formData, absences: parseInt(e.target.value) })}
                  className="w-full accent-amber-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Mother's Education: Tier {formData.Medu}/4
                </label>
                <input
                  type="range"
                  min="0"
                  max="4"
                  value={formData.Medu}
                  onChange={(e) => setFormData({ ...formData, Medu: parseInt(e.target.value) })}
                  className="w-full accent-indigo-600"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Weekend Alcohol Index: {formData.Walc}/5
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={formData.Walc}
                  onChange={(e) => setFormData({ ...formData, Walc: parseInt(e.target.value) })}
                  className="w-full accent-slate-600"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={predicting}
              className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-sm shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 mt-4 text-sm disabled:opacity-50"
            >
              {predicting ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Computing Inference Pipeline...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 text-amber-300" />
                  <span>Execute Model Inference ({activeScenario.toUpperCase()})</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Prediction Results Panel */}
        <div className="lg:col-span-5 bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 mb-1">
              Inference Forecast & Risk Profile
            </h2>
            <p className="text-xs text-slate-500 mb-4">
              Real-time model output evaluated under audited horizon constraints
            </p>

            {predictError && (
              <div className="p-3 rounded-lg bg-red-50 text-red-700 text-xs border border-red-200 mb-4">
                {predictError}
              </div>
            )}

            {!prediction ? (
              <div className="p-8 text-center border-2 border-dashed border-slate-200 rounded-xl text-slate-400 text-xs space-y-2">
                <BrainCircuit className="h-8 w-8 mx-auto text-slate-300" />
                <p className="font-semibold text-slate-600">No Inference Computed Yet</p>
                <p>Select a scenario horizon, adjust student inputs, and click "Execute Model Inference".</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Result Hero Card */}
                <div
                  className={`p-5 rounded-xl border ${
                    prediction.is_at_risk
                      ? "bg-red-50/70 border-red-200 text-red-900"
                      : "bg-emerald-50/70 border-emerald-200 text-emerald-900"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider">
                      {prediction.risk_tier}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-white/80 shadow-2xs">
                      {prediction.confidence_pct}% Confidence
                    </span>
                  </div>

                  <div className="mt-3 flex items-baseline justify-between">
                    <div>
                      <p className="text-[11px] text-slate-500">Predicted Final Grade (G3)</p>
                      <p className="text-3xl font-extrabold tracking-tight">
                        {prediction.predicted_grade_g3} <span className="text-base font-semibold text-slate-500">/ 20</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[11px] text-slate-500">Failure Risk</p>
                      <p className="text-xl font-bold">
                        {(prediction.risk_probability * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>

                  {/* Horizon tag */}
                  <div className="mt-3 pt-2 border-t border-black/5 flex items-center justify-between text-[11px]">
                    <span className="font-semibold">{prediction.scenario_used?.label}</span>
                    <span className="font-mono text-[10px] text-slate-500">
                      {prediction.scenario_used?.anti_leakage_status}
                    </span>
                  </div>

                  {/* Probability Bar */}
                  <div className="mt-2 w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        prediction.is_at_risk ? "bg-red-500" : "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.min(100, prediction.risk_probability * 100)}%` }}
                    />
                  </div>
                </div>

                {/* Recommendation */}
                <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                  <p className="font-bold text-slate-800 flex items-center gap-1.5">
                    <Info className="h-3.5 w-3.5 text-indigo-600" />
                    Recommended Institutional Action
                  </p>
                  <p className="text-slate-600 leading-relaxed">{prediction.recommendation}</p>
                </div>

                {/* Contributing Factors */}
                <div className="space-y-1.5 text-xs">
                  <p className="font-semibold text-slate-700">Driving Risk / Protective Factors:</p>
                  {prediction.contributing_factors.map((factor, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-slate-600">
                      <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                      <span>{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Model Ethics Footer */}
          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <ShieldAlert className="h-3.5 w-3.5 text-slate-400" />
              Advisory Decision Support Only
            </span>
            <span>Audited Anti-Leakage Protocol</span>
          </div>
        </div>
      </div>
    </div>
  );
};
