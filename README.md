# CORCHOS

[![Pull requests](https://img.shields.io/badge/dynamic/json.svg?label=pull%20requests&style=for-the-badge&color=limegreen&url=https://codeberg.org/api/v1/repos/Autumn64/CORCHOS&query=open_pr_counter)](https://codeberg.org/Autumn64/CORCHOS/pulls)
[![Issues](https://img.shields.io/badge/dynamic/json.svg?label=issues&style=for-the-badge&color=red&url=https://codeberg.org/api/v1/repos/Autumn64/CORCHOS&query=open_issues_count)](https://codeberg.org/Autumn64/CORCHOS/issues)
[![Stars](https://img.shields.io/badge/dynamic/json.svg?label=stars&style=for-the-badge&color=yellow&url=https://codeberg.org/api/v1/repos/Autumn64/CORCHOS&query=stars_count)](https://codeberg.org/Autumn64/CORCHOS)
[![License](https://img.shields.io/badge/license-AGPL_v3-blue?label=license&style=for-the-badge&url=)](https://codeberg.org/Autumn64/CORCHOS/src/branch/main/LICENSE)

## Sistema básico de gestión de promociones por cliente hecho en Streamlit y MongoDB (incompleto)

### Descripción

CORCHOS es un sistema de gestión de promociones por cliente originalmente diseñado para una empesa de vinos mexicana, que se quedó incompleto dado que el cliente prefirió la implementación de un sistema diferente. Dado que el _software_ no está atado por ningún contrato ni acuerdo de confidencialidad, las desarrolladoras del proyecto acordamos liberarlo como Software Libre para el beneficio de la comunidad.

### Características
- Hecho con Streamlit y MongoDB.
- Implementa una API muy sencilla con [OpenStreetMap](https://www.openstreetmap.org/) para la generación de mapas.
- Simple y eficiente.

### Consideraciones
- El programa está incompleto, lo que significa que dos módulos no fueron implementados, y hay diversas medidas de seguridad que no se incluyeron, tales como la autenticación en la base de datos MongoDB o el uso de encriptación para información sensible, debido a que se paró el desarrollo del proyecto en una etapa muy temprana y sólo se alcanzó a hacer un prototipo funcional.
- Aunque en la carpeta `schemas` se incluye la estructura de la base de datos utilizada, la información es propiedad del cliente y, por ende, no se incluye en el repositorio.
- Se incluye el archivo `.env` porque no expone ningún tipo de información sensible.

### Información extra

El proyecto es liberado al público de buena fe, para que sirva de guía a quien desee desarrollar programas con Streamlit y/o MongoDB, o quiera desarrollar una implementación sencilla de OSM.

#### Todo el código en este repositorio está bajo la [Licencia Pública General Affero de GNU v3 o superior](./LICENSE), con algunas librerías y módulos pudiendo poseer distintas licencias permisivas compatibles con la licencia principal del proyecto. Este programa está destinado a su distribución para propósitos no comerciales, y ni la propietaria del proyecto ni sus colaboradores son responsables del uso que cualquiera fuera de éste pueda dar al software proporcionado y a sus insumos.

#### All the code in this repository is licensed under the [GNU Affero General Public License version 3 or later](./LICENSE), with some libraries and modules that may be under different permissive licenses compatible with the main project's license. This program is meant to be distributed for non-commercial purposes, and neither this project's owner nor its contributors are responsible for the use anyone outside of it may give to the software provided and its assets.