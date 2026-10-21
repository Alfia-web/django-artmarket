from django.contrib import admin

from auction.models import Picture
from auction.models import Auction
from auction.models import Genre
from auction.models import Rate
from auction.models import Profile

# Register your models here.
@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ['name', 'image'] 

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_price', 'end_time']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ['id', 'auction', 'user', 'price', 'add_at']

@admin.register(Profile)
class Profile(admin.ModelAdmin):
    list_display = ['id', 'user', 'role']
