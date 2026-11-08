from rest_framework import serializers
from auction.models import Picture
from auction.models import Image
from auction.models import Genre
from auction.models import Auction
from auction.models import User
from auction.models import Rate
from auction.models import Auction

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"

class AlbumImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'picture', 'imageToAlbum']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'password', 'email', 'groups']

class AuctionSerializer(serializers.ModelSerializer):
    winner = UserSerializer(read_only=True)
    class Meta:
        model = Auction
        fields = ['id', 'start_price', 'start_time', 'end_time', 'winner', 'image']

class PictureSerializer(serializers.ModelSerializer):
    album_images = AlbumImageSerializer(many=True, read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all())
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    auction = AuctionSerializer(read_only=True)

    class Meta:
        model = Picture
        fields = ['id', 'name', 'author', 'genre', 'genre_name', 'user', 'image', 'album_images', 'auction']
        read_only_fields = ['user']

class RateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    auction = AuctionSerializer(read_only=True)
    class Meta:
        model = Rate
        fields = ['id', 'add_at', 'price', 'user', 'auction']