import os
import streamlit as st
from PIL import Image

class moduloFotos():
    def __init__(self, num_sitio, carpeta_evidencias):
        self.num_sitio = num_sitio
        self.carpeta = carpeta_evidencias
    
    async def procesar_imagen(self, imagen):
        img = Image.open(imagen)
        return img

    async def guardar_foto(self, imagen) -> str:
        try:
            imagen = await self.procesar_imagen(imagen)
            imagen.convert("RGB").save(f"{self.carpeta}{self.num_sitio}.jpg")
            return "Success"
        except Exception as e:
            return e

    async def generar_seccion(self):
        st.divider()
        st.write("### Fotografía de la Carta de Vinos")
        await self.incluir_foto()

        archivo = st.file_uploader("Subir imagen de Carta de Vinos", type=["jpg", "jpeg", "png", "webp"])
        c1, c2, c3 = st.columns([2, 1, 2])
        submit_archivo = c2.button("Guardar fotografía")

        if submit_archivo and archivo:
            resultado = await self.guardar_foto(archivo)
            if resultado == "Success":
                st.rerun()
            else:
                st.error(f"ERROR: {resultado}")

    async def incluir_foto(self):
        if os.path.isfile(f"{self.carpeta}{self.num_sitio}.jpg") == False: return

        c1, c2, c3 = st.columns(3)

        c2.image(await self.procesar_imagen(f"{self.carpeta}{self.num_sitio}.jpg"))
