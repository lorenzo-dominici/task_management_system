from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='base.html'), name='base'),
]
