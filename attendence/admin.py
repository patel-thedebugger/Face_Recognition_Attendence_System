from django.contrib import admin

from .models import *


admin.site.register(Branch)

admin.site.register(Semester)
admin.site.register(Batch)
admin.site.register(Subject)
admin.site.register(Lab)
admin.site.register(FacultySubject)
admin.site.register(StudentSubject)
admin.site.register(Attendance)