import os
import shutil
from pathlib import Path
from collections import deque
from .modelos import Archivo, Carpeta, HistorialNavegacion

class ArchiVirtualSystem:
    """
    Lógica del sistema. No contiene código Tkinter ni llamadas input()/print()
    para que pueda utilizarse desde una consola, interfaz u otra aplicación.
    """
    def __init__(self, ruta_fisica_master):
        self.ruta_master = Path(ruta_fisica_master).resolve()
        self.ruta_master.mkdir(parents=True, exist_ok=True)

        self.raiz = Carpeta("Master", ruta=self.ruta_master)
        self.actual = self.raiz
        self._cargar_desde_disco(self.ruta_master, self.raiz)

        self.historial = HistorialNavegacion(self.raiz)
        self.papelera = []                 # Pila: append() / pop()
        self.cola_impresion = deque()      # Cola: append() / popleft()

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

    def obtener_ruta_actual_str(self):
        return "Master" if self.actual == self.raiz else "Master/" + self.actual.ruta.relative_to(self.ruta_master).as_posix()

    def obtener_ruta_relativa(self, carpeta):
        if carpeta == self.raiz:
            return Path(".")
        return carpeta.ruta.relative_to(self.ruta_master)

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

    @staticmethod
    def _validar_nombre(nombre):
        nombre = nombre.strip()
        if not nombre or nombre in {".", ".."} or any(c in nombre for c in '<>:"/\\|?*'):
            raise ValueError("El nombre está vacío o contiene caracteres no permitidos.")
        return nombre

    def crear_carpeta(self, nombre):
        nombre = self._validar_nombre(nombre)
        if nombre in self.actual.subcarpetas or nombre in self.actual.archivos:
            raise FileExistsError(f"Ya existe un elemento llamado '{nombre}'.")
        ruta = self.actual.ruta / nombre
        ruta.mkdir()
        nueva = Carpeta(nombre, self.actual, ruta)
        self.actual.subcarpetas[nombre] = nueva
        return nueva

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

    def leer_archivo(self, archivo):
        return archivo.ruta.read_text(encoding="utf-8")

    def guardar_archivo(self, archivo, contenido):
        archivo.ruta.write_text(contenido, encoding="utf-8")
        archivo.contenido = contenido
        archivo.tamanio = archivo.ruta.stat().st_size

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

    def navegar_a(self, carpeta, registrar=True):
        self.actual = carpeta
        if registrar:
            self.historial.visitar(carpeta)

    def navegar_atras(self):
        destino = self.historial.atras()
        if destino:
            self.actual = destino
        return destino

    def navegar_adelante(self):
        destino = self.historial.adelante()
        if destino:
            self.actual = destino
        return destino

    def subir_directorio(self):
        if self.actual.padre:
            self.navegar_a(self.actual.padre)
            return self.actual
        return None

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

    def _actualizar_rutas(self, carpeta):
        for archivo in carpeta.archivos.values():
            archivo.ruta = carpeta.ruta / archivo.nombre
        for sub in carpeta.subcarpetas.values():
            sub.ruta = carpeta.ruta / sub.nombre
            self._actualizar_rutas(sub)

    def vaciar_papelera(self):
        while self.papelera:
            item = self.papelera.pop()
            ruta = item["ruta_papelera"]
            if ruta.is_dir():
                shutil.rmtree(ruta, ignore_errors=True)
            elif ruta.exists():
                ruta.unlink()

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

    def enviar_a_impresion(self, nombre):
        archivo = self.actual.archivos.get(nombre)
        if archivo is None:
            raise FileNotFoundError("El archivo no existe en esta carpeta.")
        self.cola_impresion.append(archivo)
        return len(self.cola_impresion)

    def procesar_impresion(self):
        if not self.cola_impresion:
            raise IndexError("La cola de impresión está vacía.")
        return self.cola_impresion.popleft()

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
