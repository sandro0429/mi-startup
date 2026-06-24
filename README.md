# Flunova

**Flunova** es un copiloto financiero con inteligencia artificial para pequeños negocios en Perú. Ayuda a dueños de bodegas, comerciantes y tiendas familiares a registrar ventas, leer boletas, calcular precios y conocer si su negocio realmente está ganando dinero.

**One-liner:**
Flunova ayuda a dueños de bodegas y pequeños negocios en Perú a conocer su rentabilidad real mediante un copiloto financiero con inteligencia artificial.

---

## Demo

* **App desplegada:** https://copiloto-financiero-pyme.streamlit.app/
* **Repositorio:** https://github.com/sandro0429/mi-startup
* **Negocio de prueba:** TIENDA BASILIO
* **Código de acceso de prueba:** `GATRZD`

---

## Problema

Muchos pequeños negocios venden todos los días, pero no saben con claridad si realmente ganan dinero. En las entrevistas exploratorias realizadas para este proyecto, se identificaron patrones comunes:

* No registran ventas de forma sistemática.
* Guardan boletas, pero no las convierten en información útil.
* Calculan precios por intuición, copiando al vecino o aplicando un markup simple.
* Confunden caja disponible con utilidad real.
* No suelen incluir su propio sueldo como parte del costo del negocio.
* Usan cuaderno, memoria, calculadora o efectivo disponible como principal sistema de control.

El problema no es solo falta de tecnología. Muchas soluciones de gestión hablan en lenguaje contable, pero el pequeño comerciante piensa de forma más práctica: “le subo tanto al costo”, “cuento lo que quedó en caja” o “compro de nuevo con lo que vendí”.

---

## Solución

Flunova transforma ventas, compras y boletas en información financiera simple.

El MVP permite:

1. Crear o ingresar a un negocio mediante un código de acceso.
2. Calcular precios usando costo y markup.
3. Comparar markup con margen real sobre precio de venta.
4. Registrar ventas diarias.
5. Subir una imagen de boleta.
6. Extraer productos, cantidades, precios y subtotales con IA.
7. Corregir los datos extraídos antes de guardarlos.
8. Registrar gastos línea por línea desde la boleta.
9. Configurar costos fijos del negocio.
10. Generar un reporte mensual con ingresos, gastos, costos fijos y utilidad.

---

## Funcionalidades principales

### Calculadora de precios

El usuario ingresa el costo de un producto y el porcentaje que quiere “subirle” al costo. La app calcula un precio sugerido y muestra la diferencia entre:

* **Markup:** cuánto se aumenta sobre el costo.
* **Margen:** cuánto representa la ganancia sobre el precio final.

Esto ayuda a evitar una confusión frecuente: subir 30% al costo no significa ganar 30% del precio de venta.

### Registro de ventas

El usuario registra las ventas del día indicando producto, cantidad y precio unitario. Esto permite construir un historial de ventas que alimenta el reporte mensual.

### Lectura de boletas

El usuario sube una imagen de una boleta física. La IA identifica proveedor, fecha, productos, cantidades, precios unitarios y subtotales. Luego muestra una tabla editable para que el usuario corrija cualquier error antes de guardar.

### Reporte mensual

La app consolida:

* Ingresos por ventas.
* Gastos variables.
* Costos fijos.
* Utilidad del mes.

El objetivo es responder una pregunta simple:

> ¿El negocio está ganando dinero o el dueño está trabajando gratis?

---

## Arquitectura del MVP

La arquitectura del MVP está diseñada para ser simple, funcional y fácil de explicar.

```text
Usuario
  ↓
Streamlit Cloud
  ↓
app.py
  ├── src/ai.py  → Gemini API
  └── src/db.py  → SQLite
  ↓
Reporte mensual y recomendaciones
```

### Componentes

* `app.py`: interfaz principal de Streamlit y coordinación de flujos.
* `src/ai.py`: módulo que centraliza las llamadas a Gemini API.
* `src/db.py`: módulo de persistencia y consultas con SQLite.
* `.streamlit/config.toml`: configuración visual de la app.
* `docs/`: dossier, capturas, arquitectura y evidencia del proyecto.
* `data/`: almacenamiento local del MVP. Las bases reales no se suben al repositorio.

---

## Stack tecnológico

* **Python**
* **Streamlit**
* **SQLite**
* **Pandas**
* **NumPy**
* **Plotly**
* **Pillow**
* **Google Gemini API**
* **python-dotenv**

---

## Herramientas de IA usadas

El proyecto utiliza IA en dos niveles:

### 1. IA dentro del producto

Flunova usa **Gemini API** para:

* Procesar imágenes de boletas.
* Extraer productos, cantidades, precios y subtotales.
* Devolver información estructurada en JSON.
* Generar diagnósticos financieros y recomendaciones simples.

Se eligió Gemini porque permite trabajar con texto e imágenes dentro de un mismo flujo, lo que resulta útil para boletas físicas o escritas a mano.

### 2. IA para construir el producto

Durante el desarrollo se usaron asistentes de IA como apoyo al solo founder:

* Claude para iterar código, estructura de la app y lógica del MVP.
* ChatGPT para organización del repositorio, commits, documentación, pitch y arquitectura.
* Agentes de código como apoyo para acelerar la construcción del prototipo.

