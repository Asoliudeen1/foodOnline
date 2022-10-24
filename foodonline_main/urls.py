from django.contrib import admin
from django.urls import path, include



from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as marketplaceviews
from .import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('accounts.urls')),
    path('vendor/', include('vendors.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('customer/', include('customers.urls')),

     # Cart
    path('cart/', marketplaceviews.cart, name='cart'),

    #SEARCH
    path('search/', marketplaceviews.search, name='search'),

    #CHECKOUT
    path('checkout/', marketplaceviews.checkout, name='checkout'),

    # ORDERS
    path('orders/', include('orders.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
