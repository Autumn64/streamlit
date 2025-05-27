import io
import os
import math
import json
import requests
import urllib.parse
import streamlit as st
from PIL import Image

class moduloMapa():
    def __init__(self, clientes, num_sitio, carpeta_mapas):
        self.clientes = clientes
        self.num_sitio = num_sitio
        self.carpeta = carpeta_mapas
        self.zoom = 15
        self.headers = {
            "User-Agent": "AppCorchosPDU/1.0 (autumn64@disroot.org)"
        }

    async def procesar_imagen(self, imagen):
        img = Image.open(imagen)

        return img

    # Función que convierte las coordenadas a tiles de OSM.
    async def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 1 << zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile

    async def sacar_direccion(self):
        cliente_actual = await self.clientes.find_one({"Número Sitio": self.num_sitio})

        if not cliente_actual:
            st.error("ERROR: No se pudo encontrar al cliente.")
            return

        return cliente_actual

    async def sacar_coordenadas(self, address) -> tuple:
        direccion = urllib.parse.quote(address)
        peticion = requests.get(f"https://nominatim.openstreetmap.org/search?q={direccion}&format=json&polygon=1&addressdetails=1", headers=self.headers)
        peticion.raise_for_status()
        resultado: dict = json.loads(peticion.text)

        if len(resultado) == 0:
            st.error("ERROR: No se encontró el lugar.")
            return -1, -1

        return float(resultado[0]["lat"]), float(resultado[0]["lon"])

    async def sacar_mapa(self, lat, lon):
        x, y = await self.deg2num(lat, lon, self.zoom)

        peticion = requests.get(f"https://tile.openstreetmap.org/{self.zoom}/{x}/{y}.png", headers=self.headers)
        peticion.raise_for_status()

        return await self.procesar_imagen(io.BytesIO(peticion.content))

    async def generar_seccion(self):
        st.divider()
        st.write("### Mapa del lugar")
        with st.container():
            esp_izquierdo, c1, c2, esp_derecho = st.columns([0.5, 1, 1, 0.5], vertical_alignment="center")

        direccion = await self.sacar_direccion()
        if not direccion: return
        x, y = await self.sacar_coordenadas(direccion["DIREC"])
        if x == -1 or y == -1: return;

        # Si bien la API usada es la de OSM, se agrega un link de Google Maps porque ese es el servicio usado por el cliente.
        c1.markdown(f"<a href='https://www.google.com/maps/place/{x},{y}' target='_blank'><h4 style='text-align: center; '>{direccion['DIREC']} {direccion['DIREC1']}</h4></a>", unsafe_allow_html=True)

        if os.path.isfile(f"{self.carpeta}{self.num_sitio}.png") == True:
            c2.image(await self.procesar_imagen(f"{self.carpeta}{self.num_sitio}.png"))
            return

        imagen_mapa = await self.sacar_mapa(x, y)

        imagen_mapa.save(f"{self.carpeta}{self.num_sitio}.png")

        c2.image(imagen_mapa)