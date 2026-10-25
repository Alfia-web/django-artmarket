from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth import get_user_model
import random
import uuid
from django.core.files.base import ContentFile
import requests
from auction.models import Picture, Image, Genre
from auction.models import Picture


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, default=None)

    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])

        user = None
        if options['user']:
            User = get_user_model()
            user = User.objects.get(username=options['user'])

        genres = list(Genre.objects.all())

        for _ in range(10):
            name = fake.name()
            response =  requests.get('https://picsum.photos/800/600')
            if response.status_code==200:
                picture = Picture.objects.create(name=name, user=user, genre=random.choice(genres))
                img = Image(picture=picture)
                img.imageToAlbum.save(f"{uuid.uuid4().hex}.jpg",
                                        ContentFile(response.content), save=True)
        