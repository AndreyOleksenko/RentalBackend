"""
URL configuration for RentalService project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rentApp.views import (RoleViewSet, UserViewSet, CarViewSet, RentalViewSet,
                         MaintenanceViewSet, PenaltyViewSet, 
                         DiscountViewSet, generate_agreement, OperatorRentalViewSet,
                         AccountingViewSet, car_financial_history)

# Создаем роутер и регистрируем наши ViewSet'ы
router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'users', UserViewSet)
router.register(r'cars', CarViewSet)
router.register(r'rentals', RentalViewSet, basename='rentals')
router.register(r'maintenance', MaintenanceViewSet)
router.register(r'penalties', PenaltyViewSet)
router.register(r'discounts', DiscountViewSet)
router.register(r'operator/rentals', OperatorRentalViewSet, basename='operator-rentals')
router.register(r'accounting', AccountingViewSet, basename='accounting')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('rentApp.urls')),
    path('api/cars/financial-history/', car_financial_history, name='car-financial-history'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
