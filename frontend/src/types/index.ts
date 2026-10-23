export interface HealthInfo {
  status: string;
  timestamp: string;
  database: string;
  ml_models: string;
  version: string;
}

export interface OverviewKPIs {
  total_students: number;
  total_enrollments: number;
  avg_final_grade: number;
  pass_rate_pct: number;
  risk_count: number;
  risk_rate_pct: number;
  avg_absences: number;
  data_quality_score: number;
  courses_count: number;
  last_pipeline_run: string | null;
}

export interface CoursePerformance {
  course_code: string;
  course_name: string;
  department: string;
  enrollments: number;
  avg_g1: number;
  avg_g2: number;
  avg_g3: number;
  avg_absences: number;
  avg_studytime: number;
  avg_failures: number;
  pass_rate_pct: number;
}

export interface GradeDistributionBin {
  grade_range: string;
  period_1: number;
  period_2: number;
  final_g3: number;
}

export interface FactorPerformance {
  factor_group: string;
  student_count: number;
  avg_grade: number;
  pass_rate_pct: number;
  risk_rate_pct: number;
}

export interface CorrelationItem {
  feature: string;
  label: string;
  correlation: number;
  impact: string;
  magnitude: string;
}

export interface StudentListItem {
  id: number;
  student_id: string;
  school: string;
  sex: string;
  age: number;
  address: string;
  courses: string[];
  final_grades: Record<string, number>;
  is_at_risk: boolean;
  performance_tier: string;
}

export interface StudentRecordSummary {
  record_id: string;
  course_code: string;
  g1: number;
  g2: number;
  g3: number;
  studytime: number;
  failures: number;
  absences: number;
  academic_risk: number;
  passing_status: boolean;
  performance_tier: string;
}

export interface StudentDetail {
  id: number;
  student_id: string;
  school: string;
  sex: string;
  age: number;
  address: string;
  famsize: string;
  pstatus: string;
  medu: number;
  fedu: number;
  mjob: string;
  fjob: string;
  reason: string;
  guardian: string;
  nursery: string;
  internet: string;
  enrollments: StudentRecordSummary[];
}

export interface PaginatedStudents {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: StudentListItem[];
}

export interface PredictionRequest {
  course_code: string;
  school: string;
  sex: string;
  age: number;
  address: string;
  famsize: string;
  Pstatus: string;
  Medu: number;
  Fedu: number;
  Mjob: string;
  Fjob: string;
  reason: string;
  guardian: string;
  traveltime: number;
  studytime: number;
  failures: number;
  schoolsup: string;
  famsup: string;
  paid: string;
  activities: string;
  nursery: string;
  higher: string;
  internet: string;
  romantic: string;
  famrel: number;
  freetime: number;
  goout: number;
  Dalc: number;
  Walc: number;
  health: number;
  absences: number;
  G1?: number | null;
  G2?: number | null;
  scenario?: string;
}

export interface PredictionResponse {
  predicted_grade_g3: number;
  is_at_risk: boolean;
  risk_probability: number;
  risk_tier: string;
  confidence_pct: number;
  recommendation: string;
  contributing_factors: string[];
  scenario_used: {
    key: string;
    label: string;
    anti_leakage_status: string;
  };
  model_used: {
    classifier: string;
    regressor: string;
  };
  timestamp: string;
}

export interface ModelEvaluation {
  framework?: string;
  active_default_scenario?: string;
  scenarios?: Record<string, {
    scenario_name: string;
    description: string;
    features_used: string[];
    best_classifier: string;
    best_regressor: string;
    classification: Record<string, any>;
    regression: Record<string, any>;
    feature_importance: Record<string, number>;
  }>;
  best_classifier: string;
  best_regressor: string;
  classification_comparison: Record<string, {
    model_name: string;
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    cv_roc_auc_mean: number;
    cv_roc_auc_std: number;
    confusion_matrix: number[][];
  }>;
  regression_comparison: Record<string, {
    model_name: string;
    mae: number;
    rmse: number;
    r2: number;
  }>;
  top_features: Record<string, number>;
  dataset_split: {
    train_samples: number;
    test_samples: number;
  };
  trained_at: string;
  responsible_ai_notice: string;
}

export interface PipelineStatus {
  is_operational: boolean;
  latest_run: {
    id: number | null;
    timestamp: string | null;
    status: string;
    duration_seconds: number;
    quality_score: number;
  };
  database_counts: {
    students: number;
    academic_records: number;
    courses: number;
    data_imports: number;
  };
}

export interface PipelineHistoryItem {
  id: number;
  timestamp: string;
  status: string;
  duration_seconds: number;
  records_processed: number;
  quality_score: number;
  details: string;
}
