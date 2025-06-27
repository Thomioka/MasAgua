from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from core.decorators import role_required
from core.forms import PedidoForm, ProductoForm
from .models import Carrito, ItemCarrito, Pedido, Producto
from django import forms
from django.views.generic import (ListView, CreateView, 
                                 UpdateView, DeleteView)

def index(request):
    return render(request, 'core/index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('client_dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'core/login.html')

@login_required
@role_required('administrador')
def admin_dashboard(request):
    # Aquí la vista para admin
    return render(request, 'core/admin_dashboard.html')

@role_required('cliente')
def client_dashboard(request):
    # Aquí la vista para cliente
    return render(request, 'core/client_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def pedidos(request):
    if request.user.is_staff:
        pedidos = Pedido.objects.all()
    else:
        pedidos = Pedido.objects.filter(cliente=request.user.username)
    return render(request, 'core/pedidos.html', {'pedidos': pedidos})

#Crear producto como admin


def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  # Redirige a una página de éxito
    else:
        form = ProductoForm()
    return render(request, 'core/agregar_producto.html', {'form': form})

#CRUD

def lista_productos(request):
    productos = Producto.objects.all().order_by('-fecha_creacion')
    return render(request, 'productos/lista.html', {
        'productos': productos,
        'titulo': 'Lista de Productos'
    })

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'productos/formulario.html', {
        'form': form,
        'titulo': 'Nuevo Producto',
        'accion': 'Crear'
    })


def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'productos/formulario.html', {
        'form': form,
        'titulo': f'Editar {producto.nombre}',
        'accion': 'Guardar'
    })

def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    producto.delete()
    return redirect('lista_productos')

#MOSTRAR LOS PRODUCTOS A LOS CLIENTES
def catalogo_productos(request):
    productos = Producto.objects.filter(activo=True).order_by('-fecha_creacion')
    return render(request, 'productos/catalogo.html', {'productos': productos})


#CARRITO DE COMPRAS
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        confirmado=False
    )
    
    item, item_created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': 1}
    )
    
    if not item_created:
        item.cantidad += 1
        item.save()
    
    return redirect('catalogo')

@login_required
def ver_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user, confirmado=False)
    return render(request, 'carrito/ver_carrito.html', {'carrito': carrito})

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')
##

#PROCESAR PAGO SE CREA UNA ORDEN Y SE HACE EL PAGO




def pedido_nuevo(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user.username  # asignado automáticamente
            pedido.save()
            total = pedido.precio_total
            return render(request, 'core/pedido_nuevo.html', {
                'form': PedidoForm(),  # formulario limpio
                'modal': True,
                'total': total
            })
    else:
        form = PedidoForm()
    return render(request, 'core/pedido_nuevo.html', {'form': form})
