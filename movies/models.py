from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# ===================== GENRE =====================
class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ===================== LANGUAGE =====================
class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ===================== MOVIE =====================
class Movie(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)

    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)

    cast = models.TextField()
    description = models.TextField(blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


# ===================== THEATER =====================
class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="theaters")
    time = models.DateTimeField()

    def __str__(self):
        return f"{self.name} - {self.movie.name}"


# ===================== SEAT =====================
class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)

    is_booked = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)   # ✅ important
    reserved_at = models.DateTimeField(null=True, blank=True)

    def reservation_expired(self):
        if self.reserved_at:
            return timezone.now() > self.reserved_at + timedelta(minutes=5)
        return False

    def __str__(self):
        return f"{self.seat_number} - {self.theater.name}"


# ===================== BOOKING =====================
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)

    payment_done = models.BooleanField(default=False)  # ✅ important
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.seat.seat_number}"
