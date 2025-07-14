from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Producto
from .forms import ProductoForm

# ========================
# Autenticación
# ========================

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST['username']
        clave = request.POST['password']
        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'registration/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'registration/login.html')

@login_required
def cerrar_sesion(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('dashboard')

# ========================
# Dashboard
# ========================

@login_required
def dashboard(request):
    total_usuarios = User.objects.count()
    total_productos = Producto.objects.count()
    return render(request, 'inventario/dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
    })

# ========================
# Productos
# ========================

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario/lista_productos.html', {'productos': productos})

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'inventario/form_producto.html', {'form': form})

@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/form_producto.html', {'form': form})

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'inventario/confirmar_eliminar.html', {'producto': producto})

# ========================
# Usuarios
# ========================

@login_required
def usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'inventario/usuarios.html', {'usuarios': usuarios})
