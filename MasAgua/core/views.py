from pyexpat.errors import messages
import time
from venv import logger
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from core.decorators import role_required
from core.forms import PedidoForm, ProductoForm
from .models import Carrito, ItemCarrito, ItemOrden, Orden, Pedido, Producto
from django import forms
from datetime import date

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.webpay.webpay_plus.transaction import WebpayOptions

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


def admin_dashboard(request):
    # Aquí la vista para admin
    return render(request, 'core/admin_dashboard.html')


def client_dashboard(request):
    # Aquí la vista para cliente
    return render(request, 'core/client_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')


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
    carrito = Carrito.objects.filter(usuario=request.user, confirmado=False).first()
    items = carrito.items.all() if carrito else []
    total = sum(item.producto.precio * item.cantidad for item in items)
    

    return render(request, 'carrito/ver_carrito.html', {
        'carrito': carrito,
        'items': items,
        'total': total
    })

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')
##

#PROCESAR PAGO SE CREA UNA ORDEN Y SE HACE EL PAGO
#pago webpay

def webpay_plus_create(request):
    carrito = get_object_or_404(Carrito, usuario=request.user, confirmado=False)
    
    # Obtener dirección desde el formulario
    direccion = request.POST.get("direccion", "")
    
    # Crear Pedido antes de iniciar el pago
    Pedido.objects.create(
        cliente=request.user.username,
        direccion=direccion,
        fecha_entrega=date.today(),
        cantidad=1  # Puedes adaptar si hay más lógica para cantidad
    )
    
    # Generar buy_order seguro
    timestamp = int(time.time())
    buy_order = f"BO_{timestamp}_{request.user.id}"

    # Crear orden
    orden = Orden.objects.create(
        usuario=request.user,
        estado='pendiente',
        direccion=direccion,
        monto_total=carrito.total(),
        buy_order=buy_order
    )

    # Configuración Transbank
    tx = Transaction(WebpayOptions(
        commerce_code=settings.TRANSBANK_CONFIG['WEBPAY_COMMERCE_CODE'],
        api_key=settings.TRANSBANK_CONFIG['WEBPAY_API_KEY'],
        integration_type=settings.TRANSBANK_CONFIG['WEBPAY_ENVIRONMENT']
    ))

    # Crear transacción
    response = tx.create(
        buy_order=buy_order,
        session_id=request.session.session_key,
        amount=orden.monto_total,
        return_url=request.build_absolute_uri(reverse('webpay_plus_commit'))
    )
    
    # Guardar token en orden
    orden.token_ws = response['token']
    orden.save()
    request.session['orden_id'] = orden.id

    return render(request, 'webpay/redirect.html', {
        'url': response['url'],
        'token': response['token']
    })



@csrf_exempt
def webpay_plus_commit(request):
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    if not token:
        return render(request, 'webpay/error.html', {'error_message': 'Token no recibido'})

    try:
        # 1. Obtener la orden existente en lugar de crear una nueva
        orden_id = request.session.get('orden_id')
        if not orden_id:
            raise ValueError("No se encontró ID de orden en la sesión")
            
        orden = Orden.objects.get(id=orden_id, token_ws=token)
        
        # 2. Configurar WebPay
        tx = Transaction(
            WebpayOptions(
                commerce_code=settings.TRANSBANK_CONFIG['WEBPAY_COMMERCE_CODE'],
                api_key=settings.TRANSBANK_CONFIG['WEBPAY_API_KEY'],
                integration_type=settings.TRANSBANK_CONFIG['WEBPAY_ENVIRONMENT']
            )
        )
        response = tx.commit(token)
        
        if response.get('status') == 'AUTHORIZED':
            # 3. Obtener el carrito
            carrito = Carrito.objects.get(usuario=request.user, confirmado=False)
            
            # 4. Actualizar la orden existente (no crear nueva)
            orden.estado = 'pagado'
            orden.monto_total = response['amount']
            orden.save()
            
            # 5. Mover items del carrito a la orden
            for item in carrito.items.all():
                ItemOrden.objects.create(
                    orden=orden,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio=item.producto.precio  # Asegúrate de guardar el precio histórico
                )
            
            # 6. Actualizar carrito
            carrito.confirmado = True
            carrito.orden_relacionada = orden
            carrito.save()
            
            # Limpiar sesión
            if 'orden_id' in request.session:
                del request.session['orden_id']
            
            return render(request, 'webpay/success.html', {
                'orden': orden,
                'mensaje': 'Pago exitoso. Tu orden está en revisión.'
            })
        else:
            orden.estado = 'rechazado'
            orden.save()
            return render(request, 'webpay/failure.html', {
                'error_message': 'Pago rechazado por Transbank',
                'response': response
            })
    
    except Exception as e:
        logger.error(f"Error en webpay_plus_commit: {str(e)}", exc_info=True)
        return render(request, 'webpay/error.html', {
            'error_message': f'Error al procesar el pago: {str(e)}'
        })
    
def procesar_pago_webpay(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Solo usuarios autenticados
    
    carrito = get_object_or_404(Carrito, usuario=request.user, confirmado=False)
    total = carrito.total()  # Usa el método total() que definimos antes
    
    # Configuración de WebPay
    tx = Transaction(WebpayOptions(
        commerce_code=settings.TRANSBANK_CONFIG['WEBPAY_COMMERCE_CODE'],
        api_key=settings.TRANSBANK_CONFIG['WEBPAY_API_KEY'],
        integration_type='TEST'
    ))
    
    # Crear transacción
    buy_order = f"BO_{carrito.id}_{int(time.time())}"
    return_url = request.build_absolute_uri(reverse('webpay_plus_commit'))
    
    response = tx.create(
        buy_order=buy_order,
        session_id=request.session.session_key,
        amount=total,
        return_url=return_url
    )
    
    # Guarda el buy_order en sesión para usarlo después
    request.session['buy_order'] = buy_order
    
    # Redirige a WebPay
    return render(request, 'webpay/redirect.html', {
        'url': response['url'],
        'token': response['token']
    })


def listar_ordenes(request):
    # Admin ve todas las órdenes, clientes solo las suyas
    if request.user.profile.role == 'administrador':
        ordenes = Orden.objects.all().order_by('-fecha')
    else:
        ordenes = Orden.objects.filter(usuario=request.user).order_by('-fecha')
    
    return render(request, 'ordenes/listar.html', {
        'ordenes': ordenes,
        'es_admin': request.user.profile.role == 'administrador'
    })

def detalle_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    
    
    
    return render(request, 'ordenes/detalle.html', {
        'orden': orden,
        'items': orden.items.all()
    })
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
