"""
URL configuration for Dynamic_Price_Prediction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users import views as uv
from admins import views
urlpatterns = [
    path('admin/', admin.site.urls),
     path('', uv.home, name='home'),
    path('register/', uv.register, name='register'),
    path('register_success/', uv.register_success, name='register_success'),
    path('admin/', views.admin, name='admin'),
    path('admin_view',views.admin,name='admin_view'),
    path('admin_approval/', views.admin_approval, name='admin_approval'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject_user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('toggle_approval/<int:user_id>/', views.toggle_approval, name='toggle_approval'),
    path('login/',uv.login,name='login'),
    path('dashboard/',uv.dashboard,name='dashboard'),
    path('training/',uv.train_view,name='training'),
    path('prediction/',uv.predict_view,name='prediction')
]
