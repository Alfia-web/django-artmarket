# времят торгов
# размер ставки
# создание ставки
# определение победителя
# завершение аука

from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

from auction.models import Auction, Image, Rate


def checkAucTime(auction):
    now = timezone.now()

    if now < auction.start_time:
        raise ValidationError("Торги ещё не начались")
    
    if now >= auction.end_time:
        raise ValidationError("Торги уже завершены")

def getCurrentPrice(auction):
    lastRate = Rate.objects.filter(auction=auction).order_by('-price').first()

    if lastRate:
        return lastRate.price

    return auction.start_price

@transaction.atomic
def addRate(auction_id, user, price):
    auction = Auction.objects.filter(id=auction_id).first()
    checkAucTime(auction)
    currentPrice = getCurrentPrice(auction)

    price = Decimal(str(price))
    if price <= currentPrice:
        raise ValidationError("Ставка должна быть больше текущей цены")

    return Rate.objects.create(auction=auction, user=user, price=price)
   
@transaction.atomic
def finishAuc(auction_id):
    auction = Auction.objects.get(id=auction_id)
    now = timezone.now()

    if now < auction.end_time:
        raise ValidationError("Торги ещё не завершены")

    highestRate = Rate.objects.filter(auction=auction).order_by('-price', '-id').first()

    if highestRate:
        auction.winner = highestRate.user
        auction.save(update_fields=['winner'])

    return auction

def check_picture_edit_permission(image, user):
    if user.is_superuser: return

    if image.user_id != user.id:
        raise PermissionDenied("Нельзя изменять чужую картину")

    if Auction.objects.filter(image=image, start_time__lte=timezone.now()).exists():
        raise PermissionDenied('Нельзя изменять или удалять картину после начала торгов.')
