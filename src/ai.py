"""
Capa de acceso a IA para Flunova.

Aisla las llamadas al proveedor de IA (hoy Gemini) detras de funciones simples.
Si en el futuro se cambia de proveedor (Claude, OpenAI, etc.), solo este archivo
necesita cambiar -- el resto de la app llama a estas funciones, no al SDK directo.
"""

import os
import json
from google import genai

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def recomendar_precio(nombre, costo, precio_venta, markup_real, margen_pct):
    """Devuelve una recomendacion corta sobre un precio especifico, o None si falla."""
    prompt = f"""
Eres un asesor de precios para bodegas y tiendas pequeñas en Perú.
Habla en español peruano simple, directo y amigable. Usa soles (S/). Máximo 120 palabras.

Producto: {nombre}
Costo de compra: S/{costo:.2f}
Precio de venta: S/{precio_venta:.2f}
Markup sobre el costo: {markup_real:.1f}%
Margen sobre el precio de venta: {margen_pct:.1f}%

Da una recomendación corta y puntual sobre este precio en particular:
1. Si es un margen saludable para este tipo de producto.
2. Si conviene ajustarlo (redondear, subir o bajar un poco) y por qué.

No menciones ganancias mensuales del negocio ni sueldo del dueño — eso se calcula
en otra parte de la app, con datos reales de ventas del mes.
"""
    try:
        response = _get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception:
        return None


def leer_boleta(imagen_base64, mime_type):
    """Lee una boleta (imagen en base64) y devuelve (datos_json, texto_crudo, error).

    datos_json: dict con los datos estructurados, o None si no se pudo parsear/fallo.
    texto_crudo: la respuesta de texto tal cual de la IA (sirve de respaldo si el JSON falla).
    error: True si la llamada a la IA fallo por completo (ej. sin conexion).
    """
    prompt_ocr = """Eres un asistente que ayuda a dueños de bodegas peruanas a digitalizar
boletas y facturas de compra.

Analiza esta boleta o factura de proveedor y responde UNICAMENTE con un JSON valido,
sin texto antes ni despues, y sin usar bloques de codigo markdown (sin ```). Usa exactamente
esta estructura:

{
  "proveedor": "nombre del proveedor, o null si no aparece",
  "fecha": "fecha de la boleta en formato texto, o null si no aparece",
  "productos": [
    {"nombre": "nombre del producto", "cantidad": numero, "precio_unitario": numero, "subtotal": numero}
  ],
  "total": numero
}

Los numeros van sin el simbolo S/, solo el valor. Si no puedes leer un campo, usa null.
Si no hay productos identificables, devuelve "productos": []."""

    try:
        response_ocr = _get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": mime_type, "data": imagen_base64}},
                        {"text": prompt_ocr}
                    ]
                }
            ]
        )
    except Exception:
        return None, None, True

    texto_crudo = response_ocr.text.strip()
    # por si la IA igual lo envuelve en ```json ... ``` a pesar de la instruccion
    if texto_crudo.startswith("```"):
        texto_crudo = texto_crudo.strip("`")
        if texto_crudo.lower().startswith("json"):
            texto_crudo = texto_crudo[4:]
        texto_crudo = texto_crudo.strip()

    try:
        return json.loads(texto_crudo), None, False
    except json.JSONDecodeError:
        return None, response_ocr.text, False