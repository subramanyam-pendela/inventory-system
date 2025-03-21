"""
URL configuration for craftstoreproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path


from django.conf import settings
from django.conf.urls.static import static

from userapp import views as userviews
from adminapp import views as adminviews



urlpatterns = [
    path('admin/', admin.site.urls),

    path('',userviews.index,name="index"),
    path('about', userviews.about,name="about"),
    path('user-login', userviews.user_login,name="user_login"),
    path('user-register', userviews.user_register,name="user_register"),
    path('admin-login', userviews.admin_login,name="admin_login"),
    path('contact', userviews.contact,name="contact"),
    path('user-otp/',userviews.otp,name="user_otp"),
    path('user/logout/',userviews.user_logout,name="user_logout"),







    path('buyer-dashboard/',userviews.user_dashboard,name="user_dashboard"),
    path('buyer-explore/',userviews.user_explore,name="user_explore"),
    path('category/<str:category_name>/', userviews.category_view, name='category_view'),
    path('get-craft-details/<int:id>/', userviews.get_craft_details, name='get_craft_details'),
    path('crafts/state/<str:state_name>/', userviews.crafts_by_state_view, name='crafts_by_state'),
    path('buyer-cartpage/',userviews.cartpage,name="cart"),
    path('buyer-payment/',userviews.payment,name="payment"),
    # path('confirm-payment/',userviews.create_order,name="create_order"),
    path('checkout/', userviews.checkout, name='checkout'),
    path('buyer/myorders', userviews.my_orders, name='my_orders'),
    path('buyer/purchases', userviews.my_purchases, name='my_purchases'),
    path('buyer/add-wishlist/<int:craft_id>/', userviews.add_wishlist, name='add_wishlist'),
    path('buyer/wishlist/', userviews.wishlist, name='wishlist'),
    path('user/profile', userviews.my_profile, name='my_profile'),
    path('user/telugu', userviews.telugu, name='telugu'),
    path('user/hindi', userviews.hindi, name='hindi'),
    path('user/tamil', userviews.tamil, name='tamil'),
    path('user/kannada', userviews.kannnada, name='kannnada'),
    path('wishlist/remove/<int:item_id>/', userviews.remove_from_wishlist, name='remove_from_wishlist'),


    





    path('add-to-cart/<int:craft_id>/', userviews.add_to_cart, name='add_to_cart'),
    path('user/feedback/<int:order_id>/', userviews.feedback, name='feedback'),





    path('user-chatbot/', userviews.user_chatbot, name='user_chatbot'),
    path('seller-dashboard/',userviews.seller_dashboard,name="seller_dashboard"),
    path('seller-customers-orders/',userviews.customers_orders,name="customers_orders"),
    path('accept-order/<int:order_id>/', userviews.accept_order, name='accept_order'),
    path('craft/<int:craft_id>/video/', userviews.video, name='craft_video'),
    path('change_delivery_status/<int:order_id>/', adminviews.change_delivery_status, name='change_delivery_status'),




    path('dashboard/admin/reports/', adminviews.generate_reports, name='admin_reports'),
    path('dashboard/admin/', adminviews.admin_dashboard, name='admin_dashboard'),
    path('allusers/admin/', adminviews.all_users, name='all_users'),
    path('allorders/admin/', adminviews.all_orders, name='all_orders'),
    path('allcrafts/admin/', adminviews.all_crafts, name='all_crafts'),
    path('pendingorders/admin/', adminviews.pending_orders, name='pending_orders'),
    path('pendingcrafts/admin/', adminviews.pending_crafts, name='pending_crafts'),
    path('delete-craft/<int:craft_id>/', adminviews.delete_craft, name='delete_craft'),
    path('toggle-user-status/<int:user_id>/', adminviews.toggle_user_status, name='toggle_user_status'),
    path('remove-user/<int:user_id>/', adminviews.remove_user, name='remove_user'),
    path('accept-order/<int:order_id>/admin/', adminviews.accept_order, name='admin_accept_order'),
    path('accept-craft/<int:craft_id>/admin/', adminviews.accept_craft, name='admin_accept_craft'),
    path('admin-logout/', adminviews.admin_logout, name='admin_logout'),
    path('admin-view-feedbacks/', adminviews.view_feedbacks, name='view_feedbacks'),
    path('admin-feedbacks-graph/', adminviews.graph, name='graph'),
    path('admin-add-events/', adminviews.add_events, name='add_events'),
    path('admin-manage-events/', adminviews.manage_events, name="manage_events"),
    path('admin-remove-event/<int:event_id>/', adminviews.remove_event, name='remove_event'),
    path('toggle-sell/<int:user_id>/', adminviews.toggle_sell_permission, name='toggle_sell_permission'),
    path('update-craft-price/<int:craft_id>/', adminviews.update_craft_price_view, name='update_craft_price'),



    path('sentiment/analysis/', adminviews.sentiment_analysis, name='sentiment_analysis'),






]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
