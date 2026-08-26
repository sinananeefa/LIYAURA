from .models import User, Wishlist, Cart

def user_nav_context(request):
    uid = request.session.get("user_id")
    user = User.objects.filter(pk=uid).first() if uid else None
    if user:
        return {
            'nav_user': user,
            'wishlist_count': Wishlist.objects.filter(user=user).count(),
            'cart_count': Cart.objects.filter(user=user).count(),
        }
    return {
        'nav_user': None,
        'wishlist_count': 0,
        'cart_count': 0,
    }
