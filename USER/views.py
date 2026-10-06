from datetime import datetime, timedelta
from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import transaction
from django.db.models import Count, Q
from django.urls import reverse

from .models import User, Cart, Wishlist, Booking, Address, Feedback
from OWNER.models import Product

RENTAL_DURATION_OPTIONS = list(range(1, 31))


def _current_user(request):
    uid = request.session.get("user_id")
    return User.objects.filter(pk=uid).first() if uid else None


def _auth_redirect(request):
    """Redirect anonymous users to login, returning to the requested page."""
    path = request.path
    if request.GET:
        path += "?" + request.GET.urlencode()
    return redirect(f"{reverse('user_login')}?next={quote(path)}")


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _rental_end(start, days):
    if not start:
        return None
    return start + timedelta(days=max(int(days or 1), 1) - 1)


def _mark_wishlisted(user, products):
    """Stamps each product with a `wishlisted` flag for the current user."""
    if not user:
        return products
    ids = set(Wishlist.objects.filter(user=user).values_list("product_id", flat=True))
    for p in products:
        p.wishlisted = p.id in ids
    return products


def _booked_overlap(product, start, end, exclude_id=None):
    """Total quantity already booked for the same period (double-booking guard)."""
    qs = Booking.objects.filter(product=product, rental_start__isnull=False).exclude(status="cancelled")
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    overlap = 0
    for b in qs:
        b_end = _rental_end(b.rental_start, b.rental_days) or b.rental_start
        if b.rental_start <= end and b_end >= start:
            overlap += b.quantity
    return overlap


def _availability(product, start, end, requested_qty=1):
    if product.quantity < requested_qty:
        return False, "Not enough units available for your selected dates."
    overlap = _booked_overlap(product, start, end)
    if overlap + requested_qty > product.quantity:
        return False, "Unavailable for selected dates."
    return True, "Available for your selected dates."


def splash(request):
    return render(request, "splash.html")


def user_login(request):
    nxt = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = User.objects.filter(username=username, password=password).first()
        if user:
            request.session["user_id"] = user.pk
            request.session["user_username"] = user.username
            if nxt and nxt.startswith("/"):
                return redirect(nxt)
            return redirect("user_landing")
        messages.error(request, "Invalid username or password.")
    return render(request, "user_login.html", {"next": nxt})


