from django.contrib import admin
from .models import TestOrder, OrderPayStatus

# Register your models here.

# @admin.register(TestOrder)
# class TestOrderAdmin(admin.ModelAdmin):
#

admin.site.register(TestOrder)
admin.site.register(OrderPayStatus)
