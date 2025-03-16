from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if 'role_id' not in extra_fields:
            # Получаем или создаем роль админа
            admin_role, _ = Role.objects.get_or_create(name='admin')
            extra_fields['role_id'] = admin_role.id
            
        return self._create_user(username, email, password, **extra_fields)

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
    
    def __str__(self):
        return self.name

class Discount(models.Model):
    id = models.AutoField(primary_key=True)
    discount_rate = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
        
    def __str__(self):
        return f"{self.discount_rate}%"

class User(AbstractUser):
    objects = CustomUserManager()
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    driver_license = models.CharField(max_length=20, blank=True, null=True)
    completed_rentals = models.IntegerField(default=0)
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)

    def get_full_name(self):
        """
        Возвращает полное имя пользователя: Имя Отчество Фамилия
        """
        full_name = f"{self.first_name} {self.middle_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def __str__(self):
        return self.username

class Car(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступна'),
        ('in_rent', 'В аренде'),
        ('maintenance', 'На обслуживании'),
        ('pending', 'Ожидает подтверждения')
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Отличное'),
        ('good', 'Хорошее'),
        ('satisfactory', 'Удовлетворительное'),
        ('needs_repair', 'Требует ремонта')
    ]
    
    brand = models.CharField(max_length=100, verbose_name='Марка')
    model = models.CharField(max_length=100, verbose_name='Модель')
    year = models.IntegerField(verbose_name='Год выпуска')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за день')
    image = models.ImageField(upload_to='cars/', null=True, blank=True, verbose_name='Фото')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='excellent',
        verbose_name='Состояние'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

class Rental(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('approved', 'Подтверждена'),
        ('active', 'Активная'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
        ('rejected', 'Отклонена')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    personal_info = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_rentals')
    approved_at = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    return_condition = models.TextField(null=True, blank=True)
    return_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='return_approved_rentals')
    rejection_reason = models.TextField(null=True, blank=True)
    applied_discount = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренды'

    def __str__(self):
        return f"Rental #{self.id} - {self.car} by {self.user}"

class Maintenance(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершено')
    ]
    
    PRIORITY_CHOICES = [
        ('normal', 'Обычный'),
        ('high', 'Высокий')
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    completed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Maintenance for {self.car} on {self.maintenance_date}"

class Penalty(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='penalties')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Штраф'
        verbose_name_plural = 'Штрафы'
        
    def __str__(self):
        return f"Штраф {self.amount} руб. для аренды {self.rental.id}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    driver_license = models.CharField(max_length=20, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"