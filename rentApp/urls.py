from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RentalViewSet, 
    UserPenaltyViewSet, 
    generate_agreement,
    LoginView,
    RegisterView,
    ProfileView,
    pay_penalty,
    get_user_discount,
    debug_discount,
    debug_rental_data,
    car_financial_history,
    debug_rentals
)

router = DefaultRouter()
router.register(r'rentals', RentalViewSet, basename='rental')
router.register(r'penalties', UserPenaltyViewSet, basename='penalty')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('generate-agreement/', generate_agreement, name='generate-agreement'),
    path('penalties/<int:pk>/pay/', pay_penalty, name='pay-penalty'),
    path('auth/penalties/<int:pk>/pay/', pay_penalty, name='pay-penalty'),
    path('user/discount/', get_user_discount, name='user-discount'),
    path('user/debug-discount/', debug_discount, name='debug-discount'),
    path('user/debug-rentals/', debug_rentals, name='debug-rentals'),
    path('rentals/<int:rental_id>/debug/', debug_rental_data, name='debug-rental-data'),
    path('cars/financial-history/', car_financial_history, name='car-financial-history'),
    path('', include(router.urls)),
] 