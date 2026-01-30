import os

def fix_file(path, replacements):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {path}")
    else:
        print(f"No changes needed or found for: {path}")

# Fix chat.html
fix_file(r'templates\content\chat.html', [
    ('{{ user.is_staff| yesno: "true,false"\n    }} || {{ user.is_teacher | yesno: "true,false" }}', 
     '{{ user.is_staff|yesno:"true,false" }} || {{ user.is_teacher|yesno:"true,false" }}')
])

# Fix home.html
fix_file(r'templates\main\home.html', [
    ('{{ user.is_staff| yesno: "true,false"\n                }\n            } || {{ user.is_teacher | yesno: "true,false" }}', 
     '{{ user.is_staff|yesno:"true,false" }} || {{ user.is_teacher|yesno:"true,false" }}')
])

# Fix forum_thread_detail.html
fix_file(r'templates\content\forum_thread_detail.html', [
    ('{% if thread.year %}<span class="badge badge-year">{% trans "Year" %} {{ thread.year }}</span>{% endif\n                %}', 
     '{% if thread.year %}<span class="badge badge-year">{% trans "Year" %} {{ thread.year }}</span>{% endif %}')
])

# Fix notifications.html
fix_file(r'templates\content\notifications.html', [
    ('{% blocktrans %}{{ notification.created_at|timesince }} ago{%\n                        endblocktrans %}', 
     '{% blocktrans %}{{ notification.created_at|timesince }} ago{% endblocktrans %}')
])
