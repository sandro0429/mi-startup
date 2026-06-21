import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

# Cargar variables de entorno
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Configuración de página
st.set_page_config(
    page_title="MiMargen",
    page_icon="📊",
    layout="wide"
)

# Header
st.title("📊 MiMargen")
st.markdown("### *¿Tu negocio te está ganando dinero... o estás trabajando gratis?*")
st.divider()

# Tabs principales
tab1, tab2, tab3 = st.tabs(["🧮 Analizar producto", "📋 Reporte del negocio", "🧾 Leer boleta"])

with tab1:
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.markdown("#### 🛒 Tu producto")
        nombre = st.text_input("¿Qué producto quieres analizar?",
                               placeholder="Ej: Gaseosa Inca Kola 1.5L")
        costo = st.number_input("Costo de compra (S/)",
                                min_value=0.0, step=0.10, format="%.2f")
        precio_venta = st.number_input("Precio de venta (S/)",
                                       min_value=0.0, step=0.10, format="%.2f")
        unidades = st.number_input("Unidades vendidas al mes",
                                   min_value=0, step=1)

    with col_der:
        st.markdown("#### 🏪 Tu negocio")
        alquiler = st.number_input("Alquiler mensual (S/)",
                                   min_value=0.0, step=10.0)
        luz = st.number_input("Luz y agua (S/)",
                              min_value=0.0, step=10.0)
        otros = st.number_input("Otros gastos fijos (S/)",
                                min_value=0.0, step=10.0)
        horas_dia = st.slider("Horas que trabajas al día", 1, 16, 10)

    st.divider()
    analizar = st.button("🔍 Analizar mi negocio", type="primary", use_container_width=True)

    if analizar:
        if not nombre or costo == 0 or precio_venta == 0 or unidades == 0:
            st.warning("⚠️ Por favor completa todos los campos antes de analizar.")
        else:
            # Cálculos financieros
            gastos_fijos = alquiler + luz + otros
            ingreso_bruto = precio_venta * unidades
            costo_mercaderia = costo * unidades
            ganancia_bruta = ingreso_bruto - costo_mercaderia
            ganancia_neta = ganancia_bruta - gastos_fijos
            horas_mes = horas_dia * 30
            sueldo_hora = ganancia_neta / horas_mes if horas_mes > 0 else 0
            margen_pct = ((precio_venta - costo) / precio_venta * 100) if precio_venta > 0 else 0
            precio_minimo = (costo_mercaderia + gastos_fijos) / unidades if unidades > 0 else 0

            # Guardar en session_state para el reporte
            st.session_state["resultados"] = {
                "nombre": nombre,
                "costo": costo,
                "precio_venta": precio_venta,
                "unidades": unidades,
                "gastos_fijos": gastos_fijos,
                "ingreso_bruto": ingreso_bruto,
                "ganancia_bruta": ganancia_bruta,
                "ganancia_neta": ganancia_neta,
                "sueldo_hora": sueldo_hora,
                "margen_pct": margen_pct,
                "precio_minimo": precio_minimo,
                "horas_mes": horas_mes
            }

            # Métricas principales
            st.markdown("### 📊 Resultados")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Ingreso bruto/mes", f"S/{ingreso_bruto:.2f}")
            m2.metric("Ganancia neta/mes", f"S/{ganancia_neta:.2f}",
                      delta="Positiva ✅" if ganancia_neta > 0 else "Pérdida ❌")
            m3.metric("Margen por unidad", f"{margen_pct:.1f}%")
            m4.metric("Tu 'sueldo' por hora", f"S/{sueldo_hora:.2f}")

            # Alerta de precio mínimo
            if ganancia_neta <= 0:
                st.error(f"⚠️ Con este precio estás perdiendo dinero. "
                         f"Deberías cobrar mínimo **S/{precio_minimo:.2f}** por unidad para no perder.")
            elif margen_pct < 25:
                st.warning(f"⚠️ Tu margen es bajo ({margen_pct:.1f}%). "
                           f"Lo recomendable para una bodega es mínimo 25%.")
            else:
                st.success("✅ ¡Tu negocio está en números positivos con este producto!")

            # Reporte IA
            with st.spinner("Generando reporte con IA..."):
                prompt = f"""
Eres un asesor financiero que ayuda a dueños de bodegas y tiendas pequeñas en Perú.
Habla en español peruano simple, directo y amigable. Usa soles (S/).
Sé honesto aunque las noticias sean malas. Máximo 250 palabras.

Datos del negocio:
- Producto analizado: {nombre}
- Costo de compra: S/{costo:.2f}
- Precio de venta: S/{precio_venta:.2f}
- Unidades vendidas al mes: {unidades}
- Gastos fijos mensuales: S/{gastos_fijos:.2f}
- Horas trabajadas al día: {horas_dia} ({horas_mes} horas al mes)

Resultados:
- Ingreso bruto mensual: S/{ingreso_bruto:.2f}
- Ganancia bruta: S/{ganancia_bruta:.2f}
- Ganancia neta (después de gastos): S/{ganancia_neta:.2f}
- Margen: {margen_pct:.1f}%
- El dueño se paga S/{sueldo_hora:.2f} por hora trabajada
- Precio mínimo para no perder: S/{precio_minimo:.2f}

Genera un reporte con estas 4 secciones:
1. 🔍 Diagnóstico: ¿está ganando o perdiendo? Sé directo.
2. 💰 Precio justo: qué precio debería cobrar y por qué.
3. 💡 Consejo clave: UNA acción concreta que puede hacer esta semana.
4. 📈 Proyección: si aplica el consejo, cuánto podría ganar al mes.
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            st.markdown("### 🤖 Reporte de tu negocio")
            st.write(response.text)

with tab2:
    if "resultados" not in st.session_state:
        st.info("👈 Primero analiza un producto en la pestaña anterior.")
    else:
        r = st.session_state["resultados"]
        st.markdown(f"### 📋 Reporte financiero — {r['nombre']}")

        st.markdown(f"""
