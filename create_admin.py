import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

from core.models import User
from team2.models import UserDetails

# اطلاعات ادمین - می‌توانید این مقادیر را تغییر دهید
email = "admin@example.com"
password = "admin123"

# یا از command line arguments استفاده کنید
if len(sys.argv) >= 2:
    email = sys.argv[1]
if len(sys.argv) >= 3:
    password = sys.argv[2]

print(f"Creating admin user with email: {email}")

if not email or not password:
    print("ERROR: Email and password are required!")
    print("Usage: python create_admin.py <email> <password>")
    exit(1)

# بررسی اینکه آیا کاربر قبلاً وجود دارد
if User.objects.filter(email=email).exists():
    print(f"WARNING: User with email {email} already exists!")
    print("Updating user to admin...")
    user = User.objects.get(email=email)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
    print(f"SUCCESS: User {email} is now an admin!")
else:
    # ایجاد کاربر ادمین جدید
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name="Admin",
        last_name="User"
    )
    print(f"SUCCESS: Admin user {email} created successfully!")

# ایجاد UserDetails برای team2
try:
    user_details, created = UserDetails.objects.using('team2').get_or_create(
        user_id=user.id,
        defaults={
            'email': user.email,
            'role': 'teacher'
        }
    )
    if created:
        print(f"SUCCESS: UserDetails for {email} created in team2!")
    else:
        print(f"INFO: UserDetails for {email} already exists.")
        user_details.role = 'teacher'
        user_details.save(using='team2')
        print(f"SUCCESS: User role updated to teacher!")
except Exception as e:
    print(f"WARNING: Error creating UserDetails: {str(e)}")

print("\n" + "="*50)
print(f"SUCCESS: Admin user is ready to use!")
print(f"Email: {email}")
print(f"Password: {password}")
print("="*50)
print("\nYou can now login with these credentials.")
