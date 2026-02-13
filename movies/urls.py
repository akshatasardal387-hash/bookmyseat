from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),

    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('theaters/<int:movie_id>/', views.theater_list, name='theater_list'),

    path('book-seats/<int:theater_id>/', views.book_seats, name='book_seats'),

    path('create-checkout/<int:booking_id>/', views.create_checkout_session, name='create_checkout'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
