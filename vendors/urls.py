from django.urls import path
from .import views
from accounts import views as accountviews
from . import views

urlpatterns = [
path('', accountviews.vendorDashboard, name='vendordashboard'),
path('registerVendor/', views.registerRestaurant, name='registervendor'),
path('profile/', views.VendorProfile, name='vendor-profile'),

path('menu-builder/', views.MenuBuilder, name='menu-builder'),
path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

# category CRUD
path('menu-builder/category/add/', views.AddCategory, name='add-category'),
path('menu-builder/category/edit/<int:pk>/', views.EditCategory, name='edit-category'),
path('menu-builder/category/delete/<int:pk>/', views.DeleteCategory, name='delete-category'),


# Fooditem CRUD
path('menu-builder/food/add/', views.Addfooditem, name='add-fooditem'),
path('menu-builder/food/edit/<int:pk>/', views.Editfooditem, name='edit-fooditem'),
path('menu-builder/food/delete/<int:pk>/', views.Deletefooditem, name='delete-fooditem'),
]