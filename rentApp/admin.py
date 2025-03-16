from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, User, Profile, Car, Rental, Maintenance, Penalty, Discount

# Расширяем стандартную админку User, чтобы добавить все поля
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'middle_name', 'last_name', 'get_role', 'is_staff')
    
    def get_role(self, obj):
        return obj.role.name if hasattr(obj, 'role') and obj.role else '-'
    get_role.short_description = 'Роль'

    # Добавляем все поля в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {'fields': ('role', 'middle_name', 'phone', 'address', 'passport_number', 'driver_license')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительные поля', {'fields': ('role', 'middle_name', 'phone', 'address', 'passport_number', 'driver_license')}),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'price_per_day', 'status')
    list_filter = ('status', 'brand', 'year')
    search_fields = ('brand', 'model')
    list_editable = ('status',)

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'user', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('car__brand', 'car__model', 'user__username')
    list_editable = ('status',)

admin.site.register(Maintenance)
admin.site.register(Penalty)
admin.site.register(Discount)