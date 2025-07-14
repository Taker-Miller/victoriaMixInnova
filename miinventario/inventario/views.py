from datetime import date
import io
import xlsxwriter
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Producto, Venta
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

@login_required
def stock_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario/stock.html', {'productos': productos})

# ========================
# Ventas
# ========================

from django.utils import timezone  # Asegúrate de tener esto al inicio del archivo

@login_required
def agregar_venta(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad'))

        producto = get_object_or_404(Producto, id=producto_id)
        precio_unitario = producto.precio
        total = precio_unitario * cantidad

        # Guardar la venta
        Venta.objects.create(
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            total=total,
            fecha=timezone.now()
        )

        return redirect('ventas')

    return render(request, 'inventario/agregar_venta.html', {'productos': productos})


@login_required
def ventas(request):
    hoy = date.today()
    ventas_dia = Venta.objects.filter(fecha=hoy)
    return render(request, 'inventario/ventas.html', {
        'ventas': ventas_dia,
        'fecha_actual': hoy
    })

@login_required
def exportar_ventas_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Ventas del día {date.today()}")

    ventas = Venta.objects.filter(fecha=date.today())
    y = 780
    for venta in ventas:
        texto = f"{venta.producto.nombre} - {venta.cantidad} unidades - ${venta.total}"
        p.drawString(100, y, texto)
        y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="ventas_dia.pdf")

@login_required
def exportar_ventas_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    encabezados = ['Producto', 'Cantidad', 'Precio Unitario', 'Total', 'Fecha']
    for i, encabezado in enumerate(encabezados):
        worksheet.write(0, i, encabezado)

    ventas = Venta.objects.filter(fecha=date.today())
    for fila, venta in enumerate(ventas, start=1):
        worksheet.write(fila, 0, venta.producto.nombre)
        worksheet.write(fila, 1, venta.cantidad)
        worksheet.write(fila, 2, float(venta.precio_unitario))
        worksheet.write(fila, 3, float(venta.total))
        worksheet.write(fila, 4, venta.fecha.strftime("%Y-%m-%d"))

    workbook.close()
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ventas_dia.xlsx"'
    return response

# ========================
# Usuarios
# ========================

@login_required
def usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'inventario/usuarios.html', {'usuarios': usuarios})
