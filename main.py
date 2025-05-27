import dotenv
from pymongo import MongoClient
import os
import time
from datetime import datetime, timedelta
import asyncio
import streamlit as st
from motor.motor_asyncio import AsyncIOMotorClient
from concurrent.futures import ThreadPoolExecutor
import modulo_interfaz
import modulo_clientes
import modulo_facturas
import modulo_crear_cliente

# Carga de variables de entorno
dotenv.load_dotenv()
carpeta_evidencias = os.getenv("EVIDENCIA_CARTAS_FOLDER")
carpeta_mapas = os.getenv("MAPS_FOLDER")

# Config DB
dbUrl = AsyncIOMotorClient("mongodb://localhost", 27017)
db = dbUrl["CORCHOS"]

# Colecciones
vendedores = db["CATALOGO_VENDEDORES"]
clientes = db["CATALOGO_CLIENTES"]
facturas = db["FACTURAS"]
productos_oracle = db["CATALOGO_PRODUCTOS_ORACLE"]
productos_copeo = db["PRODUCTOS_COPEO"]

# Función asincrónica para obtener los datos del empleado
async def get_employee_data(usuario: str, contrasena: str, db):
    vendedores = db["CATALOGO_VENDEDORES"]
    empleado_actual = await vendedores.find_one({"Numero_Empleado": int(usuario)})

    if empleado_actual is None:
        st.error("ERROR: El empleado no existe.")
        return

    if empleado_actual["Contraseña"] != contrasena:
        st.error("ERROR: Contraseña incorrecta")
        return

    st.session_state.empleado_actual = empleado_actual
    st.session_state.logged_in = True
    st.rerun()


# Función asincrónica para obtener los datos de las facturas
async def get_invoice_data(cliente_actual, empleado_actual, db):
    facturas = db["FACTURAS"]
    facturas_actuales = facturas.find({"$and": [{"envio": cliente_actual["Número Sitio"]}, {"fadter": empleado_actual["Numero_Vendedor"]}]})##.limit(5)

    invoice_list = []
    async for element in facturas_actuales:
        invoice_list.append(f'{element["fad_nuf"]} - {element["fadpro"]} - {element["unidad"]} - {element["cantidad"]}')
    return invoice_list

# Función asincrónica para obtener los datos del producto
async def get_product_data(fadpro, db):
    productos_oracle = db["CATALOGO_PRODUCTOS_ORACLE"]
    producto_oracle_actual = await productos_oracle.find_one({"ID_Producto_Oracle": fadpro})

    if producto_oracle_actual is None:
        return "ERROR: El producto no existe."

    return producto_oracle_actual

# Interfaz de login
async def interfaz_login():
    usuario = st.text_input("Introduce tu número de empleado: ", placeholder="Número de empleado")
    contrasena = st.text_input("Introduce tu contraseña: ", placeholder="Contraseña")
    login = st.button("Iniciar sesión")

    if contrasena or login: await get_employee_data(usuario, contrasena, db)

# Interfaz del menú principal
async def menu_principal():
    st.success(f"Bienvenido/a {st.session_state.empleado_actual['EMPLEADO']}")
    st.session_state.horizontal = True
    
    await moduloInterfaz.generar_seccion()

if __name__ == "__main__":
    moduloClientes = modulo_clientes.moduloClientes(clientes, facturas, productos_oracle, productos_copeo, carpeta_evidencias, carpeta_mapas)
    moduloFacturas = modulo_facturas.moduloFacturas(facturas, productos_oracle)
    moduloCrearCliente = modulo_crear_cliente.moduloCrearCliente(clientes, facturas, productos_oracle)
    moduloInterfaz = modulo_interfaz.moduloInterfaz(vendedores, clientes, facturas, productos_oracle, moduloClientes, moduloFacturas, moduloCrearCliente)


    st.set_page_config(
        page_title="CANJE DE CORCHOS",
        page_icon="🍾",
        #page_icon="🍷",
        layout="wide"
    )

    col1, col2 , col3 = st.columns([20, 2, 4])  # Ajusta proporción si quieres más grande la imagen

    with col1:
        st.markdown("<h1 style='margin-top: .5px;'>Bienvenido/a a la App de Canje de Corchos </h1>", unsafe_allow_html=True)
    with col2:
        st.image("COPA_CORCHOS.png", width = 600)
    
    ##st.title("Bienvenido a la app de Canje de Corchos,🍷")
    ##st.image("COPA_CORCHOS.png", width=50)

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.empleado_actual = None
        st.session_state.cliente_guardado = {}
        st.session_state.cliente_data_editada = {}
        st.session_state.tipo_cliente = None
        st.session_state.botella_copeo = None
 
    # Aquí le decimos que si ya está logueado, muestre el menú
    if st.session_state.logged_in == True:
        asyncio.run(menu_principal())
    else:
        asyncio.run(interfaz_login())