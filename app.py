import streamlit as st
import os
from datetime import datetime
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
tab1, tab_venta, tab2, tab3 = st.tabs([
    "🧮 Analizar producto",
    "📝 Registrar venta",
    "📋 Reporte del negocio",
    "🧾 Leer boleta"
])

with tab1:
    st.markdown("#### 🛒 Calculadora de precio")
    st.caption("Define tu precio de venta a partir de lo que te cuesta el producto y cuánto quieres ganarle.")

    col_izq, col_der = st.columns(2)

    with col_izq:
        nombre = st.text_input("¿Qué producto quieres analizar?",
                               placeholder="Ej: Gaseosa Inca Kola 1.5L")
        costo = st.number_input("Costo de compra (S/)",
                                min_value=0.0, step=0.10, format="%.2f")

    with col_der:
        markup_pct = st.slider(
            "¿Cuánto quieres subirle al costo?",
            min_value=0, max_value=200, value=30, step=5,
            help="Markup: si pones 30%, le subes 30% a lo que te costó el producto."
        )
        precio_sugerido = costo * (1 + markup_pct / 100)
        st.metric("Precio de venta sugerido", f"S/{precio_sugerido:.2f}")

    precio_venta = st.number_input(
        "Precio de venta final (ajústalo si quieres, por ejemplo para redondear)",
        min_value=0.0, step=0.10,
        value=round(precio_sugerido, 2) if costo > 0 else 0.0,
        format="%.2f"
    )

    st.divider()
    analizar = st.button("🔍 Analizar este precio", type="primary", use_container_width=True)

    if analizar:
        if not nombre or costo == 0 or precio_venta == 0:
            st.warning("⚠️ Completa el nombre, el costo y el precio antes de analizar.")
        else:
            # margen sobre el precio de venta (se usa en toda la app para mantener consistencia)
            margen_pct = ((precio_venta - costo) / precio_venta * 100) if precio_venta > 0 else 0
            # markup real sobre el costo, para mostrarlo en sus propios términos
            markup_real = ((precio_venta - costo) / costo * 100) if costo > 0 else 0
            ganancia_unitaria = precio_venta - costo

            # Guardar en la base de datos del negocio
            try:
                db.guardar_producto(
                    negocio_id=negocio_id,
                    nombre=nombre,
                    costo=costo,
                    precio_venta=precio_venta,
                    margen_pct=margen_pct
                )
            except Exception:
                st.warning("No se pudo guardar este análisis en el historial. Tus resultados de abajo igual son correctos.")

            # Métricas principales
            st.markdown("### 📊 Resultados")
            m1, m2, m3 = st.columns(3)
            m1.metric("Ganancia por unidad", f"S/{ganancia_unitaria:.2f}")
            m2.metric("Markup sobre el costo", f"{markup_real:.1f}%")
            m3.metric("Margen sobre el precio", f"{margen_pct:.1f}%")

            st.caption("✅ Este análisis quedó guardado en el historial de tu negocio (pestaña 'Reporte del negocio').")

            if precio_venta <= costo:
                st.error("⚠️ Con este precio estás perdiendo dinero en cada unidad: el precio no cubre ni el costo.")
            elif margen_pct < 25:
                st.warning(f"⚠️ Tu margen sobre el precio de venta es {margen_pct:.1f}%. "
                           f"Para una bodega, lo recomendable suele ser al menos 25%.")
            else:
                st.success("✅ Este precio te deja un margen sano.")

            # Recomendación IA, enfocada solo en este producto
            with st.spinner("Generando recomendación con IA..."):
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
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    texto_reporte = response.text
                except Exception:
                    texto_reporte = None

            st.markdown("### 🤖 Recomendación de la IA")
            if texto_reporte:
                st.write(texto_reporte)
            else:
                st.error("No se pudo generar la recomendación en este momento. Intenta de nuevo en un rato.")

