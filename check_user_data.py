import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RentalService.settings')
django.setup()

from rentApp.models import User

def check_user_data():
    print("Проверка данных пользователей в базе данных...")
    
    # Получаем всех пользователей
    users = User.objects.all()
    print(f"Найдено {users.count()} пользователей")
    
    for user in users:
        print(f"\nПользователь: {user.username}")
        print(f"ID: {user.id}")
        print(f"first_name: '{user.first_name}'")
        print(f"middle_name: '{user.middle_name}'")
        print(f"last_name: '{user.last_name}'")
        print(f"email: '{user.email}'")
        print(f"phone: '{user.phone}'")
        print(f"address: '{user.address}'")
        print(f"passport_number: '{user.passport_number}'")
        print(f"driver_license: '{user.driver_license}'")
        print(f"get_full_name(): '{user.get_full_name()}'")

if __name__ == "__main__":
    check_user_data() 