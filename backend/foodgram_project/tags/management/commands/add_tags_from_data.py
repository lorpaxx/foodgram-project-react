import csv
import os

from django.core.management.base import BaseCommand

from foodgram_project.settings import BASE_DIR
from tags.models import Tag


class Command(BaseCommand):
    help = 'Копирование данных из csv'
    shift_path = os.path.join(BASE_DIR, 'start_data')

    def handle(self, *args, **kwargs):
        '''
        Основная функция выполнения команды.
        '''
        print(self.shift_path)
        filename = os.path.join(self.shift_path, 'tags.csv')
        with open(filename, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f, delimiter=',', quotechar='"')
            for row in csv_reader:
                name = row[0]
                color = row[1]
                slug = row[2]
                tag = Tag.objects.create(
                    name=name, color=color, slug=slug
                )
                print(tag)
        print('ADD', Tag.objects.count(), 'tags')
