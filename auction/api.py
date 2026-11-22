from django.db import transaction
from rest_framework.viewsets import GenericViewSet
from auction.models import *
from rest_framework import mixins
from auction.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets
from rest_framework import pagination
from app.services import getCurrentPrice, addRate, getAuctionWinner, getRaiting
from django.utils import timezone
from app.services import check_picture_edit_permission
from openpyxl import Workbook

class PictureViewSet(viewsets.ModelViewSet):
    queryset = (Picture.objects
        .select_related('user', 'genre', 'auction', 'auction__winner').prefetch_related('album_images').order_by('-id'))
    serializer_class = PictureSerializer
    pagination_class = pagination.PageNumberPagination
    
    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('photos')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            extra = {}
            if 'image' not in request.FILES and files:
                extra['image'] = files[0]

            picture = serializer.save(user=request.user, **extra)

            if files:
                Image.objects.bulk_create(
                    [Image(picture=picture, imageToAlbum=f) for f in files]
                )

            start_price = request.data.get('start_price')
            start_time = request.data.get('start_time')
            end_time = request.data.get('end_time')

            if start_price and start_time and end_time:
                Auction.objects.create(
                    image=picture,
                    start_price=start_price,
                    start_time=start_time,
                    end_time=end_time,
                )

        picture = Picture.objects.get(pk=picture.pk)
        return Response(self.get_serializer(picture).data)

    def get_queryset(self):
        queryset = super().get_queryset()
        now = timezone.now()
        status = self.request.query_params.get('status')

        if status == 'soon':
            queryset = queryset.filter(auction__start_time__gt=now)
        elif status == 'active':
            queryset = queryset.filter(auction__start_time__lte=now, auction__end_time__gt=now)
        elif status == 'finished':
            queryset = queryset.filter(auction__end_time__lte=now)

        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre_id=genre)

        return queryset

    def update(self, request, *args, **kwargs):
        image = self.get_object()
        check_picture_edit_permission(image, request.user)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        image = self.get_object()
        check_picture_edit_permission(image, request.user)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, url_path="my", methods=['GET'], permission_classes=[IsAuthenticated])
    def my_picture(self, request):
        user_pictures = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(user_pictures)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
    
        serializer = self.get_serializer(user_pictures, many=True)
        return Response(serializer.data)

    @action(detail=False,  url_path='export/excel',methods=['GET'])
    def export_exel(self, request):
        pictures = self.get_queryset()

        wb = Workbook
        ws = wb.active
        ws.title = 'Слоты. Картины'

        ws.append([
            'ID', 
            'Название',
            'Автор',
            'Жанр',
            'Владелец',
            'Цена',
            'Начало аукциона',
            'Окончание аукциона',
        ])

        for picture in pictures:
            auction = getattr(picture, 'auction', None)

            ws.append([
                picture.id, 
                picture.name, 
                picture.author,
                picture.genre.name,
                picture.user.username,
                str(auction.start_time),
                str(auction.end_time),
                str(auction.start_price)
            ])

class AlbumImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = AlbumImageSerializer

class AuctionViewset(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
    ):
    queryset = Auction.objects.select_related('winner', 'image')
    serializer_class = AuctionSerializer
    
    @action(detail=True, url_path="winner", methods=['GET'])
    def get_winner(self, request, pk=None):
        auction = self.get_object()

        if timezone.now() < auction.end_time:
            return Response(
                {'error': 'Аукцион ещё не завершён'}
            )

        rate = getAuctionWinner(auction)

        if rate is None:
            auction.winner = None
            auction.save(update_fields=['winner'])

            return Response({
            'auction_id': auction.id,
            'winner': None,
            'message': 'На аукцион не поступило ставок'
        })

        auction.winner = rate.user
        auction.save(update_fields=['winner'])

        return Response({
            'auction_id': auction.id,
            'winner': {
                'id': rate.user.id,
                'username': rate.user.username
            },
            'winning_price': str(rate.price)
        })

    @action(detail=False, url_path="raiting", methods=['GET'])
    def get_raiting(self, request):
        raiting = getRaiting()     
        return Response(raiting)   

class UserViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        
        # фильтруем по текущему юзеру
        qs = qs.filter(user=self.request.user)

        return qs

class RateViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    permission_classes = [IsAuthenticated]
    queryset = Rate.objects.select_related('user', 'auction', 'auction__winner', 'auction__image')
    serializer_class = RateSerializer

    @action(detail=False, url_path="auction/(?P<auction_id>[^/.]+)", methods=['GET'])
    def get_rates(self, request, auction_id=None):
        auction = Auction.objects.filter(id=auction_id).first()
        rates = self.get_queryset().filter(auction_id=auction_id).order_by('-price')
        rates_data = []

        for rate in rates:
            rates_data.append({
                'id': rate.id,
                'price': str(rate.price),
                'add_at': rate.add_at,
                'user': rate.user.username 
            })    

        return Response({
            'auction_id': auction_id,
            'current_price': str(getCurrentPrice(auction)),
            'rates': rates_data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auction = serializer.validated_data['auction']
        price = serializer.validated_data['price']

        rate = addRate(
            auction.id, 
            request.user, 
            price)
        
        return Response(self.get_serializer(rate).data)

class GenreViewset(
    mixins.ListModelMixin,
    mixins.CreateModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class ProfileViewset(GenericViewSet):
    queryset = User.objects.all().order_by('id')

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

        return Response(data)


    @action(detail=False, url_path="logout", methods=['POST'])
    def logout(self, *args, **kwargs):
        django_logout(self.request)
        return Response()

    @action(detail=False, url_path="login", methods=['POST'])
    def login(self, *args, **kwargs):
        username = self.request.data['username']
        password = self.request.data['password']

        user = authenticate(username=username, password=password)
        if user: 
            success = True
            status_code = 200
            django_login(self.request, user)
        else:
            success = False
            status_code = 400

        return Response({
            'success': success
        }, status=status_code)

