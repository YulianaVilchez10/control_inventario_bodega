import streamlit as st
import requests
import pandas as pd
from datetime import date

# ------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------------------------------

st.set_page_config(
    page_title="Sistema de Laboratorio",
    page_icon="🧪",
    layout="wide"
)

# ------------------------------------------------------
# CONEXIÓN CON SUPABASE
# ------------------------------------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

TABLA = "BASE_DE_DATOS_LABORATORIO"

URL_TABLA = f"{SUPABASE_URL}/{TABLA}"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json"
}

# ------------------------------------------------------
# OPCIONES
# ------------------------------------------------------

MARCAS = [
    "Lenovo",
    "HP",
    "Dell",
    "Acer",
    "ASUS",
    "SAMSUNG",
    "KUKA",
    "EPSON",
    "Yaskawa"
]

ESTADOS = [
    "OPERATIVO",
    "NO OPERATIVO"
]

# ------------------------------------------------------
# FUNCIONES CRUD
# ------------------------------------------------------

# READ
def obtener_equipos():

    parametros = {
        "select": "*",
        "order": "id.asc"
    }

    respuesta = requests.get(
        URL_TABLA,
        headers=HEADERS,
        params=parametros
    )

    respuesta.raise_for_status()

    return respuesta.json()


# CREATE
def agregar_equipo(
    equipo,
    codigo,
    marca,
    estado,
    fecha_adquisicion,
    descripcion
):

    datos = {
        "EQUIPO": equipo,
        "CODIGO": codigo,
        "MARCA": marca,
        "ESTADO": estado,
        "FECHA_ADQUISICIÓN": fecha_adquisicion.isoformat(),
        "DESCRIPCIÓN": descripcion
    }

    headers_insert = HEADERS.copy()

    headers_insert["Prefer"] = "return=representation"

    respuesta = requests.post(
        URL_TABLA,
        headers=headers_insert,
        json=datos
    )

    respuesta.raise_for_status()

    return respuesta.json()


# UPDATE
def actualizar_equipo(
    id_equipo,
    equipo,
    codigo,
    marca,
    estado,
    fecha_adquisicion,
    descripcion
):

    datos = {
        "EQUIPO": equipo,
        "CODIGO": codigo,
        "MARCA": marca,
        "ESTADO": estado,
        "FECHA_ADQUISICIÓN": fecha_adquisicion.isoformat(),
        "DESCRIPCIÓN": descripcion
    }

    parametros = {
        "id": f"eq.{id_equipo}"
    }

    headers_update = HEADERS.copy()

    headers_update["Prefer"] = "return=representation"

    respuesta = requests.patch(
        URL_TABLA,
        headers=headers_update,
        params=parametros,
        json=datos
    )

    respuesta.raise_for_status()

    return respuesta.json()


# DELETE
def eliminar_equipo(id_equipo):

    parametros = {
        "id": f"eq.{id_equipo}"
    }

    headers_delete = HEADERS.copy()

    headers_delete["Prefer"] = "return=representation"

    respuesta = requests.delete(
        URL_TABLA,
        headers=headers_delete,
        params=parametros
    )

    respuesta.raise_for_status()

    return respuesta.json()


# BUSCAR
def buscar_codigo(codigo):

    parametros = {
        "select": "*",
        "CODIGO": f"eq.{codigo}"
    }

    respuesta = requests.get(
        URL_TABLA,
        headers=HEADERS,
        params=parametros
    )

    respuesta.raise_for_status()

    return respuesta.json()


# ------------------------------------------------------
# TÍTULO
# ------------------------------------------------------

st.title("🧪 Sistema de Control de Equipos de Laboratorio")

st.write(
    "Aplicación desarrollada con Python, Streamlit y Supabase."
)

# ------------------------------------------------------
# MENÚ LATERAL
# ------------------------------------------------------

menu = st.sidebar.selectbox(
    "Seleccione una opción",
    [
        "Inicio",
        "Ver equipos",
        "Agregar equipo",
        "Actualizar equipo",
        "Eliminar equipo",
        "Buscar equipo"
    ]
)

# ------------------------------------------------------
# INICIO
# ------------------------------------------------------

if menu == "Inicio":

    st.header("Sistema CRUD de Laboratorio")

    st.write(
        """
        Este sistema permite administrar los equipos del laboratorio.

        Operaciones disponibles:

        - Consultar equipos
        - Agregar equipos
        - Actualizar equipos
        - Eliminar equipos
        - Buscar equipos
        """
    )

    try:

        equipos = obtener_equipos()

        if equipos:

            df = pd.DataFrame(equipos)

            total = len(df)

            operativos = len(
                df[df["ESTADO"] == "OPERATIVO"]
            )

            no_operativos = len(
                df[df["ESTADO"] == "NO OPERATIVO"]
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total de equipos",
                total
            )

            col2.metric(
                "Equipos operativos",
                operativos
            )

            col3.metric(
                "Equipos no operativos",
                no_operativos
            )

    except Exception as error:

        st.error(
            f"Error de conexión: {error}"
        )


# ------------------------------------------------------
# VER EQUIPOS
# ------------------------------------------------------

elif menu == "Ver equipos":

    st.header("📋 Equipos registrados")

    try:

        equipos = obtener_equipos()

        if equipos:

            df = pd.DataFrame(equipos)

            columnas = [
                "id",
                "EQUIPO",
                "CODIGO",
                "MARCA",
                "ESTADO",
                "FECHA_ADQUISICIÓN",
                "DESCRIPCIÓN"
            ]

            st.dataframe(
                df[columnas],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No existen equipos registrados."
            )

    except Exception as error:

        st.error(
            f"Error: {error}"
        )


