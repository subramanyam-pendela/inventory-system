from .models import *

def cart_item_count(request):
    if 'user_login_id' in request.session:
        user_id = request.session['user_login_id']
        try:
            cart = Cart.objects.get(user__id=user_id)
            item_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            item_count = 0
    else:
        item_count = 0
    return {'cart_item_count': item_count}



def wishlist_item_count(request):
    if 'user_login_id' in request.session:
        user_id = request.session['user_login_id']
        try:
            user = User.objects.get(id=user_id)
            wishlist_items_count = sum(1 for item in WishlistItem.objects.filter(user=user))
        except User.DoesNotExist:
            wishlist_items_count = 0
    else:
        wishlist_items_count = 0
    return {'wishlist_item_count': wishlist_items_count}
