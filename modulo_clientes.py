import datetime
import streamlit as st
import modulo_fotos
import modulo_mapa
import modulo_pdf
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from concurrent.futures import ThreadPoolExecutor

class moduloClientes():
    def __init__(self, clientes, facturas, productos_oracle, productos_copeo, carpeta_evidencias, carpeta_mapas):
        self.clientes = clientes
        self.facturas = facturas
        self.productos_oracle = productos_oracle
        self.productos_copeo = productos_copeo
        self.carpeta_evidencias = carpeta_evidencias
        self.carpeta_mapas = carpeta_mapas

    # Función para obtener los clientes
    async def get_client_data(self, empleado_actual):
        cursor = self.clientes.find({"Numero vendedor": empleado_actual["Numero_Vendedor"]})##.limit(5)

        client_list = []

        async for element in cursor:
            try:
                client_list.append(f'{element["Número Sitio"]} - {element["Nombre Sitio"]} - {element["DIREC"]}')
                
            except KeyError:
                pass
        return client_list

    # Función asincrónica para obtener los datos del cliente
    async def get_full_client(self, numero_sitio):
        orden = ["Clave_de_cliente", "Tipo_de_cliente", "Numero vendedor", "Nombre Sitio",
        "Descripción Cuenta", "Razón Social", "DIREC", "DIREC1","TELÉFONO",
        "EMAIL", "RFC", "AFORO", "MESAS", "Mayorista_o_Proveedor", "DUEÑO", "GERENTE", "CAPITÁN", "COMPRAS",
        "ALMACÉN", "SOMMELIER", "CATEGORÍA", "Tipo_de_Comida"]
        cliente_actual = await self.clientes.find_one({"Número Sitio": numero_sitio})

        if cliente_actual is None:
            return None
        cliente_actual_ordenado = {clave: cliente_actual[clave] for clave in orden if clave in cliente_actual}
        return cliente_actual_ordenado

    # Interfaz que lista los clientes en el select box
    async def listar_clientes(self):
        clientes = await self.get_client_data(st.session_state.empleado_actual)
        if not clientes or len(clientes) == 0:
            st.error("No se encontraron clientes.")
            return

        cliente_seleccionado = st.selectbox(
            "Selecciona un cliente", 
            ["Selecciona un cliente..."] + clientes,  # Opción inicial vacía
            index=0,
            key="cliente_seleccionado"
        )

        if cliente_seleccionado == "Selecciona un cliente...": return

        numero_sitio_cliente = cliente_seleccionado.split(" - ")[0]

        if not st.session_state.cliente_guardado or numero_sitio_cliente not in st.session_state.cliente_guardado:
            cliente_actual = await self.get_full_client(numero_sitio_cliente)
            if cliente_actual is not None: st.session_state.cliente_guardado[numero_sitio_cliente] = cliente_actual.copy()

        if numero_sitio_cliente not in st.session_state.cliente_guardado:
            st.error("Error al obtener el cliente.")
            return
            
        return numero_sitio_cliente

    # Interfaz que muestra la información del cliente seleccionado
    async def mostrar_cliente(self, numero_sitio: str, cliente_actual: dict):
        st.divider()
        st.write("### Datos completos del cliente:")
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
                clave_cliente = st.text_input("No. Carnet", cliente_actual["Clave_de_cliente"], disabled=True)
                num_vendedor = st.text_input("Num. Vendedor", cliente_actual["Numero vendedor"], disabled=True)
                desc_cuenta = st.text_input("Razón Social", cliente_actual["Descripción Cuenta"], disabled=True)
                direc1 = st.text_input("C.P. - Municipio - Estado", cliente_actual["DIREC1"], disabled=True)
                email = st.text_input("E-mail", cliente_actual["EMAIL"])
                mesas = st.text_input("Num. de Mesas", cliente_actual["MESAS"])
                dueno = st.text_input("Nombre del Dueño", cliente_actual["DUEÑO"])
                capitan = st.text_input("Nombre del Capitán", cliente_actual["CAPITÁN"])
                compras = st.text_input("Compras", cliente_actual["COMPRAS"])
                sommelier = st.text_input("Nombre del Sommelier", cliente_actual["SOMMELIER"])
                tipo_comida = st.text_input("Tipo de Comida", cliente_actual["Tipo_de_Comida"])
            
            with c2:
                tipo_cliente = st.text_input("Tipo de Cliente", cliente_actual["Tipo_de_cliente"], disabled=True)
                nombre_sitio = st.text_input("Nombre Comercial", cliente_actual["Nombre Sitio"], disabled=True)
                direc = st.text_input("Calle - Número - Colonia", cliente_actual["DIREC"], disabled=True)
                telefono = st.text_input("Teléfono", cliente_actual["TELÉFONO"])
                rfc = st.text_input("R.F.C", cliente_actual["RFC"], disabled=True)
                aforo = st.text_input("Capacidad de Aforo", cliente_actual["AFORO"])
                may_o_prov = st.text_input("Mayoristas o Proveedores más usuales de vinos y licores")
                gerente = st.text_input("Nombre del Gerente", cliente_actual["GERENTE"])
                almacen = st.text_input("Almacén", cliente_actual["ALMACÉN"])
                # El campo "CATEGORÍA" no existe aún en MongoDB.
                categoria = st.text_input("Categoría", cliente_actual["CATEGORÍA"])
            
        if st.button("Guardar cambios"):
            actualizacion: str = await self.actualizar_cliente(numero_sitio, {
                    "Clave_de_cliente": clave_cliente,
                    "Tipo_de_cliente": tipo_cliente,
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
                st.success("Cliente actualizado exitosamente.")
            else:
                st.error(f"ERROR: {actualizacion}")

        st.divider()

        st.write("### Seleccione el tipo de promoción:")

        espacio_izq, c1, c2, espacio_der = st.columns([3, 1, 1, 3])
        vinos_encartados = await self.obtener_vinos_encartados(numero_sitio)
        if c1.button("Botella"):
            st.session_state.botella_copeo = "Botella"
        if c2.button("Copa"):
            st.session_state.botella_copeo = "Copa"
            

        if st.session_state.botella_copeo == "Botella":
            await self.listar_vinos_encartados(vinos_encartados)
        elif st.session_state.botella_copeo == "Copa":
            await self.listar_vinos_copeo(vinos_encartados, numero_sitio)

        fotografias = modulo_fotos.moduloFotos(numero_sitio, self.carpeta_evidencias)
        await fotografias.generar_seccion()

        mapas = modulo_mapa.moduloMapa(self.clientes, numero_sitio, self.carpeta_mapas)
        await mapas.generar_seccion()

    # Lógica para el guardado de información
    async def actualizar_cliente(self, filtro: str, nuevo_documento: dict) -> str:
        try:
            self.clientes.update_one({"Número Sitio": filtro}, {"$set": nuevo_documento})
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

    async def listar_vinos_copeo(self, registros: list, numero_sitio: int):
        productos: list = []

        if len(registros) == 0:
            st.error("No hay vinos de copeo.")
            return

        st.write("### Seleccione los vinos para canje por copeo:")

        for element in registros:
            productos.append(st.checkbox(element["Producto"], value=await self.revisar_copeo(element["Producto"])))

        if st.button("Guardar"):
            await self.guardar_productos_copeo(registros, productos, numero_sitio)

    async def guardar_productos_copeo(self, registros: list, productos: list, numero_sitio: int):
        print(registros)
        nuevo_documento: dict = {
            "Número Sitio": numero_sitio,
            "Numero vendedor": st.session_state.empleado_actual["Numero_Vendedor"],
            "Productos copeo": [element["Producto"] for i, element in enumerate(registros) if productos[i] == True]
        }

        cliente_actual = await self.productos_copeo.find_one({"Número Sitio": numero_sitio});

        if cliente_actual is not None:
            try:
                self.productos_copeo.update_one({"Número Sitio": numero_sitio}, {"$set": nuevo_documento})
            except Exception as e:
                st.error(f"ERROR: {e}")
                return
            st.success("Productos por copeo actualizados exitosamente.")
            return
        
        self.productos_copeo.insert_one(nuevo_documento)
        st.success("Productos por copeo agregados exitosamente.")

    async def revisar_copeo(self, nombre_producto: str):
        return True if await self.productos_copeo.find_one({"Productos copeo": nombre_producto}) else False