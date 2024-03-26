from django.contrib import admin

# Register your models here.
from .models import Export

class ExportAdmin(admin.ModelAdmin):
    list_display = ['type', 'timestamp' ,'latest']
    list_filter = ['type', 'timestamp' ,'latest']
admin.site.register(Export, ExportAdmin)
