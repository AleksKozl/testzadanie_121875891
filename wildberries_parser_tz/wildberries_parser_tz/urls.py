from django.contrib import admin
from django.urls import path, include

from products.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('parser/', include('parser.urls')),
    path('api/', include('products.urls')),
    path('', HomeView.as_view(), name='home'),
]
