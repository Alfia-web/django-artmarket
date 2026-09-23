from rest_framework import serializers
from auction.models import Image
from auction.models import Genre
from auction.models import Auction
from auction.models import User
from auction.models import Rate

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"

class ImageSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)
    class Meta:
        model = Image
        fields = ['id', 'name', 'image', 'genre']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'password', 'email', 'groups']

class AuctionSerializer(serializers.ModelSerializer):
    winner = UserSerializer(read_only=True)
    class Meta:
        model = Auction
        fields = ['id', 'start_price', 'start_time', 'end_time', 'status', 'winner']

class RateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    auction = AuctionSerializer(read_only=True)
    class Meta:
        model = Rate
        fields = ['id', 'add_at', 'price', 'user', 'auction']