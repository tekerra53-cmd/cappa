from app import create_app
from app.extensions import db
from app.models import Student, Result
app = create_app()
with app.app_context():
    students = Student.query.all()
    counts = [len(s.results) for s in students]
    from collections import Counter
    c = Counter(counts)
    print('Students total:', len(students))
    print('Result count histogram (per student):')
    for k in sorted(c.keys()):
        print(f' {k}: {c[k]} students')
    total = Result.query.count()
    print('Total results:', total)
    grades = [r.grade for r in Result.query.all()]
    print('Grade distribution:')
    print({g:grades.count(g) for g in sorted(set(grades))})
