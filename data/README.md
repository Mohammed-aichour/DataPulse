# DataPulse — Dataset Documentation & Data Dictionary

## 1. Provenance and Attribution

- **Dataset Name**: Student Performance Dataset (Mathematics and Portuguese Language)
- **Source**: UCI Machine Learning Repository (Dataset ID: 320)
- **URL**: https://archive.ics.uci.edu/dataset/320/student+performance
- **Direct Archive**: `https://archive.ics.uci.edu/static/public/320/student+performance.zip`
- **Authors**: Paulo Cortez and Alice Silva (University of Minho, Guimarães, Portugal)
- **Citation**:
  > Cortez, P., & Silva, A. (2008). *Using Data Mining to Predict Secondary School Student Performance*. In A. de Carvalho et al. (Eds.), Proceedings of 5th FUture BUsiness TEChnology Conference (FUBUTEC 2008), pp. 5-12, Porto, Portugal, ISBN 978-9077381-39-7. EUROSIS.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).

---

## 2. Dataset Structure

The raw dataset consists of two CSV files with semicolon (`;`) delimiters:
- `student-mat.csv`: 395 student enrollment records in Secondary School Mathematics.
- `student-por.csv`: 649 student enrollment records in Secondary School Portuguese Language.
- **Total Course Records**: 1,044 enrollments.
- **Unique Physical Students**: 662 students identified across both courses using the 13 unique demographic/family linkage attributes (`school`, `sex`, `age`, `address`, `famsize`, `Pstatus`, `Medu`, `Fedu`, `Mjob`, `Fjob`, `reason`, `nursery`, `internet`). 382 students are enrolled in both courses.

---

## 3. Comprehensive Data Dictionary

| # | Attribute Name | Data Type | Domain / Allowed Values | Description & Academic Meaning |
|---|----------------|-----------|-------------------------|---------------------------------|
| 1 | `school` | String (Binary) | `'GP'`, `'MS'` | Student's school ('GP' - Gabriel Pereira, 'MS' - Mousinho da Silveira) |
| 2 | `sex` | String (Binary) | `'F'`, `'M'` | Student's biological sex ('F' - female, 'M' - male) |
| 3 | `age` | Integer | `15` to `22` | Student's age in years |
| 4 | `address` | String (Binary) | `'U'`, `'R'` | Student's home address type ('U' - urban, 'R' - rural) |
| 5 | `famsize` | String (Binary) | `'LE3'`, `'GT3'` | Family size ('LE3' - $\le 3$, 'GT3' - $> 3$) |
| 6 | `Pstatus` | String (Binary) | `'T'`, `'A'` | Parent's cohabitation status ('T' - living together, 'A' - apart) |
| 7 | `Medu` | Integer | `0` to `4` | Mother's education (0: none, 1: primary 4th grade, 2: 5th-9th grade, 3: secondary, 4: higher education) |
| 8 | `Fedu` | Integer | `0` to `4` | Father's education (0: none, 1: primary 4th grade, 2: 5th-9th grade, 3: secondary, 4: higher education) |
| 9 | `Mjob` | String | `'teacher'`, `'health'`, `'services'`, `'at_home'`, `'other'` | Mother's occupation |
| 10 | `Fjob` | String | `'teacher'`, `'health'`, `'services'`, `'at_home'`, `'other'` | Father's occupation |
| 11 | `reason` | String | `'home'`, `'reputation'`, `'course'`, `'other'` | Primary reason to choose this school |
| 12 | `guardian` | String | `'mother'`, `'father'`, `'other'` | Student's legal guardian |
| 13 | `traveltime` | Integer | `1` to `4` | Home to school travel time (1: <15 min, 2: 15-30 min, 3: 30 min-1 hour, 4: >1 hour) |
| 14 | `studytime` | Integer | `1` to `4` | Weekly study time (1: <2 hours, 2: 2-5 hours, 3: 5-10 hours, 4: >10 hours) |
| 15 | `failures` | Integer | `0` to `4` | Number of past class failures |
| 16 | `schoolsup` | String (Binary) | `'yes'`, `'no'` | Extra educational support from school |
| 17 | `famsup` | String (Binary) | `'yes'`, `'no'` | Family educational support |
| 18 | `paid` | String (Binary) | `'yes'`, `'no'` | Extra paid tutoring classes within course subject |
| 19 | `activities` | String (Binary) | `'yes'`, `'no'` | Extra-curricular activities participation |
| 20 | `nursery` | String (Binary) | `'yes'`, `'no'` | Attended nursery school in early childhood |
| 21 | `higher` | String (Binary) | `'yes'`, `'no'` | Aspires to pursue higher education |
| 22 | `internet` | String (Binary) | `'yes'`, `'no'` | Home Internet access |
| 23 | `romantic` | String (Binary) | `'yes'`, `'no'` | With a romantic relationship |
| 24 | `famrel` | Integer | `1` to `5` | Quality of family relationships (1: very bad to 5: excellent) |
| 25 | `freetime` | Integer | `1` to `5` | Free time after school (1: very low to 5: very high) |
| 26 | `goout` | Integer | `1` to `5` | Going out with friends (1: very low to 5: very high) |
| 27 | `Dalc` | Integer | `1` to `5` | Workday alcohol consumption (1: very low to 5: very high) |
| 28 | `Walc` | Integer | `1` to `5` | Weekend alcohol consumption (1: very low to 5: very high) |
| 29 | `health` | Integer | `1` to `5` | Current health status (1: very bad to 5: very good) |
| 30 | `absences` | Integer | `0` to `93` | Number of school absences |
| 31 | `G1` | Integer | `0` to `20` | First period grade (evaluation scale 0 - 20) |
| 32 | `G2` | Integer | `0` to `20` | Second period grade (evaluation scale 0 - 20) |
| 33 | `G3` | Integer | `0` to `20` | **Final Grade (Target variable)** (evaluation scale 0 - 20) |

---

## 4. Derived & Engineered Features

| Feature Name | Type | Formula / Definition | Purpose |
|--------------|------|----------------------|---------|
| `parent_edu_avg` | Float | `(Medu + Fedu) / 2.0` | Composite parental educational capital indicator |
| `alcohol_index` | Float | `(Dalc * 5 + Walc * 2) / 7.0` | Weekly weighted alcohol consumption index |
| `study_to_social_ratio`| Float | `studytime / (goout + freetime + 0.1)` | Balance between academic focus and leisure |
| `grade_delta` | Integer | `G2 - G1` | Academic performance trajectory across periods |
| `academic_risk` | Binary | `1 if G3 < 10 else 0` | Binary classification target: student failure risk |
| `passing_status`| Boolean | `G3 >= 10` | Standard Portuguese secondary passing threshold |
| `performance_tier`| String | `'Needs Support' (<10)`, `'Satisfactory' (10-13)`, `'Good' (14-15)`, `'Excellent' (16-20)` | Four-tier institutional academic ranking |

---

## 5. Known Limitations & Responsible AI Guidelines

1. **Contextual Scope**: The data originates from two secondary schools in Portugal (2005-2006). Cultural, curricular, and grading conventions apply to this specific context.
2. **Predictive Utility vs. Causation**: Machine learning models identify statistical correlations, not deterministic causation. High risk predictions must trigger supportive pedagogical interventions (tutoring, mentorship), never disciplinary or exclusionary actions.
3. **Sensitive Demographics**: Demographic attributes such as sex, home address, and family structure are audited for bias and should not be used in isolation to evaluate individual student merit.
