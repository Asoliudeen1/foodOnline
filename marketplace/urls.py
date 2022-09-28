from django.urls import path
from . import views


urlpatterns = [
   path('', views.MarketPlace, name='marketplace'),
   path('<slug:vendor_slug>/', views.VendorDetail, name='vendordetail'),

   # Add To Cart
   path('add_to_cart/<int:food_id>/', views.AddToCart, name='addtocart'),
   # Decrease Cart
   path('decrease_cart/<int:food_id>/', views.DecreaseCart, name='decreasecart'),
   #Delete Cart Item
   path('delete_cart/<int:cart_id>/', views.DeleteCart, name='deletecart'),
]