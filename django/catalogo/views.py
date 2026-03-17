from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Imagen
from .serializers import ImagenSerializer

class ImagenViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para Imagen.
    GET    /api/imagenes/          → lista todas
    POST   /api/imagenes/          → crea una nueva  ← Lambda usará este
    GET    /api/imagenes/{id}/     → detalle
    PUT    /api/imagenes/{id}/     → actualiza
    DELETE /api/imagenes/{id}/     → elimina
    """
    queryset           = Imagen.objects.all()
    serializer_class   = ImagenSerializer
    permission_classes = [AllowAny]