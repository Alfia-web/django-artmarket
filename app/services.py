from decimal import Decimal

from django.db import transaction
from django.utils import timezone
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

    if auction.image.user_id == user.id:
        raise ValidationError('Нельзя делать ставки на собственную картину')

    return Rate.objects.create(auction=auction, user=user, price=price)
   
def check_picture_edit_permission(image, user):
    if user.is_superuser: return

    if image.user_id != user.id:
        raise PermissionDenied("Нельзя изменять чужую картину")

    if Auction.objects.filter(image=image, start_time__lte=timezone.now()).exists():
        raise PermissionDenied('Нельзя изменять или удалять картину после начала торгов')

def getAuctionWinner(auction):
    rate = Rate.objects.filter(auction=auction).select_related('user').order_by('-price', '-id').first()
    
    if rate is None:
        return None

    return rate

def sortedRaiting(user):
    return -user['total_spent']

def getRaiting():
    raiting = {}
    now = timezone.now()

    for auction in Auction.objects.all():
        if auction.end_time > now or auction.end_time is None:
            continue

        rate = getAuctionWinner(auction)

        if rate is None: continue

        user_id = rate.user.id

        if user_id not in raiting:
            raiting[user_id] = {
                'user_id': user_id,
                'username': rate.user.username,
                'total_spent': 0,
                'auctions_won': 0
            }

        raiting[user_id]['total_spent'] += rate.price
        raiting[user_id]['auctions_won'] += 1

    return sorted(raiting.values(), key=sortedRaiting)