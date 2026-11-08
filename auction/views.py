from rest_framework.decorators import action
from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Picture, Image, Profile, User, Auction
from .serializers import PictureSerializer, AlbumImageSerializer, AuctionSerializer

class PictureViewSet(viewsets.ModelViewSet):
    queryset = (Picture.objects.select_related('user', 'genre', 'auction', 'auction__winner')
                .prefetch_related('album_images'))
    serializer_class = PictureSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        qs = self.get_queryset().filter(user=request.user)
        return Response(self.get_serializer(qs, many=True).data)

class AlbumImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = AlbumImageSerializer

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.select_related('winner', 'image')
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated]