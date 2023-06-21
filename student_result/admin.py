from django.contrib import admin
from .models import Session, Student, Semester, Exam, Result

admin.site.register(Session)
admin.site.register(Student)
admin.site.register(Semester)
admin.site.register(Exam)
admin.site.register(Result)
