from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError 
from django.db.models.signals import post_save
from django.dispatch import receiver

class Genre(models.Model):
    name = models.TextField("Жанр", default="Без жанра")

    def __str__(self):
        return self.name
    
# Create your models here.
class Image(models.Model):
    name = models.TextField("Название")   
    image = models.ImageField("Картина",  upload_to='images/', null=True, blank=True)
    author = models.TextField("Автор", default="Неизвестный")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True)
    class Meta:
        verbose_name = "Картина"
        verbose_name_plural = "Картины"

    def __str__(self):
        return self.name

class Auction(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('pending', 'В ожидании'),
    ]    

    start_price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Время окончания должно быть позже времени начала")

        if self.winner and self.status != 'inactive':
            raise ValidationError("Победитель может быть назначен только после окончания торгов")

    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        verbose_name = "Аукцион"
        verbose_name_plural = "Аукционы"

    def __str__(self):
        return str(self.id)

class Rate(models.Model):
    add_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, null=True)


# у юзера точно есть профиль
# тут типа топ инфа - паспорт и тд
# джанго только даст имя, имайл, пароль
# в профиль ничё руками не добавляем
# в админе запретить добавление !
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

#     def __str__(self):
#         return self.user.username if self.user else f"Profile {self.id}"
    
# @receiver(post_save, sender=User)
# def on_user_create(sender, instance, created, *args, **kwards):
#     if created:
#         Profile.objects.create(user=instance)