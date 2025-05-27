import datetime
import streamlit as st
import modulo_fotos
import modulo_mapa
import modulo_pdf
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from concurrent.futures import ThreadPoolExecutor

class moduloCrearCliente():
    def __init__(self, clientes, facturas, productos_oracle):
        self.clientes = clientes
        self.facturas = facturas
        self.productos_oracle = productos_oracle

    # Interfaz que muestra la información del cliente seleccionado
    async def mostrar_cliente(self):
        st.divider()
        st.write("### Crear un cliente nuevo:")
        # Agregar estilo de CSS para las 3 columnas 
        st.markdown(
            """
            <style>
                .block-container {
                    padding: 1rem;
                    max-width: 100% !important;
                }
                .stColumns {
                    display: flex;
                    justify-content: space-between;
                    width: 100%;
                }
                .stColumns > div {
                    flex: 1;
                    padding: 0 10px;
                }
            </style>
            """,
            unsafe_allow_html=True                          
        )
        ## ESTILO PARA LOS CAMPOS DE SOLO LECTURA

        st.markdown("""
            <style>
                /* Estilo para campos solo lectura */
                .readonly-field {
                    background-color: #e8f4f8;  /* Color de fondo suave (azul claro) */
                    border: 1px solid #3b82f6;  /* Borde azul más fuerte */
                    border-radius: 5px;
                    color: #1a1a5f;  /* Gris oscuro que resalta más */
                    font-weight: bold;  /* Hacer que el texto sea más grueso (negrita) */
                }
                .readonly-field:focus {
                    border-color: #1e40af;  /* Cambia el borde cuando se enfoca */
                }

                /* Estilo para campos editables */
                .editable-field {
                    background-color: #f7f7f7;  /* Fondo más claro para los campos editables */
                    border: 1px solid #4CAF50;  /* Borde verde para resaltar */
                    border-radius: 5px;
                }
                .editable-field:focus {
                    border-color: #8BC34A;  /* Borde verde más destacado cuando se enfoque */
                }
            </style>
        """, unsafe_allow_html=True)

        with st.container():
            c1, c2 = st.columns(2, gap="large")
            
            with c1:
                numero_sitio = st.text_input("Número Sitio", placeholder="Número Sitio")
                num_vendedor = st.text_input("Num. Vendedor", value=st.session_state.empleado_actual["Numero_Vendedor"], disabled=True)
                desc_cuenta = st.text_input("Razón Social", placeholder="Razón Social")
                direc1 = st.text_input("C.P. - Municipio - Estado", placeholder="C.P. - Municipio - Estado")
                email = st.text_input("E-mail", placeholder="E-mail")
                mesas = st.text_input("Num. de Mesas", placeholder="Num. de Mesas")
                dueno = st.text_input("Nombre del Dueño", placeholder="Nombre del Dueño")
                capitan = st.text_input("Nombre del Capitán", placeholder="Nombre del Capitán")
                compras = st.text_input("Compras", placeholder="Compras")
                sommelier = st.text_input("Nombre del Sommelier", placeholder="Nombre del Sommelier")
                tipo_comida = st.text_input("Tipo de Comida", placeholder="Tipo de Comida")
                
            with c2:
                tipo_cliente = st.text_input("Tipo de Cliente", value="Indirecto", disabled=True)
                nombre_sitio = st.text_input("Nombre Comercial", placeholder="Nombre Comercial")
                direc = st.text_input("Calle - Número - Colonia", placeholder="Calle - Número - Colonia")
                telefono = st.text_input("Teléfono", placeholder="Teléfono")
                rfc = st.text_input("R.F.C", placeholder="R.F.C")
                aforo = st.text_input("Capacidad de Aforo", placeholder="Capacidad de Aforo")
                may_o_prov = st.text_input("Mayoristas o Proveedores más usuales de vinos y licores", placeholder="Mayoristas o Proveedores más usuales de vinos y licores")
                gerente = st.text_input("Nombre del Gerente", placeholder="Nombre del Gerente")
                almacen = st.text_input("Almacén", placeholder="Almacén")
                categoria = st.text_input("Categoría", placeholder="Categoría")

            
        if st.button("Guardar cambios"):
            if not numero_sitio or not num_vendedor or not desc_cuenta or not nombre_sitio or not direc or not rfc:
                st.error("Debe llenar por lo menos el número de sitio, número de vendedor, descripción de cuenta, R.F.C, nombre de sitio y dirección.")
                return

            actualizacion: str = await self.crear_cliente(numero_sitio, {
                    "Número Sitio": numero_sitio,
                    "Clave_de_cliente": f"{numero_sitio}-{num_vendedor}",
                    "Tipo_de_cliente": "Indirecto",
                    "Numero vendedor": int(num_vendedor),
                    "Nombre Sitio"   : nombre_sitio,
                    "Descripción Cuenta": desc_cuenta,
                    "DIREC"          : direc,
                    "DIREC1"         : direc1,
                    "TELÉFONO"       : telefono,
                    "EMAIL"          : email,
                    "RFC"            : rfc,
                    "AFORO"          : aforo,
                    "MESAS"          : mesas,
                    "Mayorista_o_Proveedor": may_o_prov,
                    "DUEÑO"          : dueno,
                    "GERENTE"        : gerente,
                    "CAPITÁN"        : capitan,
                    "COMPRAS"        : compras,
                    "ALMACÉN"        : almacen,
                    "SOMMELIER"      : sommelier,
                    "CATEGORÍA"      : categoria,
                    "Tipo_de_Comida" : tipo_comida,
                    "Fecha_Modificación": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })
        
            if actualizacion == "Success":
                st.success("Cliente creado exitosamente.")
            else:
                st.error(f"ERROR: {actualizacion}")

        st.divider()

        # st.write("### Seleccione el tipo de promoción:")

        # espacio_izq, c1, c2, espacio_der = st.columns([3, 1, 1, 3])
        # if c1.button("Botella"):
        #     vinos_encartados = await self.obtener_vinos_encartados(numero_sitio)
        #     await self.listar_vinos_encartados(vinos_encartados)
        # if c2.button("Copa"):
        #     pass


    # Lógica para el guardado de información
    async def crear_cliente(self, filtro: str, nuevo_documento: dict) -> str:
        if await self.clientes.find_one({"Número Sitio": filtro}) is not None:
            return "El cliente ya existe."
        try:
            self.clientes.insert_one(nuevo_documento)
            st.session_state.cliente_guardado[filtro] = nuevo_documento
        except Exception as e:
            return str(e)
        return "Success"

    async def obtener_vinos_encartados(self, numero_sitio: str) -> list:
        productos_listados: set = set()
        registros: list = []

        facturas_actuales = self.facturas.find({"envio": str(numero_sitio)})

        async for element in facturas_actuales:
            productos_listados.add(element["fadpro"])
        
        for element in productos_listados:
            producto_actual = await self.productos_oracle.find_one({"ID_Producto_Oracle": element})
            if producto_actual is None: continue
            registros.append({
                "Sublínea": producto_actual["Sublínea"],
                "Producto": producto_actual["Producto"]
            })

        return registros


    async def listar_vinos_encartados(self, registros: list):
        if len(registros) == 0:
            st.error("No hay vinos encartados.")
            return

        sublineas: dict = {}

        for element in registros:
            if element["Sublínea"] not in sublineas:
                sublineas[element["Sublínea"]] = ""
            
            sublineas[element["Sublínea"]] = element["Producto"] if sublineas[element["Sublínea"]] == "" else f"{sublineas[element['Sublínea']]}, {element['Producto']}"
        st.write("### Vinos Encartados:")

        for key, value in sublineas.items():
            with st.container():
                c1, c2 = st.columns([0.5, 1], gap="small")
                c1.write(key)
                c2.text_input(key, value, disabled=True, label_visibility="collapsed")