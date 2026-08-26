from django.urls import path
from . import views

urlpatterns = [
    path("", views.staff_login, name="staff_login"),
    path("logout/", views.staff_logout, name="staff_logout"),
    path("dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("orders/<int:booking_id>/status/", views.staff_booking_status, name="staff_booking_status"),
    path("users/register/", views.staff_user_register, name="staff_user_register"),
    path("users/delete/<int:user_id>/", views.staff_user_delete, name="staff_user_delete"),
    path("products/update-quantity/<int:product_id>/", views.staff_product_qty_update, name="staff_product_qty_update"),
]
