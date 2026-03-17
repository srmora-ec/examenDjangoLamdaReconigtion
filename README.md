# Clasificador de Imágenes — Django + Lambda + Rekognition

## Arquitectura

```
1 index.html (servido por Django, ya que si lo servía fuera de django daba fallo por las cors)
2 Envía imagen en base64 a Lambda (API Gateway)
3 Lambda guarda imagen en S3
4 Lambda analiza imagen con Rekognition
5 Lambda guarda resultado en Django API
6 index.html muestra resultado y lista historial
```

---

## Requisitos previos

- Cuenta AWS con acceso a: Lambda, API Gateway, S3, Rekognition, Lightsail
- Python 3.10+
- Git

---

## Parte 1: Backend Django

### Estructura del proyecto

```
catalogo_project/
├── catalogo_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── catalogo/
│   ├── models.py       # Modelo Imagen
│   ├── serializers.py  # DRF serializer
│   ├── views.py        # ViewSet + vista index
│   ├── urls.py         # Rutas API
│   └── admin.py        # Registro en Admin
├── templates/
│   └── index.html      # Interfaz web
├── manage.py
└── requirements.txt
```

### Modelo

```python
class Imagen(models.Model):
    nombre       = models.CharField(max_length=255)
    tipo_detectado = models.CharField(max_length=100)
    descripcion  = models.TextField(blank=True)
    archivo      = models.ImageField(upload_to='imagenes/', blank=True, null=True)
    creado_en    = models.DateTimeField(auto_now_add=True)
```

### API REST (Django REST Framework)

La API es pública (`AllowAny`) para que Lambda pueda guardar sin autenticación.

### Instalación local (Windows)

```bash
pip install django djangorestframework pillow django-cors-headers
python manage.py makemigrations catalogo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Parte 2: Función Lambda

### Descripción

La función Lambda recibe una imagen en base64 desde el HTML, la guarda en S3, la analiza con Amazon Rekognition y guarda el resultado en Django.

### Flujo interno

```
1. Recibe { imagen_base64, nombre_archivo }
2. Decodifica el base64 y sube la imagen a S3 (put_object)
3. Llama a Rekognition (detect_labels) para obtener etiquetas (El trabajo pedia un modelo sencillo. Así que se uso el propio de AWS. Pero si no podriamos usar groc que es gratis y esta muy completo)
4. Clasifica las etiquetas en categorías: Foto, Documento, Factura, Paisaje, etc.
5. Hace POST a Django API con nombre, tipo_detectado y descripcion
6. Devuelve el resultado al HTML
```


### Permisos IAM requeridos en el rol de la Lambda

- `AmazonRekognitionReadOnlyAccess`
- `AmazonS3FullAccess`


### Política del bucket

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "mi bucket"
    }
  ]
}

```
---

## Parte 4: Despliegue en Lightsail

### Crear instancia

1. AWS Lightsail → Create instance
2. Platform: Linux / Blueprint: Django (Bitnami)
3. Plan: $7/mes (Da varios dias gratis)
4. Abrir puerto 8000 en Networking → Firewall → Add rule → TCP 8000 → `0.0.0.0/0`

---

## Parte 5: Interfaz Web

El `index.html` permite:

1. Seleccionar una imagen desde el dispositivo
2. Ver una vista previa antes de analizar
3. Enviar la imagen a Lambda que la clasifica automáticamente
4. Ver el resultado: tipo detectado, descripción, ID en BD y nombre en S3
5. Consultar el historial completo de imágenes escaneadas en una tabla

## Evidencia:



https://github.com/user-attachments/assets/29d5ad31-bbb3-483e-9cca-dee941759c3a






