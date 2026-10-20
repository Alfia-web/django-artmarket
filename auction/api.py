from rest_framework.viewsets import GenericViewSet
from auction.models import *
from rest_framework import mixins
from auction.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response

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

class ProfileViewset(GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, url_path="me", methods=['GET'])
    def get_me(self, request, *args, **kwargs ):
        data = {
            'is_authenticated': self.request.user.is_authenticated
        }

        if self.request.user.is_authenticated:
            data.update({
                "username": self.request.user.username,
                "id": self.request.user.id,
                "role": self.request.user.profile.role,
            })

        return Response(data=data)