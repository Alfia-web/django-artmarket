from django.core.management.base import BaseCommand
from django.utils import timezone

from app.services import finishAuc
from auction.models import Auction

class Command(BaseCommand):
    def handle(self,  *args, **kwargs):
        now = timezone.now()

        auctions = Auction.objects.filter(end_time__lte=now, winner__isnull=True)

        for auction in auctions:
            finishAuc(auction.id)
