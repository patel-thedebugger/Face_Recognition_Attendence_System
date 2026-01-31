from django.contrib import admin

from .models import Branch, Semester, Batch, Subject, Lab


admin.site.register(Branch)

admin.site.register(Semester)
admin.site.register(Batch)
admin.site.register(Subject)
admin.site.register(Lab)