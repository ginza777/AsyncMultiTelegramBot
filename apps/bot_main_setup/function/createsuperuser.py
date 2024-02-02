import environ
from asgiref.sync import sync_to_async
from django.db import connection
from django.db.utils import ProgrammingError

env = environ.Env()
env.read_env()

print("SUPERUSER_USERNAME:", env.str("SUPERUSER_USERNAME"))
print("SUPERUSER_PASSWORD:", env.str("SUPERUSER_PASSWORD"))


@sync_to_async
def create_superuser():
    if "auth_user" in connection.introspection.table_names():
        username = env.str("SUPERUSER_USERNAME") or "admin"
        email = env.str("SUPERUSER_EMAIL") or "admin@gmail.com"
        password = env.str("SUPERUSER_PASSWORD") or "123"
        try:
            from django.contrib.auth.models import User

            # Check if the user already exists
            if not User.objects.filter(username=username).exists():
                # Create a new superuser
                User.objects.create_superuser(username, email, password)
                print(f"Superuser '{username}' created successfully.")
            else:
                print(f"Superuser '{username}' already exists.")
        except ProgrammingError:
            print("you must migrate")
