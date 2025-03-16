from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Role, User, Car, Rental, Maintenance, Penalty, Discount, Profile
from django.utils import timezone

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        # Получаем или создаем роль клиента
        client_role, _ = Role.objects.get_or_create(name='client')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=client_role  # Устанавливаем роль клиента
        )
        return user

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'middle_name', 'last_name', 'email', 'phone', 'address', 'passport_number', 'driver_license', 'role', 'role_id', 'full_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def get_full_name(self, obj):
        return obj.get_full_name()

    def create(self, validated_data):
        role_id = validated_data.pop('role_id', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        if role_id:
            user.role_id = role_id
        user.save()
        return user

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            'id', 
            'brand', 
            'model', 
            'year', 
            'price_per_day', 
            'image', 
            'description', 
            'condition',
            'status'  # Заменяем is_available на status
        ]


class RentalSerializer(serializers.ModelSerializer):
    car_details = CarSerializer(source='car', read_only=True)
    
    class Meta:
        model = Rental
        fields = [
            'id', 'car', 'car_details', 'start_date', 'end_date', 
            'return_date', 'total_price', 'personal_info', 'status',
            'created_at', 'approved_at', 'return_condition', 'applied_discount'
        ]
        read_only_fields = ['status']

    def validate(self, data):
        # Проверяем, что дата начала меньше даты окончания
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                {"end_date": "Дата окончания должна быть позже даты начала"}
            )
        return data

    def create(self, validated_data):
        # Получаем текущего пользователя из контекста
        user = self.context['request'].user
        
        # Добавляем пользователя к данным
        validated_data['user'] = user
        
        # Устанавливаем начальный статус pending
        validated_data['status'] = 'pending'
        
        # Создаем объект аренды
        rental = super().create(validated_data)
        
        # Не меняем статус автомобиля пока аренда не подтверждена
        return rental

class RentalCreateSerializer(serializers.ModelSerializer):
    car_id = serializers.IntegerField(write_only=True)
    personal_info = serializers.JSONField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    applied_discount = serializers.IntegerField(default=0)

    class Meta:
        model = Rental
        fields = ['car_id', 'start_date', 'end_date', 'personal_info', 'total_price', 'applied_discount']

    def create(self, validated_data):
        car_id = validated_data.pop('car_id')
        try:
            car = Car.objects.get(id=car_id)
            user = self.context['request'].user
            
            rental = Rental.objects.create(
                car=car,
                user=user,
                start_date=validated_data['start_date'],
                end_date=validated_data['end_date'],
                total_price=validated_data['total_price'],
                personal_info=validated_data['personal_info'],
                status='pending',
                applied_discount=validated_data.get('applied_discount', 0)
            )
            return rental
        except Car.DoesNotExist:
            raise serializers.ValidationError({'car_id': 'Автомобиль не найден'})

class MaintenanceSerializer(serializers.ModelSerializer):
    car_details = CarSerializer(source='car', read_only=True)
    
    class Meta:
        model = Maintenance
        fields = ['id', 'car', 'car_details', 'maintenance_date', 'description', 'cost', 'status', 'priority', 'completed_date']

class PenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty
        fields = ['id', 'rental', 'amount', 'description', 'created_at', 'is_paid', 'paid_at']

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'discount_rate']



class RentalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['id', 'car', 'start_date', 'end_date', 'total_price', 'personal_info']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'middle_name', 'last_name', 'email', 'phone', 'address', 'passport_number', 'driver_license']

class RentalOperatorSerializer(serializers.ModelSerializer):
    car_details = CarSerializer(source='car', read_only=True)
    user_details = UserDetailSerializer(source='user', read_only=True)
    
    class Meta:
        model = Rental
        fields = ['id', 'car', 'car_details', 'user_details', 'start_date', 
                 'end_date', 'total_price', 'personal_info', 'status', 
                 'created_at', 'approved_by', 'approved_at', 'return_date', 
                 'return_condition', 'rejection_reason', 'applied_discount']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = instance.user
        
        # Получаем данные напрямую из модели User
        base_info = {
            'full_name': instance.personal_info.get('fullName') or user.get_full_name(),
            'phone': instance.personal_info.get('phone') or user.phone or '',
            'email': instance.personal_info.get('email') or user.email or '',
            'address': instance.personal_info.get('address') or user.address or '',
            'passport_data': instance.personal_info.get('passportNumber') or user.passport_number or '',
            'driver_license': instance.personal_info.get('driverLicense') or user.driver_license or ''
        }
        
        # Добавляем информацию в user_details
        if 'user_details' in data:
            data['user_details']['full_name'] = base_info['full_name']
            data['user_details']['phone'] = base_info['phone']
            data['user_details']['email'] = base_info['email']
            data['user_details']['address'] = base_info['address']
            data['user_details']['passport_data'] = base_info['passport_data']
            data['user_details']['driver_license'] = base_info['driver_license']
        
        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect credentials')


