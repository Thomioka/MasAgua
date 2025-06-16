from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('pedido/nuevo/', views.pedido_nuevo, name='pedido_nuevo'),
]
