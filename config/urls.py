from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/performance/", include("performance.urls", namespace="performance")),
    path("api/ticket/", include("ticket.urls", namespace="ticket")),
]
