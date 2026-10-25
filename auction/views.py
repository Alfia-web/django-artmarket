from rest_framework.decorators import action
from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Picture, Image, Profile, User
from .serializers import PictureSerializer, AlbumImageSerializer
from rest_framework.viewsets import GenericViewSet

class PictureViewSet(viewsets.ModelViewSet):
    queryset = Picture.objects.prefetch_related('album_images')
    serializer_class = PictureSerializer

    # добавляем отдельный api
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        qs = self.get_queryset().filter(user=request.user)
        return Response(self.get_serializer(qs, many=True).data)

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('photos')
      
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = request.user if request.user.is_authenticated else None
            picture = serializer.save(user=user)
            Image.objects.bulk_create(
                [Image(picture=picture, imageToAlbum=f) for f in files]
            )

        picture = self.get_queryset().get(pk=picture.pk)
        return Response(self.get_serializer(picture).data, status=201)

class AlbumImageViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = AlbumImageSerializer

