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
    
    #CRUD
    path('lista', views.lista_productos, name='lista_productos'),
    path('nuevo/', views.crear_producto, name='crear_producto'),
    path('editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),

    #Mostrar productos
    path('catalogo/', views.catalogo_productos, name='catalogo'),

    #Carrito
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar-carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),

]
