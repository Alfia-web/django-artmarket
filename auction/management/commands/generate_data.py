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

        if options['user']:
            User = get_user_model()
            user = User.objects.get(username=options['user'])

        genres = list(Genre.objects.all())

        response = requests.get(
            'https://api.artic.edu/api/v1/artworks/search',
            params={
                "q": "painting",
                "limit": 10,
                "page": random.randint(1, 50),
                "fields": "id,title,artist_title,image_id,is_public_domain",
            },
            headers={"User-Agent": "auction_/1.0 (student project)"},
            timeout=15,
        )
        artworks = response.json()["data"]

        for _ in artworks[:10]:
            name = _["title"]
            image_id = _["image_id"]
            img_resp = requests.get(
                'https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg'.format(image_id=image_id),
                headers={"User-Agent": "auction-seed/1.0 (student project)"},
                timeout=30,
            )
            if img_resp.status_code==200:
                picture = Picture.objects.create(name=name, user=user, genre=random.choice(genres))
                img = Image(picture=picture)
                img.imageToAlbum.save(f"{uuid.uuid4().hex}.jpg", ContentFile(img_resp.content), save=True)
        