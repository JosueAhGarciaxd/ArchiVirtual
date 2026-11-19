# Archivo: core/sistema.py (o el módulo correspondiente a ArchiVirtualSystem)
# Descripción: Este archivo contiene la clase ArchiVirtualSystem, que implementa la lógica principal del sistema de archivos virtual y su sincronización con el disco físico, manteniendo estructuras como historial, papelera, cola de impresión y recorridos de árbol/grafo.
# os: módulo estándar para interactuar con el sistema operativo.
import os
# shutil: módulo estándar para operaciones de alto nivel sobre archivos y directorios, como mover o eliminar árboles completos.
import shutil
# Path: clase orientada a objetos de pathlib para manipular rutas de archivos y directorios de forma limpia y multiplataforma.
from pathlib import Path
# deque: estructura de datos de doble extremo de collections, ideal para implementar colas eficientes con operaciones en ambos extremos.
from collections import deque
# .modelos: importa las clases Archivo, Carpeta y HistorialNavegacion desde el módulo modelos del paquete actual.
from .modelos import Archivo, Carpeta, HistorialNavegacion

# La clase ArchiVirtualSystem coordina la estructura virtual de carpetas y archivos con su respaldo físico en disco, gestionando navegación, papelera, ordenamiento, búsqueda, cola de impresión, accesos directos y recorridos.
class ArchiVirtualSystem:
    # Logica del sistema. No contiene código Tkinter ni llamadas input()/print() para que pueda utilizarse desde una consola, interfaz u otra aplicación.

    # Constructor de ArchiVirtualSystem: inicializa la ruta raíz física, crea la carpeta raíz si no existe, construye el árbol virtual cargando los elementos desde el disco y prepara las estructuras auxiliares (historial, papelera y cola de impresión).
    def __init__(self, ruta_fisica_master):
        self.ruta_master = Path(ruta_fisica_master).resolve()
        self.ruta_master.mkdir(parents=True, exist_ok=True)

        self.raiz = Carpeta("Master", ruta=self.ruta_master)
        self.actual = self.raiz
        self._cargar_desde_disco(self.ruta_master, self.raiz)

        self.historial = HistorialNavegacion(self.raiz)
        self.papelera = []                 # Pila: append() / pop()
        self.cola_impresion = deque()      # Cola: append() / popleft()

    # Método auxiliar privado que recorre recursivamente un directorio físico en disco y puebla la carpeta virtual correspondiente con sus subcarpetas y archivos.
    # Omite enlaces simbólicos para evitar ciclos o lecturas fuera de la estructura esperada, y maneja excepciones de permisos o codificación de forma segura.
    def _cargar_desde_disco(self, ruta, carpeta_virtual):
        try:
            elementos = sorted(ruta.iterdir(), key=lambda p: p.name.lower())
        except (FileNotFoundError, PermissionError):
            return

        for elemento in elementos:
            try:
                if elemento.is_symlink():
                    continue
                if elemento.is_dir():
                    sub = Carpeta(elemento.name, carpeta_virtual, elemento)
                    carpeta_virtual.subcarpetas[elemento.name] = sub
                    self._cargar_desde_disco(elemento, sub)
                elif elemento.is_file():
                    try:
                        contenido = elemento.read_text(encoding="utf-8")
                    except (UnicodeDecodeError, OSError):
                        contenido = ""
                    arch = Archivo(elemento.name, contenido, elemento)
                    arch.tamanio = elemento.stat().st_size
                    carpeta_virtual.archivos[elemento.name] = arch
            except OSError:
                continue

    # Devuelve una representación en cadena de la carpeta actual partiendo desde "Master" como raíz.
    def obtener_ruta_actual_str(self):
        return "Master" if self.actual == self.raiz else "Master/" + self.actual.ruta.relative_to(self.ruta_master).as_posix()

    # Calcula y devuelve la ruta relativa de una carpeta dada respecto a la carpeta física master (o "." si es la raíz).
    def obtener_ruta_relativa(self, carpeta):
        if carpeta == self.raiz:
            return Path(".")
        return carpeta.ruta.relative_to(self.ruta_master)

    # Lista los elementos contenidos en la carpeta indicada (o en la carpeta actual por defecto), agrupándolos en tuplas según su tipo: subcarpetas, accesos directos y archivos.
    def listar_elementos(self, carpeta=None):
        carpeta = carpeta or self.actual
        resultado = []
        for sub in carpeta.subcarpetas.values():
            resultado.append(("Carpeta", sub))
        for alias, destino in carpeta.accesos_directos.items():
            resultado.append(("Acceso directo", alias, destino))
        for arch in carpeta.archivos.values():
            resultado.append(("Archivo", arch))
        return resultado

    # Método estático que valida que un nombre de archivo, carpeta o acceso directo no esté vacío, no sea "." o ".." y no contenga caracteres prohibidos en rutas.
    @staticmethod
    def _validar_nombre(nombre):
        nombre = nombre.strip()
        if not nombre or nombre in {".", ".."} or any(c in nombre for c in '<>:"/\\|?*'):
            raise ValueError("El nombre está vacío o contiene caracteres no permitidos.")
        return nombre

    # Crea una nueva subcarpeta tanto en el disco físico como en la estructura virtual dentro de la carpeta actual, verificando primero que el nombre sea válido y no exista previamente.
    def crear_carpeta(self, nombre):
        nombre = self._validar_nombre(nombre)
        if nombre in self.actual.subcarpetas or nombre in self.actual.archivos:
            raise FileExistsError(f"Ya existe un elemento llamado '{nombre}'.")
        ruta = self.actual.ruta / nombre
        ruta.mkdir()
        nueva = Carpeta(nombre, self.actual, ruta)
        self.actual.subcarpetas[nombre] = nueva
        return nueva

    # Crea un nuevo archivo con el contenido indicado en el disco físico y lo registra en la carpeta virtual actual, actualizando su tamaño en bytes.
    def crear_archivo(self, nombre, contenido=""):
        nombre = self._validar_nombre(nombre)
        if nombre in self.actual.archivos or nombre in self.actual.subcarpetas:
            raise FileExistsError(f"Ya existe un elemento llamado '{nombre}'.")
        ruta = self.actual.ruta / nombre
        ruta.write_text(contenido, encoding="utf-8")
        arch = Archivo(nombre, contenido, ruta)
        arch.tamanio = ruta.stat().st_size
        self.actual.archivos[nombre] = arch
        return arch

    # Lee y devuelve el contenido textual de un objeto Archivo desde su ruta física en disco utilizando codificación UTF-8.
    def leer_archivo(self, archivo):
        return archivo.ruta.read_text(encoding="utf-8")

    # Escribe el nuevo contenido en el archivo físico en disco y actualiza los atributos contenido y tamanio del objeto Archivo en memoria.
    def guardar_archivo(self, archivo, contenido):
        archivo.ruta.write_text(contenido, encoding="utf-8")
        archivo.contenido = contenido
        archivo.tamanio = archivo.ruta.stat().st_size

    # Cambia la carpeta actual según el nombre dado (".." para subir al padre, o el nombre de una subcarpeta o acceso directo) y registra la visita en el historial.
    def cambiar_directorio(self, nombre):
        if nombre == "..":
            destino = self.actual.padre
            if destino is None:
                return self.actual
        else:
            destino = self.actual.subcarpetas.get(nombre)
            if destino is None:
                destino = self.actual.accesos_directos.get(nombre)
            if destino is None:
                raise FileNotFoundError(f"No se encontró la carpeta '{nombre}'.")
        self.actual = destino
        self.historial.visitar(destino)
        return destino

    # Mueve la carpeta actual hacia la carpeta destino indicada y, opcionalmente, registra el movimiento en el historial de navegación.
    def navegar_a(self, carpeta, registrar=True):
        self.actual = carpeta
        if registrar:
            self.historial.visitar(carpeta)

    # Retrocede a la carpeta anterior en el historial de navegación si existe y actualiza self.actual.
    def navegar_atras(self):
        destino = self.historial.atras()
        if destino:
            self.actual = destino
        return destino

    # Avanza a la carpeta siguiente en el historial de navegación si existe y actualiza self.actual.
    def navegar_adelante(self):
        destino = self.historial.adelante()
        if destino:
            self.actual = destino
        return destino

    # Sube a la carpeta padre de la carpeta actual registrando la navegación en el historial, o devuelve None si ya se está en la raíz.
    def subir_directorio(self):
        if self.actual.padre:
            self.navegar_a(self.actual.padre)
            return self.actual
        return None

    # Envía un archivo o carpeta de la carpeta actual a la carpeta física de papelera y registra el metadato del elemento eliminado en la pila self.papelera para permitir su posterior restauración.
    def eliminar_elemento(self, nombre, tipo):
        if tipo == "Archivo" and nombre in self.actual.archivos:
            elemento = self.actual.archivos[nombre]
            origen = elemento.ruta
        elif tipo == "Carpeta" and nombre in self.actual.subcarpetas:
            elemento = self.actual.subcarpetas[nombre]
            origen = elemento.ruta
        else:
            raise FileNotFoundError("No se encontró el elemento seleccionado.")

        papelera_dir = self.ruta_master / ".papelera_archivirtual"
        papelera_dir.mkdir(exist_ok=True)
        destino = papelera_dir / f"{len(self.papelera)}_{origen.name}"
        contador = 1
        while destino.exists():
            destino = papelera_dir / f"{len(self.papelera)}_{contador}_{origen.name}"
            contador += 1
        shutil.move(str(origen), str(destino))

        if tipo == "Archivo":
            del self.actual.archivos[nombre]
        else:
            del self.actual.subcarpetas[nombre]

        self.papelera.append({
            "elemento": elemento, "tipo": tipo, "padre": self.actual,
            "nombre_original": nombre, "ruta_papelera": destino
        })
        return elemento

    # Restaura el último elemento eliminado (cima de la pila self.papelera) de vuelta a su carpeta padre original, reinsertándolo en la estructura virtual y actualizando rutas si es una carpeta.
    def restaurar_papelera(self):
        if not self.papelera:
            raise IndexError("La papelera está vacía.")
        item = self.papelera[-1]
        padre = item["padre"]
        nombre = item["nombre_original"]
        destino = padre.ruta / nombre
        if destino.exists():
            raise FileExistsError(f"Ya existe '{nombre}' en la ubicación original.")
        shutil.move(str(item["ruta_papelera"]), str(destino))
        self.papelera.pop()

        elemento = item["elemento"]
        elemento.ruta = destino
        if item["tipo"] == "Archivo":
            padre.archivos[nombre] = elemento
        else:
            elemento.padre = padre
            padre.subcarpetas[nombre] = elemento
            self._actualizar_rutas(elemento)
        return elemento

    # Método auxiliar recursivo que actualiza la ruta física (atributo ruta) de todos los archivos y subcarpetas dentro de una carpeta tras moverla o restaurarla.
    def _actualizar_rutas(self, carpeta):
        for archivo in carpeta.archivos.values():
            archivo.ruta = carpeta.ruta / archivo.nombre
        for sub in carpeta.subcarpetas.values():
            sub.ruta = carpeta.ruta / sub.nombre
            self._actualizar_rutas(sub)

    # Vacía por completo la papelera eliminando físicamente del disco cada archivo o carpeta almacenado en ella y desapilando todos los registros de self.papelera.
    def vaciar_papelera(self):
        while self.papelera:
            item = self.papelera.pop()
            ruta = item["ruta_papelera"]
            if ruta.is_dir():
                shutil.rmtree(ruta, ignore_errors=True)
            elif ruta.exists():
                ruta.unlink()

    # Ordena los archivos de la carpeta actual mediante el algoritmo de ordenamiento burbuja según el criterio indicado ("nombre" o "tamanio") y reconstruye el diccionario de archivos con el nuevo orden.
    def ordenar_archivos_burbuja(self, criterio="nombre"):
        archivos = list(self.actual.archivos.values())
        if criterio not in ("nombre", "tamanio"):
            raise ValueError("Criterio no válido.")
        n = len(archivos)
        for i in range(n):
            for j in range(n - i - 1):
                a, b = archivos[j], archivos[j + 1]
                valor_a = a.nombre.lower() if criterio == "nombre" else a.tamanio
                valor_b = b.nombre.lower() if criterio == "nombre" else b.tamanio
                if valor_a > valor_b:
                    archivos[j], archivos[j + 1] = archivos[j + 1], archivos[j]
        self.actual.archivos = {a.nombre: a for a in archivos}
        return archivos

    # Busca un archivo por nombre en la carpeta actual utilizando búsqueda binaria sobre los nombres ordenados previamente con ordenar_archivos_burbuja("nombre").
    def buscar_archivo_binario(self, nombre):
        self.ordenar_archivos_burbuja("nombre")
        nombres = list(self.actual.archivos.keys())
        izquierda, derecha = 0, len(nombres) - 1
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            actual = nombres[medio]
            if actual.lower() == nombre.lower():
                return self.actual.archivos[actual]
            if actual.lower() < nombre.lower():
                izquierda = medio + 1
            else:
                derecha = medio - 1
        return None

    # Agrega un archivo existente de la carpeta actual al final de la cola de impresión (FIFO) y devuelve la cantidad actual de trabajos en cola.
    def enviar_a_impresion(self, nombre):
        archivo = self.actual.archivos.get(nombre)
        if archivo is None:
            raise FileNotFoundError("El archivo no existe en esta carpeta.")
        self.cola_impresion.append(archivo)
        return len(self.cola_impresion)

    # Extrae y devuelve el primer archivo en espera de la cola de impresión (FIFO), o lanza IndexError si la cola está vacía.
    def procesar_impresion(self):
        if not self.cola_impresion:
            raise IndexError("La cola de impresión está vacía.")
        return self.cola_impresion.popleft()

    # Crea un acceso directo (arista dirigida) en la carpeta actual hacia una subcarpeta destino, validando el alias, verificando que no exista duplicado y comprobando que no se forme un ciclo.
    def crear_acceso_directo(self, alias, nombre_destino):
        alias = self._validar_nombre(alias)
        destino = self.actual.subcarpetas.get(nombre_destino)
        if destino is None:
            raise FileNotFoundError("La carpeta destino no existe en esta ubicación.")
        if alias in self.actual.subcarpetas or alias in self.actual.archivos or alias in self.actual.accesos_directos:
            raise FileExistsError("Ya existe un elemento con ese nombre.")
        # Los accesos directos se representan como aristas dirigidas.
        # Se evita un ciclo comprobando si el destino ya puede alcanzar el origen.
        if self._alcanzable(destino, self.actual):
            raise ValueError("El acceso directo produciría un ciclo.")
        self.actual.accesos_directos[alias] = destino

    # Recorre de forma iterativa (DFS con pila) desde el nodo inicio siguiendo subcarpetas y accesos directos para determinar si es posible llegar al nodo objetivo.
    def _alcanzable(self, inicio, objetivo):
        pendientes = [inicio]
        visitados = set()
        while pendientes:
            nodo = pendientes.pop()
            if nodo is objetivo:
                return True
            if id(nodo) in visitados:
                continue
            visitados.add(id(nodo))
            pendientes.extend(nodo.subcarpetas.values())
            pendientes.extend(nodo.accesos_directos.values())
        return False

    # Realiza un recorrido en preorden (recursivo) a partir de la carpeta raíz para generar una lista indentada con carpetas y archivos.
    def recorrido_preorden(self):
        resultado = []
        def visitar(nodo, nivel):
            resultado.append(("  " * nivel) + nodo.nombre + "/")
            for archivo in nodo.archivos.values():
                resultado.append(("  " * (nivel + 1)) + archivo.nombre)
            for sub in nodo.subcarpetas.values():
                visitar(sub, nivel + 1)
        visitar(self.raiz, 0)
        return resultado

    # Realiza un recorrido por niveles (BFS con cola deque) a partir de la carpeta raíz para generar una lista indentada con carpetas y archivos.
    def recorrido_por_niveles(self):
        resultado, cola = [], deque([(self.raiz, 0)])
        while cola:
            nodo, nivel = cola.popleft()
            resultado.append(("  " * nivel) + nodo.nombre + "/")
            for archivo in nodo.archivos.values():
                resultado.append(("  " * (nivel + 1)) + archivo.nombre)
            for sub in nodo.subcarpetas.values():
                cola.append((sub, nivel + 1))
        return resultado