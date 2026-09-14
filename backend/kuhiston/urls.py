"""
URL configuration for kuhiston project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from places import views, api
from routes import api as routes_api

urlpatterns = [
    path('', views.home, name='home'),
    path('api/places/', api.PlaceListView.as_view(), name='api-places-list'),
    path('api/places/<int:pk>/', api.PlaceDetailView.as_view(), name='api-places-detail'),
    path('api/route/simple/', api.SimpleRouteView.as_view(), name='api-route-simple'),
    path('api/routes/', routes_api.RouteListView.as_view(), name='api-routes-list'),
    path('api/routes/<int:pk>/', routes_api.RouteDetailView.as_view(), name='api-routes-detail'),
    path('api/categories/', api.CategoryListView.as_view(), name='api-categories'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
