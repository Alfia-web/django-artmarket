from rest_framework.viewsets import GenericViewSet
from auction.models import *
from rest_framework import mixins
from auction.serializers import *

class PictureViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

class AuctionViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

class UserViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

class RateViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    queryset = Rate.objects.all()
    serializer_class = RateSerializer

class GenreViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer