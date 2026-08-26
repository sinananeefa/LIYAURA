from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("", views.owner_login, name="owner_login"),
    path("login/", views.owner_login, name="owner_login_explicit"),
    path("register/", views.owner_register, name="owner_register"),
    path("logout/", views.owner_logout, name="owner_logout"),

    # Main Dashboard Suite
    path("dashboard/", views.owner_dashboard, name="owner_dashboard"),

    # Interactive AJAX & API Endpoints
    path("api/chart-data/", views.api_chart_data, name="owner_api_chart_data"),
    path("api/booking/<int:booking_id>/update-status/", views.api_update_booking_status, name="owner_api_update_booking_status"),
    path("api/booking/<int:booking_id>/details/", views.api_booking_details, name="owner_api_booking_details"),
    path("api/customer/<int:user_id>/details/", views.api_customer_details, name="owner_api_customer_details"),
    path("api/generate-gemini-image/", views.api_generate_gemini_image, name="owner_api_generate_gemini_image"),

    # Product Management
    path("product/add/", views.product_add, name="product_add"),
    path("product/edit/<int:product_id>/", views.product_edit, name="product_edit"),
    path("product/delete/<int:product_id>/", views.product_delete, name="product_delete"),
    path("product/duplicate/<int:product_id>/", views.product_duplicate, name="product_duplicate"),

    # Category & Occasion Management
    path("category-1/add/", views.category_one_add, name="category_one_add"),
    path("category-1/edit/<int:category_id>/", views.category_one_edit, name="category_one_edit"),
    path("category-1/delete/<int:category_id>/", views.category_one_delete, name="category_one_delete"),

    path("category-2/add/", views.category_two_add, name="category_two_add"),
    path("category-2/edit/<int:category_id>/", views.category_two_edit, name="category_two_edit"),
    path("category-2/delete/<int:category_id>/", views.category_two_delete, name="category_two_delete"),

    # Offers & Promotions
    path("offer/add/", views.offer_add, name="offer_add"),
    path("offer/toggle/<int:offer_id>/", views.offer_toggle, name="offer_toggle"),
    path("offer/delete/<int:offer_id>/", views.offer_delete, name="offer_delete"),

    # Feedback & User Management
    path("feedback/<int:feedback_id>/approve/", views.feedback_approve, name="feedback_approve"),
    path("feedback/<int:feedback_id>/delete/", views.feedback_delete, name="owner_feedback_delete"),
    path("users/<int:user_id>/delete/", views.owner_user_delete, name="owner_user_delete"),

    # Legacy compatibility routes
    path("orders/<int:booking_id>/status/", views.booking_status_update, name="booking_status_update"),
    path("rack/add/", views.section_add, name="section_add"),
    path("rack/edit/<int:section_id>/", views.section_edit, name="section_edit"),
    path("rack/delete/<int:section_id>/", views.section_delete, name="section_delete"),
    path("staff/add/", views.staff_add, name="staff_add"),
    path("staff/edit/<int:staff_id>/", views.staff_edit, name="staff_edit"),
    path("staff/delete/<int:staff_id>/", views.staff_delete, name="staff_delete"),
]