def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")
        if not all([username, email, phone, password]):
            messages.error(request, "All fields are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            User.objects.create(username=username, email=email, phone=phone, password=password)
            messages.success(request, "Registration successful! Please sign in.")
            return redirect("user_login")
    return render(request, "user_register.html")


def user_logout(request):
    request.session.flush()
    return redirect("user_login")


def user_landing(request):
    user = _current_user(request)
    from OWNER.models import CategoryOne, Product

    occasions = CategoryOne.objects.all().order_by("id")
    trending_products = (
        Product.objects.annotate(booking_count=Count("booking"))
        .order_by("-booking_count", "id")[:8]
    )

    bride_edit_names = [
        "Bridal Lehenga", "Lehenga", "Kanchipuram Saree", "Banarasi Saree",
        "Saree", "Gown", "Ball Gown", "A-Line Gown", "Mermaid Gown",
        "Anarkali", "Sharara", "Gharara", "Indo Western", "Muslim Bridal Lehenga",
    ]
    groom_edit_names = [
        "Sherwani", "Suit", "Tuxedo", "Kurta Set", "Indo-Western",
        "Dhoti Kurta", "Pathani Suit", "Floral Kurta",
    ]
    bride_edit = (
        Product.objects.annotate(booking_count=Count("booking"))
        .filter(category_2__gender_type="bride", category_2__name__in=bride_edit_names)
        .distinct().order_by("-booking_count", "-id")[:8]
    )
    groom_edit = (
        Product.objects.annotate(booking_count=Count("booking"))
        .filter(category_2__gender_type="groom", category_2__name__in=groom_edit_names)
        .distinct().order_by("-booking_count", "-id")[:8]
    )
    _mark_wishlisted(user, trending_products)
    _mark_wishlisted(user, bride_edit)
    _mark_wishlisted(user, groom_edit)

    return render(request, "user_landing.html", {
        "user": user,
        "occasions": occasions,
        "trending_products": trending_products,
        "bride_edit": bride_edit,
        "groom_edit": groom_edit,
    })


def user_shop(request):
    user = _current_user(request)
    from OWNER.models import CategoryOne, Product

    q = request.GET.get("q", "").strip()
    gender = request.GET.get("gender", "").strip()
    occasion = request.GET.get("occasion", "").strip()
    category = request.GET.get("category", "").strip()
    price = request.GET.get("price", "").strip()
    size = request.GET.get("size", "").strip()
    availability = request.GET.get("availability", "").strip()
    sort = request.GET.get("sort", "recommended").strip()

    products = (
        Product.objects.select_related("category_1", "category_2")
        .annotate(
            booking_count=Count("booking", distinct=True),
            feedback_count=Count("feedback", distinct=True),
        )
    )

    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(category_2__name__icontains=q)
        )
    if gender:
        products = products.filter(category_2__gender_type=gender)
    if occasion:
        products = products.filter(category_1_id=occasion)
    if category:
        products = products.filter(category_2__name__icontains=category)
    if price:
        if price == "under-2000":
            products = products.filter(offer_price__lt=2000)
        elif price == "under-5000":
            products = products.filter(offer_price__lt=5000)
        elif price == "under-10000":
            products = products.filter(offer_price__lt=10000)
        elif price == "under-15000":
            products = products.filter(offer_price__lt=15000)
        elif price == "2000-4000":
            products = products.filter(offer_price__gte=2000, offer_price__lte=4000)
        elif price == "4000-8000":
            products = products.filter(offer_price__gt=4000, offer_price__lte=8000)
        elif price == "8000-plus":
            products = products.filter(offer_price__gt=8000)
    if availability == "available":
        products = products.filter(quantity__gt=0)
    if size:
        products = products.filter(quantity__gt=0)

    if sort == "newest":
        products = products.order_by("-id")
    elif sort == "price-asc":
        products = products.order_by("offer_price")
    elif sort == "price-desc":
        products = products.order_by("-offer_price")
    elif sort == "popular":
        products = products.order_by("-booking_count", "-id")
    else:
        products = products.order_by("id")

    occasions_all = CategoryOne.objects.all().order_by("id")
    _mark_wishlisted(user, products)

    bride_products = None
    groom_products = None
    if not gender:
        bride_products = _mark_wishlisted(user, products.filter(category_2__gender_type="bride"))
        groom_products = _mark_wishlisted(user, products.filter(category_2__gender_type="groom"))

    return render(request, "user_browse.html", {
        "user": user,
        "current_view": "shop",
        "products": products,
        "bride_products": bride_products,
        "groom_products": groom_products,
        "occasions_all": occasions_all,
        "filters": {
            "q": q, "gender": gender, "occasion": occasion, "category": category,
            "price": price, "size": size, "availability": availability, "sort": sort,
        },
    })


def user_category_one(request, gender_type):
    user = _current_user(request)
    from OWNER.models import CategoryOne
    categories = CategoryOne.objects.all().order_by("name")
    return render(request, "user_browse.html", {
        "user": user,
        "current_view": "category_one",
        "gender_type": gender_type,
        "categories": categories,
    })


def user_occasion(request, category_one_id):
    user = _current_user(request)
    from OWNER.models import CategoryOne, CategoryTwo
    occasion = CategoryOne.objects.filter(id=category_one_id).first()
    if not occasion:
        return redirect("user_landing")
    bride_count = CategoryTwo.objects.filter(category_1=occasion, gender_type="bride").count()
    groom_count = CategoryTwo.objects.filter(category_1=occasion, gender_type="groom").count()
    return render(request, "user_browse.html", {
        "user": user,
        "current_view": "occasion",
        "category_one": occasion,
        "bride_count": bride_count,
        "groom_count": groom_count,
    })


def user_category_two(request, gender_type, category_one_id):
    user = _current_user(request)
    from OWNER.models import CategoryOne, CategoryTwo
    category_one = CategoryOne.objects.filter(id=category_one_id).first()
    if not category_one:
        return redirect("user_landing")
    subcategories = CategoryTwo.objects.filter(
        category_1=category_one,
        gender_type=gender_type,
    ).order_by("name")
    return render(request, "user_browse.html", {
        "user": user,
        "current_view": "category_two",
        "gender_type": gender_type,
        "category_one": category_one,
        "subcategories": subcategories,
    })


