# времят торгов
# размер ставки
# создание ставки
# определение победителя
# завершение аука

from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from requests import Response
from rest_framework.exceptions import ValidationError

from auction.models import Auction, Image, Rate

def create(self, request, *args, **kwargs):
    files = request.FILES.getlist('photos')

    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    start_price = request.data.get('start_price')
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')

    with transaction.atomic():
        user = request.user if request.user.is_authenticated else None
        picture = serializer.save(user=user)
        Image.objects.bulk_create(
            [Image(picture=picture, imageToAlbum=f) for f in files])

        auction = Auction.objects.create(
            image=picture, 
            start_price=start_price, 
            start_time=start_time,
            end_time=end_time,)

    picture = self.get_queryset().get(pk=picture.pk)
    return Response(self.get_serializer(picture).data)

def checkAucTime(auction):
    now = timezone.now()

    if now < auction.start_time:
        raise ValidationError("Торги ещё не начались")
    else:
        raise ValidationError("Торги уже завершены")

def getCurrentPrice(auction):
    lastRate = Rate.object.filter(auction=auction).order_by('-price', '-id').first()

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
 