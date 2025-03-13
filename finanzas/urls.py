from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='finanzas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='finanzas:dashboard'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Aquí añadiremos más URLs en el futuro
] 