def user_products(request, gender_type, category_one_id, category_two_id):
    user = _current_user(request)
    from OWNER.models import CategoryOne, CategoryTwo, Product
    category_one = CategoryOne.objects.filter(id=category_one_id).first()
    category_two = CategoryTwo.objects.filter(id=category_two_id).first()
    if not category_one or not category_two:
        return redirect("user_landing")

    products = (
        Product.objects.filter(
            category_1=category_one,
            category_2=category_two,
            quantity__gt=0,
        )
        .distinct()
        .order_by("-id")
    )
    _mark_wishlisted(user, products)

    return render(request, "user_browse.html", {
        "user": user,
        "current_view": "products",
        "gender_type": gender_type,
        "category_one": category_one,
        "category_two": category_two,
        "products": products,
    })


def user_product_detail(request, product_id):
    user = _current_user(request)
    from OWNER.models import Product
    product = (
        Product.objects.select_related("category_1", "category_2", "section")
        .filter(id=product_id)
        .first()
    )
    if not product:
        return redirect("user_landing")
    is_wishlisted = Wishlist.objects.filter(user=user, product=product).exists()
    in_cart = Cart.objects.filter(user=user, product=product).exists()
    related_products = (
        Product.objects.filter(
            category_1=product.category_1,
            category_2=product.category_2,
            quantity__gt=0,
        )
        .exclude(id=product.id)
        .distinct()
        .order_by("-id")[:4]
    )
    _mark_wishlisted(user, related_products)
    booked_ranges = []
    for b in Booking.objects.filter(product=product, rental_start__isnull=False).exclude(status="cancelled"):
        end = _rental_end(b.rental_start, b.rental_days) or b.rental_start
        booked_ranges.append({
            "start": b.rental_start.isoformat(),
            "end": end.isoformat(),
            "qty": b.quantity,
        })
    feedbacks = Feedback.objects.filter(product=product).select_related("user").order_by("-created_at")
    import json
    return render(request, "user_product_detail.html", {
        "user": user,
        "product": product,
        "is_wishlisted": is_wishlisted,
        "in_cart": in_cart,
        "related_products": related_products,
        "rental_duration_options": RENTAL_DURATION_OPTIONS,
        "available_units": product.quantity,
        "booked_json": json.dumps(booked_ranges),
        "feedbacks": feedbacks,
        "feedbacks_count": feedbacks.count(),
    })


