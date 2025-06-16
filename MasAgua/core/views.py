from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Pedido
from django import forms

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
def admin_dashboard(request):
    # Aquí la vista para admin
    return render(request, 'core/admin_dashboard.html')

@login_required
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


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['direccion', 'fecha_entrega', 'cantidad']
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
        }

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
