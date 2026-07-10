from .constants import GRADE_SCALE


def calculate_grade(attendance, assignment, test, exam=None):
    if exam is None:
        # backward-compat for old two-value use: (ca, exam)
        ca = attendance
        total = ca + assignment
    else:
        total = attendance + assignment + test + exam

    for threshold, grade, gp in GRADE_SCALE:
        if total >= threshold:
            return total, grade, gp
    return total, 'F', 0.0


def calculate_gpa(results):
    total_points = sum(r.grade_point * r.course.unit for r in results)
    total_units = sum(r.course.unit for r in results)
    return round((total_points / total_units) if total_units else 0, 2)