def add_to_wishlist(request, product_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    from OWNER.models import Product
    product = Product.objects.get(pk=product_id)
    existing = Wishlist.objects.filter(user=user, product=product).first()
    if existing:
        existing.delete()
        messages.success(request, "Removed from wishlist.")
    else:
        Wishlist.objects.create(user=user, product=product)
        messages.success(request, "Added to wishlist.")
    nxt = request.GET.get("next")
    if nxt:
        return redirect(nxt)
    return redirect("user_product_detail", product_id=product_id)


def add_to_cart(request, product_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    from OWNER.models import Product
    product = Product.objects.get(pk=product_id)

    size = (request.POST.get("size") or "").strip()
    rental_days = 1
    try:
        rental_days = int(request.POST.get("rental_days") or 1)
    except ValueError:
        rental_days = 1
    rental_days = max(1, min(rental_days, 30))
    rental_start = _parse_date(request.POST.get("rental_start"))
    try:
        qty = int(request.POST.get("quantity") or 1)
    except ValueError:
        qty = 1
    qty = max(1, qty)

    if rental_start:
        end = _rental_end(rental_start, rental_days)
        ok, msg = _availability(product, rental_start, end, qty)
        if not ok:
            messages.error(request, f"{product.name}: {msg}")
            return redirect("user_product_detail", product_id=product_id)

    action = request.POST.get("action", "add_to_cart").strip().lower()
    cart_item = Cart.objects.filter(user=user, product=product).first()
    if cart_item:
        cart_item.size = size or cart_item.size
        cart_item.rental_start = rental_start or cart_item.rental_start
        cart_item.rental_days = rental_days
        cart_item.quantity += qty
        cart_item.save()
    else:
        Cart.objects.create(
            user=user, product=product, quantity=qty,
            size=size, rental_start=rental_start, rental_days=rental_days,
        )
    messages.success(request, f"{product.name} added to your cart.")
    if action == "rent_now":
        return redirect("checkout")
    return redirect("user_cart")


def user_cart(request):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    cart_items = Cart.objects.filter(user=user).select_related("product")
    item_count = len(cart_items)
    for item in cart_items:
        item.subtotal = item.product.offer_price * item.quantity
        item.rental_total = item.product.offer_price * item.quantity * item.rental_days
        item.rental_end = _rental_end(item.rental_start, item.rental_days)
    total_per_day = sum(item.subtotal for item in cart_items)
    total_rental = sum(item.rental_total for item in cart_items)
    sec_dep = 2000 * item_count
    discount_saved = sum(
        (item.product.actual_price - item.product.offer_price) * item.quantity * item.rental_days
        for item in cart_items
        if item.product.actual_price > item.product.offer_price
    )
    return render(request, "user_cart.html", {
        "user": user,
        "cart_items": cart_items,
        "total": total_per_day,
        "total_rental": total_rental,
        "security_deposit": sec_dep,
        "grand_total": total_rental + sec_dep,
        "discount_saved": discount_saved,
    })


def cart_remove(request, cart_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    Cart.objects.filter(id=cart_id, user_id=user.id).delete()
    return redirect("user_cart")


def cart_update(request, cart_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    if request.method == "POST":
        try:
            qty = int(request.POST.get("quantity", 1))
        except ValueError:
            qty = 1
        if qty < 1:
            qty = 1
        Cart.objects.filter(id=cart_id, user_id=user.id).update(quantity=qty)
    return redirect("user_cart")


def _format_address(address):
    parts = [address.house]
    if address.street:
        parts.append(address.street)
    parts.extend([address.city, address.state + " - " + address.pin])
    return address.name + ", " + address.phone + ", " + ", ".join(parts)


def checkout(request):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    cart_items = Cart.objects.filter(user=user).select_related("product")
    for item in cart_items:
        item.subtotal = item.product.offer_price * item.quantity
        item.rental_total = item.product.offer_price * item.quantity * item.rental_days
    total = sum(item.subtotal for item in cart_items)
    total_rental = sum(item.rental_total for item in cart_items)
    addresses = Address.objects.filter(user=user).order_by("-is_default", "-id")

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "save_address":
            name = request.POST.get("name", "").strip()
            phone = request.POST.get("phone", "").strip()
            house = request.POST.get("house", "").strip()
            street = request.POST.get("street", "").strip()
            city = request.POST.get("city", "").strip()
            state = request.POST.get("state", "").strip()
            pin = request.POST.get("pin", "").strip()

            if not all([name, phone, house, city, state, pin]):
                messages.error(request, "Name, phone, address, city, state, and PIN are required.")
            elif not phone.isdigit() or len(phone) != 10:
                messages.error(request, "Enter a valid 10-digit phone number.")
            elif not pin.isdigit() or len(pin) != 6:
                messages.error(request, "Enter a valid 6-digit PIN code.")
            else:
                is_default = request.POST.get("is_default") == "on" or not addresses.exists()
                Address.objects.create(
                    user=user, name=name, phone=phone, house=house,
                    street=street, city=city, state=state, pin=pin,
                    is_default=is_default,
                )
                messages.success(request, "Address saved successfully.")
            return redirect("checkout")

        else:
            address_id = request.POST.get("address_id", "").strip()
            try:
                rental_days = int(request.POST.get("rental_days", "1"))
            except ValueError:
                rental_days = 1
            if rental_days < 1 or rental_days > 30:
                messages.error(request, "Rental days must be between 1 and 30.")
                return redirect("checkout")
            rental_start = _parse_date(request.POST.get("rental_start")) or (datetime.today() + timedelta(days=7)).date()
            payment_method = request.POST.get("payment_method", "upi")
            if payment_method not in dict(Booking.PAYMENT_CHOICES):
                payment_method = "upi"

            address = Address.objects.filter(user=user, id=address_id).first()
            if not address:
                messages.error(request, "Please select a delivery address.")
                return redirect("checkout")
            if not cart_items.exists():
                messages.error(request, "Your cart is empty.")
                return redirect("checkout")
            address_text = _format_address(address)

            with transaction.atomic():
                locked_items = list(
                    Cart.objects.select_related("product")
                    .filter(user=user)
                )

                checked_products = {}
                for item in locked_items:
                    product = Product.objects.select_for_update().get(pk=item.product.id)
                    checked_products[item.id] = product
                    if item.quantity > product.quantity:
                        messages.error(
                            request,
                            f"Not enough stock for {product.name}. Available: {product.quantity}.",
                        )
                        return redirect("checkout")
                    start = item.rental_start or rental_start
                    end = _rental_end(start, item.rental_days)
                    ok, msg = _availability(product, start, end, item.quantity)
                    if not ok:
                        messages.error(request, f"{product.name}: {msg}")
                        return redirect("checkout")

                from decimal import Decimal
                total_original = Decimal(str(sum(item.product.offer_price * item.quantity * item.rental_days for item in locked_items)))
                promo_code = request.POST.get("applied_promo", "").strip()
                discount_total = Decimal("0")
                if promo_code:
                    from OWNER.models import Offer
                    from django.utils import timezone
                    offer = Offer.objects.filter(code__iexact=promo_code, is_active=True).first()
                    if offer:
                        today = timezone.now().date()
                        if (not offer.start_date or offer.start_date <= today) and (not offer.end_date or offer.end_date >= today):
                            if offer.offer_type == "percentage":
                                discount_total = total_original * (Decimal(str(offer.discount_value)) / Decimal("100"))
                            elif offer.offer_type == "fixed":
                                discount_total = Decimal(str(offer.discount_value))
                            if discount_total > total_original:
                                discount_total = total_original

                for item in locked_items:
                    product = checked_products[item.id]
                    start = item.rental_start or rental_start
                    item_original_price = Decimal(str(product.offer_price * item.quantity * item.rental_days))
                    if total_original > 0:
                        discount_share = (item_original_price / total_original) * discount_total
                    else:
                        discount_share = Decimal("0")
                    item_discounted_price = item_original_price - discount_share

                    Booking.objects.create(
                        user=user,
                        product=product,
                        address=address_text,
                        quantity=item.quantity,
                        size=item.size,
                        rental_start=start,
                        rental_days=item.rental_days,
                        payment_method=payment_method,
                        total_price=item_discounted_price,
                        status="confirmed",
                    )

                Cart.objects.filter(user=user).delete()

            messages.success(request, "Booking placed successfully!")
            return redirect("user_bookings")

    return render(request, "checkout.html", {
        "user": user,
        "cart_items": cart_items,
        "total": total,
        "total_rental": total_rental,
        "security_deposit": 2000 * len(cart_items),
        "addresses": addresses,
    })


def address_set_default(request, address_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    Address.objects.filter(user=user, is_default=True).update(is_default=False)
    address = Address.objects.filter(user=user, id=address_id).first()
    if address:
        address.is_default = True
        address.save()
        messages.success(request, "Default address updated.")
    return redirect("checkout")


def address_delete(request, address_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    address = Address.objects.filter(user=user, id=address_id).first()
    if address:
        was_default = address.is_default
        address.delete()
        if was_default:
            next_addr = Address.objects.filter(user=user).order_by("-id").first()
            if next_addr:
                next_addr.is_default = True
                next_addr.save()
        messages.success(request, "Address removed.")
    return redirect("checkout")


def user_bookings(request):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    status_flow = ["pending", "confirmed", "preparing", "out_for_delivery", "delivered", "returned"]
    bookings = Booking.objects.filter(user=user).select_related("product").order_by("-id")
    for b in bookings:
        b.rental_end = _rental_end(b.rental_start, b.rental_days)
        b.status_flow = status_flow
        b.status_index = status_flow.index(b.status) if b.status in status_flow else -1
    return render(request, "user_bookings.html", {"user": user, "bookings": bookings})


def user_wishlist(request):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    wishlist_items = Wishlist.objects.filter(user=user).select_related("product")
    for item in wishlist_items:
        item.product.wishlisted = True
    return render(request, "user_wishlist.html", {"user": user, "wishlist_items": wishlist_items})


def user_profile(request):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)

    bookings = Booking.objects.filter(user=user).select_related("product").order_by("-id")
    wishlist_count = Wishlist.objects.filter(user=user).count()
    cart_count = Cart.objects.filter(user=user).count()
    addresses = Address.objects.filter(user=user).order_by("-is_default", "-id")

    return render(request, "user_profile.html", {
        "user": user,
        "bookings": bookings,
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
        "addresses": addresses,
    })


def profile_edit(request):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")

        if not all([username, email, phone]):
            messages.error(request, "Username, email, and phone are required.")

        elif User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, "Username already exists.")

        elif User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, "Email already exists.")

        elif User.objects.exclude(pk=user.pk).filter(phone=phone).exists():
            messages.error(request, "Phone number already exists.")

        elif new_password and not current_password:
            messages.error(request, "Enter your current password to change it.")

        elif current_password and current_password != user.password:
            messages.error(request, "Current password is incorrect.")

        else:
            user.username = username
            user.email = email
            user.phone = phone

            if new_password:
                user.password = new_password

            user.save()
            request.session["user_username"] = user.username
            messages.success(request, "Profile updated successfully.")
            return redirect("user_profile")

    return render(request, "user_profile.html", {
        "user": user,
        "edit_mode": True,
    })


def booking_cancel(request, booking_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)

    booking = Booking.objects.filter(id=booking_id, user_id=user.id).first()
    if booking:
        if booking.status in ["pending", "confirmed"]:
            booking.status = "cancelled"
            booking.save(update_fields=["status"])
            messages.success(request, "Booking cancelled successfully.")
        else:
            messages.error(request, "This booking cannot be cancelled at this stage.")
    return redirect("user_bookings")


def submit_feedback(request, product_id):
    user = _current_user(request)
    if not user:
        return _auth_redirect(request)
    if request.method == "POST":
        from OWNER.models import Product
        from django.shortcuts import get_object_or_404
        product = get_object_or_404(Product, id=product_id)
        feedback_text = request.POST.get("feedback", "").strip()
        try:
            rating = int(request.POST.get("rating", "5"))
        except ValueError:
            rating = 5
        rating = max(1, min(5, rating))

        if not feedback_text:
            messages.error(request, "Feedback cannot be empty.")
        else:
            Feedback.objects.create(user=user, product=product, feedback=feedback_text, rating=rating)
    return redirect("user_product_detail", product_id=product_id)


def api_validate_promo(request):
    from decimal import Decimal
    from django.utils import timezone
    from OWNER.models import Offer
    from django.http import JsonResponse
    
    code = request.GET.get("code", "").strip()
    if not code:
        return JsonResponse({"status": "error", "message": "Promo code is required"}, status=400)
    
    offer = Offer.objects.filter(code__iexact=code, is_active=True).first()
    if not offer:
        return JsonResponse({"status": "error", "message": "Invalid promo code"}, status=400)
    
    today = timezone.now().date()
    if offer.start_date and offer.start_date > today:
        return JsonResponse({"status": "error", "message": "This promo code is not active yet"}, status=400)
    if offer.end_date and offer.end_date < today:
        return JsonResponse({"status": "error", "message": "This promo code has expired"}, status=400)
        
    try:
        subtotal = Decimal(request.GET.get("subtotal", "0"))
    except (ValueError, TypeError):
        subtotal = Decimal("0")
        
    discount = Decimal("0")
    if offer.offer_type == "percentage":
        discount = subtotal * (Decimal(str(offer.discount_value)) / Decimal("100"))
    elif offer.offer_type == "fixed":
        discount = Decimal(str(offer.discount_value))
        
    if discount > subtotal:
        discount = subtotal
        
    new_total = subtotal - discount
    
    return JsonResponse({
        "status": "success",
        "code": offer.code,
        "offer_name": offer.name,
        "offer_type": offer.offer_type,
        "discount_value": float(offer.discount_value),
        "discount_amount": float(discount),
        "new_total": float(new_total)
    })
