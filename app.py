import streamlit as st
import pandas as pd
from supabase import create_client


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

st.set_page_config(
    page_title="Control de Inventario - Bodega",
    page_icon="🏪",
    layout="wide"
)

# ==========================================================
# DISEÑO VISUAL
# ==========================================================

st.markdown("""
<style>

/* FONDO GENERAL */
.stApp {
    background: linear-gradient(135deg, #f4f9ff 0%, #eef7f4 100%);
}

/* CONTENIDO PRINCIPAL */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* BARRA LATERAL */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f4e78 0%, #2f75b5 100%);
}

/* TEXTO DE LA BARRA LATERAL */
section[data-testid="stSidebar"] * {
    color: white;
}

/* SELECTBOX DEL MENÚ */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: white;
    color: #1f2937;
    border-radius: 10px;
}

/* TITULOS */
h1 {
    color: #1f4e78;
    font-weight: 800;
}

h2, h3 {
    color: #2f75b5;
}

/* BOTONES */
.stButton > button {
    background: linear-gradient(90deg, #2f75b5, #1f4e78);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg, #1f4e78, #163a5c);
    color: white;
}

/* METRICAS */
div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #dbeafe;
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* INPUTS */
div[data-baseweb="input"] > div {
    border-radius: 10px;
}

/* SELECTBOX */
div[data-baseweb="select"] > div {
    border-radius: 10px;
}

/* TABS */
button[data-baseweb="tab"] {
    font-weight: 700;
    border-radius: 8px 8px 0 0;
}

/* TAB ACTIVO */
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1f4e78;
    background-color: #dbeafe;
}

/* TABLAS */
div[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 12px;
    padding: 10px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
}

/* MENSAJES */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* LINEAS */
hr {
    border: none;
    height: 1px;
    background-color: #dbeafe;
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #2f75b5;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)
# ==========================================================
# CONEXIÓN CON SUPABASE
# ==========================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==========================================================
# FUNCIONES GENERALES
# ==========================================================

def obtener_productos():
    respuesta = (
        supabase
        .table("productos")
        .select("*")
        .order("codigo_producto")
        .execute()
    )
    return respuesta.data


def obtener_movimientos():
    respuesta = (
        supabase
        .table("movimientos_inventario")
        .select("*")
        .order("fecha_movimiento", desc=True)
        .execute()
    )
    return respuesta.data


def obtener_categorias():
    respuesta = (
        supabase
        .table("categorias")
        .select("*")
        .eq("estado", True)
        .order("nombre_categoria")
        .execute()
    )
    return respuesta.data


def obtener_marcas():
    respuesta = (
        supabase
        .table("marcas")
        .select("*")
        .eq("estado", True)
        .order("nombre_marca")
        .execute()
    )
    return respuesta.data


def obtener_unidades():
    respuesta = (
        supabase
        .table("unidades_medida")
        .select("*")
        .eq("estado", True)
        .order("nombre_unidad")
        .execute()
    )
    return respuesta.data


def obtener_productos_completos():
    respuesta = (
        supabase
        .table("productos")
        .select(
            "*, categorias(nombre_categoria), "
            "marcas(nombre_marca), "
            "unidades_medida(nombre_unidad,abreviatura)"
        )
        .order("codigo_producto")
        .execute()
    )
    return respuesta.data


# ==========================================================
# MENÚ LATERAL
# ==========================================================

st.sidebar.title("🏪 INVENTARIO")

opcion = st.sidebar.selectbox(
    "Seleccione una opción",
    [
        "Inicio",
        "Productos",
        "Proveedores",
        "Clientes",
        "Compras",
        "Ventas",
        "Kardex",
        "Stock bajo",
        "Reportes"
    ]
)


# ==========================================================
# INICIO / DASHBOARD
# ==========================================================

if opcion == "Inicio":

    st.title("🏪 Sistema de Control de Inventario")

    st.write(
        "Bodega de Abarrotes - Panel principal de control"
    )

    st.divider()

    try:

        productos = obtener_productos()
        df_productos = pd.DataFrame(productos)

        if df_productos.empty:

            st.warning(
                "No existen productos registrados."
            )

        else:

            # --------------------------------------------------
            # INDICADORES
            # --------------------------------------------------

            total_productos = len(df_productos)

            stock_bajo = df_productos[
                df_productos["stock_actual"]
                <=
                df_productos["stock_minimo"]
            ]

            total_stock_bajo = len(stock_bajo)

            agotados = df_productos[
                df_productos["stock_actual"] == 0
            ]

            total_agotados = len(agotados)

            df_productos["valor_inventario"] = (
                df_productos["stock_actual"]
                *
                df_productos["precio_compra"]
            )

            valor_total = (
                df_productos["valor_inventario"].sum()
            )

            st.subheader(
                "📊 Indicadores del inventario"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "📦 Productos registrados",
                    total_productos
                )

            with col2:
                st.metric(
                    "⚠️ Stock bajo",
                    total_stock_bajo
                )

            with col3:
                st.metric(
                    "❌ Productos agotados",
                    total_agotados
                )

            with col4:
                st.metric(
                    "💰 Valor del inventario",
                    f"S/ {valor_total:,.2f}"
                )

            st.divider()

            # --------------------------------------------------
            # ENTRADAS Y SALIDAS
            # --------------------------------------------------

            movimientos = obtener_movimientos()

            df_movimientos = pd.DataFrame(
                movimientos
            )

            total_entradas = 0
            total_salidas = 0

            if not df_movimientos.empty:

                entradas = df_movimientos[
                    df_movimientos[
                        "tipo_movimiento"
                    ] == "ENTRADA"
                ]

                salidas = df_movimientos[
                    df_movimientos[
                        "tipo_movimiento"
                    ] == "SALIDA"
                ]

                if not entradas.empty:
                    total_entradas = (
                        entradas["cantidad"].sum()
                    )

                if not salidas.empty:
                    total_salidas = (
                        salidas["cantidad"].sum()
                    )

            col5, col6 = st.columns(2)

            with col5:
                st.metric(
                    "📥 Entradas de inventario",
                    f"{total_entradas:,.0f} unidades"
                )

            with col6:
                st.metric(
                    "📤 Salidas de inventario",
                    f"{total_salidas:,.0f} unidades"
                )

            st.divider()

            # --------------------------------------------------
            # INVENTARIO ACTUAL
            # --------------------------------------------------

            st.subheader(
                "📦 Estado actual del inventario"
            )

            columnas = [
                "codigo_producto",
                "nombre_producto",
                "stock_actual",
                "stock_minimo",
                "stock_maximo",
                "precio_compra",
                "precio_venta",
                "ubicacion"
            ]

            st.dataframe(
                df_productos[columnas],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # --------------------------------------------------
            # ALERTA STOCK BAJO
            # --------------------------------------------------

            st.subheader(
                "⚠️ Productos que necesitan reposición"
            )

            if total_stock_bajo > 0:

                st.warning(
                    f"Hay {total_stock_bajo} productos "
                    "que necesitan reposición."
                )

                st.dataframe(
                    stock_bajo[
                        [
                            "codigo_producto",
                            "nombre_producto",
                            "stock_actual",
                            "stock_minimo"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "✅ No existen productos "
                    "con stock bajo."
                )

    except Exception as e:

        st.error(
            "❌ Ocurrió un error al consultar Supabase."
        )

        st.code(str(e))


# ==========================================================
# PRODUCTOS
# ==========================================================

elif opcion == "Productos":

    st.title("📦 Gestión de Productos")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔎 Consultar",
            "➕ Agregar",
            "✏️ Actualizar",
            "🚫 Desactivar"
        ]
    )


    # ======================================================
    # TAB 1 - CONSULTAR
    # ======================================================

    with tab1:

        st.subheader("🔎 Consultar productos")

        try:

            productos = obtener_productos_completos()

            df = pd.DataFrame(productos)

            if df.empty:

                st.warning(
                    "No hay productos registrados."
                )

            else:

                buscar = st.text_input(
                    "Buscar por código o nombre"
                )

                if buscar:

                    texto = buscar.lower()

                    df = df[
                        df["codigo_producto"]
                        .str.lower()
                        .str.contains(
                            texto,
                            na=False
                        )
                        |
                        df["nombre_producto"]
                        .str.lower()
                        .str.contains(
                            texto,
                            na=False
                        )
                    ]

                df["categoria"] = df[
                    "categorias"
                ].apply(
                    lambda x:
                    x.get(
                        "nombre_categoria",
                        ""
                    )
                    if isinstance(x, dict)
                    else ""
                )

                df["marca"] = df[
                    "marcas"
                ].apply(
                    lambda x:
                    x.get(
                        "nombre_marca",
                        ""
                    )
                    if isinstance(x, dict)
                    else ""
                )

                df["unidad"] = df[
                    "unidades_medida"
                ].apply(
                    lambda x:
                    x.get(
                        "nombre_unidad",
                        ""
                    )
                    if isinstance(x, dict)
                    else ""
                )

                columnas = [
                    "codigo_producto",
                    "nombre_producto",
                    "categoria",
                    "marca",
                    "unidad",
                    "presentacion",
                    "precio_compra",
                    "precio_venta",
                    "stock_actual",
                    "stock_minimo",
                    "stock_maximo",
                    "ubicacion",
                    "estado"
                ]

                st.dataframe(
                    df[columnas],
                    use_container_width=True,
                    hide_index=True
                )

                st.info(
                    f"📦 Productos encontrados: {len(df)}"
                )

        except Exception as e:

            st.error(
                "❌ No se pudieron consultar "
                "los productos."
            )

            st.code(str(e))


    # ======================================================
    # TAB 2 - AGREGAR
    # ======================================================

    with tab2:

        st.subheader(
            "➕ Registrar nuevo producto"
        )

        try:

            categorias = obtener_categorias()
            marcas = obtener_marcas()
            unidades = obtener_unidades()

            dic_categorias = {
                x["nombre_categoria"]:
                x["id_categoria"]
                for x in categorias
            }

            dic_marcas = {
                x["nombre_marca"]:
                x["id_marca"]
                for x in marcas
            }

            dic_unidades = {
                x["nombre_unidad"]:
                x["id_unidad"]
                for x in unidades
            }

            with st.form(
                "form_nuevo_producto"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    codigo = st.text_input(
                        "Código del producto",
                        placeholder="Ejemplo: PROD101"
                    )

                    nombre = st.text_input(
                        "Nombre del producto",
                        placeholder="Ejemplo: Gaseosa Fanta"
                    )

                    categoria = st.selectbox(
                        "Categoría",
                        list(
                            dic_categorias.keys()
                        )
                    )

                    marca = st.selectbox(
                        "Marca",
                        list(
                            dic_marcas.keys()
                        )
                    )

                    unidad = st.selectbox(
                        "Unidad de medida",
                        list(
                            dic_unidades.keys()
                        )
                    )

                    presentacion = st.text_input(
                        "Presentación",
                        placeholder="Ejemplo: Botella 500 ml"
                    )

                with col2:

                    precio_compra = (
                        st.number_input(
                            "Precio de compra",
                            min_value=0.0,
                            value=0.0,
                            step=0.10,
                            format="%.2f"
                        )
                    )

                    precio_venta = (
                        st.number_input(
                            "Precio de venta",
                            min_value=0.0,
                            value=0.0,
                            step=0.10,
                            format="%.2f"
                        )
                    )

                    stock_actual = (
                        st.number_input(
                            "Stock inicial",
                            min_value=0.0,
                            value=0.0,
                            step=1.0
                        )
                    )

                    stock_minimo = (
                        st.number_input(
                            "Stock mínimo",
                            min_value=0.0,
                            value=5.0,
                            step=1.0
                        )
                    )

                    stock_maximo = (
                        st.number_input(
                            "Stock máximo",
                            min_value=0.0,
                            value=50.0,
                            step=1.0
                        )
                    )

                    ubicacion = st.text_input(
                        "Ubicación",
                        placeholder="Ejemplo: Estante A1"
                    )

                descripcion = st.text_area(
                    "Descripción"
                )

                guardar = (
                    st.form_submit_button(
                        "💾 Guardar producto"
                    )
                )

                if guardar:

                    codigo_limpio = (
                        codigo.strip().upper()
                    )

                    if codigo_limpio == "":

                        st.error(
                            "❌ Ingresa el código."
                        )

                    elif nombre.strip() == "":

                        st.error(
                            "❌ Ingresa el nombre."
                        )

                    elif precio_compra <= 0:

                        st.error(
                            "❌ El precio de compra "
                            "debe ser mayor que 0."
                        )

                    elif precio_venta <= 0:

                        st.error(
                            "❌ El precio de venta "
                            "debe ser mayor que 0."
                        )

                    elif (
                        precio_venta
                        <
                        precio_compra
                    ):

                        st.error(
                            "❌ El precio de venta "
                            "no debe ser menor que "
                            "el precio de compra."
                        )

                    elif (
                        stock_maximo
                        <
                        stock_minimo
                    ):

                        st.error(
                            "❌ El stock máximo no "
                            "puede ser menor que "
                            "el stock mínimo."
                        )

                    else:

                        existe = (
                            supabase
                            .table("productos")
                            .select("id_producto")
                            .eq(
                                "codigo_producto",
                                codigo_limpio
                            )
                            .execute()
                        )

                        if existe.data:

                            st.error(
                                f"❌ El código "
                                f"{codigo_limpio} "
                                "ya existe."
                            )

                        else:

                            nuevo = {
                                "codigo_producto":
                                    codigo_limpio,
                                "nombre_producto":
                                    nombre.strip(),
                                "id_categoria":
                                    dic_categorias[
                                        categoria
                                    ],
                                "id_marca":
                                    dic_marcas[
                                        marca
                                    ],
                                "id_unidad":
                                    dic_unidades[
                                        unidad
                                    ],
                                "presentacion":
                                    presentacion.strip(),
                                "descripcion":
                                    descripcion.strip(),
                                "precio_compra":
                                    precio_compra,
                                "precio_venta":
                                    precio_venta,
                                "stock_actual":
                                    stock_actual,
                                "stock_minimo":
                                    stock_minimo,
                                "stock_maximo":
                                    stock_maximo,
                                "ubicacion":
                                    ubicacion.strip(),
                                "estado":
                                    True
                            }

                            (
                                supabase
                                .table("productos")
                                .insert(nuevo)
                                .execute()
                            )

                            st.success(
                                "✅ Producto registrado "
                                "correctamente."
                            )

                            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo registrar "
                "el producto."
            )

            st.code(str(e))


    # ======================================================
    # TAB 3 - ACTUALIZAR
    # ======================================================

    with tab3:

        st.subheader(
            "✏️ Actualizar producto"
        )

        try:

            productos = (
                supabase
                .table("productos")
                .select("*")
                .eq("estado", True)
                .order("nombre_producto")
                .execute()
                .data
            )

            categorias = obtener_categorias()
            marcas = obtener_marcas()
            unidades = obtener_unidades()

            if not productos:

                st.warning(
                    "No hay productos activos."
                )

            else:

                opciones = {
                    (
                        f'{p["codigo_producto"]} - '
                        f'{p["nombre_producto"]}'
                    ): p
                    for p in productos
                }

                seleccionado = st.selectbox(
                    "Selecciona un producto",
                    list(opciones.keys()),
                    key="producto_actualizar"
                )

                producto = opciones[
                    seleccionado
                ]

                dic_categorias = {
                    x["nombre_categoria"]:
                    x["id_categoria"]
                    for x in categorias
                }

                dic_marcas = {
                    x["nombre_marca"]:
                    x["id_marca"]
                    for x in marcas
                }

                dic_unidades = {
                    x["nombre_unidad"]:
                    x["id_unidad"]
                    for x in unidades
                }

                nombres_categorias = list(
                    dic_categorias.keys()
                )

                nombres_marcas = list(
                    dic_marcas.keys()
                )

                nombres_unidades = list(
                    dic_unidades.keys()
                )

                categoria_actual = next(
                    (
                        nombre
                        for nombre, identificador
                        in dic_categorias.items()
                        if identificador
                        ==
                        producto["id_categoria"]
                    ),
                    nombres_categorias[0]
                )

                marca_actual = next(
                    (
                        nombre
                        for nombre, identificador
                        in dic_marcas.items()
                        if identificador
                        ==
                        producto["id_marca"]
                    ),
                    nombres_marcas[0]
                )

                unidad_actual = next(
                    (
                        nombre
                        for nombre, identificador
                        in dic_unidades.items()
                        if identificador
                        ==
                        producto["id_unidad"]
                    ),
                    nombres_unidades[0]
                )

                with st.form(
                    "form_actualizar_producto"
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        nombre_nuevo = st.text_input(
                            "Nombre",
                            value=producto[
                                "nombre_producto"
                            ]
                        )

                        categoria_nueva = (
                            st.selectbox(
                                "Categoría",
                                nombres_categorias,
                                index=(
                                    nombres_categorias
                                    .index(
                                        categoria_actual
                                    )
                                )
                            )
                        )

                        marca_nueva = st.selectbox(
                            "Marca",
                            nombres_marcas,
                            index=(
                                nombres_marcas
                                .index(
                                    marca_actual
                                )
                            )
                        )

                        unidad_nueva = (
                            st.selectbox(
                                "Unidad",
                                nombres_unidades,
                                index=(
                                    nombres_unidades
                                    .index(
                                        unidad_actual
                                    )
                                )
                            )
                        )

                        presentacion_nueva = (
                            st.text_input(
                                "Presentación",
                                value=(
                                    producto[
                                        "presentacion"
                                    ]
                                    or ""
                                )
                            )
                        )

                        ubicacion_nueva = (
                            st.text_input(
                                "Ubicación",
                                value=(
                                    producto[
                                        "ubicacion"
                                    ]
                                    or ""
                                )
                            )
                        )

                    with col2:

                        compra_nueva = (
                            st.number_input(
                                "Precio compra",
                                min_value=0.0,
                                value=float(
                                    producto[
                                        "precio_compra"
                                    ]
                                ),
                                step=0.10,
                                format="%.2f"
                            )
                        )

                        venta_nueva = (
                            st.number_input(
                                "Precio venta",
                                min_value=0.0,
                                value=float(
                                    producto[
                                        "precio_venta"
                                    ]
                                ),
                                step=0.10,
                                format="%.2f"
                            )
                        )

                        minimo_nuevo = (
                            st.number_input(
                                "Stock mínimo",
                                min_value=0.0,
                                value=float(
                                    producto[
                                        "stock_minimo"
                                    ]
                                ),
                                step=1.0
                            )
                        )

                        maximo_nuevo = (
                            st.number_input(
                                "Stock máximo",
                                min_value=0.0,
                                value=float(
                                    producto[
                                        "stock_maximo"
                                    ]
                                ),
                                step=1.0
                            )
                        )

                    descripcion_nueva = (
                        st.text_area(
                            "Descripción",
                            value=(
                                producto[
                                    "descripcion"
                                ]
                                or ""
                            )
                        )
                    )

                    actualizar = (
                        st.form_submit_button(
                            "💾 Actualizar producto"
                        )
                    )

                    if actualizar:

                        if (
                            maximo_nuevo
                            <
                            minimo_nuevo
                        ):

                            st.error(
                                "❌ El stock máximo "
                                "no puede ser menor "
                                "que el mínimo."
                            )

                        elif (
                            venta_nueva
                            <
                            compra_nueva
                        ):

                            st.error(
                                "❌ El precio de venta "
                                "no debe ser menor que "
                                "el precio de compra."
                            )

                        else:

                            datos = {
                                "nombre_producto":
                                    nombre_nuevo.strip(),
                                "id_categoria":
                                    dic_categorias[
                                        categoria_nueva
                                    ],
                                "id_marca":
                                    dic_marcas[
                                        marca_nueva
                                    ],
                                "id_unidad":
                                    dic_unidades[
                                        unidad_nueva
                                    ],
                                "presentacion":
                                    presentacion_nueva.strip(),
                                "descripcion":
                                    descripcion_nueva.strip(),
                                "precio_compra":
                                    compra_nueva,
                                "precio_venta":
                                    venta_nueva,
                                "stock_minimo":
                                    minimo_nuevo,
                                "stock_maximo":
                                    maximo_nuevo,
                                "ubicacion":
                                    ubicacion_nueva.strip()
                            }

                            (
                                supabase
                                .table("productos")
                                .update(datos)
                                .eq(
                                    "id_producto",
                                    producto[
                                        "id_producto"
                                    ]
                                )
                                .execute()
                            )

                            st.success(
                                "✅ Producto actualizado."
                            )

                            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo actualizar "
                "el producto."
            )

            st.code(str(e))


    # ======================================================
    # TAB 4 - DESACTIVAR
    # ======================================================

    with tab4:

        st.subheader(
            "🚫 Desactivar producto"
        )

        st.warning(
            "El producto no se eliminará de "
            "la base de datos. Solo quedará inactivo."
        )

        try:

            activos = (
                supabase
                .table("productos")
                .select(
                    "id_producto,"
                    "codigo_producto,"
                    "nombre_producto,"
                    "stock_actual"
                )
                .eq("estado", True)
                .order("nombre_producto")
                .execute()
                .data
            )

            if not activos:

                st.info(
                    "No existen productos activos."
                )

            else:

                opciones = {
                    (
                        f'{p["codigo_producto"]} - '
                        f'{p["nombre_producto"]} '
                        f'(Stock: {p["stock_actual"]})'
                    ): p["id_producto"]
                    for p in activos
                }

                seleccionado = st.selectbox(
                    "Selecciona el producto",
                    list(opciones.keys()),
                    key="producto_desactivar"
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo "
                    "desactivar este producto."
                )

                if st.button(
                    "🚫 Desactivar producto"
                ):

                    if not confirmar:

                        st.warning(
                            "⚠️ Debes confirmar "
                            "la operación."
                        )

                    else:

                        (
                            supabase
                            .table("productos")
                            .update(
                                {"estado": False}
                            )
                            .eq(
                                "id_producto",
                                opciones[
                                    seleccionado
                                ]
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Producto desactivado."
                        )

                        st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo desactivar "
                "el producto."
            )

            st.code(str(e))



# ==========================================================
# PROVEEDORES
# ==========================================================

elif opcion == "Proveedores":

    st.title("🚚 Gestión de Proveedores")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔎 Consultar",
            "➕ Agregar",
            "✏️ Actualizar",
            "🚫 Desactivar"
        ]
    )


    # ======================================================
    # TAB 1 - CONSULTAR PROVEEDORES
    # ======================================================

    with tab1:

        st.subheader("🔎 Consultar proveedores")

        try:

            respuesta = (
                supabase
                .table("proveedores")
                .select("*")
                .order("razon_social")
                .execute()
            )

            proveedores = respuesta.data

            df_proveedores = pd.DataFrame(proveedores)

            if df_proveedores.empty:

                st.warning(
                    "No hay proveedores registrados."
                )

            else:

                buscar = st.text_input(
                    "Buscar por razón social, RUC o contacto",
                    key="buscar_proveedor"
                )

                if buscar:

                    texto = buscar.lower()

                    filtro = (
                        df_proveedores["razon_social"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_proveedores["ruc"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_proveedores["nombre_contacto"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                    )

                    df_proveedores = df_proveedores[
                        filtro
                    ]

                columnas = [
                    "id_proveedor",
                    "razon_social",
                    "ruc",
                    "nombre_contacto",
                    "telefono",
                    "correo",
                    "direccion",
                    "distrito",
                    "ciudad",
                    "metodo_pago_preferido",
                    "estado"
                ]

                columnas_existentes = [
                    col
                    for col in columnas
                    if col in df_proveedores.columns
                ]

                st.dataframe(
                    df_proveedores[
                        columnas_existentes
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                st.info(
                    f"🚚 Proveedores encontrados: "
                    f"{len(df_proveedores)}"
                )

        except Exception as e:

            st.error(
                "❌ No se pudieron consultar "
                "los proveedores."
            )

            st.code(str(e))


    # ======================================================
    # TAB 2 - AGREGAR PROVEEDOR
    # ======================================================

    with tab2:

        st.subheader("➕ Registrar nuevo proveedor")

        try:

            with st.form(
                "form_nuevo_proveedor"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    razon_social = st.text_input(
                        "Razón social",
                        placeholder=(
                            "Ejemplo: Distribuidora "
                            "San José SAC"
                        )
                    )

                    ruc = st.text_input(
                        "RUC",
                        placeholder="Ejemplo: 20123456789"
                    )

                    nombre_contacto = st.text_input(
                        "Nombre del contacto",
                        placeholder="Ejemplo: Carlos Pérez"
                    )

                    telefono = st.text_input(
                        "Teléfono",
                        placeholder="Ejemplo: 987654321"
                    )

                    correo = st.text_input(
                        "Correo",
                        placeholder=(
                            "Ejemplo: "
                            "ventas@proveedor.com"
                        )
                    )

                with col2:

                    direccion = st.text_input(
                        "Dirección",
                        placeholder=(
                            "Ejemplo: Av. Principal 123"
                        )
                    )

                    distrito = st.text_input(
                        "Distrito",
                        placeholder="Ejemplo: Huacho"
                    )

                    ciudad = st.text_input(
                        "Ciudad",
                        placeholder="Ejemplo: Huacho"
                    )

                    metodo_pago = st.selectbox(
                        "Método de pago preferido",
                        [
                            "Efectivo",
                            "Transferencia",
                            "Crédito",
                            "Yape",
                            "Plin",
                            "Otro"
                        ]
                    )

                observaciones = st.text_area(
                    "Observaciones"
                )

                guardar = (
                    st.form_submit_button(
                        "💾 Guardar proveedor"
                    )
                )

                if guardar:

                    razon_limpia = (
                        razon_social.strip()
                    )

                    ruc_limpio = ruc.strip()

                    if razon_limpia == "":

                        st.error(
                            "❌ Debes ingresar "
                            "la razón social."
                        )

                    elif (
                        ruc_limpio != ""
                        and
                        len(ruc_limpio) != 11
                    ):

                        st.error(
                            "❌ El RUC debe tener "
                            "11 dígitos."
                        )

                    elif (
                        ruc_limpio != ""
                        and
                        not ruc_limpio.isdigit()
                    ):

                        st.error(
                            "❌ El RUC debe contener "
                            "solo números."
                        )

                    else:

                        existe = []

                        if ruc_limpio != "":

                            verificar = (
                                supabase
                                .table("proveedores")
                                .select(
                                    "id_proveedor, ruc"
                                )
                                .eq(
                                    "ruc",
                                    ruc_limpio
                                )
                                .execute()
                            )

                            existe = verificar.data

                        if existe:

                            st.error(
                                f"❌ El RUC "
                                f"{ruc_limpio} "
                                "ya está registrado."
                            )

                        else:

                            nuevo_proveedor = {
                                "razon_social":
                                    razon_limpia,
                                "ruc":
                                    (
                                        ruc_limpio
                                        if ruc_limpio
                                        else None
                                    ),
                                "nombre_contacto":
                                    nombre_contacto.strip(),
                                "telefono":
                                    telefono.strip(),
                                "correo":
                                    correo.strip(),
                                "direccion":
                                    direccion.strip(),
                                "distrito":
                                    distrito.strip(),
                                "ciudad":
                                    ciudad.strip(),
                                "metodo_pago_preferido":
                                    metodo_pago,
                                "observaciones":
                                    observaciones.strip(),
                                "estado":
                                    True
                            }

                            (
                                supabase
                                .table("proveedores")
                                .insert(
                                    nuevo_proveedor
                                )
                                .execute()
                            )

                            st.success(
                                "✅ Proveedor registrado "
                                "correctamente."
                            )

                            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo registrar "
                "el proveedor."
            )

            st.code(str(e))


    # ======================================================
    # TAB 3 - ACTUALIZAR PROVEEDOR
    # ======================================================

    with tab3:

        st.subheader("✏️ Actualizar proveedor")

        try:

            proveedores_activos = (
                supabase
                .table("proveedores")
                .select("*")
                .eq("estado", True)
                .order("razon_social")
                .execute()
                .data
            )

            if not proveedores_activos:

                st.warning(
                    "No hay proveedores activos."
                )

            else:

                opciones = {
                    (
                        f'{p["razon_social"]} - '
                        f'RUC: {p["ruc"] or "Sin RUC"}'
                    ): p
                    for p in proveedores_activos
                }

                seleccionado = st.selectbox(
                    "Selecciona el proveedor",
                    list(opciones.keys()),
                    key="proveedor_actualizar"
                )

                proveedor = opciones[
                    seleccionado
                ]

                metodos = [
                    "Efectivo",
                    "Transferencia",
                    "Crédito",
                    "Yape",
                    "Plin",
                    "Otro"
                ]

                metodo_actual = (
                    proveedor[
                        "metodo_pago_preferido"
                    ]
                    or "Efectivo"
                )

                if metodo_actual not in metodos:

                    metodo_actual = "Otro"

                with st.form(
                    "form_actualizar_proveedor"
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        razon_nueva = st.text_input(
                            "Razón social",
                            value=(
                                proveedor[
                                    "razon_social"
                                ]
                                or ""
                            )
                        )

                        ruc_nuevo = st.text_input(
                            "RUC",
                            value=(
                                proveedor["ruc"]
                                or ""
                            )
                        )

                        contacto_nuevo = (
                            st.text_input(
                                "Nombre del contacto",
                                value=(
                                    proveedor[
                                        "nombre_contacto"
                                    ]
                                    or ""
                                )
                            )
                        )

                        telefono_nuevo = (
                            st.text_input(
                                "Teléfono",
                                value=(
                                    proveedor[
                                        "telefono"
                                    ]
                                    or ""
                                )
                            )
                        )

                        correo_nuevo = st.text_input(
                            "Correo",
                            value=(
                                proveedor[
                                    "correo"
                                ]
                                or ""
                            )
                        )

                    with col2:

                        direccion_nueva = (
                            st.text_input(
                                "Dirección",
                                value=(
                                    proveedor[
                                        "direccion"
                                    ]
                                    or ""
                                )
                            )
                        )

                        distrito_nuevo = (
                            st.text_input(
                                "Distrito",
                                value=(
                                    proveedor[
                                        "distrito"
                                    ]
                                    or ""
                                )
                            )
                        )

                        ciudad_nueva = (
                            st.text_input(
                                "Ciudad",
                                value=(
                                    proveedor[
                                        "ciudad"
                                    ]
                                    or ""
                                )
                            )
                        )

                        metodo_nuevo = (
                            st.selectbox(
                                "Método de pago preferido",
                                metodos,
                                index=metodos.index(
                                    metodo_actual
                                )
                            )
                        )

                    observaciones_nuevas = (
                        st.text_area(
                            "Observaciones",
                            value=(
                                proveedor[
                                    "observaciones"
                                ]
                                or ""
                            )
                        )
                    )

                    actualizar = (
                        st.form_submit_button(
                            "💾 Actualizar proveedor"
                        )
                    )

                    if actualizar:

                        razon_limpia = (
                            razon_nueva.strip()
                        )

                        ruc_limpio = (
                            ruc_nuevo.strip()
                        )

                        if razon_limpia == "":

                            st.error(
                                "❌ La razón social "
                                "no puede quedar vacía."
                            )

                        elif (
                            ruc_limpio != ""
                            and
                            len(ruc_limpio) != 11
                        ):

                            st.error(
                                "❌ El RUC debe tener "
                                "11 dígitos."
                            )

                        elif (
                            ruc_limpio != ""
                            and
                            not ruc_limpio.isdigit()
                        ):

                            st.error(
                                "❌ El RUC debe contener "
                                "solo números."
                            )

                        else:

                            datos = {
                                "razon_social":
                                    razon_limpia,
                                "ruc":
                                    (
                                        ruc_limpio
                                        if ruc_limpio
                                        else None
                                    ),
                                "nombre_contacto":
                                    contacto_nuevo.strip(),
                                "telefono":
                                    telefono_nuevo.strip(),
                                "correo":
                                    correo_nuevo.strip(),
                                "direccion":
                                    direccion_nueva.strip(),
                                "distrito":
                                    distrito_nuevo.strip(),
                                "ciudad":
                                    ciudad_nueva.strip(),
                                "metodo_pago_preferido":
                                    metodo_nuevo,
                                "observaciones":
                                    observaciones_nuevas.strip()
                            }

                            (
                                supabase
                                .table("proveedores")
                                .update(datos)
                                .eq(
                                    "id_proveedor",
                                    proveedor[
                                        "id_proveedor"
                                    ]
                                )
                                .execute()
                            )

                            st.success(
                                "✅ Proveedor actualizado "
                                "correctamente."
                            )

                            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo actualizar "
                "el proveedor."
            )

            st.code(str(e))


    # ======================================================
    # TAB 4 - DESACTIVAR PROVEEDOR
    # ======================================================

    with tab4:

        st.subheader("🚫 Desactivar proveedor")

        st.warning(
            "El proveedor no será eliminado "
            "de la base de datos. "
            "Solo cambiará a estado inactivo."
        )

        try:

            proveedores_activos = (
                supabase
                .table("proveedores")
                .select(
                    "id_proveedor,"
                    "razon_social,"
                    "ruc"
                )
                .eq("estado", True)
                .order("razon_social")
                .execute()
                .data
            )

            if not proveedores_activos:

                st.info(
                    "No existen proveedores activos."
                )

            else:

                opciones = {
                    (
                        f'{p["razon_social"]} - '
                        f'RUC: {p["ruc"] or "Sin RUC"}'
                    ): p["id_proveedor"]
                    for p in proveedores_activos
                }

                proveedor_desactivar = (
                    st.selectbox(
                        "Selecciona el proveedor",
                        list(opciones.keys()),
                        key="proveedor_desactivar"
                    )
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo "
                    "desactivar este proveedor.",
                    key="confirmar_proveedor"
                )

                if st.button(
                    "🚫 Desactivar proveedor"
                ):

                    if not confirmar:

                        st.warning(
                            "⚠️ Debes confirmar "
                            "la operación."
                        )

                    else:

                        (
                            supabase
                            .table("proveedores")
                            .update(
                                {"estado": False}
                            )
                            .eq(
                                "id_proveedor",
                                opciones[
                                    proveedor_desactivar
                                ]
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Proveedor desactivado."
                        )

                        st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo desactivar "
                "el proveedor."
            )

            st.code(str(e))


# ==========================================================
# CLIENTES
# ==========================================================

elif opcion == "Clientes":

    st.title("👥 Gestión de Clientes")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔎 Consultar",
            "➕ Agregar",
            "✏️ Actualizar",
            "🚫 Desactivar"
        ]
    )


    # ======================================================
    # TAB 1 - CONSULTAR CLIENTES
    # ======================================================

    with tab1:

        st.subheader("🔎 Consultar clientes")

        try:

            respuesta = (
                supabase
                .table("clientes")
                .select("*")
                .order("nombres")
                .execute()
            )

            clientes = respuesta.data

            df_clientes = pd.DataFrame(clientes)

            if df_clientes.empty:

                st.warning(
                    "No hay clientes registrados."
                )

            else:

                buscar = st.text_input(
                    "Buscar por nombre, documento o teléfono",
                    key="buscar_cliente"
                )

                if buscar:

                    texto = buscar.lower()

                    filtro = (
                        df_clientes["nombres"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_clientes["numero_documento"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_clientes["telefono"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                    )

                    df_clientes = df_clientes[
                        filtro
                    ]

                columnas = [
                    "id_cliente",
                    "nombres",
                    "tipo_documento",
                    "numero_documento",
                    "telefono",
                    "correo",
                    "direccion",
                    "tipo_cliente",
                    "estado"
                ]

                columnas_existentes = [
                    col
                    for col in columnas
                    if col in df_clientes.columns
                ]

                st.dataframe(
                    df_clientes[
                        columnas_existentes
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                st.info(
                    f"👥 Clientes encontrados: "
                    f"{len(df_clientes)}"
                )

        except Exception as e:

            st.error(
                "❌ No se pudieron consultar "
                "los clientes."
            )

            st.code(str(e))


    # ======================================================
    # TAB 2 - AGREGAR CLIENTE
    # ======================================================

    with tab2:

        st.subheader("➕ Registrar nuevo cliente")

        try:

            with st.form(
                "form_nuevo_cliente"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    nombres = st.text_input(
                        "Nombres o razón social",
                        placeholder="Ejemplo: Juan Pérez"
                    )

                    tipo_documento = st.selectbox(
                        "Tipo de documento",
                        [
                            "DNI",
                            "RUC",
                            "CE",
                            "Sin documento"
                        ]
                    )

                    numero_documento = st.text_input(
                        "Número de documento",
                        placeholder="Ejemplo: 12345678"
                    )

                    telefono = st.text_input(
                        "Teléfono",
                        placeholder="Ejemplo: 987654321"
                    )

                with col2:

                    correo = st.text_input(
                        "Correo",
                        placeholder="Ejemplo: cliente@gmail.com"
                    )

                    direccion = st.text_input(
                        "Dirección",
                        placeholder="Ejemplo: Av. Grau 250"
                    )

                    tipo_cliente = st.selectbox(
                        "Tipo de cliente",
                        [
                            "Público general",
                            "Cliente frecuente",
                            "Mayorista",
                            "Empresa"
                        ]
                    )

                guardar = (
                    st.form_submit_button(
                        "💾 Guardar cliente"
                    )
                )

                if guardar:

                    nombres_limpio = nombres.strip()
                    documento_limpio = (
                        numero_documento.strip()
                    )

                    if nombres_limpio == "":

                        st.error(
                            "❌ Debes ingresar "
                            "el nombre del cliente."
                        )

                    elif (
                        tipo_documento == "DNI"
                        and
                        documento_limpio != ""
                        and
                        len(documento_limpio) != 8
                    ):

                        st.error(
                            "❌ El DNI debe tener "
                            "8 dígitos."
                        )

                    elif (
                        tipo_documento == "RUC"
                        and
                        documento_limpio != ""
                        and
                        len(documento_limpio) != 11
                    ):

                        st.error(
                            "❌ El RUC debe tener "
                            "11 dígitos."
                        )

                    elif (
                        tipo_documento in [
                            "DNI",
                            "RUC"
                        ]
                        and
                        documento_limpio != ""
                        and
                        not documento_limpio.isdigit()
                    ):

                        st.error(
                            "❌ El documento debe contener "
                            "solo números."
                        )

                    else:

                        existe = []

                        if documento_limpio != "":

                            verificar = (
                                supabase
                                .table("clientes")
                                .select(
                                    "id_cliente, numero_documento"
                                )
                                .eq(
                                    "numero_documento",
                                    documento_limpio
                                )
                                .execute()
                            )

                            existe = verificar.data

                        if existe:

                            st.error(
                                f"❌ El documento "
                                f"{documento_limpio} "
                                "ya está registrado."
                            )

                        else:

                            nuevo_cliente = {
                                "nombres":
                                    nombres_limpio,
                                "tipo_documento":
                                    tipo_documento,
                                "numero_documento":
                                    (
                                        documento_limpio
                                        if documento_limpio
                                        else None
                                    ),
                                "telefono":
                                    telefono.strip(),
                                "correo":
                                    correo.strip(),
                                "direccion":
                                    direccion.strip(),
                                "tipo_cliente":
                                    tipo_cliente,
                                "estado":
                                    True
                            }

                            (
                                supabase
                                .table("clientes")
                                .insert(
                                    nuevo_cliente
                                )
                                .execute()
                            )

                            st.success(
                                "✅ Cliente registrado "
                                "correctamente."
                            )

                            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo registrar "
                "el cliente."
            )

            st.code(str(e))


    # ======================================================
    # TAB 3 - ACTUALIZAR CLIENTE
    # ======================================================

    with tab3:

        st.subheader("✏️ Actualizar cliente")

        try:

            clientes_activos = (
                supabase
                .table("clientes")
                .select("*")
                .eq("estado", True)
                .order("nombres")
                .execute()
                .data
            )

            if not clientes_activos:

                st.warning(
                    "No hay clientes activos."
                )

            else:

                opciones = {
                    (
                        f'{c["nombres"]} - '
                        f'{c["numero_documento"] or "Sin documento"}'
                    ): c
                    for c in clientes_activos
                }

                seleccionado = st.selectbox(
                    "Selecciona el cliente",
                    list(opciones.keys()),
                    key="cliente_actualizar"
                )

                cliente = opciones[
                    seleccionado
                ]

                tipos_documento = [
                    "DNI",
                    "RUC",
                    "CE",
                    "Sin documento"
                ]

                tipos_cliente = [
                    "Público general",
                    "Cliente frecuente",
                    "Mayorista",
                    "Empresa"
                ]

                tipo_doc_actual = (
                    cliente["tipo_documento"]
                    or "Sin documento"
                )

                if (
                    tipo_doc_actual
                    not in tipos_documento
                ):

                    tipo_doc_actual = (
                        "Sin documento"
                    )

                tipo_cliente_actual = (
                    cliente["tipo_cliente"]
                    or "Público general"
                )

                if (
                    tipo_cliente_actual
                    not in tipos_cliente
                ):

                    tipo_cliente_actual = (
                        "Público general"
                    )

                with st.form(
                    "form_actualizar_cliente"
                ):

                    col1, col2 = st.columns(2)

                    with col1:

                        nombres_nuevo = (
                            st.text_input(
                                "Nombres o razón social",
                                value=(
                                    cliente[
                                        "nombres"
                                    ]
                                    or ""
                                )
                            )
                        )

                        tipo_documento_nuevo = (
                            st.selectbox(
                                "Tipo de documento",
                                tipos_documento,
                                index=(
                                    tipos_documento
                                    .index(
                                        tipo_doc_actual
                                    )
                                )
                            )
                        )

                        documento_nuevo = (
                            st.text_input(
                                "Número de documento",
                                value=(
                                    cliente[
                                        "numero_documento"
                                    ]
                                    or ""
                                )
                            )
                        )

                        telefono_nuevo = (
                            st.text_input(
                                "Teléfono",
                                value=(
                                    cliente[
                                        "telefono"
                                    ]
                                    or ""
                                )
                            )
                        )

                    with col2:

                        correo_nuevo = (
                            st.text_input(
                                "Correo",
                                value=(
                                    cliente[
                                        "correo"
                                    ]
                                    or ""
                                )
                            )
                        )

                        direccion_nueva = (
                            st.text_input(
                                "Dirección",
                                value=(
                                    cliente[
                                        "direccion"
                                    ]
                                    or ""
                                )
                            )
                        )

                        tipo_cliente_nuevo = (
                            st.selectbox(
                                "Tipo de cliente",
                                tipos_cliente,
                                index=(
                                    tipos_cliente
                                    .index(
                                        tipo_cliente_actual
                                    )
                                )
                            )
                        )

                    actualizar = (
                        st.form_submit_button(
                            "💾 Actualizar cliente"
                        )
                    )

                    if actualizar:

                        nombres_limpio = (
                            nombres_nuevo.strip()
                        )

                        documento_limpio = (
                            documento_nuevo.strip()
                        )

                        if nombres_limpio == "":

                            st.error(
                                "❌ El nombre no puede "
                                "quedar vacío."
                            )

                        elif (
                            tipo_documento_nuevo
                            == "DNI"
                            and
                            documento_limpio != ""
                            and
                            len(documento_limpio)
                            != 8
                        ):

                            st.error(
                                "❌ El DNI debe tener "
                                "8 dígitos."
                            )

                        elif (
                            tipo_documento_nuevo
                            == "RUC"
                            and
                            documento_limpio != ""
                            and
                            len(documento_limpio)
                            != 11
                        ):

                            st.error(
                                "❌ El RUC debe tener "
                                "11 dígitos."
                            )

                        elif (
                            tipo_documento_nuevo
                            in ["DNI", "RUC"]
                            and
                            documento_limpio != ""
                            and
                            not documento_limpio.isdigit()
                        ):

                            st.error(
                                "❌ El documento debe "
                                "contener solo números."
                            )

                        else:

                            datos = {
                                "nombres":
                                    nombres_limpio,
                                "tipo_documento":
                                    tipo_documento_nuevo,
                                "numero_documento":
                                    (
                                        documento_limpio
                                        if documento_limpio
                                        else None
                                    ),
                                "telefono":
                                    telefono_nuevo.strip(),
                                "correo":
                                    correo_nuevo.strip(),
                                "direccion":
                                    direccion_nueva.strip(),
                                "tipo_cliente":
                                    tipo_cliente_nuevo
                            }

                            (
                                supabase
                                .table("clientes")
                                .update(datos)
                                .eq(
                                    "id_cliente",
                                    cliente[
                                        "id_cliente"
                                    ]
                                )
                                .execute()
                            )

                            st.success(
                                "✅ Cliente actualizado "
                                "correctamente."
                            )

                            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo actualizar "
                "el cliente."
            )

            st.code(str(e))


    # ======================================================
    # TAB 4 - DESACTIVAR CLIENTE
    # ======================================================

    with tab4:

        st.subheader("🚫 Desactivar cliente")

        st.warning(
            "El cliente no será eliminado "
            "de la base de datos. "
            "Solo cambiará a estado inactivo."
        )

        try:

            clientes_activos = (
                supabase
                .table("clientes")
                .select(
                    "id_cliente,"
                    "nombres,"
                    "numero_documento"
                )
                .eq("estado", True)
                .order("nombres")
                .execute()
                .data
            )

            if not clientes_activos:

                st.info(
                    "No existen clientes activos."
                )

            else:

                opciones = {
                    (
                        f'{c["nombres"]} - '
                        f'{c["numero_documento"] or "Sin documento"}'
                    ): c["id_cliente"]
                    for c in clientes_activos
                }

                cliente_desactivar = (
                    st.selectbox(
                        "Selecciona el cliente",
                        list(opciones.keys()),
                        key="cliente_desactivar"
                    )
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo "
                    "desactivar este cliente.",
                    key="confirmar_cliente"
                )

                if st.button(
                    "🚫 Desactivar cliente"
                ):

                    if not confirmar:

                        st.warning(
                            "⚠️ Debes confirmar "
                            "la operación."
                        )

                    else:

                        (
                            supabase
                            .table("clientes")
                            .update(
                                {"estado": False}
                            )
                            .eq(
                                "id_cliente",
                                opciones[
                                    cliente_desactivar
                                ]
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Cliente desactivado."
                        )

                        st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo desactivar "
                "el cliente."
            )

            st.code(str(e))



# ==========================================================
# COMPRAS
# ==========================================================

elif opcion == "Compras":

    st.title("🛒 Gestión de Compras")

    tab1, tab2, tab3 = st.tabs(
        [
            "🔎 Consultar compras",
            "➕ Registrar compra",
            "📦 Ver detalle"
        ]
    )


    # ======================================================
    # TAB 1 - CONSULTAR COMPRAS
    # ======================================================

    with tab1:

        st.subheader("🔎 Consultar compras registradas")

        try:

            respuesta = (
                supabase
                .table("compras")
                .select(
                    "*, proveedores(razon_social)"
                )
                .order(
                    "fecha_compra",
                    desc=True
                )
                .execute()
            )

            compras = respuesta.data

            df_compras = pd.DataFrame(
                compras
            )

            if df_compras.empty:

                st.warning(
                    "No hay compras registradas."
                )

            else:

                df_compras["proveedor"] = (
                    df_compras["proveedores"]
                    .apply(
                        lambda x:
                        x.get(
                            "razon_social",
                            ""
                        )
                        if isinstance(x, dict)
                        else ""
                    )
                )

                buscar = st.text_input(
                    "Buscar por código de compra, comprobante o proveedor",
                    key="buscar_compra"
                )

                if buscar:

                    texto = buscar.lower()

                    filtro = (
                        df_compras[
                            "codigo_compra"
                        ]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_compras[
                            "numero_comprobante"
                        ]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_compras[
                            "proveedor"
                        ]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                    )

                    df_compras = (
                        df_compras[
                            filtro
                        ]
                    )

                columnas = [
                    "codigo_compra",
                    "fecha_compra",
                    "proveedor",
                    "tipo_comprobante",
                    "numero_comprobante",
                    "metodo_pago",
                    "subtotal",
                    "igv",
                    "total_compra",
                    "estado"
                ]

                st.dataframe(
                    df_compras[
                        columnas
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                st.info(
                    f"🛒 Compras encontradas: "
                    f"{len(df_compras)}"
                )

        except Exception as e:

            st.error(
                "❌ No se pudieron consultar "
                "las compras."
            )

            st.code(str(e))


    # ======================================================
    # TAB 2 - REGISTRAR COMPRA
    # ======================================================

    with tab2:

        st.subheader(
            "➕ Registrar nueva compra"
        )

        st.info(
            "Al guardar una compra, el stock del producto "
            "aumentará automáticamente."
        )

        try:

            proveedores = (
                supabase
                .table("proveedores")
                .select(
                    "id_proveedor, razon_social, ruc"
                )
                .eq("estado", True)
                .order("razon_social")
                .execute()
                .data
            )

            productos = (
                supabase
                .table("productos")
                .select(
                    "id_producto, codigo_producto, "
                    "nombre_producto, precio_compra, "
                    "stock_actual, estado"
                )
                .eq("estado", True)
                .order("nombre_producto")
                .execute()
                .data
            )

            if not proveedores:

                st.warning(
                    "⚠️ Primero debes registrar "
                    "al menos un proveedor."
                )

            elif not productos:

                st.warning(
                    "⚠️ No existen productos activos."
                )

            else:

                opciones_proveedores = {
                    (
                        f'{p["razon_social"]} - '
                        f'RUC: {p["ruc"] or "Sin RUC"}'
                    ): p["id_proveedor"]
                    for p in proveedores
                }

                opciones_productos = {
                    (
                        f'{p["codigo_producto"]} - '
                        f'{p["nombre_producto"]} '
                        f'(Stock: {p["stock_actual"]})'
                    ): p
                    for p in productos
                }

                st.write(
                    "### Datos generales de la compra"
                )

                col1, col2 = st.columns(2)

                with col1:

                    codigo_compra = (
                        st.text_input(
                            "Código de compra",
                            placeholder=(
                                "Ejemplo: COMP001"
                            )
                        )
                    )

                    proveedor_seleccionado = (
                        st.selectbox(
                            "Proveedor",
                            list(
                                opciones_proveedores
                                .keys()
                            )
                        )
                    )

                    tipo_comprobante = (
                        st.selectbox(
                            "Tipo de comprobante",
                            [
                                "Factura",
                                "Boleta",
                                "Nota de venta",
                                "Sin comprobante"
                            ]
                        )
                    )

                with col2:

                    numero_comprobante = (
                        st.text_input(
                            "Número de comprobante",
                            placeholder=(
                                "Ejemplo: F001-000123"
                            )
                        )
                    )

                    metodo_pago = (
                        st.selectbox(
                            "Método de pago",
                            [
                                "Efectivo",
                                "Transferencia",
                                "Crédito",
                                "Yape",
                                "Plin",
                                "Otro"
                            ]
                        )
                    )

                    observaciones = (
                        st.text_input(
                            "Observaciones",
                            placeholder="Opcional"
                        )
                    )

                st.divider()

                st.write(
                    "### Producto comprado"
                )

                producto_seleccionado = (
                    st.selectbox(
                        "Producto",
                        list(
                            opciones_productos.keys()
                        ),
                        key="producto_compra"
                    )
                )

                producto = (
                    opciones_productos[
                        producto_seleccionado
                    ]
                )

                col3, col4, col5 = (
                    st.columns(3)
                )

                with col3:

                    cantidad = (
                        st.number_input(
                            "Cantidad comprada",
                            min_value=1.0,
                            value=1.0,
                            step=1.0
                        )
                    )

                with col4:

                    precio_unitario = (
                        st.number_input(
                            "Precio unitario de compra",
                            min_value=0.0,
                            value=float(
                                producto[
                                    "precio_compra"
                                ]
                                or 0
                            ),
                            step=0.10,
                            format="%.2f"
                        )
                    )

                with col5:

                    subtotal_producto = (
                        cantidad
                        *
                        precio_unitario
                    )

                    st.metric(
                        "Subtotal del producto",
                        f"S/ {subtotal_producto:,.2f}"
                    )

                st.divider()

                aplicar_igv = st.checkbox(
                    "Aplicar IGV (18%)",
                    value=False
                )

                subtotal_compra = (
                    subtotal_producto
                )

                if aplicar_igv:

                    igv = (
                        subtotal_compra
                        *
                        0.18
                    )

                else:

                    igv = 0

                total_compra = (
                    subtotal_compra
                    +
                    igv
                )

                col6, col7, col8 = (
                    st.columns(3)
                )

                with col6:

                    st.metric(
                        "Subtotal",
                        f"S/ {subtotal_compra:,.2f}"
                    )

                with col7:

                    st.metric(
                        "IGV",
                        f"S/ {igv:,.2f}"
                    )

                with col8:

                    st.metric(
                        "Total compra",
                        f"S/ {total_compra:,.2f}"
                    )

                st.divider()

                guardar_compra = st.button(
                    "💾 Guardar compra",
                    key="guardar_compra"
                )

                if guardar_compra:

                    codigo_limpio = (
                        codigo_compra
                        .strip()
                        .upper()
                    )

                    if codigo_limpio == "":

                        st.error(
                            "❌ Debes ingresar "
                            "el código de compra."
                        )

                    elif precio_unitario <= 0:

                        st.error(
                            "❌ El precio unitario "
                            "debe ser mayor que 0."
                        )

                    else:

                        verificar = (
                            supabase
                            .table("compras")
                            .select(
                                "id_compra"
                            )
                            .eq(
                                "codigo_compra",
                                codigo_limpio
                            )
                            .execute()
                        )

                        if verificar.data:

                            st.error(
                                f"❌ El código "
                                f"{codigo_limpio} "
                                "ya existe."
                            )

                        else:

                            nueva_compra = {
                                "codigo_compra":
                                    codigo_limpio,
                                "id_proveedor":
                                    opciones_proveedores[
                                        proveedor_seleccionado
                                    ],
                                "tipo_comprobante":
                                    tipo_comprobante,
                                "numero_comprobante":
                                    numero_comprobante
                                    .strip(),
                                "metodo_pago":
                                    metodo_pago,
                                "subtotal":
                                    subtotal_compra,
                                "igv":
                                    igv,
                                "total_compra":
                                    total_compra,
                                "estado":
                                    "COMPLETADA",
                                "observaciones":
                                    observaciones
                                    .strip()
                            }

                            respuesta_compra = (
                                supabase
                                .table("compras")
                                .insert(
                                    nueva_compra
                                )
                                .execute()
                            )

                            if (
                                respuesta_compra.data
                            ):

                                id_compra = (
                                    respuesta_compra
                                    .data[0]
                                    ["id_compra"]
                                )

                                detalle = {
                                    "id_compra":
                                        id_compra,
                                    "id_producto":
                                        producto[
                                            "id_producto"
                                        ],
                                    "cantidad":
                                        cantidad,
                                    "precio_unitario":
                                        precio_unitario,
                                    "subtotal":
                                        subtotal_producto
                                }

                                (
                                    supabase
                                    .table(
                                        "detalle_compras"
                                    )
                                    .insert(
                                        detalle
                                    )
                                    .execute()
                                )

                                st.success(
                                    "✅ Compra registrada "
                                    "correctamente."
                                )

                                st.success(
                                    "📦 El stock del producto "
                                    "aumentó automáticamente."
                                )

                                st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo registrar "
                "la compra."
            )

            st.code(str(e))


    # ======================================================
    # TAB 3 - VER DETALLE DE COMPRA
    # ======================================================

    with tab3:

        st.subheader(
            "📦 Detalle de compras"
        )

        try:

            compras = (
                supabase
                .table("compras")
                .select(
                    "id_compra, codigo_compra, "
                    "fecha_compra, total_compra"
                )
                .order(
                    "fecha_compra",
                    desc=True
                )
                .execute()
                .data
            )

            if not compras:

                st.info(
                    "No existen compras registradas."
                )

            else:

                opciones = {
                    (
                        f'{c["codigo_compra"]} - '
                        f'S/ {c["total_compra"]}'
                    ): c
                    for c in compras
                }

                compra_seleccionada = (
                    st.selectbox(
                        "Selecciona una compra",
                        list(opciones.keys()),
                        key="detalle_compra"
                    )
                )

                compra = (
                    opciones[
                        compra_seleccionada
                    ]
                )

                detalle = (
                    supabase
                    .table("detalle_compras")
                    .select(
                        "*, "
                        "productos("
                        "codigo_producto, "
                        "nombre_producto"
                        ")"
                    )
                    .eq(
                        "id_compra",
                        compra[
                            "id_compra"
                        ]
                    )
                    .execute()
                    .data
                )

                if not detalle:

                    st.warning(
                        "Esta compra no tiene "
                        "productos registrados."
                    )

                else:

                    df_detalle = pd.DataFrame(
                        detalle
                    )

                    df_detalle[
                        "codigo_producto"
                    ] = (
                        df_detalle[
                            "productos"
                        ]
                        .apply(
                            lambda x:
                            x.get(
                                "codigo_producto",
                                ""
                            )
                            if isinstance(
                                x,
                                dict
                            )
                            else ""
                        )
                    )

                    df_detalle[
                        "producto"
                    ] = (
                        df_detalle[
                            "productos"
                        ]
                        .apply(
                            lambda x:
                            x.get(
                                "nombre_producto",
                                ""
                            )
                            if isinstance(
                                x,
                                dict
                            )
                            else ""
                        )
                    )

                    columnas = [
                        "codigo_producto",
                        "producto",
                        "cantidad",
                        "precio_unitario",
                        "subtotal",
                        "lote",
                        "fecha_vencimiento"
                    ]

                    columnas_existentes = [
                        col
                        for col in columnas
                        if col in df_detalle.columns
                    ]

                    st.dataframe(
                        df_detalle[
                            columnas_existentes
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    total_detalle = (
                        df_detalle[
                            "subtotal"
                        ]
                        .sum()
                    )

                    st.metric(
                        "💰 Total de productos",
                        f"S/ {total_detalle:,.2f}"
                    )

        except Exception as e:

            st.error(
                "❌ No se pudo consultar "
                "el detalle de la compra."
            )

            st.code(str(e))

# ==========================================================
# VENTAS
# ==========================================================

elif opcion == "Ventas":

    st.title("💵 Gestión de Ventas")

    tab1, tab2, tab3 = st.tabs(
        [
            "🔎 Consultar ventas",
            "➕ Registrar venta",
            "📦 Ver detalle"
        ]
    )


    # ======================================================
    # TAB 1 - CONSULTAR VENTAS
    # ======================================================

    with tab1:

        st.subheader("🔎 Consultar ventas registradas")

        try:

            respuesta = (
                supabase
                .table("ventas")
                .select("*, clientes(nombres)")
                .order("fecha_venta", desc=True)
                .execute()
            )

            ventas = respuesta.data

            df_ventas = pd.DataFrame(ventas)

            if df_ventas.empty:

                st.warning("No hay ventas registradas.")

            else:

                df_ventas["cliente"] = (
                    df_ventas["clientes"]
                    .apply(
                        lambda x:
                        x.get("nombres", "")
                        if isinstance(x, dict)
                        else "Público general"
                    )
                )

                buscar = st.text_input(
                    "Buscar por código, comprobante o cliente",
                    key="buscar_venta"
                )

                if buscar:

                    texto = buscar.lower()

                    filtro = (
                        df_ventas["codigo_venta"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_ventas["numero_comprobante"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                        |
                        df_ventas["cliente"]
                        .fillna("")
                        .str.lower()
                        .str.contains(texto)
                    )

                    df_ventas = df_ventas[filtro]

                columnas = [
                    "codigo_venta",
                    "fecha_venta",
                    "cliente",
                    "tipo_comprobante",
                    "numero_comprobante",
                    "metodo_pago",
                    "subtotal",
                    "descuento",
                    "total_venta",
                    "estado"
                ]

                st.dataframe(
                    df_ventas[columnas],
                    use_container_width=True,
                    hide_index=True
                )

                st.info(
                    f"💵 Ventas encontradas: {len(df_ventas)}"
                )

        except Exception as e:

            st.error(
                "❌ No se pudieron consultar las ventas."
            )

            st.code(str(e))


    # ======================================================
    # TAB 2 - REGISTRAR VENTA CON VARIOS PRODUCTOS
    # ======================================================

    with tab2:

        st.subheader("➕ Registrar nueva venta")

        st.info(
            "Puedes agregar varios productos al carrito "
            "antes de guardar la venta."
        )

        try:

            # --------------------------------------------------
            # CREAR CARRITO EN SESSION STATE
            # --------------------------------------------------

            if "carrito_venta" not in st.session_state:

                st.session_state.carrito_venta = []


            # --------------------------------------------------
            # OBTENER CLIENTES
            # --------------------------------------------------

            clientes = (
                supabase
                .table("clientes")
                .select(
                    "id_cliente, nombres, numero_documento"
                )
                .eq("estado", True)
                .order("nombres")
                .execute()
                .data
            )


            # --------------------------------------------------
            # OBTENER PRODUCTOS
            # --------------------------------------------------

            productos = (
                supabase
                .table("productos")
                .select(
                    "id_producto, codigo_producto, "
                    "nombre_producto, precio_venta, "
                    "stock_actual"
                )
                .eq("estado", True)
                .gt("stock_actual", 0)
                .order("nombre_producto")
                .execute()
                .data
            )


            if not clientes:

                st.warning(
                    "⚠️ Primero debes registrar al menos un cliente."
                )

            elif not productos:

                st.warning(
                    "⚠️ No hay productos con stock disponible."
                )

            else:

                # --------------------------------------------------
                # CLIENTES
                # --------------------------------------------------

                opciones_clientes = {
                    (
                        f'{c["nombres"]} - '
                        f'{c["numero_documento"] or "Sin documento"}'
                    ): c["id_cliente"]
                    for c in clientes
                }


                # --------------------------------------------------
                # PRODUCTOS
                # --------------------------------------------------

                opciones_productos = {
                    (
                        f'{p["codigo_producto"]} - '
                        f'{p["nombre_producto"]} '
                        f'(Stock: {p["stock_actual"]})'
                    ): p
                    for p in productos
                }


                # ==================================================
                # DATOS GENERALES DE LA VENTA
                # ==================================================

                st.write("### 🧾 Datos generales")

                col1, col2 = st.columns(2)

                with col1:

                    codigo_venta = st.text_input(
                        "Código de venta",
                        placeholder="Ejemplo: VENT010"
                    )

                    cliente_seleccionado = st.selectbox(
                        "Cliente",
                        list(opciones_clientes.keys())
                    )

                    tipo_comprobante = st.selectbox(
                        "Tipo de comprobante",
                        [
                            "Boleta",
                            "Factura",
                            "Nota de venta",
                            "Sin comprobante"
                        ]
                    )

                with col2:

                    numero_comprobante = st.text_input(
                        "Número de comprobante",
                        placeholder="Ejemplo: B001-000010"
                    )

                    metodo_pago = st.selectbox(
                        "Método de pago",
                        [
                            "Efectivo",
                            "Yape",
                            "Plin",
                            "Transferencia",
                            "Tarjeta",
                            "Crédito",
                            "Otro"
                        ]
                    )

                    observaciones = st.text_input(
                        "Observaciones",
                        placeholder="Opcional"
                    )


                st.divider()


                # ==================================================
                # AGREGAR PRODUCTOS
                # ==================================================

                st.write("### 🛒 Agregar productos")

                producto_seleccionado = st.selectbox(
                    "Producto",
                    list(opciones_productos.keys()),
                    key="producto_venta_multiple"
                )

                producto = (
                    opciones_productos[
                        producto_seleccionado
                    ]
                )

                stock_disponible = float(
                    producto["stock_actual"]
                )

                col3, col4, col5 = st.columns(3)

                with col3:

                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=1.0,
                        max_value=stock_disponible,
                        value=1.0,
                        step=1.0,
                        key="cantidad_venta_multiple"
                    )

                with col4:

                    precio_unitario = st.number_input(
                        "Precio unitario",
                        min_value=0.0,
                        value=float(
                            producto["precio_venta"] or 0
                        ),
                        step=0.10,
                        format="%.2f",
                        key="precio_venta_multiple"
                    )

                with col5:

                    subtotal_producto = (
                        cantidad * precio_unitario
                    )

                    st.metric(
                        "Subtotal",
                        f"S/ {subtotal_producto:,.2f}"
                    )


                agregar = st.button(
                    "➕ Agregar producto al carrito"
                )


                if agregar:

                    # ----------------------------------------------
                    # VERIFICAR SI YA ESTÁ EN EL CARRITO
                    # ----------------------------------------------

                    producto_existente = None

                    for item in st.session_state.carrito_venta:

                        if (
                            item["id_producto"]
                            ==
                            producto["id_producto"]
                        ):

                            producto_existente = item
                            break


                    if producto_existente:

                        nueva_cantidad = (
                            producto_existente["cantidad"]
                            +
                            cantidad
                        )

                        if (
                            nueva_cantidad
                            >
                            stock_disponible
                        ):

                            st.error(
                                "❌ La cantidad total supera "
                                "el stock disponible."
                            )

                        else:

                            producto_existente[
                                "cantidad"
                            ] = nueva_cantidad

                            producto_existente[
                                "precio_unitario"
                            ] = precio_unitario

                            producto_existente[
                                "subtotal"
                            ] = (
                                nueva_cantidad
                                *
                                precio_unitario
                            )

                            st.success(
                                "✅ Cantidad actualizada "
                                "en el carrito."
                            )

                            st.rerun()

                    else:

                        nuevo_item = {
                            "id_producto":
                                producto["id_producto"],
                            "codigo_producto":
                                producto["codigo_producto"],
                            "producto":
                                producto["nombre_producto"],
                            "cantidad":
                                cantidad,
                            "precio_unitario":
                                precio_unitario,
                            "subtotal":
                                subtotal_producto
                        }

                        st.session_state.carrito_venta.append(
                            nuevo_item
                        )

                        st.success(
                            "✅ Producto agregado al carrito."
                        )

                        st.rerun()


                st.divider()


                # ==================================================
                # MOSTRAR CARRITO
                # ==================================================

                st.write("### 🛍️ Carrito de venta")

                if not st.session_state.carrito_venta:

                    st.info(
                        "Todavía no has agregado productos."
                    )

                else:

                    df_carrito = pd.DataFrame(
                        st.session_state.carrito_venta
                    )

                    st.dataframe(
                        df_carrito[
                            [
                                "codigo_producto",
                                "producto",
                                "cantidad",
                                "precio_unitario",
                                "subtotal"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )


                    # ----------------------------------------------
                    # ELIMINAR PRODUCTO DEL CARRITO
                    # ----------------------------------------------

                    opciones_eliminar = {
                        (
                            f'{item["codigo_producto"]} - '
                            f'{item["producto"]}'
                        ): index
                        for index, item
                        in enumerate(
                            st.session_state.carrito_venta
                        )
                    }

                    col6, col7 = st.columns(2)

                    with col6:

                        producto_eliminar = st.selectbox(
                            "Producto a eliminar",
                            list(opciones_eliminar.keys()),
                            key="eliminar_producto_carrito"
                        )

                    with col7:

                        st.write("")
                        st.write("")

                        if st.button(
                            "🗑️ Eliminar del carrito"
                        ):

                            indice = (
                                opciones_eliminar[
                                    producto_eliminar
                                ]
                            )

                            st.session_state.carrito_venta.pop(
                                indice
                            )

                            st.rerun()


                    st.divider()


                    # ==================================================
                    # TOTALES
                    # ==================================================

                    subtotal_venta = sum(
                        item["subtotal"]
                        for item in
                        st.session_state.carrito_venta
                    )

                    col8, col9 = st.columns(2)

                    with col8:

                        descuento = st.number_input(
                            "Descuento total",
                            min_value=0.0,
                            max_value=float(
                                subtotal_venta
                            ),
                            value=0.0,
                            step=0.50,
                            format="%.2f",
                            key="descuento_venta_multiple"
                        )

                    total_venta = (
                        subtotal_venta
                        -
                        descuento
                    )

                    with col9:

                        st.metric(
                            "💰 Total de venta",
                            f"S/ {total_venta:,.2f}"
                        )


                    st.write(
                        f"Subtotal: "
                        f"**S/ {subtotal_venta:,.2f}**"
                    )

                    st.write(
                        f"Descuento: "
                        f"**S/ {descuento:,.2f}**"
                    )

                    st.write(
                        f"Total: "
                        f"**S/ {total_venta:,.2f}**"
                    )


                    st.divider()


                    # ==================================================
                    # GUARDAR TODA LA VENTA
                    # ==================================================

                    if st.button(
                        "💾 REGISTRAR VENTA COMPLETA",
                        type="primary"
                    ):

                        codigo_limpio = (
                            codigo_venta
                            .strip()
                            .upper()
                        )


                        if codigo_limpio == "":

                            st.error(
                                "❌ Debes ingresar "
                                "el código de venta."
                            )

                        else:

                            # ------------------------------------------
                            # VERIFICAR CÓDIGO DUPLICADO
                            # ------------------------------------------

                            verificar = (
                                supabase
                                .table("ventas")
                                .select("id_venta")
                                .eq(
                                    "codigo_venta",
                                    codigo_limpio
                                )
                                .execute()
                            )

                            if verificar.data:

                                st.error(
                                    f"❌ El código "
                                    f"{codigo_limpio} "
                                    "ya existe."
                                )

                            else:

                                # --------------------------------------
                                # VALIDAR STOCK ANTES DE GUARDAR
                                # --------------------------------------

                                stock_correcto = True

                                for item in (
                                    st.session_state
                                    .carrito_venta
                                ):

                                    producto_actual = (
                                        supabase
                                        .table("productos")
                                        .select(
                                            "stock_actual"
                                        )
                                        .eq(
                                            "id_producto",
                                            item[
                                                "id_producto"
                                            ]
                                        )
                                        .single()
                                        .execute()
                                    )

                                    stock_actual = float(
                                        producto_actual
                                        .data[
                                            "stock_actual"
                                        ]
                                    )

                                    if (
                                        item["cantidad"]
                                        >
                                        stock_actual
                                    ):

                                        st.error(
                                            f"❌ Stock insuficiente "
                                            f"para "
                                            f'{item["producto"]}. '
                                            f"Disponible: "
                                            f"{stock_actual}"
                                        )

                                        stock_correcto = False


                                if stock_correcto:

                                    # ----------------------------------
                                    # INSERTAR CABECERA DE VENTA
                                    # ----------------------------------

                                    nueva_venta = {
                                        "codigo_venta":
                                            codigo_limpio,
                                        "id_cliente":
                                            opciones_clientes[
                                                cliente_seleccionado
                                            ],
                                        "tipo_comprobante":
                                            tipo_comprobante,
                                        "numero_comprobante":
                                            numero_comprobante
                                            .strip(),
                                        "metodo_pago":
                                            metodo_pago,
                                        "subtotal":
                                            subtotal_venta,
                                        "descuento":
                                            descuento,
                                        "total_venta":
                                            total_venta,
                                        "estado":
                                            "COMPLETADA",
                                        "observaciones":
                                            observaciones
                                            .strip()
                                    }


                                    respuesta_venta = (
                                        supabase
                                        .table("ventas")
                                        .insert(
                                            nueva_venta
                                        )
                                        .execute()
                                    )


                                    if respuesta_venta.data:

                                        id_venta = (
                                            respuesta_venta
                                            .data[0]
                                            ["id_venta"]
                                        )


                                        # ------------------------------
                                        # INSERTAR TODOS LOS PRODUCTOS
                                        # ------------------------------

                                        detalles = []

                                        for item in (
                                            st.session_state
                                            .carrito_venta
                                        ):

                                            detalles.append(
                                                {
                                                    "id_venta":
                                                        id_venta,
                                                    "id_producto":
                                                        item[
                                                            "id_producto"
                                                        ],
                                                    "cantidad":
                                                        item[
                                                            "cantidad"
                                                        ],
                                                    "precio_unitario":
                                                        item[
                                                            "precio_unitario"
                                                        ],
                                                    "descuento":
                                                        0,
                                                    "subtotal":
                                                        item[
                                                            "subtotal"
                                                        ]
                                                }
                                            )


                                        (
                                            supabase
                                            .table(
                                                "detalle_ventas"
                                            )
                                            .insert(
                                                detalles
                                            )
                                            .execute()
                                        )


                                        st.success(
                                            "✅ Venta registrada "
                                            "correctamente."
                                        )

                                        st.success(
                                            "📦 Se descontó "
                                            "automáticamente el stock "
                                            "de todos los productos."
                                        )


                                        # ------------------------------
                                        # LIMPIAR CARRITO
                                        # ------------------------------

                                        st.session_state[
                                            "carrito_venta"
                                        ] = []

                                        st.rerun()


        except Exception as e:

            st.error(
                "❌ No se pudo registrar la venta."
            )

            st.code(str(e))


    # ======================================================
    # TAB 3 - VER DETALLE DE VENTA
    # ======================================================

    with tab3:

        st.subheader("📦 Detalle de ventas")

        try:

            ventas = (
                supabase
                .table("ventas")
                .select(
                    "id_venta, codigo_venta, "
                    "fecha_venta, total_venta"
                )
                .order(
                    "fecha_venta",
                    desc=True
                )
                .execute()
                .data
            )

            if not ventas:

                st.info(
                    "No existen ventas registradas."
                )

            else:

                opciones = {
                    (
                        f'{v["codigo_venta"]} - '
                        f'S/ {v["total_venta"]}'
                    ): v
                    for v in ventas
                }

                venta_seleccionada = st.selectbox(
                    "Selecciona una venta",
                    list(opciones.keys()),
                    key="detalle_venta_multiple"
                )

                venta = opciones[
                    venta_seleccionada
                ]

                detalle = (
                    supabase
                    .table("detalle_ventas")
                    .select(
                        "*, "
                        "productos("
                        "codigo_producto, "
                        "nombre_producto"
                        ")"
                    )
                    .eq(
                        "id_venta",
                        venta["id_venta"]
                    )
                    .execute()
                    .data
                )

                if not detalle:

                    st.warning(
                        "Esta venta no tiene productos registrados."
                    )

                else:

                    df_detalle = pd.DataFrame(
                        detalle
                    )

                    df_detalle[
                        "codigo_producto"
                    ] = (
                        df_detalle["productos"]
                        .apply(
                            lambda x:
                            x.get(
                                "codigo_producto",
                                ""
                            )
                            if isinstance(x, dict)
                            else ""
                        )
                    )

                    df_detalle[
                        "producto"
                    ] = (
                        df_detalle["productos"]
                        .apply(
                            lambda x:
                            x.get(
                                "nombre_producto",
                                ""
                            )
                            if isinstance(x, dict)
                            else ""
                        )
                    )

                    columnas = [
                        "codigo_producto",
                        "producto",
                        "cantidad",
                        "precio_unitario",
                        "subtotal"
                    ]

                    st.dataframe(
                        df_detalle[columnas],
                        use_container_width=True,
                        hide_index=True
                    )

                    total_productos = (
                        df_detalle[
                            "cantidad"
                        ].sum()
                    )

                    total_detalle = (
                        df_detalle[
                            "subtotal"
                        ].sum()
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "📦 Unidades vendidas",
                            f"{total_productos:,.0f}"
                        )

                    with col2:

                        st.metric(
                            "💰 Total productos",
                            f"S/ {total_detalle:,.2f}"
                        )

        except Exception as e:

            st.error(
                "❌ No se pudo consultar "
                "el detalle de la venta."
            )

            st.code(str(e))

# ==========================================================
# KARDEX
# ==========================================================


elif opcion == "Kardex":

    st.title("📋 Kardex de Inventario")

    st.write(
        "Consulta las entradas y salidas de mercadería "
        "registradas en el sistema."
    )

    try:

        # ==================================================
        # OBTENER MOVIMIENTOS CON DATOS DEL PRODUCTO
        # ==================================================

        movimientos = (
            supabase
            .table("movimientos_inventario")
            .select(
                "*, "
                "productos("
                "codigo_producto, "
                "nombre_producto"
                ")"
            )
            .order(
                "fecha_movimiento",
                desc=True
            )
            .execute()
            .data
        )

        if not movimientos:

            st.info(
                "📭 Todavía no existen movimientos "
                "de inventario."
            )

        else:

            df_kardex = pd.DataFrame(
                movimientos
            )


            # ==================================================
            # OBTENER CÓDIGO Y NOMBRE DEL PRODUCTO
            # ==================================================

            df_kardex["codigo_producto"] = (
                df_kardex["productos"]
                .apply(
                    lambda x:
                    x.get(
                        "codigo_producto",
                        ""
                    )
                    if isinstance(x, dict)
                    else ""
                )
            )

            df_kardex["producto"] = (
                df_kardex["productos"]
                .apply(
                    lambda x:
                    x.get(
                        "nombre_producto",
                        ""
                    )
                    if isinstance(x, dict)
                    else ""
                )
            )


            # ==================================================
            # CONVERTIR FECHA
            # ==================================================

            df_kardex[
                "fecha_movimiento"
            ] = pd.to_datetime(
                df_kardex[
                    "fecha_movimiento"
                ],
                errors="coerce"
            )


            # ==================================================
            # CREAR COLUMNAS DE ENTRADA Y SALIDA
            # ==================================================

            df_kardex["entrada"] = (
                df_kardex.apply(
                    lambda fila:
                    fila["cantidad"]
                    if fila["tipo_movimiento"]
                    == "ENTRADA"
                    else 0,
                    axis=1
                )
            )

            df_kardex["salida"] = (
                df_kardex.apply(
                    lambda fila:
                    fila["cantidad"]
                    if fila["tipo_movimiento"]
                    == "SALIDA"
                    else 0,
                    axis=1
                )
            )


            # ==================================================
            # FILTROS
            # ==================================================

            st.subheader("🔎 Filtros")

            col1, col2 = st.columns(2)


            # --------------------------------------------------
            # FILTRO POR PRODUCTO
            # --------------------------------------------------

            productos_disponibles = (
                df_kardex[
                    [
                        "codigo_producto",
                        "producto"
                    ]
                ]
                .drop_duplicates()
                .sort_values(
                    "producto"
                )
            )

            opciones_productos = [
                "Todos"
            ]

            for _, fila in (
                productos_disponibles
                .iterrows()
            ):

                opciones_productos.append(
                    f'{fila["codigo_producto"]} - '
                    f'{fila["producto"]}'
                )


            with col1:

                filtro_producto = (
                    st.selectbox(
                        "Producto",
                        opciones_productos,
                        key="filtro_producto_kardex"
                    )
                )


            # --------------------------------------------------
            # FILTRO POR TIPO DE MOVIMIENTO
            # --------------------------------------------------

            with col2:

                filtro_movimiento = (
                    st.selectbox(
                        "Tipo de movimiento",
                        [
                            "Todos",
                            "ENTRADA",
                            "SALIDA",
                            "AJUSTE"
                        ],
                        key="filtro_movimiento_kardex"
                    )
                )


            # ==================================================
            # APLICAR FILTRO DE PRODUCTO
            # ==================================================

            df_filtrado = (
                df_kardex.copy()
            )

            if filtro_producto != "Todos":

                codigo_seleccionado = (
                    filtro_producto
                    .split(" - ")[0]
                )

                df_filtrado = (
                    df_filtrado[
                        df_filtrado[
                            "codigo_producto"
                        ]
                        ==
                        codigo_seleccionado
                    ]
                )


            # ==================================================
            # APLICAR FILTRO DE MOVIMIENTO
            # ==================================================

            if filtro_movimiento != "Todos":

                df_filtrado = (
                    df_filtrado[
                        df_filtrado[
                            "tipo_movimiento"
                        ]
                        ==
                        filtro_movimiento
                    ]
                )


            st.divider()


            # ==================================================
            # INDICADORES DEL KARDEX
            # ==================================================

            total_entradas = (
                df_filtrado[
                    "entrada"
                ].sum()
            )

            total_salidas = (
                df_filtrado[
                    "salida"
                ].sum()
            )

            cantidad_movimientos = (
                len(df_filtrado)
            )


            col3, col4, col5 = (
                st.columns(3)
            )

            with col3:

                st.metric(
                    "📥 Entradas",
                    f"{total_entradas:,.0f}"
                )

            with col4:

                st.metric(
                    "📤 Salidas",
                    f"{total_salidas:,.0f}"
                )

            with col5:

                st.metric(
                    "📋 Movimientos",
                    cantidad_movimientos
                )


            st.divider()


            # ==================================================
            # TABLA KARDEX
            # ==================================================

            st.subheader(
                "📋 Movimientos de inventario"
            )

            if df_filtrado.empty:

                st.warning(
                    "No existen movimientos "
                    "con los filtros seleccionados."
                )

            else:

                df_mostrar = (
                    df_filtrado.copy()
                )

                df_mostrar[
                    "fecha"
                ] = (
                    df_mostrar[
                        "fecha_movimiento"
                    ]
                    .dt.strftime(
                        "%d/%m/%Y %H:%M"
                    )
                )


                columnas = [
                    "fecha",
                    "codigo_producto",
                    "producto",
                    "tipo_movimiento",
                    "entrada",
                    "salida",
                    "stock_anterior",
                    "stock_nuevo",
                    "tipo_documento",
                    "id_documento",
                    "observacion"
                ]


                st.dataframe(
                    df_mostrar[
                        columnas
                    ],
                    use_container_width=True,
                    hide_index=True
                )


            # ==================================================
            # RESUMEN POR PRODUCTO
            # ==================================================

            st.divider()

            st.subheader(
                "📊 Resumen de movimientos por producto"
            )


            resumen = (
                df_kardex
                .groupby(
                    [
                        "codigo_producto",
                        "producto"
                    ],
                    as_index=False
                )
                .agg(
                    Entradas=(
                        "entrada",
                        "sum"
                    ),
                    Salidas=(
                        "salida",
                        "sum"
                    ),
                    Movimientos=(
                        "id_movimiento",
                        "count"
                    )
                )
            )


            st.dataframe(
                resumen,
                use_container_width=True,
                hide_index=True
            )


            # ==================================================
            # EXPLICACIÓN
            # ==================================================

            st.divider()

            st.info(
                "📌 ENTRADA = mercadería que ingresa "
                "por una compra. "
                "SALIDA = mercadería que sale "
                "por una venta."
            )


    except Exception as e:

        st.error(
            "❌ No se pudo cargar el Kardex."
        )

        st.code(str(e))

# ==========================================================
# STOCK BAJO
# ==========================================================

elif opcion == "Stock bajo":

    st.title("⚠️ Control de Stock Bajo")

    st.write(
        "Consulta los productos que necesitan reposición "
        "y los productos que ya se encuentran agotados."
    )

    try:

        productos = (
            supabase
            .table("productos")
            .select(
                "id_producto, codigo_producto, "
                "nombre_producto, stock_actual, "
                "stock_minimo, stock_maximo, "
                "ubicacion, estado"
            )
            .eq("estado", True)
            .order("nombre_producto")
            .execute()
            .data
        )

        if not productos:

            st.info(
                "No existen productos activos registrados."
            )

        else:

            df_stock = pd.DataFrame(productos)

            # ==================================================
            # CLASIFICAR PRODUCTOS
            # ==================================================

            agotados = df_stock[
                df_stock["stock_actual"] == 0
            ].copy()

            stock_bajo = df_stock[
                (
                    df_stock["stock_actual"]
                    <=
                    df_stock["stock_minimo"]
                )
                &
                (
                    df_stock["stock_actual"] > 0
                )
            ].copy()

            stock_normal = df_stock[
                df_stock["stock_actual"]
                >
                df_stock["stock_minimo"]
            ].copy()


            # ==================================================
            # INDICADORES
            # ==================================================

            st.subheader("📊 Resumen de inventario")

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "📦 Productos activos",
                    len(df_stock)
                )

            with col2:

                st.metric(
                    "⚠️ Stock bajo",
                    len(stock_bajo)
                )

            with col3:

                st.metric(
                    "❌ Agotados",
                    len(agotados)
                )

            with col4:

                st.metric(
                    "✅ Stock normal",
                    len(stock_normal)
                )


            st.divider()


            # ==================================================
            # PRODUCTOS AGOTADOS
            # ==================================================

            st.subheader("❌ Productos agotados")

            if agotados.empty:

                st.success(
                    "✅ No existen productos agotados."
                )

            else:

                st.error(
                    f"Hay {len(agotados)} productos agotados."
                )

                agotados["cantidad_reponer"] = (
                    agotados["stock_maximo"]
                    -
                    agotados["stock_actual"]
                )

                st.dataframe(
                    agotados[
                        [
                            "codigo_producto",
                            "nombre_producto",
                            "stock_actual",
                            "stock_minimo",
                            "stock_maximo",
                            "cantidad_reponer",
                            "ubicacion"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )


            st.divider()


            # ==================================================
            # PRODUCTOS CON STOCK BAJO
            # ==================================================

            st.subheader(
                "⚠️ Productos con stock bajo"
            )

            if stock_bajo.empty:

                st.success(
                    "✅ No existen productos "
                    "con stock bajo."
                )

            else:

                st.warning(
                    f"Hay {len(stock_bajo)} productos "
                    "que necesitan reposición."
                )

                stock_bajo["cantidad_reponer"] = (
                    stock_bajo["stock_maximo"]
                    -
                    stock_bajo["stock_actual"]
                )

                stock_bajo["nivel_stock_%"] = (
                    (
                        stock_bajo["stock_actual"]
                        /
                        stock_bajo["stock_maximo"]
                    )
                    *
                    100
                ).round(2)

                st.dataframe(
                    stock_bajo[
                        [
                            "codigo_producto",
                            "nombre_producto",
                            "stock_actual",
                            "stock_minimo",
                            "stock_maximo",
                            "nivel_stock_%",
                            "cantidad_reponer",
                            "ubicacion"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )


            st.divider()


            # ==================================================
            # BUSCAR PRODUCTO
            # ==================================================

            st.subheader(
                "🔎 Consultar nivel de stock de un producto"
            )

            opciones_productos = {
                (
                    f'{p["codigo_producto"]} - '
                    f'{p["nombre_producto"]}'
                ): p
                for p in productos
            }

            producto_seleccionado = st.selectbox(
                "Selecciona un producto",
                list(opciones_productos.keys()),
                key="producto_stock_bajo"
            )

            producto = opciones_productos[
                producto_seleccionado
            ]

            stock_actual = float(
                producto["stock_actual"]
            )

            stock_minimo = float(
                producto["stock_minimo"]
            )

            stock_maximo = float(
                producto["stock_maximo"]
            )


            if stock_maximo > 0:

                nivel_stock = (
                    stock_actual
                    /
                    stock_maximo
                    *
                    100
                )

            else:

                nivel_stock = 0


            col5, col6, col7, col8 = st.columns(4)

            with col5:

                st.metric(
                    "Stock actual",
                    f"{stock_actual:,.0f}"
                )

            with col6:

                st.metric(
                    "Stock mínimo",
                    f"{stock_minimo:,.0f}"
                )

            with col7:

                st.metric(
                    "Stock máximo",
                    f"{stock_maximo:,.0f}"
                )

            with col8:

                st.metric(
                    "Nivel de stock",
                    f"{nivel_stock:.1f}%"
                )


            # ==================================================
            # ESTADO DEL PRODUCTO
            # ==================================================

            if stock_actual == 0:

                st.error(
                    "❌ PRODUCTO AGOTADO. "
                    "Se recomienda realizar una compra."
                )

            elif stock_actual <= stock_minimo:

                cantidad_reponer = (
                    stock_maximo
                    -
                    stock_actual
                )

                st.warning(
                    f"⚠️ STOCK BAJO. "
                    f"Se recomienda reponer aproximadamente "
                    f"{cantidad_reponer:,.0f} unidades."
                )

            else:

                st.success(
                    "✅ El producto tiene un nivel "
                    "de stock adecuado."
                )


            # ==================================================
            # BARRA DE NIVEL DE STOCK
            # ==================================================

            porcentaje_barra = min(
                max(
                    nivel_stock / 100,
                    0
                ),
                1
            )

            st.progress(
                porcentaje_barra
            )


    except Exception as e:

        st.error(
            "❌ No se pudo consultar "
            "el control de stock."
        )

        st.code(str(e))

# ==========================================================
# REPORTES
# ==========================================================

elif opcion == "Reportes":

    st.title("📊 Reportes e Indicadores")

    st.write(
        "Consulta los principales indicadores de compras, "
        "ventas e inventario de la bodega."
    )

    try:

        # ==================================================
        # OBTENER DATOS
        # ==================================================

        productos = (
            supabase
            .table("productos")
            .select("*")
            .execute()
            .data
        )

        compras = (
            supabase
            .table("compras")
            .select("*")
            .order(
                "fecha_compra",
                desc=True
            )
            .execute()
            .data
        )

        ventas = (
            supabase
            .table("ventas")
            .select("*")
            .order(
                "fecha_venta",
                desc=True
            )
            .execute()
            .data
        )

        detalles_ventas = (
            supabase
            .table("detalle_ventas")
            .select(
                "*, "
                "productos("
                "codigo_producto, "
                "nombre_producto, "
                "precio_compra"
                ")"
            )
            .execute()
            .data
        )

        movimientos = (
            supabase
            .table("movimientos_inventario")
            .select("*")
            .execute()
            .data
        )


        # ==================================================
        # CREAR DATAFRAMES
        # ==================================================

        df_productos = pd.DataFrame(
            productos
        )

        df_compras = pd.DataFrame(
            compras
        )

        df_ventas = pd.DataFrame(
            ventas
        )

        df_detalles_ventas = pd.DataFrame(
            detalles_ventas
        )

        df_movimientos = pd.DataFrame(
            movimientos
        )


        # ==================================================
        # TABS
        # ==================================================

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📊 Resumen general",
                "💵 Ventas",
                "🛒 Compras",
                "📦 Inventario"
            ]
        )


        # ======================================================
        # TAB 1 - RESUMEN GENERAL
        # ======================================================

        with tab1:

            st.subheader(
                "📊 Resumen general del negocio"
            )


            # --------------------------------------------------
            # TOTAL DE VENTAS
            # --------------------------------------------------

            total_ventas = 0

            if not df_ventas.empty:

                ventas_completadas = (
                    df_ventas[
                        df_ventas["estado"]
                        ==
                        "COMPLETADA"
                    ]
                )

                if not ventas_completadas.empty:

                    total_ventas = (
                        ventas_completadas[
                            "total_venta"
                        ]
                        .astype(float)
                        .sum()
                    )


            # --------------------------------------------------
            # TOTAL DE COMPRAS
            # --------------------------------------------------

            total_compras = 0

            if not df_compras.empty:

                compras_completadas = (
                    df_compras[
                        df_compras["estado"]
                        ==
                        "COMPLETADA"
                    ]
                )

                if not compras_completadas.empty:

                    total_compras = (
                        compras_completadas[
                            "total_compra"
                        ]
                        .astype(float)
                        .sum()
                    )


            # --------------------------------------------------
            # VALOR ACTUAL DEL INVENTARIO
            # --------------------------------------------------

            valor_inventario = 0

            if not df_productos.empty:

                df_productos[
                    "valor_stock"
                ] = (
                    df_productos[
                        "stock_actual"
                    ].astype(float)
                    *
                    df_productos[
                        "precio_compra"
                    ].astype(float)
                )

                valor_inventario = (
                    df_productos[
                        "valor_stock"
                    ]
                    .sum()
                )


            # --------------------------------------------------
            # CANTIDAD TOTAL DE UNIDADES EN STOCK
            # --------------------------------------------------

            unidades_stock = 0

            if not df_productos.empty:

                unidades_stock = (
                    df_productos[
                        "stock_actual"
                    ]
                    .astype(float)
                    .sum()
                )


            # --------------------------------------------------
            # INDICADORES PRINCIPALES
            # --------------------------------------------------

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            with col1:

                st.metric(
                    "💵 Total vendido",
                    f"S/ {total_ventas:,.2f}"
                )

            with col2:

                st.metric(
                    "🛒 Total comprado",
                    f"S/ {total_compras:,.2f}"
                )

            with col3:

                st.metric(
                    "📦 Valor del inventario",
                    f"S/ {valor_inventario:,.2f}"
                )

            with col4:

                st.metric(
                    "📋 Unidades en stock",
                    f"{unidades_stock:,.0f}"
                )


            st.divider()


            # --------------------------------------------------
            # SEGUNDA FILA DE INDICADORES
            # --------------------------------------------------

            cantidad_ventas = (
                len(df_ventas)
                if not df_ventas.empty
                else 0
            )

            cantidad_compras = (
                len(df_compras)
                if not df_compras.empty
                else 0
            )

            productos_activos = 0
            productos_stock_bajo = 0

            if not df_productos.empty:

                productos_activos = len(
                    df_productos[
                        df_productos["estado"]
                        ==
                        True
                    ]
                )

                productos_stock_bajo = len(
                    df_productos[
                        (
                            df_productos[
                                "stock_actual"
                            ]
                            <=
                            df_productos[
                                "stock_minimo"
                            ]
                        )
                        &
                        (
                            df_productos[
                                "estado"
                            ]
                            ==
                            True
                        )
                    ]
                )


            col5, col6, col7, col8 = (
                st.columns(4)
            )

            with col5:

                st.metric(
                    "🧾 Número de ventas",
                    cantidad_ventas
                )

            with col6:

                st.metric(
                    "📑 Número de compras",
                    cantidad_compras
                )

            with col7:

                st.metric(
                    "📦 Productos activos",
                    productos_activos
                )

            with col8:

                st.metric(
                    "⚠️ Productos con stock bajo",
                    productos_stock_bajo
                )


            st.divider()


            # ==================================================
            # UTILIDAD BRUTA ESTIMADA
            # ==================================================

            st.subheader(
                "💰 Utilidad bruta estimada"
            )

            costo_productos_vendidos = 0

            if not df_detalles_ventas.empty:

                for _, fila in (
                    df_detalles_ventas
                    .iterrows()
                ):

                    datos_producto = (
                        fila["productos"]
                    )

                    if isinstance(
                        datos_producto,
                        dict
                    ):

                        precio_compra = float(
                            datos_producto.get(
                                "precio_compra",
                                0
                            )
                            or 0
                        )

                        cantidad = float(
                            fila["cantidad"]
                        )

                        costo_productos_vendidos += (
                            precio_compra
                            *
                            cantidad
                        )


            utilidad_bruta = (
                total_ventas
                -
                costo_productos_vendidos
            )


            if total_ventas > 0:

                margen_utilidad = (
                    utilidad_bruta
                    /
                    total_ventas
                    *
                    100
                )

            else:

                margen_utilidad = 0


            col9, col10, col11 = (
                st.columns(3)
            )

            with col9:

                st.metric(
                    "💵 Ventas",
                    f"S/ {total_ventas:,.2f}"
                )

            with col10:

                st.metric(
                    "📦 Costo estimado vendido",
                    f"S/ {costo_productos_vendidos:,.2f}"
                )

            with col11:

                st.metric(
                    "📈 Utilidad bruta estimada",
                    f"S/ {utilidad_bruta:,.2f}",
                    f"{margen_utilidad:.1f}%"
                )

            st.caption(
                "La utilidad mostrada es una estimación "
                "calculada con el precio de compra actual "
                "de cada producto."
            )


        # ======================================================
        # TAB 2 - REPORTE DE VENTAS
        # ======================================================

        with tab2:

            st.subheader(
                "💵 Análisis de ventas"
            )

            if df_ventas.empty:

                st.info(
                    "Todavía no existen ventas registradas."
                )

            else:

                # ------------------------------------------------
                # CONVERTIR FECHA
                # ------------------------------------------------

                df_ventas[
                    "fecha_venta"
                ] = pd.to_datetime(
                    df_ventas[
                        "fecha_venta"
                    ],
                    errors="coerce"
                )


                # ------------------------------------------------
                # INDICADORES
                # ------------------------------------------------

                total_ventas_reporte = (
                    df_ventas[
                        "total_venta"
                    ]
                    .astype(float)
                    .sum()
                )

                numero_ventas = len(
                    df_ventas
                )

                if numero_ventas > 0:

                    ticket_promedio = (
                        total_ventas_reporte
                        /
                        numero_ventas
                    )

                else:

                    ticket_promedio = 0


                col1, col2, col3 = (
                    st.columns(3)
                )

                with col1:

                    st.metric(
                        "💰 Ingresos por ventas",
                        f"S/ {total_ventas_reporte:,.2f}"
                    )

                with col2:

                    st.metric(
                        "🧾 Ventas realizadas",
                        numero_ventas
                    )

                with col3:

                    st.metric(
                        "🎫 Venta promedio",
                        f"S/ {ticket_promedio:,.2f}"
                    )


                st.divider()


                # ==================================================
                # PRODUCTOS MÁS VENDIDOS
                # ==================================================

                st.subheader(
                    "🏆 Productos más vendidos"
                )

                if df_detalles_ventas.empty:

                    st.info(
                        "No existen detalles de ventas."
                    )

                else:

                    df_detalles = (
                        df_detalles_ventas.copy()
                    )

                    df_detalles[
                        "producto"
                    ] = (
                        df_detalles[
                            "productos"
                        ]
                        .apply(
                            lambda x:
                            x.get(
                                "nombre_producto",
                                ""
                            )
                            if isinstance(
                                x,
                                dict
                            )
                            else ""
                        )
                    )

                    df_detalles[
                        "codigo_producto"
                    ] = (
                        df_detalles[
                            "productos"
                        ]
                        .apply(
                            lambda x:
                            x.get(
                                "codigo_producto",
                                ""
                            )
                            if isinstance(
                                x,
                                dict
                            )
                            else ""
                        )
                    )

                    df_detalles[
                        "cantidad"
                    ] = (
                        df_detalles[
                            "cantidad"
                        ]
                        .astype(float)
                    )

                    df_detalles[
                        "subtotal"
                    ] = (
                        df_detalles[
                            "subtotal"
                        ]
                        .astype(float)
                    )


                    productos_vendidos = (
                        df_detalles
                        .groupby(
                            [
                                "codigo_producto",
                                "producto"
                            ],
                            as_index=False
                        )
                        .agg(
                            Unidades_vendidas=(
                                "cantidad",
                                "sum"
                            ),
                            Ingresos=(
                                "subtotal",
                                "sum"
                            )
                        )
                        .sort_values(
                            "Unidades_vendidas",
                            ascending=False
                        )
                    )


                    # ------------------------------------------------
                    # TOP 10
                    # ------------------------------------------------

                    top10 = (
                        productos_vendidos
                        .head(10)
                    )


                    st.dataframe(
                        top10,
                        use_container_width=True,
                        hide_index=True
                    )


                    # ------------------------------------------------
                    # GRÁFICO
                    # ------------------------------------------------

                    if not top10.empty:

                        grafico_top = (
                            top10[
                                [
                                    "producto",
                                    "Unidades_vendidas"
                                ]
                            ]
                            .set_index(
                                "producto"
                            )
                        )

                        st.write(
                            "#### 📊 Top 10 por unidades vendidas"
                        )

                        st.bar_chart(
                            grafico_top
                        )


                st.divider()


                # ==================================================
                # MÉTODOS DE PAGO
                # ==================================================

                st.subheader(
                    "💳 Ventas por método de pago"
                )

                resumen_pago = (
                    df_ventas
                    .groupby(
                        "metodo_pago",
                        as_index=False
                    )
                    .agg(
                        Cantidad_ventas=(
                            "id_venta",
                            "count"
                        ),
                        Total_vendido=(
                            "total_venta",
                            "sum"
                        )
                    )
                )

                st.dataframe(
                    resumen_pago,
                    use_container_width=True,
                    hide_index=True
                )


                st.divider()


                # ==================================================
                # HISTORIAL DE VENTAS
                # ==================================================

                st.subheader(
                    "📋 Historial de ventas"
                )

                df_ventas_mostrar = (
                    df_ventas.copy()
                )

                df_ventas_mostrar[
                    "fecha"
                ] = (
                    df_ventas_mostrar[
                        "fecha_venta"
                    ]
                    .dt.strftime(
                        "%d/%m/%Y %H:%M"
                    )
                )


                columnas_ventas = [
                    "codigo_venta",
                    "fecha",
                    "tipo_comprobante",
                    "numero_comprobante",
                    "metodo_pago",
                    "subtotal",
                    "descuento",
                    "total_venta",
                    "estado"
                ]


                st.dataframe(
                    df_ventas_mostrar[
                        columnas_ventas
                    ],
                    use_container_width=True,
                    hide_index=True
                )


        # ======================================================
        # TAB 3 - REPORTE DE COMPRAS
        # ======================================================

        with tab3:

            st.subheader(
                "🛒 Análisis de compras"
            )

            if df_compras.empty:

                st.info(
                    "Todavía no existen compras registradas."
                )

            else:

                df_compras[
                    "fecha_compra"
                ] = pd.to_datetime(
                    df_compras[
                        "fecha_compra"
                    ],
                    errors="coerce"
                )


                total_compras_reporte = (
                    df_compras[
                        "total_compra"
                    ]
                    .astype(float)
                    .sum()
                )

                numero_compras = (
                    len(df_compras)
                )

                if numero_compras > 0:

                    compra_promedio = (
                        total_compras_reporte
                        /
                        numero_compras
                    )

                else:

                    compra_promedio = 0


                col1, col2, col3 = (
                    st.columns(3)
                )

                with col1:

                    st.metric(
                        "💰 Total invertido",
                        f"S/ {total_compras_reporte:,.2f}"
                    )

                with col2:

                    st.metric(
                        "📑 Compras realizadas",
                        numero_compras
                    )

                with col3:

                    st.metric(
                        "🛒 Compra promedio",
                        f"S/ {compra_promedio:,.2f}"
                    )


                st.divider()


                # ==================================================
                # COMPRAS POR MÉTODO DE PAGO
                # ==================================================

                st.subheader(
                    "💳 Compras por método de pago"
                )

                resumen_compras_pago = (
                    df_compras
                    .groupby(
                        "metodo_pago",
                        as_index=False
                    )
                    .agg(
                        Cantidad_compras=(
                            "id_compra",
                            "count"
                        ),
                        Total_comprado=(
                            "total_compra",
                            "sum"
                        )
                    )
                )

                st.dataframe(
                    resumen_compras_pago,
                    use_container_width=True,
                    hide_index=True
                )


                st.divider()


                # ==================================================
                # HISTORIAL DE COMPRAS
                # ==================================================

                st.subheader(
                    "📋 Historial de compras"
                )

                df_compras_mostrar = (
                    df_compras.copy()
                )

                df_compras_mostrar[
                    "fecha"
                ] = (
                    df_compras_mostrar[
                        "fecha_compra"
                    ]
                    .dt.strftime(
                        "%d/%m/%Y %H:%M"
                    )
                )


                columnas_compras = [
                    "codigo_compra",
                    "fecha",
                    "tipo_comprobante",
                    "numero_comprobante",
                    "metodo_pago",
                    "subtotal",
                    "igv",
                    "total_compra",
                    "estado"
                ]


                st.dataframe(
                    df_compras_mostrar[
                        columnas_compras
                    ],
                    use_container_width=True,
                    hide_index=True
                )


        # ======================================================
        # TAB 4 - REPORTE DE INVENTARIO
        # ======================================================

        with tab4:

            st.subheader(
                "📦 Análisis del inventario"
            )

            if df_productos.empty:

                st.info(
                    "No existen productos registrados."
                )

            else:

                df_inventario = (
                    df_productos.copy()
                )

                df_inventario[
                    "stock_actual"
                ] = (
                    df_inventario[
                        "stock_actual"
                    ]
                    .astype(float)
                )

                df_inventario[
                    "stock_minimo"
                ] = (
                    df_inventario[
                        "stock_minimo"
                    ]
                    .astype(float)
                )

                df_inventario[
                    "stock_maximo"
                ] = (
                    df_inventario[
                        "stock_maximo"
                    ]
                    .astype(float)
                )

                df_inventario[
                    "precio_compra"
                ] = (
                    df_inventario[
                        "precio_compra"
                    ]
                    .astype(float)
                )


                # --------------------------------------------------
                # VALOR INVENTARIO
                # --------------------------------------------------

                df_inventario[
                    "valor_inventario"
                ] = (
                    df_inventario[
                        "stock_actual"
                    ]
                    *
                    df_inventario[
                        "precio_compra"
                    ]
                )


                # --------------------------------------------------
                # ESTADO DE STOCK
                # --------------------------------------------------

                def clasificar_stock(fila):

                    if (
                        fila["stock_actual"]
                        ==
                        0
                    ):

                        return "AGOTADO"

                    elif (
                        fila["stock_actual"]
                        <=
                        fila["stock_minimo"]
                    ):

                        return "STOCK BAJO"

                    else:

                        return "NORMAL"


                df_inventario[
                    "estado_stock"
                ] = (
                    df_inventario.apply(
                        clasificar_stock,
                        axis=1
                    )
                )


                # --------------------------------------------------
                # CANTIDAD A REPONER
                # --------------------------------------------------

                df_inventario[
                    "cantidad_reponer"
                ] = (
                    df_inventario[
                        "stock_maximo"
                    ]
                    -
                    df_inventario[
                        "stock_actual"
                    ]
                )

                df_inventario[
                    "cantidad_reponer"
                ] = (
                    df_inventario[
                        "cantidad_reponer"
                    ]
                    .clip(lower=0)
                )


                # --------------------------------------------------
                # INDICADORES
                # --------------------------------------------------

                total_unidades = (
                    df_inventario[
                        "stock_actual"
                    ]
                    .sum()
                )

                valor_total_stock = (
                    df_inventario[
                        "valor_inventario"
                    ]
                    .sum()
                )

                agotados = len(
                    df_inventario[
                        df_inventario[
                            "estado_stock"
                        ]
                        ==
                        "AGOTADO"
                    ]
                )

                bajos = len(
                    df_inventario[
                        df_inventario[
                            "estado_stock"
                        ]
                        ==
                        "STOCK BAJO"
                    ]
                )


                col1, col2, col3, col4 = (
                    st.columns(4)
                )

                with col1:

                    st.metric(
                        "📦 Unidades almacenadas",
                        f"{total_unidades:,.0f}"
                    )

                with col2:

                    st.metric(
                        "💰 Valor del stock",
                        f"S/ {valor_total_stock:,.2f}"
                    )

                with col3:

                    st.metric(
                        "⚠️ Stock bajo",
                        bajos
                    )

                with col4:

                    st.metric(
                        "❌ Agotados",
                        agotados
                    )


                st.divider()


                # ==================================================
                # TABLA DE INVENTARIO
                # ==================================================

                st.subheader(
                    "📋 Situación actual de productos"
                )

                columnas_inventario = [
                    "codigo_producto",
                    "nombre_producto",
                    "stock_actual",
                    "stock_minimo",
                    "stock_maximo",
                    "estado_stock",
                    "cantidad_reponer",
                    "precio_compra",
                    "precio_venta",
                    "valor_inventario",
                    "ubicacion"
                ]


                st.dataframe(
                    df_inventario[
                        columnas_inventario
                    ],
                    use_container_width=True,
                    hide_index=True
                )


                st.divider()


                # ==================================================
                # PRODUCTOS CON MAYOR STOCK
                # ==================================================

                st.subheader(
                    "📊 Productos con mayor cantidad en stock"
                )

                top_stock = (
                    df_inventario[
                        [
                            "nombre_producto",
                            "stock_actual"
                        ]
                    ]
                    .sort_values(
                        "stock_actual",
                        ascending=False
                    )
                    .head(10)
                )


                if not top_stock.empty:

                    st.bar_chart(
                        top_stock.set_index(
                            "nombre_producto"
                        )
                    )


                st.divider()


                # ==================================================
                # PRODUCTOS QUE NECESITAN REPOSICIÓN
                # ==================================================

                st.subheader(
                    "⚠️ Productos que necesitan reposición"
                )

                reposicion = (
                    df_inventario[
                        df_inventario[
                            "estado_stock"
                        ]
                        .isin(
                            [
                                "STOCK BAJO",
                                "AGOTADO"
                            ]
                        )
                    ]
                )


                if reposicion.empty:

                    st.success(
                        "✅ No existen productos "
                        "que necesiten reposición."
                    )

                else:

                    st.dataframe(
                        reposicion[
                            [
                                "codigo_producto",
                                "nombre_producto",
                                "stock_actual",
                                "stock_minimo",
                                "stock_maximo",
                                "estado_stock",
                                "cantidad_reponer"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )


    except Exception as e:

        st.error(
            "❌ No se pudieron generar los reportes."
        )

        st.code(str(e))