# ------------------------------------------------------
# AGREGAR EQUIPO
# ------------------------------------------------------

elif menu == "Agregar equipo":

    st.header("➕ Agregar nuevo equipo")

    with st.form("formulario_agregar"):

        equipo = st.text_input(
            "Nombre del equipo"
        )

        codigo = st.number_input(
            "Código",
            min_value=1,
            step=1
        )

        marca = st.selectbox(
            "Marca",
            MARCAS
        )

        estado = st.selectbox(
            "Estado",
            ESTADOS
        )

        fecha_adquisicion = st.date_input(
            "Fecha de adquisición",
            value=date.today()
        )

        descripcion = st.text_area(
            "Descripción"
        )

        boton_agregar = st.form_submit_button(
            "Guardar equipo"
        )

    if boton_agregar:

        if equipo == "":

            st.warning(
                "Debe ingresar el nombre del equipo."
            )

        else:

            try:

                agregar_equipo(
                    equipo,
                    int(codigo),
                    marca,
                    estado,
                    fecha_adquisicion,
                    descripcion
                )

                st.success(
                    "Equipo agregado correctamente."
                )

            except Exception as error:

                st.error(
                    f"Error al agregar: {error}"
                )


# ------------------------------------------------------
# ACTUALIZAR EQUIPO
# ------------------------------------------------------

elif menu == "Actualizar equipo":

    st.header("✏️ Actualizar equipo")

    try:

        equipos = obtener_equipos()

        if equipos:

            opciones = {}

            for equipo in equipos:

                texto = (
                    f'{equipo["id"]} - '
                    f'{equipo["EQUIPO"]} - '
                    f'Código {equipo["CODIGO"]}'
                )

                opciones[texto] = equipo

            seleccion = st.selectbox(
                "Seleccione el equipo",
                opciones.keys()
            )

            equipo_actual = opciones[seleccion]

            marca_actual = equipo_actual["MARCA"]

            if marca_actual in MARCAS:

                indice_marca = MARCAS.index(
                    marca_actual
                )

            else:

                indice_marca = 0

            estado_actual = equipo_actual["ESTADO"]

            if estado_actual in ESTADOS:

                indice_estado = ESTADOS.index(
                    estado_actual
                )

            else:

                indice_estado = 0

            fecha_actual = pd.to_datetime(
                equipo_actual["FECHA_ADQUISICIÓN"]
            ).date()

            with st.form(
                "formulario_actualizar"
            ):

                equipo = st.text_input(
                    "Equipo",
                    value=equipo_actual["EQUIPO"]
                )

                codigo = st.number_input(
                    "Código",
                    min_value=1,
                    step=1,
                    value=int(
                        float(
                            equipo_actual["CODIGO"]
                        )
                    )
                )

                marca = st.selectbox(
                    "Marca",
                    MARCAS,
                    index=indice_marca
                )

                estado = st.selectbox(
                    "Estado",
                    ESTADOS,
                    index=indice_estado
                )

                fecha_adquisicion = st.date_input(
                    "Fecha de adquisición",
                    value=fecha_actual
                )

                descripcion = st.text_area(
                    "Descripción",
                    value=equipo_actual["DESCRIPCIÓN"]
                    if equipo_actual["DESCRIPCIÓN"]
                    else ""
                )

                boton_actualizar = (
                    st.form_submit_button(
                        "Actualizar equipo"
                    )
                )

            if boton_actualizar:

                actualizar_equipo(
                    equipo_actual["id"],
                    equipo,
                    int(codigo),
                    marca,
                    estado,
                    fecha_adquisicion,
                    descripcion
                )

                st.success(
                    "Equipo actualizado correctamente."
                )

        else:

            st.info(
                "No existen equipos registrados."
            )

    except Exception as error:

        st.error(
            f"Error: {error}"
        )


# ------------------------------------------------------
# ELIMINAR EQUIPO
# ------------------------------------------------------

elif menu == "Eliminar equipo":

    st.header("🗑️ Eliminar equipo")

    try:

        equipos = obtener_equipos()

        if equipos:

            opciones = {}

            for equipo in equipos:

                texto = (
                    f'{equipo["id"]} - '
                    f'{equipo["EQUIPO"]} - '
                    f'Código {equipo["CODIGO"]}'
                )

                opciones[texto] = equipo

            seleccion = st.selectbox(
                "Seleccione el equipo",
                opciones.keys()
            )

            equipo_actual = opciones[seleccion]

            st.warning(
                f'Va a eliminar el equipo: '
                f'{equipo_actual["EQUIPO"]}'
            )

            confirmar = st.checkbox(
                "Confirmo que deseo eliminarlo"
            )

            if st.button(
                "Eliminar definitivamente"
            ):

                if confirmar:

                    eliminar_equipo(
                        equipo_actual["id"]
                    )

                    st.success(
                        "Equipo eliminado correctamente."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Debe confirmar la eliminación."
                    )

        else:

            st.info(
                "No existen equipos registrados."
            )

    except Exception as error:

        st.error(
            f"Error: {error}"
        )


# ------------------------------------------------------
# BUSCAR EQUIPO
# ------------------------------------------------------

elif menu == "Buscar equipo":

    st.header("🔎 Buscar equipo")

    codigo = st.number_input(
        "Ingrese el código",
        min_value=1,
        step=1
    )

    if st.button("Buscar"):

        try:

            resultado = buscar_codigo(
                int(codigo)
            )

            if resultado:

                df = pd.DataFrame(
                    resultado
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    "No se encontró el equipo."
                )

        except Exception as error:

            st.error(
                f"Error: {error}"
            )
