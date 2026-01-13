from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указать Django settings как модуль по умолчанию
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

# Создать экземпляр Celery
app = Celery("foodgram")

# ЗАГРУЗИТЬ КОНФИГУРАЦИЮ ИЗ ОТДЕЛЬНОГО ФАЙЛА
app.config_from_object("foodgram.celeryconfig", namespace="CELERY")

# Автоматически находить задачи в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")