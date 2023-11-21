from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',catalog, name='index'),
    path('superadmin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'), name='logout'),
    path('profil/',profil,name='profil'),
    path('register/', register, name='register'),
    path('request/<int:pk>/', catalog_request_detail, name='catalog_request_detail'),
    path('request/new/', catalog_request_create, name='catalog_request_create'),
    path('request/<int:pk>/edit/', catalog_request_edit, name='catalog_request_edit'),
    path('request/<int:pk>/delete/', catalog_request_delete, name='catalog_request_delete'),
    path('request/', catalog_request_list, name='catalog_request_list'),
    path('request/<str:username>', catalog_request_list, name='catalog_request_list'),
    path('category/', category_list, name='category-list'),
    path('category/new/', category_create, name='category-create'),
    path('category/<int:pk>/', category_detail, name='category-detail'),
    path('category/<int:pk>/edit/', category_edit, name='category-edit'),
    path('category/<int:pk>/delete/', category_delete, name='category-delete'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
