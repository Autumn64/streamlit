import os
import datetime
import streamlit as st

class moduloInterfaz():
    def __init__(self, vendedores, clientes, facturas, productos_oracle, modulo_clientes, modulo_facturas, modulo_crear_cliente):
        self.vendedores = vendedores
        self.clientes = clientes
        self.facturas = facturas
        self.productos_oracle = productos_oracle
        self.moduloClientes = modulo_clientes
        self.moduloFacturas = modulo_facturas
        self.moduloCrearCliente = modulo_crear_cliente
        self.numero_sitio_cliente = ""

    async def seccion_clientes_nuevos(self):
        if st.button("Volver"):
            st.session_state.tipo_cliente = None
            st.session_state.botella_copeo = None
            st.rerun()

        await self.moduloCrearCliente.mostrar_cliente()

    async def seccion_clientes_existentes(self):
        if st.button("Volver"):
            st.session_state.tipo_cliente = None
            st.session_state.botella_copeo = None
            st.rerun()

        self.numero_sitio_cliente = await self.moduloClientes.listar_clientes()

        if self.numero_sitio_cliente is None or len(self.numero_sitio_cliente) <= 0:
            return

        selected_option = st.radio(
            "Selecciona una opción",  # Etiqueta del radio
            ["Clientes", "Call Book", "Canje/Corchos", "Reporte/Entrega"],  # Las 4 opciones
            index=0,  # Opción por defecto seleccionada
            horizontal=st.session_state.horizontal,
        )

        match selected_option:
            case "Clientes":
                await self.moduloClientes.mostrar_cliente(self.numero_sitio_cliente, st.session_state.cliente_guardado[self.numero_sitio_cliente])
            case "Call Book":
                await self.moduloFacturas.mostrar_cliente(self.numero_sitio_cliente, st.session_state.cliente_guardado[self.numero_sitio_cliente])

    async def generar_seccion(self):
        if st.session_state.tipo_cliente == "Existente":
            await self.seccion_clientes_existentes()
            return
        
        elif st.session_state.tipo_cliente == "Nuevo":
            await self.seccion_clientes_nuevos()
            return

        esp_izq, c1, c2, esp_der = st.columns(4)

        if c1.button("Ver clientes existentes"):
            st.session_state.tipo_cliente = "Existente"
            st.rerun()

        if c2.button("Crear cliente nuevo"):
            st.session_state.tipo_cliente = "Nuevo"
            st.rerun()
