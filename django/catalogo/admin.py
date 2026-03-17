from django.contrib import admin
from .models import Imagen

@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'tipo_detectado', 'creado_en')
    search_fields = ('nombre', 'tipo_detectado')
    list_filter   = ('tipo_detectado',)