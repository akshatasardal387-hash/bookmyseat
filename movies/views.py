from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
import stripe

from .models import Movie, Theater, Seat, Booking, Genre, Language


stripe.api_key = settings.STRIPE_SECRET_KEY
# ===================== MOVIE LIST =====================
def movie_list(request):
    movies = Movie.objects.select_related('genre', 'language').all()
    genres = Genre.objects.all()
    languages = Language.objects.all()

    search = request.GET.get('search', '').strip()
    genre_id = request.GET.get('genre', '')
    language_id = request.GET.get('language', '')

    if search:
        movies = movies.filter(name__icontains=search)
    if genre_id.isdigit():
        movies = movies.filter(genre_id=genre_id)
    if language_id.isdigit():
        movies = movies.filter(language_id=language_id)

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'genres': genres,
        'languages': languages,
    })


# ===================== MOVIE DETAIL =====================
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'theaters': theaters
    })


# ===================== THEATER LIST =====================
def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    return render(request, 'movies/theater_list.html', {
        'movie': movie,
        'theaters': theaters
    })


# ===================== SEAT BOOKING =====================
@login_required
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    movie = theater.movie
    seats = Seat.objects.filter(theater=theater)

    if request.method == "POST":
        selected_seats = request.POST.getlist("seats")

        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            if not seat.is_booked:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=movie,
                    theater=theater
                )
                seat.is_booked = True
                seat.save()

        last_booking = Booking.objects.filter(user=request.user).last()
        return redirect("create_checkout", booking_id=last_booking.id)

    return render(request, "movies/seat_selection.html", {
        'theater': theater,
        'movie': movie,
        'seats': seats
    })


# ===================== STRIPE CHECKOUT =====================
def create_checkout_session(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': f"{booking.movie.name} - Seat {booking.seat.seat_number}"
                },
                'unit_amount': 150 * 100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(
            f'/movies/payment-success/{booking.id}/?session_id={{CHECKOUT_SESSION_ID}}'
        ),
        cancel_url=request.build_absolute_uri('/movies/payment-failed/'),
    )

    return redirect(session.url)


# ===================== PAYMENT SUCCESS =====================
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if not booking.payment_done:
        booking.payment_done = True
        booking.save()

        try:
            send_mail(
                subject='Booking Confirmation - BookMySeat 🎬',
                message=f"""
Hello {booking.user.username},

Your booking is confirmed!

Movie: {booking.movie.name}
Theater: {booking.theater.name}
Seat: {booking.seat.seat_number}
Amount Paid: ₹150

Enjoy your show! 🍿
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                fail_silently=False,
            )
            print("✅ Email sent")
        except Exception as e:
            print("❌ Email error:", e)

    return render(request, "movies/payment_success.html", {
        "booking": booking,
        "amount": 150,
    })


# ===================== PAYMENT FAILED =====================
def payment_failed(request):
    return render(request, "movies/payment_failed.html")


# ===================== ADMIN DASHBOARD =====================
def admin_dashboard(request):
    total_bookings = Booking.objects.count()
    total_revenue = total_bookings * 150

    popular_movies = (
        Booking.objects.values("movie__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    busy_theaters = (
        Booking.objects.values("theater__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    return render(request, "movies/admin_dashboard.html", {
        "total_revenue": total_revenue,
        "popular_movies": popular_movies,
        "busy_theaters": busy_theaters,
    })
