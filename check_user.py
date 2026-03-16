import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studybud.settings")
django.setup()

from django.contrib.auth import authenticate
from base.models import User

email = "shubhamarboel@gmail.com"
password = "62106210"

user = User.objects.filter(email=email).first()
if user:
    print(f"User {email} found.")
    print(f"Is active: {user.is_active}")
    print(f"Password set: {user.has_usable_password()}")
    
    auth_user = authenticate(email=email, password=password)
    if auth_user:
        print("Authentication Successful!")
    else:
        print("Authentication Failed!")
else:
    print(f"User {email} NOT found.")
    print("Creating user...")
    user = User.objects.create_user(email=email, password=password)
    print("User created successfully!")
    auth_user = authenticate(email=email, password=password)
    if auth_user:
        print("Authentication after creation Successful!")
    else:
        print("Authentication after creation Failed!")
