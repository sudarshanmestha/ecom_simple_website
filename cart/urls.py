from django.urls import path
from . import views



app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='summary'),
    path('shop/', views.ProductListView.as_view(), name='product-list'),
    path('shop/<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path("increase-quantity/<pk>", views.IncreaseQuantityView.as_view(), name='increase-quantity'),
    path("decrease-quantity/<pk>", views.DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path("remove-from-cart/<pk>", views.RemoveFromView.as_view(), name='remove-from-cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path("payment/", views.PaymentView.as_view(), name='payment'),
]