El código fue revisado y adaptado para que el founder pueda explicarlo durante la sustentación.

---

## Estructura del repositorio

```text
mi-startup/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── ai.py
│   └── db.py
│
├── .streamlit/
│   └── config.toml
│
├── docs/
│   ├── Flunova_dossier_final.pdf
│   ├── Flunova_dossier_final.pptx
│   ├── architecture/
│   ├── screenshots/
│   ├── research/
│   └── assets/
│
└── data/
```

---

## Cómo correr el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/sandro0429/mi-startup.git
cd mi-startup
```

### 2. Crear entorno virtual

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto usando `.env.example` como referencia:

```env
GEMINI_API_KEY=tu_api_key_aqui
```

Importante: el archivo `.env` no debe subirse al repositorio.

### 5. Ejecutar la app

```bash
streamlit run app.py
```

Si el comando anterior falla, usar:

```bash
python -m streamlit run app.py
```

La app se abrirá localmente en:

```text
http://localhost:8501
```

---

## Variables de entorno

El proyecto usa la siguiente variable:

```env
GEMINI_API_KEY=your_api_key_here
```

En local se carga desde `.env`.
En Streamlit Cloud se configura mediante **Secrets**, no desde el código.

---

## Seguridad y privacidad

* No se sube el archivo `.env`.
* No se suben API keys ni credenciales.
* Las bases de datos locales en `data/*.db` están excluidas del repositorio.
* La boleta real usada como evidencia debe estar anonimizada antes de incluirse en el repositorio público.
* El código de acceso por negocio funciona para el MVP, pero no reemplaza un sistema real de autenticación.

---

## Validación inicial

Se realizaron 5 entrevistas exploratorias no grabadas a pequeños comerciantes y negocios familiares:

1. Comerciante de artículos de cocina y repuestos.
2. Comerciante ambulante nocturna.
3. Bodega familiar.
4. Bodega ubicada en mercado.
5. Emprendedor de artesanía.

Principales hallazgos:

* Ninguno llevaba un registro financiero completamente estructurado.
* La mayoría entiende la ganancia como “lo que queda” al final del día o del mes.
* Los precios se definen por markup, comparación con negocios cercanos o intuición.
* La lectura automática de boletas fue percibida como útil para reducir trabajo manual.
* En negocios de alta rotación, el registro por voz apareció como una mejora futura relevante.

---

## Mercado y modelo de negocio

Flunova parte del sector comercio al por menor en Perú, con foco inicial en Lima y Callao.

* **TAM:** 383,337 empresas de comercio al por menor en Perú.
* **SAM:** 161,922 negocios formales de comercio al por menor en Lima y Callao.
* **SOM año 1:** capturar 2% del mercado direccionable inicial.

### Pricing propuesto

| Plan      |      Precio | Incluye                                                          |
| --------- | ----------: | ---------------------------------------------------------------- |
| Gratis    |     S/0/mes | Hasta 3 análisis de productos y 1 boleta al mes                  |
| Bodeguero |  S/29.9/mes | Registro de ventas, lectura de boletas, gastos y reporte mensual |
| Negocio   | S/59.0/mes | Todo lo anterior + exportación de reportes y funciones avanzadas |

La estrategia inicial no busca maximizar el ingreso por usuario, sino reducir la fricción de adopción. Para un segmento con baja madurez digital, el primer reto es crear el hábito de registrar ventas y boletas.

---

## Roadmap

### 3 meses

* Lanzar versión paga.
* Conseguir 50 usuarios activos.
* Mejorar la recomendación estratégica mensual de la IA.

### 6 meses

* Alcanzar 300 usuarios activos.
* Explorar alianza con la Asociación de Bodegueros del Perú o programas de digitalización.
* Agregar benchmarks por distrito.
* Explorar registro de ventas por voz.

### 12 meses

* Llegar a 1,000 usuarios activos.
* Implementar login real.
* Migrar a PostgreSQL o Supabase.
* Explorar integración con Yape o Plin para registro automático de ventas.

---

## Riesgos principales

1. **Fricción de adopción diaria:** si registrar ventas toma demasiado tiempo, el usuario abandona.
2. **Baja madurez digital:** algunos usuarios pueden necesitar acompañamiento inicial.
3. **Dependencia de proveedor de IA:** el MVP depende de Gemini API.
4. **Autenticación limitada:** el código de negocio funciona para prototipo, pero no para escala.
5. **Confianza:** algunos negocios pueden dudar en compartir información financiera.
6. **Competencia con cuaderno o Excel:** el producto debe demostrar valor inmediato.
7. **Ejecución como solo founder:** el desarrollo depende de una sola persona apoyada por agentes de IA.

---

## Estado actual

* MVP funcional.
* App desplegada en Streamlit Cloud.
* Lectura de boletas con IA funcionando.
* Persistencia con SQLite.
* Registro de ventas y gastos.
* Reporte mensual.
* Dossier final en `docs/`.
* Arquitectura y capturas del producto incluidas.

---

## Autor

**Sandro Sotacuro Escobar**
Estudiante de Economía con concentración en Finanzas, Universidad del Pacífico.
Practicante en el Instituto Peruano de Economía, con experiencia en análisis económico, estudios de mercado, datos y redacción técnica.

---

## Licencia

Este proyecto se distribuye bajo la licencia incluida en el repositorio.
