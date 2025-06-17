import csv
import os
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient
from django.conf import settings


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv'),
            help='Путь к CSV файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        if not os.path.exists(file_path):
            raise CommandError(f"Файл {file_path} не найден.")

        count = 0
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=["name", "measurement_unit"])
            for row in reader:
                name = row.get('name', '').strip()
                measurement_unit = row.get('measurement_unit', '').strip()
                if name and measurement_unit:
                    obj, created = Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    if created:
                        count += 1
        self.stdout.write(self.style.SUCCESS(f"Успешно загружено {count} ингредиентов из файла {file_path}"))