import os
import django
from django.conf import settings
from django.template import Template, Engine

# Minimal Django configuration for template validation
if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [r'c:\Users\EXPERT INFO\.gemini\antigravity\scratch\afaqblog\templates'],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
    )
    django.setup()

def validate_templates():
    engine = Engine.get_default()
    root = r'c:\Users\EXPERT INFO\.gemini\antigravity\scratch\afaqblog\templates'
    errors = []
    
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.html'):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    Template(content, engine=engine)
                except Exception as e:
                    errors.append(f"{path}: {e}")
                    
    if errors:
        print("ERRORS FOUND:")
        for err in errors:
            print(err)
    else:
        print("ALL TEMPLATES OK")

if __name__ == "__main__":
    validate_templates()
