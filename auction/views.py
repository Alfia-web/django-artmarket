from rest_framework.decorators import action
from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Picture, Image, Profile, User, Auction
from .serializers import PictureSerializer, AlbumImageSerializer, AuctionSerializer
from rest_framework.viewsets import GenericViewSet

class PictureViewSet(viewsets.ModelViewSet):
    queryset = (Picture.objects.select_related('user', 'genre', 'auction', 'auction__winner')
                .prefetch_related('album_images'))
    serializer_class = PictureSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        qs = self.get_queryset().filter(user=request.user)
        return Response(self.get_serializer(qs, many=True).data)

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

            auction = Auction.objects.create(image=picture, start_price=start_price, start_time=start_time,
                                            end_time=end_time, status='pending')

        picture = self.get_queryset().get(pk=picture.pk)
        return Response(self.get_serializer(picture).data)

class AlbumImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = AlbumImageSerializer

class AuctionViewSet(viewsets.ModelViewSet):
    serializer_class = AuctionSerializer
    isAuth = IsAuthenticated

    queryset = Auction.objects.select_related('winner', 'image')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data) 