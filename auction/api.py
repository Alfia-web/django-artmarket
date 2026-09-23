from rest_framework.viewsets import GenericViewSet
from auction.models import Image
from rest_framework import mixins
from auction.serializers import ImageSerializer

class ImageViewset(mixins.ListModelMixin, GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer