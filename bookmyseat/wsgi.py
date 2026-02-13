import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')

app = get_wsgi_application()


# -------- AUTO CREATE SUPERUSER (SAFE FOR VERCEL) --------
def create_superuser():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if username and email and password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)

create_superuser()
# ---------------------------------------------------------