| Concepto | Monto |
|---|---|
| Ingreso bruto mensual | S/{r['ingreso_bruto']:.2f} |
| Costo de mercadería | S/{r['costo'] * r['unidades']:.2f} |
| Ganancia bruta | S/{r['ganancia_bruta']:.2f} |
| Gastos fijos | S/{r['gastos_fijos']:.2f} |
| **Ganancia neta** | **S/{r['ganancia_neta']:.2f}** |
| Precio mínimo por unidad | S/{r['precio_minimo']:.2f} |
| Tu 'sueldo' por hora | S/{r['sueldo_hora']:.2f} |
""")

        if r['ganancia_neta'] > 0:
            st.success(f"✅ Tu negocio genera S/{r['ganancia_neta']:.2f} al mes con este producto.")
        else:
            st.error(f"❌ Estás perdiendo S/{abs(r['ganancia_neta']):.2f} al mes. Ajusta tu precio.")

with tab3:
    st.markdown("#### 🧾 Sube la boleta de tu proveedor")
    st.markdown("Sube una foto o imagen de tu boleta y Gemini extraerá los productos y precios automáticamente.")

    imagen = st.file_uploader("Sube tu boleta (foto o imagen)", type=["jpg", "jpeg", "png"])

    if imagen:
        st.image(imagen, caption="Boleta cargada", use_column_width=True)

        if st.button("📖 Leer boleta con IA", type="primary", use_container_width=True):
            with st.spinner("Analizando boleta con IA..."):
                import base64

                # Leer imagen y convertir a base64
                imagen_bytes = imagen.read()
                imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")

                # Detectar tipo de imagen
                tipo = imagen.type  # ej: image/jpeg

                # Llamar a Gemini Vision
                response_ocr = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": tipo,
                                        "data": imagen_base64
                                    }
                                },
                                {
                                    "text": """Eres un asistente que ayuda a dueños de bodegas peruanas.
Analiza esta boleta o factura de proveedor y extrae:
1. Nombre del proveedor (si aparece)
2. Fecha (si aparece)
3. Lista completa de productos con cantidad, precio unitario y subtotal
4. Total de la boleta

Responde en este formato exacto:
**Proveedor:** [nombre o "No encontrado"]
**Fecha:** [fecha o "No encontrado"]

| Producto | Cantidad | Precio unitario | Subtotal |
|---|---|---|---|
| [producto] | [cantidad] | S/[precio] | S/[subtotal] |

**Total: S/[total]**

Al final agrega este consejo:
💡 Tip: Usa estos costos en la pestaña Analizar producto para calcular tu rentabilidad."""
                                }
                            ]
                        }
                    ]
                )

            st.markdown("### 🤖 Productos identificados")
            st.write(response_ocr.text)
            st.info("💡 Copia el costo unitario de cada producto y úsalo en la pestaña 'Analizar producto'.")