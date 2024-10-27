# Proyecto MonitorAI Obserbilidad +  IA

Este proyecto ayuda a hacer mucho más fácil la comunicación de los ejecutivos de soporte con los usuarios bajando las barreras de reporting, permitiendo que los usuarios reporten sus prblemas al momento y de la forma mas clara para el ejecutivo.

Basta de tener que ir a indagar sin información, la IA realiza la captura de datos y la decisión sobre que hacer con el ticket.

## Demo

Puedes probar el widget y cargar un error en el siguiente enlace:

- [Página del Widget](https://fastidious-maamoul-920dad.netlify.app/)

Mientras que la visualización en streamlit se ven en siguiente
## Arquitectura

![Arquitectura de la Solución](./Arquitectura_Solucion.png)

Esta es la arquitectura que representa la interacción entre las dos aplicaciones (FastAPI y Streamlit).

## Instalación y Ejecución

Para ejecutar la aplicación localmente con Docker, sigue los siguientes pasos:

1. Clona este repositorio:
    ```bash
    git clone https://github.com/tu-usuario/tu-repo.git
    cd tu-repo
    ```

2. Asegúrate de tener Docker y Docker Compose instalados.

3. Inicia los contenedores:
    ```bash
    docker-compose up -d
    ```

4. La aplicación Streamlit estará disponible en `http://localhost:8501` y la API de FastAPI en `http://localhost:4000`.

## Estructura del Proyecto

- **FastAPI**: Es la API backend que maneja las solicitudes de datos y se integra con la aplicación de Streamlit.
- **Streamlit**: Proporciona la interfaz de usuario y visualización de datos.
- **Docker**: Ambas aplicaciones se ejecutan dentro de contenedores Docker para facilitar su despliegue.

## Gifs del Proceso

Aquí se mostrarán dos GIFs que explican el proceso de la solución:

- ![GIF 1 - Explicación](./gif1.gif) *(Aún no disponible)*
- ![GIF 2 - Explicación](./gif2.gif) *(Aún no disponible)*

