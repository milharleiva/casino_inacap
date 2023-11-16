from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Cliente, Administrador, Menu, Carrito, ItemCarrito, Boleta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm 
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.views.generic import(View,TemplateView,ListView,DeleteView)
from django.contrib import messages
from django.views.decorators.http import require_POST
from .services import TransbankService, initialize_transbank_sdk
from django.urls import reverse
import uuid



class Error404View8(TemplateView):
    template_name = "web/error404.html"




def index(request):
    return render(request, 'logins/index.html')



def register(request):
    if request.method == 'POST':
        
        rut = request.POST.get('usuario')
        nombre = request.POST.get('nombre')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re-password')

        
        if password == re_password:
          
           

          
            user = User.objects.create(
                username=rut,
                first_name=nombre,
                last_name=last_name,
                email=email,
                password=make_password(password) 
            )

          
            cliente = Cliente.objects.create(
                usuario=user,
                nombre=nombre
            )

           
            login(request, user)
            return redirect('/login')
        else:
            
            return redirect('/')

   
    return render(request, 'logins/register.html')

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        password = request.POST.get('password')
        user = authenticate(request, username=usuario, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'logins/login.html', {'error_message': 'Credenciales incorrectas'})
    return render(request, 'logins/login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='inicio')
def dashboard(request):
    users = User.objects.all()
    data = {'users':users}
    return render(request, 'logins/dashboard.html', data)

@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='inicio')
def crear_usuario(request):

    if not request.user.is_superuser:
      
        return HttpResponseNotFound("No tienes permisos para ver esta página.")



    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nombre = request.POST.get('nombre')
        is_admin = request.POST.get('is_admin') == 'on'

       
        user = User.objects.create(
            username=username,
            password=make_password(password),
            first_name=nombre,
            is_superuser=is_admin,
            is_staff=is_admin  
        )

        
        if is_admin:
            Administrador.objects.create(usuario=user, nombre=nombre)

       
        return redirect('/')
    else:
        
        return render(request, 'web/crear_usuario.html')
    


@login_required
@user_passes_test(lambda u: u.is_superuser)
def crear_menu(request):
    if not request.user.is_superuser:
      
        return HttpResponseNotFound("No tienes permisos para ver esta página.")
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')

    
        menu = Menu(nombre=nombre, descripcion=descripcion, precio=precio)
        menu.save()

       
        return redirect('/')
    else:
        
        return render(request, 'web/crear_menu.html')

@login_required    
def listar_menu(request):
    
    menus = Menu.objects.all()
   
    context = {'menus': menus}
    return render(request, 'web/listar_menu.html', context)



@login_required
def carrito(request):
    try:
        
        carrito = Carrito.objects.get(usuario=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito)
        total = sum(item.get_cost() for item in items)
    except Carrito.DoesNotExist:
        
        items = []
        total = 0

    context = {
        'items': items,
        'total': total
    }
    return render(request, 'web/carrito.html', context)





@login_required
def añadir_al_carrito(request, id_menu):
    menu = get_object_or_404(Menu, id=id_menu)
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)

   
    item_carrito, creado = ItemCarrito.objects.get_or_create(carrito=carrito, menu=menu)
    if not creado:
        item_carrito.cantidad += 1
        item_carrito.save()

    messages.success(request, f'Has añadido {menu.nombre} a tu carrito.')

    return redirect('/listar_menu')

@require_POST
@login_required
def actualizar_carrito(request):
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')
    item = ItemCarrito.objects.get(id=item_id)

    if action == 'remove_one':
        item.cantidad -= 1
        if item.cantidad < 0:
            item.delete()
        else:
            item.save()
    elif action == 'remove_all':
        item.delete()

    return redirect('/carrito')

@login_required
def procesar_pago(request):
    
    initialize_transbank_sdk()

   
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    total = sum(item.get_cost() for item in items)

    
    orden_compra = uuid.uuid4().hex

    
    sesion_id = request.session.session_key
    
    url_retorno = request.build_absolute_uri(reverse('confirmacion_pago'))

   
    url_pago, token = TransbankService.iniciar_transaccion(
        monto=total,
        orden_compra=orden_compra,
        sesion_id=sesion_id,
        url_retorno=url_retorno
    )

    if url_pago:
        # Si todo está bien, redirige al usuario a la URL de pago
        return redirect(url_pago)
        
    else:
       
        messages.error(request, 'Error al iniciar la transacción con Transbank.')
        return redirect('/carrito')


@login_required
def confirmacion_pago(request):
    
    token_transbank = request.GET.get('token')  
    
   
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)
    total = sum(item.get_cost() for item in items)

    
    boleta = Boleta.objects.create(
        usuario=request.user,
        estado='aprobado',
        total=total,
        
        codigo_autorizacion='codigo_autorizacion_obtenido',
        token_transbank=token_transbank
    )

    
    items.delete()  

   
    return redirect('mostrar_boleta', boleta_id=boleta.id)



@login_required
def mostrar_boleta(request, boleta_id):
    
    boleta = get_object_or_404(Boleta, id=boleta_id, usuario=request.user)
    context = {'boleta': boleta}
    return render(request, 'web/mostrar_boleta.html', context)


def transbank_respuesta(request):
    token = request.GET.get('token_ws')
    resultado = TransbankService.confirmar_transaccion(token)

    if resultado.respuesta_codigo == 0:  
        boleta = Boleta.objects.create(
            usuario=request.user,
            estado='aprobado',
            total=resultado.monto,
            codigo_autorizacion=resultado.codigo_autorizacion,
            token_transbank=token
        )
        
        messages.success(request, 'Pago exitoso.')
    else:
        boleta = Boleta.objects.create(
            usuario=request.user,
            estado='rechazado',
            total=resultado.monto,
            token_transbank=token
        )
        messages.error(request, 'Pago rechazado por Transbank.')

    
    return render(request, 'transbank_respuesta.html', {'boleta': boleta})    
