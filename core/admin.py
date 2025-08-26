from django.contrib import admin

from .models import Client, Project, Task, TimeEntry

admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(TimeEntry)
