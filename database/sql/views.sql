-- DataPulse Analytical SQL Views
-- Designed for complete cross-compatibility with PostgreSQL 16 and SQLite 3.
-- Uses standard ANSI SQL constructs, explicit NUMERIC casting for ROUND(), and CTE binning.

-- 1. Student Academic Overview View
CREATE VIEW IF NOT EXISTS v_student_overview AS
SELECT 
    s.student_id,
    s.school,
    s.sex,
    s.age,
    s.address,
    s.famsize,
    s.pstatus,
    s.medu,
    s.fedu,
    s.mjob,
    s.fjob,
    s.guardian,
    s.internet,
    c.course_code,
    c.course_name,
    r.record_id,
    r.studytime,
    r.failures,
    r.schoolsup,
    r.famsup,
    r.paid,
    r.higher,
    r.absences,
    r.g1,
    r.g2,
    r.g3,
    r.parent_edu_avg,
    r.alcohol_index,
    r.study_to_social_ratio,
    r.grade_delta,
    r.academic_risk,
    r.passing_status,
    r.performance_tier
FROM students s
JOIN academic_records r ON s.student_id = r.student_id
JOIN courses c ON r.course_id = c.id;

-- 2. Course Performance Aggregate View
CREATE VIEW IF NOT EXISTS v_course_performance AS
SELECT 
    c.course_code,
    c.course_name,
    COUNT(r.id) AS total_enrollments,
    ROUND(CAST(AVG(r.g1) AS NUMERIC), 2) AS avg_g1,
    ROUND(CAST(AVG(r.g2) AS NUMERIC), 2) AS avg_g2,
    ROUND(CAST(AVG(r.g3) AS NUMERIC), 2) AS avg_g3,
    ROUND(CAST(100.0 * SUM(CASE WHEN r.g3 >= 10 THEN 1 ELSE 0 END) / COUNT(r.id) AS NUMERIC), 2) AS pass_rate_pct,
    ROUND(CAST(100.0 * SUM(CASE WHEN r.academic_risk = 1 THEN 1 ELSE 0 END) / COUNT(r.id) AS NUMERIC), 2) AS risk_rate_pct,
    ROUND(CAST(AVG(r.absences) AS NUMERIC), 2) AS avg_absences,
    ROUND(CAST(AVG(r.studytime) AS NUMERIC), 2) AS avg_studytime,
    ROUND(CAST(AVG(r.failures) AS NUMERIC), 2) AS avg_failures
FROM courses c
JOIN academic_records r ON c.id = r.course_id
GROUP BY c.course_code, c.course_name;

-- 3. Risk Factor Analysis View
CREATE VIEW IF NOT EXISTS v_risk_analysis AS
SELECT 
    r.academic_risk,
    CASE WHEN r.academic_risk = 1 THEN 'At Risk (G3 < 10)' ELSE 'Passing (G3 >= 10)' END AS risk_category,
    COUNT(r.id) AS student_count,
    ROUND(CAST(AVG(r.g3) AS NUMERIC), 2) AS avg_final_grade,
    ROUND(CAST(AVG(r.failures) AS NUMERIC), 2) AS avg_past_failures,
    ROUND(CAST(AVG(r.studytime) AS NUMERIC), 2) AS avg_study_time,
    ROUND(CAST(AVG(r.absences) AS NUMERIC), 2) AS avg_absences,
    ROUND(CAST(AVG(r.alcohol_index) AS NUMERIC), 2) AS avg_alcohol_index,
    ROUND(CAST(AVG(r.parent_edu_avg) AS NUMERIC), 2) AS avg_parent_education
FROM academic_records r
GROUP BY r.academic_risk;

-- 4. School Absence Impact View (Uses CTE for ANSI GROUP BY compatibility)
CREATE VIEW IF NOT EXISTS v_absence_impact AS
WITH binned_absences AS (
    SELECT 
        CASE 
            WHEN absences = 0 THEN '0 Days (Perfect Attendance)'
            WHEN absences BETWEEN 1 AND 5 THEN '1 - 5 Days (Low Absences)'
            WHEN absences BETWEEN 6 AND 10 THEN '6 - 10 Days (Moderate Absences)'
            WHEN absences BETWEEN 11 AND 20 THEN '11 - 20 Days (Elevated Absences)'
            ELSE '21+ Days (Severe Chronic Absenteeism)'
        END AS absence_tier,
        g3
    FROM academic_records
)
SELECT 
    absence_tier,
    COUNT(*) AS student_count,
    ROUND(CAST(AVG(g3) AS NUMERIC), 2) AS avg_final_grade,
    ROUND(CAST(100.0 * SUM(CASE WHEN g3 >= 10 THEN 1 ELSE 0 END) / COUNT(*) AS NUMERIC), 2) AS pass_rate_pct
FROM binned_absences
GROUP BY absence_tier;

-- Backward compatibility alias
CREATE VIEW IF NOT EXISTS v_attendance_impact AS
SELECT * FROM v_absence_impact;

-- 5. Performance Tier Distribution View
CREATE VIEW IF NOT EXISTS v_performance_distribution AS
SELECT 
    r.performance_tier,
    COUNT(r.id) AS student_count,
    ROUND(CAST(100.0 * COUNT(r.id) / (SELECT COUNT(*) FROM academic_records) AS NUMERIC), 2) AS percentage_of_total,
    ROUND(CAST(AVG(r.g3) AS NUMERIC), 2) AS avg_grade
FROM academic_records r
GROUP BY r.performance_tier;