with tab_venta:
    st.markdown("### 📝 Registra lo que vendiste")
    st.caption("Tómate 10 segundos para anotar cada venta del día. Esto es lo que arma tu reporte mensual real.")

    productos_historial = db.listar_productos(negocio_id)
    nombres_productos = sorted(set(p["nombre"] for p in productos_historial))
    opciones_producto = nombres_productos + ["➕ Otro producto (nuevo)"]

    seleccion = st.selectbox("Producto vendido", opciones_producto)

    if seleccion == "➕ Otro producto (nuevo)":
        producto_venta = st.text_input("Nombre del producto")
    else:
        producto_venta = seleccion

    # Si el producto ya fue analizado antes, sugerimos su precio de venta
    precio_sugerido = 0.0
    for p in productos_historial:
        if p["nombre"] == producto_venta:
            precio_sugerido = p["precio_venta"]
            break

    col1, col2 = st.columns(2)
    with col1:
        cantidad_venta = st.number_input("Cantidad vendida", min_value=0.0, step=1.0)
    with col2:
        precio_venta_unitario = st.number_input(
            "Precio de venta unitario (S/)",
            min_value=0.0, step=0.10, value=precio_sugerido, format="%.2f"
        )

    if st.button("✅ Registrar venta", type="primary", use_container_width=True):
        if producto_venta and cantidad_venta > 0 and precio_venta_unitario > 0:
            db.guardar_venta(negocio_id, producto_venta, cantidad_venta, precio_venta_unitario)
            st.success(f"Registrado: {cantidad_venta:g} x {producto_venta} = S/{cantidad_venta * precio_venta_unitario:.2f}")
            st.rerun()
        else:
            st.warning("⚠️ Completa producto, cantidad y precio antes de registrar.")

    st.divider()
    st.markdown("#### 🧾 Ventas de hoy")

    todas_ventas = db.listar_ventas(negocio_id)
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    ventas_hoy = [v for v in todas_ventas if v["fecha"].startswith(hoy_str)]

    if not ventas_hoy:
        st.info("Todavía no registraste ninguna venta hoy.")
    else:
        total_hoy = sum(v["cantidad"] * v["precio_unitario"] for v in ventas_hoy)
        st.metric("Total vendido hoy", f"S/{total_hoy:.2f}")

        filas_ventas = [{
            "Producto": v["producto_nombre"],
            "Cantidad": v["cantidad"],
            "Precio unit.": f"S/{v['precio_unitario']:.2f}",
            "Subtotal": f"S/{v['cantidad'] * v['precio_unitario']:.2f}",
            "Hora": v["fecha"][11:16],
        } for v in ventas_hoy]
        st.dataframe(filas_ventas, use_container_width=True, hide_index=True)

with tab2:
    st.markdown(f"### 📋 Reporte del negocio — {negocio_nombre}")

    # --- Costos fijos del negocio: se configuran una vez, no por producto ---
    costos_actuales = db.obtener_costos_fijos(negocio_id)
    with st.expander("⚙️ Costos fijos del negocio (alquiler, luz, otros)"):
        st.caption(
            "Esto se configura una sola vez y se usa para todos los meses, hasta que lo "
            "actualices. Edítalo cuando tu alquiler o tus gastos fijos cambien."
        )
        cf1, cf2, cf3 = st.columns(3)
        with cf1:
            alquiler_input = st.number_input("Alquiler mensual (S/)", min_value=0.0, step=10.0,
                                              value=float(costos_actuales["alquiler"]))
        with cf2:
            luz_input = st.number_input("Luz y agua (S/)", min_value=0.0, step=10.0,
                                        value=float(costos_actuales["luz"]))
        with cf3:
            otros_input = st.number_input("Otros gastos fijos (S/)", min_value=0.0, step=10.0,
                                          value=float(costos_actuales["otros"]))
        if st.button("Guardar costos fijos"):
            db.guardar_costos_fijos(negocio_id, alquiler_input, luz_input, otros_input)
            st.success("Costos fijos actualizados.")
            st.rerun()

    # --- Resumen mensual real: ventas - gastos variables - costos fijos ---
    meses = db.meses_disponibles(negocio_id)
    mes_actual = datetime.now().strftime("%Y-%m")
    if mes_actual not in meses:
        meses = [mes_actual] + meses

    mes_seleccionado = st.selectbox(
        "Mes a revisar",
        meses,
        index=meses.index(mes_actual)
    )

    resumen = db.resumen_mensual(negocio_id, mes_seleccionado)

    st.markdown("#### 💰 Resultado real del mes")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos por ventas", f"S/{resumen['ingresos']:.2f}")
    c2.metric("Gastos variables", f"S/{resumen['gastos']:.2f}")
    c3.metric("Costos fijos", f"S/{resumen['costos_fijos']:.2f}")
    c4.metric(
        "Utilidad del mes",
        f"S/{resumen['utilidad']:.2f}",
        delta="Ganando ✅" if resumen["utilidad"] > 0 else "Perdiendo ❌"
    )

    if resumen["num_ventas"] == 0:
        st.warning(
            "⚠️ Todavía no hay ventas registradas en este mes. Este resultado no refleja tu "
            "negocio real — ve a la pestaña 'Registrar venta' y anota lo que vendes cada día."
        )
    elif resumen["utilidad"] <= 0:
        st.error("Con lo registrado hasta ahora, este mes estás perdiendo dinero.")
    else:
        st.success("Vas ganando este mes, según lo que llevas registrado.")

    st.caption(
        "Este es un flujo de caja simplificado: ingresos por ventas, menos tus gastos variables "
        "(compras), menos tus costos fijos del negocio."
    )

    st.divider()
    st.markdown("### 🧮 Historial de productos analizados")

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
                "Ganancia/unidad": f"S/{p['precio_venta'] - p['costo']:.2f}",
                "Margen sobre precio": f"{p['margen_pct']:.1f}%",
                "Fecha": p["fecha_registro"][:16].replace("T", " "),
            })
        st.dataframe(filas_tabla, use_container_width=True, hide_index=True)

        st.caption("ℹ️ Esta tabla es para comparar el margen de tus productos entre sí.")

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