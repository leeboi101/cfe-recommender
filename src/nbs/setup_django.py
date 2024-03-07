import os
import sys

DJANGO_SETTINGS_MODULE = "cfehome.settings"

def init():
    PWD = os.getenv("PWD")
    if PWD is None:
        # Set PWD to the desired directory path if it's not set
        PWD = ".."
        print("PWD environment variable is not set. Setting it to:", PWD)
    
    os.chdir(PWD)
    sys.path.insert(0, PWD)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    import django
    django.setup()