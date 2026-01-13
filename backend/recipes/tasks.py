import os

from celery import shared_task
import requests


@shared_task(bind=True)
def hello_task(self, name: str = "world") -> dict:
    """
    Простой тестовый таск для проверки Celery.

    Args:
        name: Имя, которое попадёт в ответ.

    Returns:
        dict с сообщением и id таска.
    """
    return {
        "message": f"Hello, {name}!",
        "task_id": self.request.id,
    }

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def fetch_random_meal(self):
    """
    Получает случайное блюдо из TheMealDB.
    """
    api_key = os.getenv("apiMealDB")
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/random.php"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "source": "TheMealDB",
            "data": data,
            "task_id": self.request.id,
        }
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def fetch_random_cocktail(self):
    """
    Получает случайный коктейль из TheCocktailDB.
    """
    api_key = os.getenv('apiCocktailDB')
    url = f"https://www.thecocktaildb.com/api/json/v1/{api_key}/random.php"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "source": "TheCocktailDB",
            "data": data,
            "task_id": self.request.id,
        }
    except Exception as e:
        raise self.retry(exc=e)