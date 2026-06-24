import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from src import db
from src import ai

# Cargar variables de entorno
load_dotenv()

# Inicializar base de datos (crea las tablas si no existen)
db.init_db()

# Configuración de página
st.set_page_config(
    page_title="Flunova",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# ESTILO VISUAL — paleta navy/teal tomada del diagrama de arquitectura
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Métricas como tarjetas */
div[data-testid="stMetric"] {
    background-color: #EAF6F3;
    border: 1px solid #DCEAE7;
    border-left: 4px solid #0F9B8E;
    border-radius: 10px;
    padding: 1rem 1.1rem;
}
div[data-testid="stMetricValue"] {
    color: #0B1F3F;
    font-weight: 700;
}
div[data-testid="stMetricLabel"] {
    color: #5B6B7C;
    font-weight: 500;
}

/* Pestañas */
div[data-testid="stTabs"] button {
    font-weight: 600;
    color: #5B6B7C;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #0B1F3F;
    border-bottom-color: #0F9B8E !important;
}

/* Botones primarios */
button[kind="primary"] {
    border-radius: 8px;
    font-weight: 600;
}

/* Encabezados */
h1, h2, h3 {
    color: #0B1F3F;
    font-weight: 800;
}

/* Expanders (costos fijos) */
div[data-testid="stExpander"] {
    border: 1px solid #DCEAE7;
    border-radius: 10px;
}

/* Tarjeta de identificación del negocio */
.flunova-badge {
    background-color: #EAF6F3;
    border: 1px solid #DCEAE7;
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    text-align: right;
}
.flunova-badge .nombre { color: #0B1F3F; font-weight: 700; font-size: 0.95rem; }
.flunova-badge .codigo { color: #5B6B7C; font-size: 0.8rem; }

/* Dataframes con bordes redondeados */
div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

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
    st.markdown("""
    <div style="border-bottom: 3px solid #0F9B8E; padding-bottom: 1rem; margin-bottom: 1.5rem;">
        <h1 style="color:#0B1F3F; font-weight:800; margin:0;">📊 Flunova</h1>
        <p style="color:#0F9B8E; font-weight:600; font-size:1.05rem; margin:0.3rem 0 0 0;">
            Copiloto financiero para pequeños negocios
        </p>
    </div>
    """, unsafe_allow_html=True)
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
    st.markdown("""
    <div>
        <h1 style="color:#0B1F3F; font-weight:800; margin:0;">📊 Flunova</h1>
        <p style="color:#0F9B8E; font-weight:600; font-size:1.05rem; margin:0.3rem 0 0 0;">
            ¿Tu negocio te está ganando dinero... o estás trabajando gratis?
        </p>
    </div>
    """, unsafe_allow_html=True)
with col_negocio:
    st.markdown(f"""
    <div class="flunova-badge">
        <div class="nombre">🏪 {negocio_nombre}</div>
        <div class="codigo">Código: {negocio_id}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Cambiar de negocio"):
        del st.session_state["negocio_id"]
        del st.session_state["negocio_nombre"]
        st.query_params.clear()
        st.rerun()
st.markdown('<hr style="border: none; border-top: 3px solid #0F9B8E; margin: 1rem 0 1.5rem 0;">', unsafe_allow_html=True)

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
                texto_reporte = ai.recomendar_precio(nombre, costo, precio_venta, markup_real, margen_pct)

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
    st.markdown("Sube una foto o imagen de tu boleta y la IA va a identificar cada producto, "
                "para que los guardes como gastos sin tener que tipearlos uno por uno.")

    imagen = st.file_uploader("Sube tu boleta (foto o imagen)", type=["jpg", "jpeg", "png"])

    if imagen:
        st.image(imagen, caption="Boleta cargada", use_container_width=True)

        if st.button("📖 Leer boleta con IA", type="primary", use_container_width=True):
            with st.spinner("Analizando boleta con IA..."):
                import base64

                imagen_bytes = imagen.read()
                imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")
                tipo = imagen.type

                datos_json, texto_crudo_fallback, hubo_error = ai.leer_boleta(imagen_base64, tipo)

                if hubo_error:
                    st.session_state["boleta_datos"] = None
                    st.session_state["boleta_texto_crudo"] = None
                    st.error("No se pudo leer la boleta en este momento. Intenta de nuevo.")
                else:
                    st.session_state["boleta_datos"] = datos_json
                    st.session_state["boleta_texto_crudo"] = texto_crudo_fallback

        # --- Caso 1: la IA devolvió datos estructurados correctamente ---
        if st.session_state.get("boleta_datos"):
            datos = st.session_state["boleta_datos"]
            productos_boleta = datos.get("productos") or []

            st.markdown("### 🤖 Productos identificados")
            col_p, col_f = st.columns(2)
            col_p.write(f"**Proveedor:** {datos.get('proveedor') or 'No encontrado'}")
            col_f.write(f"**Fecha en la boleta:** {datos.get('fecha') or 'No encontrada'}")

            if not productos_boleta:
                st.warning("No se identificaron productos en la boleta. Puedes intentar con otra foto más nítida.")
            else:
                st.caption("Revisa y corrige si algo salió mal antes de guardar — puedes editar cualquier celda.")
                productos_editados = st.data_editor(
                    productos_boleta,
                    use_container_width=True,
                    num_rows="dynamic",
                    key="editor_boleta",
                    column_config={
                        "nombre": "Producto",
                        "cantidad": "Cantidad",
                        "precio_unitario": "Precio unitario",
                        "subtotal": "Subtotal",
                    }
                )

                total_calculado = sum((p.get("subtotal") or 0) for p in productos_editados)
                st.metric("Total según las líneas", f"S/{total_calculado:.2f}")
                if datos.get("total") is not None:
                    st.caption(f"La boleta dice un total de S/{datos['total']:.2f}. "
                               f"Si no coincide, revisa las líneas arriba.")

                if st.button("💾 Guardar estos gastos en mi negocio", type="primary", use_container_width=True):
                    proveedor_final = datos.get("proveedor") or "Sin proveedor"
                    guardados = 0
                    for p in productos_editados:
                        nombre_p = p.get("nombre")
                        subtotal_p = p.get("subtotal")
                        if nombre_p and subtotal_p:
                            db.guardar_gasto(
                                negocio_id=negocio_id,
                                proveedor=proveedor_final,
                                descripcion=str(nombre_p),
                                monto=float(subtotal_p),
                                fuente="boleta"
                            )
                            guardados += 1
                    if guardados:
                        st.success(f"Se guardaron {guardados} gastos en tu historial. "
                                   f"Los puedes ver en 'Reporte del negocio'.")
                    else:
                        st.warning("No había líneas válidas para guardar (revisa que tengan nombre y subtotal).")

        # --- Caso 2: la IA no devolvió JSON válido -> fallback manual ---
        elif st.session_state.get("boleta_texto_crudo"):
            st.markdown("### 🤖 No se pudo estructurar automáticamente")
            st.write(st.session_state["boleta_texto_crudo"])
            st.info("La IA respondió, pero no en el formato esperado. Puedes registrar el gasto a mano abajo.")

            col_a, col_b = st.columns(2)
            with col_a:
                proveedor_guardar = st.text_input("Proveedor (opcional)", key="proveedor_guardar")
            with col_b:
                monto_guardar = st.number_input("Monto total de la boleta (S/)",
                                                min_value=0.0, step=0.10, key="monto_guardar")
            if st.button("Guardar gasto manual", type="primary"):
                if monto_guardar > 0:
                    db.guardar_gasto(
                        negocio_id=negocio_id,
                        proveedor=proveedor_guardar,
                        descripcion="Boleta leída con IA (manual)",
                        monto=monto_guardar,
                        fuente="boleta"
                    )
                    st.success("Gasto guardado. Lo puedes ver en 'Reporte del negocio'.")
                else:
                    st.warning("Ingresa el monto total antes de guardar.")