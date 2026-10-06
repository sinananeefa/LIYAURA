from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from OWNER.models import Product, Section, Staff
from USER.models import Booking, User


def staff_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        staff = Staff.objects.filter(username=username, password=password).first()
        if staff:
            request.session["staff_id"] = staff.pk
            request.session["staff_name"] = staff.staff_name
            return redirect("staff_dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "staff_login.html")


def staff_logout(request):
    request.session.flush()
    return redirect("staff_login")


def staff_dashboard(request):
    if not request.session.get("staff_id"):
        return redirect("staff_login")

    bookings = Booking.objects.select_related("user", "product").order_by("-created_at", "-id")
    products = Product.objects.select_related("category_1", "category_2", "section").order_by("-id")
    users = User.objects.all().order_by("-id")

    active_bookings = bookings.exclude(status="cancelled")
    total_revenue = sum(booking.total_price for booking in active_bookings)

    section_data = []
    for section in Section.objects.all().order_by("rack_no"):
        section_products = products.filter(section=section)
        section_data.append({
            "section": section,
            "products": section_products,
            "product_count": section_products.count(),
            "total_stock": sum(p.quantity for p in section_products),
        })

    return render(request, "staff_dashboard.html", {
        "staff_name": request.session.get("staff_name", ""),
        "bookings": bookings,
        "recent_bookings": bookings[:5],
        "products": products,
        "low_stock": products.filter(quantity__lte=2),
        "total_bookings": bookings.count(),
        "pending_count": bookings.filter(status="pending").count(),
        "confirmed_count": bookings.filter(status="confirmed").count(),
        "completed_count": bookings.filter(status="completed").count(),
        "cancelled_count": bookings.filter(status="cancelled").count(),
        "total_revenue": total_revenue,
        "product_count": products.count(),
        "sections": section_data,
        "users": users,
        "user_count": users.count(),
    })


def staff_booking_status(request, booking_id):
    if not request.session.get("staff_id"):
        return redirect("staff_login")
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        status = request.POST.get("status", "")
        valid_statuses = {value for value, _ in Booking._meta.get_field("status").choices}
        if status in valid_statuses:
            booking.status = status
            booking.save(update_fields=["status"])
            messages.success(request, "Order status updated.")
        else:
            messages.error(request, "Invalid order status.")
    return redirect(f"{reverse('staff_dashboard')}#orders")


def staff_user_register(request):
    if not request.session.get("staff_id"):
        return redirect("staff_login")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        if not all([username, email, phone, password]):
            messages.error(request, "All fields are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists.")
        else:
            User.objects.create(username=username, email=email, phone=phone, password=password)
            messages.success(request, f"Customer account '{username}' created successfully.")
    return redirect(f"{reverse('staff_dashboard')}#users")


def staff_user_delete(request, user_id):
    if not request.session.get("staff_id"):
        return redirect("staff_login")
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()
        messages.success(request, "Customer account removed.")
    return redirect(f"{reverse('staff_dashboard')}#users")


def staff_product_qty_update(request, product_id):
    if not request.session.get("staff_id"):
        return redirect("staff_login")
    if request.method == "POST":
        from OWNER.models import Product
        product = get_object_or_404(Product, id=product_id)
        try:
            qty = int(request.POST.get("quantity", 0))
            if qty < 0:
                messages.error(request, "Quantity cannot be negative.")
            else:
                product.quantity = qty
                product.save(update_fields=["quantity"])
                messages.success(request, f"Stock quantity for '{product.name}' updated to {qty} successfully.")
        except ValueError:
            messages.error(request, "Invalid quantity value.")
    return redirect(f"{reverse('staff_dashboard')}#products")
