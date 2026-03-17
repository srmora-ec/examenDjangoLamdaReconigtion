import json
import boto3
import base64
import urllib.request

# ─────────────────────────────────────────────────────────────
DJANGO_API_URL = "/api/imagenes/"
S3_BUCKET      = "clasificador-imagenes-andres"
# ─────────────────────────────────────────────────────────────

rekognition = boto3.client('rekognition', region_name='us-east-1')
s3          = boto3.client('s3',          region_name='us-east-1')

CORS_HEADERS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Headers': 'content-type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
}


def clasificar_etiquetas(etiquetas):
    nombres = [e['Name'].lower() for e in etiquetas]
    reglas  = {
        "Factura":   ["invoice", "receipt", "bill", "check"],
        "Documento": ["document", "text", "paper", "form", "letter", "page", "id card", "passport"],
        "Foto":      ["person", "people", "human", "face", "selfie", "portrait"],
        "Paisaje":   ["nature", "sky", "mountain", "beach", "landscape", "outdoor", "tree", "forest"],
        "Vehículo":  ["car", "vehicle", "truck", "bus", "motorcycle", "automobile"],
        "Alimento":  ["food", "meal", "dish", "fruit", "vegetable", "drink"],
        "Animal":    ["animal", "dog", "cat", "bird", "pet"],
    }
    for tipo, palabras_clave in reglas.items():
        for palabra in palabras_clave:
            if any(palabra in nombre for nombre in nombres):
                return tipo
    return "Otro"


def construir_descripcion(etiquetas, tipo):
    top = [e['Name'] for e in etiquetas[:5]]
    return f"Tipo detectado: {tipo}. Elementos encontrados: {', '.join(top)}."


def lambda_handler(event, context):
    """
    Recibe:
    {
        "imagen_base64": "...",
        "nombre_archivo": "foto.jpg"
    }
    La Lambda guarda la imagen en S3, la analiza con Rekognition y guarda en Django.
    """

    # Preflight CORS
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        # Parsear body
        body = event
        if 'body' in event:
            raw = event['body']
            if event.get('isBase64Encoded'):
                raw = base64.b64decode(raw).decode('utf-8')
            body = json.loads(raw) if isinstance(raw, str) else raw

        imagen_base64  = body.get('imagen_base64')
        nombre_archivo = body.get('nombre_archivo', 'imagen.jpg')

        if not imagen_base64:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Se requiere imagen_base64'})
            }

        # ── 1. Decodificar imagen ───────────────────────────────────
        imagen_bytes = base64.b64decode(imagen_base64)

        # ── 2. Guardar en S3 ────────────────────────────────────────
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=nombre_archivo,
            Body=imagen_bytes,
            ContentType='image/jpeg',
        )

        # ── 3. Rekognition lee desde S3 ─────────────────────────────
        respuesta_rek = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': S3_BUCKET, 'Name': nombre_archivo}},
            MaxLabels=15,
            MinConfidence=60
        )

        etiquetas   = respuesta_rek.get('Labels', [])
        tipo        = clasificar_etiquetas(etiquetas)
        descripcion = construir_descripcion(etiquetas, tipo)

        # ── 4. Guardar en Django ────────────────────────────────────
        payload = json.dumps({
            "nombre":         nombre_archivo,
            "tipo_detectado": tipo,
            "descripcion":    descripcion,
        }).encode('utf-8')

        req = urllib.request.Request(
            DJANGO_API_URL,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            django_response = json.loads(resp.read().decode())

        # ── 5. Respuesta ────────────────────────────────────────────
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'tipo_detectado': tipo,
                'descripcion':    descripcion,
                'guardado_id':    django_response.get('id'),
                'etiquetas_raw':  [e['Name'] for e in etiquetas],
                's3_key':         nombre_archivo,
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }