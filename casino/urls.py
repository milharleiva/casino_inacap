
from django.contrib import admin
from django.urls import path
from menusapp import views
from django.conf.urls import handler404



urlpatterns = [
    path('', views.index),
    path('register/', views.register),
    path('login/', views.login_view),
    path('dashboard/', views.dashboard),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'), 
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('crear_menu/', views.crear_menu, name='crear_menu'),
    path('listar_menu/', views.listar_menu, name='listar_menu'),
    path('carrito/', views.carrito, name='carrito'),
    path('añadir_al_carrito/<int:id_menu>/', views.añadir_al_carrito, name='añadir_al_carrito'),
    path('carrito/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),
    path('confirmacion_pago/', views.confirmacion_pago, name='confirmacion_pago'),
    path('mostrar_boleta/<int:boleta_id>/', views.mostrar_boleta, name='mostrar_boleta'),

]

handler404 = views.Error404View8.as_view()