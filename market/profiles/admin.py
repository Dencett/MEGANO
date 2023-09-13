from django.contrib import admin
from .models import Profile, User


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "get_username",
        "phone_number",
        "residence",
        "address",
    )
    list_display_links = (
        "pk",
        "get_username",
    )
    ordering = ("pk",)
    search_fields = (
        "pk",
        "residence",
    )
    fieldsets = [
        (None, {"fields": ("user",), "classes": ("collapse",)}),
        (
            "Personal information",
            {
                "fields": ("phone_number", "residence"),
                "classes": (
                    "wide",
                    "collapse",
                ),
            },
        ),
        (
            "Extra options",
            {
                "fields": ("address",),
                "classes": ("collapse",),
                "description": "Extra options. The 'address' field is intended for additional information",
            },
        ),
    ]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Временная модель для Пользователей в админке. В разработке.
    fields = ["username", "email", "first_name", "last_name", "is_superuser", "is_staff", "password"]
