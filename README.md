# ARCHIVIRTUAL — Sistema de Gestión de Archivos Virtual

Bienvenido al repositorio oficial de **ArchiVirtual**. Este es un proyecto académico desarrollado en Python que simula el funcionamiento interno del sistema de gestión de archivos de un sistema operativo, integrando estructuras de datos clásicas, algoritmos de búsqueda y ordenamiento, y sincronización persistente con el almacenamiento local.

El sistema administra de manera integral el ciclo de vida de directorios y documentos: desde la navegación jerárquica y el historial de rutas, hasta la recuperación de elementos eliminados, la simulación de colas de impresión y la creación de accesos directos con prevención de bucles.

---

## Descripción del Proyecto

Este software fue diseñado para modelar y comprender cómo los sistemas operativos organizan, indexan y acceden a la información almacenada. Su arquitectura separa la lógica de negocio y estructuras de datos (`core/`) de la capa de presentación (`interfaz/`), operando sobre un directorio raíz denominado `Master` dentro de la carpeta `almacenamiento/`.

Al iniciar la ejecución, el sistema escanea el directorio físico `Master` y reconstruye automáticamente la jerarquía completa en memoria RAM, garantizando la persistencia de los datos entre sesiones sin comprometer la integridad de los archivos reales del equipo anfitrión.

---

## Características Principales y Estructuras de Datos

- **Árbol General (Jerarquía de Directorios):** Modela la relación padre-hijo entre carpetas y archivos dentro del nodo raíz `Master`. Permite calcular el tamaño total de forma recursiva y ejecutar recorridos en **Preorden** y **por Niveles (BFS)**.
- **Lista Doblemente Ligada (Historial de Navegación):** Gestiona el desplazamiento entre directorios mediante punteros bidireccionales, habilitando las funciones de navegación *Atrás* y *Adelante* de forma fluida.
- **Pila / LIFO (Papelera de Reciclaje):** Almacena temporalmente los archivos y carpetas eliminados bajo el principio *Last In, First Out*, permitiendo restaurar el último elemento borrado hacia su ubicación original.
- **Cola / FIFO (Cola de Impresión):** Administra los documentos enviados a impresión bajo el principio *First In, First Out*, procesando y despachando cada archivo en estricto orden de llegada.
- **Grafos Dirigidos (Accesos Directos y Detección de Ciclos):** Implementa enlaces directos entre carpetas como aristas dirigidas. Antes de crear un enlace, ejecuta un recorrido en profundidad (**DFS**) para detectar y bloquear referencias circulares que puedan generar bucles infinitos.
- **Algoritmos de Ordenamiento y Búsqueda:**
  - **Ordenamiento Burbuja:** Organiza el contenido de un directorio por nombre, tamaño en bytes o fecha de creación.
  - **Búsqueda Secuencial y Binaria:** Permite localizar archivos de forma lineal o mediante búsqueda binaria optimizada sobre listas previamente ordenadas.

---

## Estructura del Repositorio

```text
ArchiVirtual/
├── almacenamiento/
│   └── Master/              # Directorio raíz físico sincronizado con el árbol virtual
├── core/
│   ├── __init__.py
│   ├── modelos.py           # Definición de clases base (Archivo, Carpeta, Nodos)
│   └── sistema.py           # Lógica del árbol, pila, cola, grafos y algoritmos
├── interfaz/
│   ├── __init__.py
│   └── ventana_principal.py # Interfaz gráfica de usuario (GUI) del sistema
├── main.py                  # Punto de entrada principal de la aplicación
└── README.md                # Documentación oficial del proyecto

```

## Tecnologías Utilizadas
Para garantizar la portabilidad, eficiencia y facilidad de ejecución en cualquier entorno, el proyecto fue construido utilizando herramientas estándar de Python:
- Python 3.13+ (Lenguaje principal de desarrollo)
- Programación Orientada a Objetos (POO) (Modelado modular de estructuras de datos)
- Módulos estándar (os, shutil, datetime, collections) (Sincronización con disco, manejo de marcas de tiempo y estructuras auxiliares)

## Instalación y Ejecución

- Clonar el repositorio en su equipo local:
git clone [https://github.com/josueahgarciaxd/archivirtual.git](https://github.com/josueahgarciaxd/archivirtual.git)

- Acceder al directorio del proyecto:
  (`cd archivirtual`)
 
- Ejecutar el archivo principal:
  (`python main.py`)
 
## Consideraciones
Esta es una primera versión educativa. La papelera y los accesos directos se mantienen en memoria durante la ejecución; sus elementos eliminados sí se mueven a `.papelera_archivirtual` dentro de Master. Al cerrar y volver a abrir, la pila de papelera no se reconstruye todavía.

El sistema administra su propia carpeta `almacenamiento/Master`. No selecciones carpetas del sistema operativo como raíz de pruebas.
