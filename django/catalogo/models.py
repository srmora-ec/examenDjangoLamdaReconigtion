from django.db import models

class Imagen(models.Model):
    nombre       = models.CharField(max_length=255)
    tipo_detectado = models.CharField(max_length=100)
    descripcion  = models.TextField(blank=True)
    archivo      = models.ImageField(upload_to='imagenes/', blank=True, null=True)
    creado_en    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} — {self.tipo_detectado}"

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"
        ordering = ['-creado_en']