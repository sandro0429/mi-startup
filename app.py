import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from src import db

# Cargar variables de entorno
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Inicializar base de datos (crea las tablas si no existen)
db.init_db()

# Configuración de página
st.set_page_config(
    page_title="MiMargen",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# IDENTIFICACIÓN DEL NEGOCIO (aislamiento de datos por negocio)
# ============================================================
# Como el link es público y compartido, usamos un código simple
# para que cada negocio vea solo su propia información, sin
# necesitar un sistema de login completo.

if "negocio_id" not in st.session_state:
    codigo_url = st.query_params.get("negocio")
    if codigo_url:
        nombre_existente = db.obtener_negocio(codigo_url)
        if nombre_existente:
            st.session_state["negocio_id"] = codigo_url
            st.session_state["negocio_nombre"] = nombre_existente

if "negocio_id" not in st.session_state:
    st.title("📊 MiMargen")
    st.markdown("### Antes de empezar, identifiquemos tu negocio")
    st.info("Esto evita que tu información se mezcle con la de otros negocios que usen este mismo link.")

    modo = st.radio(
        "¿Qué quieres hacer?",
        ["Crear mi negocio (primera vez)", "Ya tengo un código"],
        horizontal=True
    )

    if modo == "Crear mi negocio (primera vez)":
        nombre_negocio = st.text_input("Nombre de tu bodega o negocio")
        if st.button("Crear mi negocio", type="primary", use_container_width=True):
            if nombre_negocio.strip():
                codigo = db.crear_negocio(nombre_negocio.strip())
                st.session_state["negocio_id"] = codigo
                st.session_state["negocio_nombre"] = nombre_negocio.strip()
                st.query_params["negocio"] = codigo
                st.success(f"¡Listo! Tu código es **{codigo}**. Guarda el link de esta página (ya quedó con tu código) para volver a tus datos.")
                st.rerun()
            else:
                st.warning("⚠️ Escribe el nombre de tu negocio antes de continuar.")
    else:
        codigo_input = st.text_input("Ingresa tu código de negocio").strip().upper()
        if st.button("Entrar", type="primary", use_container_width=True):
            nombre = db.obtener_negocio(codigo_input)
            if nombre:
                st.session_state["negocio_id"] = codigo_input
                st.session_state["negocio_nombre"] = nombre
                st.query_params["negocio"] = codigo_input
                st.rerun()
            else:
                st.error("No encontramos ese código. Revisa que esté bien escrito.")

    st.stop()

negocio_id = st.session_state["negocio_id"]
negocio_nombre = st.session_state["negocio_nombre"]

# Header
col_titulo, col_negocio = st.columns([4, 1])
with col_titulo:
    st.title("📊 MiMargen")
    st.markdown("### *¿Tu negocio te está ganando dinero... o estás trabajando gratis?*")
with col_negocio:
    st.markdown(f"🏪 **{negocio_nombre}**")
    st.caption(f"Código: {negocio_id}")
    if st.button("Cambiar de negocio"):
        del st.session_state["negocio_id"]
        del st.session_state["negocio_nombre"]
        st.query_params.clear()
        st.rerun()
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

            # Guardar en session_state para esta sesión
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

            # Guardar en la base de datos del negocio (esto es lo nuevo)
            try:
                db.guardar_producto(
                    negocio_id=negocio_id,
                    nombre=nombre,
                    costo=costo,
                    precio_venta=precio_venta,
                    unidades_mes=unidades,
                    margen_pct=margen_pct,
                    precio_minimo=precio_minimo,
                    ganancia_neta=ganancia_neta,
                    sueldo_hora=sueldo_hora
                )
            except Exception:
                st.warning("No se pudo guardar este análisis en el historial. Tus resultados de abajo igual son correctos.")

            # Métricas principales
            st.markdown("### 📊 Resultados")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Ingreso bruto/mes", f"S/{ingreso_bruto:.2f}")
            m2.metric("Ganancia neta/mes", f"S/{ganancia_neta:.2f}",
                      delta="Positiva ✅" if ganancia_neta > 0 else "Pérdida ❌")
            m3.metric("Margen por unidad", f"{margen_pct:.1f}%")
            m4.metric("Tu 'sueldo' por hora", f"S/{sueldo_hora:.2f}")

            st.caption("✅ Este análisis quedó guardado en el historial de tu negocio (pestaña 'Reporte del negocio').")

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
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    texto_reporte = response.text
                except Exception:
                    texto_reporte = None

            st.markdown("### 🤖 Reporte de tu negocio")
            if texto_reporte:
                st.write(texto_reporte)
            else:
                st.error("No se pudo generar el reporte con IA en este momento. Intenta de nuevo en un rato.")

with tab2:
    st.markdown(f"### 📋 Historial de productos — {negocio_nombre}")

    productos = db.listar_productos(negocio_id)

    if not productos:
        st.info("👈 Aún no has analizado ningún producto. Ve a la pestaña 'Analizar producto' para empezar.")
    else:
        filas_tabla = []
        for p in productos:
            filas_tabla.append({
                "Producto": p["nombre"],
                "Costo": f"S/{p['costo']:.2f}",
                "Precio venta": f"S/{p['precio_venta']:.2f}",
                "Margen": f"{p['margen_pct']:.1f}%",
                "Ganancia neta est.": f"S/{p['ganancia_neta']:.2f}",
                "Sueldo/hora est.": f"S/{p['sueldo_hora']:.2f}",
                "Fecha": p["fecha_registro"][:16].replace("T", " "),
            })
        st.dataframe(filas_tabla, use_container_width=True, hide_index=True)

        st.caption(
            "ℹ️ Cada fila asume que ese producto fuera el único que vendes en el mes "
            "(por eso se le resta el 100% de tus gastos fijos). Cuando tengamos el registro "
            "de ventas diarias, el reporte mensual va a combinar todos tus productos de verdad."
        )

    st.divider()
    st.markdown("### 💸 Gastos registrados")
    gastos = db.listar_gastos(negocio_id)

    if not gastos:
        st.info("Aún no has registrado gastos. Puedes hacerlo desde la pestaña 'Leer boleta'.")
    else:
        total_gastos = sum(g["monto"] for g in gastos)
        st.metric("Total de gastos registrados", f"S/{total_gastos:.2f}")

        filas_gastos = []
        for g in gastos:
            filas_gastos.append({
                "Proveedor": g["proveedor"] or "—",
                "Descripción": g["descripcion"] or "—",
                "Monto": f"S/{g['monto']:.2f}",
                "Origen": g["fuente"],
                "Fecha": g["fecha"][:16].replace("T", " "),
            })
        st.dataframe(filas_gastos, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### 🧾 Sube la boleta de tu proveedor")
    st.markdown("Sube una foto o imagen de tu boleta y Gemini extraerá los productos y precios automáticamente.")

    imagen = st.file_uploader("Sube tu boleta (foto o imagen)", type=["jpg", "jpeg", "png"])

    if imagen:
        st.image(imagen, caption="Boleta cargada", use_container_width=True)

        if st.button("📖 Leer boleta con IA", type="primary", use_container_width=True):
            with st.spinner("Analizando boleta con IA..."):
                import base64

                imagen_bytes = imagen.read()
                imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")
                tipo = imagen.type

                try:
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
                    st.session_state["ocr_texto"] = response_ocr.text
                except Exception:
                    st.session_state["ocr_texto"] = None
                    st.error("No se pudo leer la boleta en este momento. Intenta de nuevo.")

        if st.session_state.get("ocr_texto"):
            st.markdown("### 🤖 Productos identificados")
            st.write(st.session_state["ocr_texto"])
            st.info("💡 Copia el costo unitario de cada producto y úsalo en la pestaña 'Analizar producto'.")

            st.divider()
            st.markdown("#### 💾 Guardar este gasto en tu negocio")
            st.caption("Por ahora se guarda el total de la boleta como un solo gasto. Más adelante esto se va a guardar línea por línea, automáticamente.")
            col_a, col_b = st.columns(2)
            with col_a:
                proveedor_guardar = st.text_input("Proveedor (opcional)", key="proveedor_guardar")
            with col_b:
                monto_guardar = st.number_input("Monto total de la boleta (S/)",
                                                min_value=0.0, step=0.10, key="monto_guardar")
            if st.button("Guardar gasto", type="primary"):
                if monto_guardar > 0:
                    db.guardar_gasto(
                        negocio_id=negocio_id,
                        proveedor=proveedor_guardar,
                        descripcion="Boleta leída con IA",
                        monto=monto_guardar,
                        fuente="boleta"
                    )
                    st.success("Gasto guardado. Lo puedes ver en 'Reporte del negocio'.")
                else:
                    st.warning("Ingresa el monto total antes de guardar.")