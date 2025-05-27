import os
import datetime
import streamlit as st

class moduloFacturas():
    def __init__(self, facturas, productos_oracle):
        self.facturas = facturas
        self.productos_oracle = productos_oracle
        self.productos_dict = {}

    # Función reutilizable para generar los campos del cliente.
    async def generar_tabla_datos(self, nombre, valor):
        with st.container():
            esp_izq, c1, c2, esp_der = st.columns([1, 1.5, 1.5, 1], vertical_alignment="center")
            c1.write(nombre)
            c2.text_input(nombre, valor, disabled=True, label_visibility="collapsed")

    async def llenar_diccionario_productos(self, numero_sitio):
        self.productos_dict = {}
        facturas = self.facturas.find({"envio": numero_sitio})

        if len(await facturas.clone().to_list()) < 1:
            st.error("No se encontraron facturas.")
            return

        async for element in facturas:
            if element["fadpro"] not in self.productos_dict:
                self.productos_dict[element["fadpro"]] = [int(element["cantidad"]), element['fadbta_'], element['unidad']]
                continue

            self.productos_dict[element["fadpro"]][0] += int(element["cantidad"])
            self.productos_dict[element["fadpro"]][1] += element["fadbta_"]

    async def generar_seccion_puntos(self, numero_sitio):
        for idx, (key, value) in enumerate(self.productos_dict.items()):
            producto_actual = await self.productos_oracle.find_one({"ID_Producto_Oracle": key})
            if producto_actual is None:
                continue

            # Fadbta entre cantidad total comprada entre conversión de cajas a botellas (si son cajas).
            if value[2] == "CJA":
                costo_unitario = value[1] / value[0] / producto_actual["Botxcaja"]
            else:
                costo_unitario = value[1] / value[0]

            costo_unitario = float(f"{costo_unitario:.2f}")

            c1, c2, c3, c4 = st.container().columns(4, gap="large")
            # Los key son porque Streamlit se rompe si no los ponemos. No los usamos para nada.
            c1.text_input("Línea", producto_actual["Sublínea"], disabled=True, key=f"linea_{idx}")
            c2.text_input("Valor en Puntos", producto_actual["puntos"], disabled=True, key=f"puntos_{idx}")
            c3.text_input("Producto", producto_actual["Producto"], disabled=True, key=f"producto_{idx}")
            c4.text_input("Costo Unitario", costo_unitario, disabled=True, key=f"costo_{idx}")

    # Sección de producto a puntos
    async def generar_seccion_prod_puntos(self, numero_sitio):
        productos_canjeables: dict = {}
        facturas_canjeables: dict = {}
        for key, value in self.productos_dict.items():
            p_actual = await self.productos_oracle.find_one({"ID_Producto_Oracle": key})
            if p_actual is None:
                continue
            productos_canjeables[p_actual["ID_Producto_Oracle"]] = p_actual["Producto"]

        st.write("### Seleccione el producto que quiere canjear")
        producto_actual = st.selectbox("Producto a canjear", productos_canjeables.values(), placeholder="Seleccione un producto")

        if len(productos_canjeables) == 0: return

        id_actual = list(productos_canjeables.keys())[list(productos_canjeables.values()).index(producto_actual)]

        facturas_disponibles = self.facturas.find({"$and": [{"envio": numero_sitio}, {"fadpro": id_actual}]})

        if len(await facturas_disponibles.clone().to_list()) < 1:
            st.warning("No hay facturas disponibles.")
            return

        async for element in facturas_disponibles:
            facturas_canjeables[element["fad_nuf"]] = element["cantidad"]

        st.write("### Seleccione la factura")

        factura_actual = st.selectbox("Factura a canjear", facturas_canjeables.keys(), placeholder="Seleccione una factura")

        st.write(f"### Con la factura {factura_actual} puede canjear {int(facturas_canjeables[factura_actual])} {'corcho' if int(facturas_canjeables[factura_actual]) == 1 else 'corchos'} de este producto.")

        st.write("### Escriba la cantidad de botellas a canjear:")

        cantidad_canje = st.text_input("Cantidad a canjear", placeholder="Cantidad")

        if not cantidad_canje:
            return

        try:
            cantidad = int(cantidad_canje)
        except:
            st.error("Debe escribir sólo números enteros.")
            return
        
        if cantidad > int(facturas_canjeables[factura_actual]):
            st.error("La cantidad ingresada es mayor a la cantidad máxima que se puede canjear.")
            return

        producto_a_canjear = await self.productos_oracle.find_one({"ID_Producto_Oracle": id_actual})
        
        cantidad_puntos = int(producto_a_canjear["puntos"]) * cantidad

        st.success(f"Se agregaron {cantidad_puntos} puntos a su cuenta.")

    # Interfaz que muestra la información del cliente seleccionado
    async def mostrar_cliente(self, numero_sitio: str, cliente_actual: dict):
        st.divider()
        st.write("### Datos del cliente:")
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

        await self.generar_tabla_datos("R.F.C", cliente_actual["RFC"])
        await self.generar_tabla_datos("Fecha", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        await self.generar_tabla_datos("No. Carnet", cliente_actual["Clave_de_cliente"])
        await self.generar_tabla_datos("Razón Social", cliente_actual["Descripción Cuenta"])
        await self.generar_tabla_datos("Nombre Solicitante", st.session_state.empleado_actual["EMPLEADO"])
        await self.generar_tabla_datos("Nombre del Mayorista o Distribuidor", cliente_actual["Mayorista_o_Proveedor"])
        await self.generar_tabla_datos("Tipo de Cliente", cliente_actual["Tipo_de_cliente"])

        st.divider()

        st.write("### Bonificaciones por Puntos:")

        await self.llenar_diccionario_productos(numero_sitio)
        await self.generar_seccion_puntos(numero_sitio)
        await self.generar_seccion_prod_puntos(numero_sitio)