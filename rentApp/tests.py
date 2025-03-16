from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import Rental, Car, Discount
from .views import calculate_discount

User = get_user_model()

class DiscountCalculationTest(TestCase):
    """
    Тест с подключением к базе данных для проверки функции расчета скидки
    """
    
    def setUp(self):
        # Создаем тестовые скидки
        Discount.objects.create(id=1, discount_rate=5)
        Discount.objects.create(id=2, discount_rate=10)
        Discount.objects.create(id=3, discount_rate=15)
        Discount.objects.create(id=4, discount_rate=20)
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Создаем тестовый автомобиль
        self.car = Car.objects.create(
            brand='Test Brand',
            model='Test Model',
            year=2023,
            price_per_day=100,
            condition='excellent',
            status='available'
        )
        
        # Текущая дата для тестов
        self.current_date = timezone.now()
    
    def create_completed_rentals(self, count, in_current_month=True):
        """Создает указанное количество завершенных аренд"""
        rentals = []
        
        for i in range(count):
            # Если аренды должны быть в текущем месяце, используем текущую дату
            # Иначе используем дату предыдущего месяца
            if in_current_month:
                return_date = self.current_date - timedelta(days=i)
            else:
                # Дата предыдущего месяца
                previous_month = self.current_date.replace(month=self.current_date.month - 1 if self.current_date.month > 1 else 12)
                return_date = previous_month - timedelta(days=i)
            
            rental = Rental.objects.create(
                user=self.user,
                car=self.car,
                start_date=return_date - timedelta(days=3),
                end_date=return_date - timedelta(days=1),
                return_date=return_date,
                total_price=300,
                personal_info={'name': 'Test User'},
                status='completed'
            )
            rentals.append(rental)
        
        return rentals
    
    def test_discount_calculation_with_different_rental_counts(self):
        """Тестирует расчет скидки с разным количеством аренд в текущем месяце"""
        
        # Тест 1: Нет аренд - скидка 0%
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 0)
        
        # Тест 2: 2 аренды в текущем месяце - скидка 0%
        self.create_completed_rentals(2)
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 0)
        
        # Тест 3: 3 аренды в текущем месяце - скидка 5%
        self.create_completed_rentals(1)  # Добавляем еще 1 к существующим 2
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 5)
        
        # Тест 4: 5 аренд в текущем месяце - скидка 10%
        self.create_completed_rentals(2)  # Добавляем еще 2 к существующим 3
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 10)
        
        # Тест 5: 10 аренд в текущем месяце - скидка 15%
        self.create_completed_rentals(5)  # Добавляем еще 5 к существующим 5
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 15)
        
        # Тест 6: 20 аренд в текущем месяце - скидка 20%
        self.create_completed_rentals(10)  # Добавляем еще 10 к существующим 10
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 20)
    
    def test_discount_calculation_only_counts_current_month(self):
        """Тестирует, что расчет скидки учитывает только аренды текущего месяца"""
        
        # Создаем 10 аренд в предыдущем месяце - они не должны учитываться
        self.create_completed_rentals(10, in_current_month=False)
        
        # Проверяем, что скидка 0%, так как нет аренд в текущем месяце
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 0)
        
        # Создаем 3 аренды в текущем месяце - должна быть скидка 5%
        self.create_completed_rentals(3)
        discount = calculate_discount(self.user)
        self.assertEqual(discount, 5)


class DateProcessingTest(TestCase):
    """
    Тест без подключения к базе данных для проверки логики обработки дат
    """
    
    def test_date_in_current_month_check(self):
        """Тестирует логику проверки, находится ли дата в текущем месяце"""
        
        # Текущая дата
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        # Тест 1: Дата в текущем месяце
        date_in_current_month = datetime(current_year, current_month, 15)
        self.assertTrue(
            date_in_current_month.month == current_month and 
            date_in_current_month.year == current_year
        )
        
        # Тест 2: Дата в предыдущем месяце
        previous_month = current_month - 1 if current_month > 1 else 12
        previous_year = current_year if current_month > 1 else current_year - 1
        date_in_previous_month = datetime(previous_year, previous_month, 15)
        self.assertFalse(
            date_in_previous_month.month == current_month and 
            date_in_previous_month.year == current_year
        )
        
        # Тест 3: Дата в следующем месяце
        next_month = current_month + 1 if current_month < 12 else 1
        next_year = current_year if current_month < 12 else current_year + 1
        date_in_next_month = datetime(next_year, next_month, 15)
        self.assertFalse(
            date_in_next_month.month == current_month and 
            date_in_next_month.year == current_year
        )
    
    def test_date_string_parsing(self):
        """Тестирует парсинг строк с датами в разных форматах"""
        
        # Тест 1: ISO формат
        iso_date_str = "2023-03-15T12:30:45+00:00"
        try:
            date_obj = datetime.fromisoformat(iso_date_str)
            self.assertEqual(date_obj.year, 2023)
            self.assertEqual(date_obj.month, 3)
            self.assertEqual(date_obj.day, 15)
        except ValueError:
            self.fail("Не удалось распарсить ISO дату")
        
        # Тест 2: Формат с Z в конце
        z_date_str = "2023-03-15T12:30:45Z"
        try:
            date_obj = datetime.fromisoformat(z_date_str.replace('Z', '+00:00'))
            self.assertEqual(date_obj.year, 2023)
            self.assertEqual(date_obj.month, 3)
            self.assertEqual(date_obj.day, 15)
        except ValueError:
            self.fail("Не удалось распарсить дату с Z")
        
        # Тест 3: Простой формат даты
        simple_date_str = "2023-03-15"
        try:
            date_obj = datetime.strptime(simple_date_str, '%Y-%m-%d')
            self.assertEqual(date_obj.year, 2023)
            self.assertEqual(date_obj.month, 3)
            self.assertEqual(date_obj.day, 15)
        except ValueError:
            self.fail("Не удалось распарсить простую дату")
