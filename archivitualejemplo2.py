# Proyecto Archivirtual
# Importamos las librerías necesarias
# Os: Para manejar rutas y directorios del sistema operativo
# Shutil: Para operaciones de alto nivel con archivos y directorios
# Datetime: Para manejar fechas y horas
# Collections: Para usar estructuras de datos como deque (cola)
import os
import shutil
from datetime import datetime
from collections import deque

# 1- DEFINICIÓN DE CLASES PARA ARCHIVOS Y CARPETAS
class Archivo:
    def __init__(self, nombre, contenido=""):
        self.nombre = nombre
        self.contenido = contenido
        # Calculamos el tamaño del archivo en bytes usando la codificación UTF-8
        self.tamanio = len(contenido.encode('utf-8')) 
        self.fecha_creacion = datetime.now()

    # Representación en cadena del objeto Archivo
    def __str__(self):
        return f"[ARCHIVO] {self.nombre} ({self.tamanio} bytes) - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"


class Carpeta:
    def __init__(self, nombre, padre=None):
        self.nombre = nombre
        self.padre = padre  # Referencia al nodo padre en el árbol
        self.subcarpetas = {}  # {nombre: Objeto Carpeta}
        self.archivos = {}     # {nombre: Objeto Archivo}
        self.accesos_directos = {} # Grafo: {nombre_alias: Objeto Carpeta destino}
        self.fecha_creacion = datetime.now()

    def calcular_tamanio(self):
        # Calcula el tamaño total de la carpeta sumando los tamaños de sus archivos y subcarpetas
        total = sum(arch.tamanio for arch in self.archivos.values())
        for sub in self.subcarpetas.values():
            total += sub.calcular_tamanio()
        return total

    def __str__(self):
        # Imprime la carpeta con su nombre y una barra al final para indicar que es una carpeta
        return f"[CARPETA] {self.nombre}/"

# 2- LISTA DOBLEMENTE LIGADA (Historial de Navegación)

# NodoHistorial encargado de almacenar cada carpeta visitada en el historial
class NodoHistorial:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.siguiente = None
        self.anterior = None

# HistorialNavegacion maneja la navegación hacia adelante y hacia atrás en el historial de carpetas visitadas
class HistorialNavegacion:
    def __init__(self, carpeta_inicial):
        self.actual = NodoHistorial(carpeta_inicial)

    # Permite visitar una nueva carpeta, agregándola al historial
    def visitar(self, carpeta):
        nuevo_nodo = NodoHistorial(carpeta)
        nuevo_nodo.anterior = self.actual
        self.actual.siguiente = nuevo_nodo
        self.actual = nuevo_nodo

    # Permite retroceder en el historial, devolviendo la carpeta anterior si existe
    def atras(self):
        if self.actual.anterior:
            self.actual = self.actual.anterior
            return self.actual.carpeta
        return None

    # Permite avanzar en el historial, devolviendo la carpeta siguiente si existe
    def adelante(self):
        if self.actual.siguiente:
            self.actual = self.actual.siguiente
            return self.actual.carpeta
        return None

# La clase ArchiVirtualSystem encapsula toda la funcionalidad del sistema de archivos virtual
class ArchiVirtualSystem:
    def __init__(self, ruta_fisica_master):
        # Inicializa el sistema virtual con la ruta física donde se almacenará la estructura de carpetas y archivos
        self.ruta_master = ruta_fisica_master
        os.makedirs(self.ruta_master, exist_ok=True)

        # Inicializa la carpeta raíz "Master" y establece la carpeta actual como la raíz 
        # Árbol en memoria RAM 
        self.raiz = Carpeta("Master")
        self.actual = self.raiz

        # Cargar automáticamente lo que ya exista en el disco al iniciar
        self.cargar_desde_disco(self.ruta_master, self.raiz)

        # Inicializa el historial de navegación, la papelera de reciclaje y la cola de impresión
        self.historial = HistorialNavegacion(self.raiz)
        # Inicializa la papelera de reciclaje como una lista vacía y la cola de impresión como una deque (cola doblemente terminada)
        self.papelera = []
        # Inicializa la cola de impresión como una deque (cola doblemente terminada) para manejar los archivos que se enviarán a imprimir
        self.cola_impresion = deque()

    # Carga la estructura de carpetas y archivos desde el disco al sistema virtual en memoria 
    def cargar_desde_disco(self, ruta_fisica, carpeta_virtual):
        #Lee la carpeta real del disco y reconstruye el árbol virtual en memoria.
        try:
            elementos = os.listdir(ruta_fisica)
        except FileNotFoundError:
            return

        # Recorre cada elemento en la carpeta física
        # Si es una carpeta, crea un objeto Carpeta y llama recursivamente a cargar_desde_disco para sus subcarpetas.
        # Si es un archivo, crea un objeto Archivo y lo agrega a la carpeta virtual.
        for elemento in elementos:
            ruta_completa = os.path.join(ruta_fisica, elemento)
            if os.path.isdir(ruta_completa):
                nueva_sub = Carpeta(elemento, padre=carpeta_virtual)
                carpeta_virtual.subcarpetas[elemento] = nueva_sub
                self.cargar_desde_disco(ruta_completa, nueva_sub)
            elif os.path.isfile(ruta_completa):
                try:
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                except Exception:
                    contenido = "[Contenido binario o no legible]"
                nuevo_arch = Archivo(elemento, contenido)
                carpeta_virtual.archivos[elemento] = nuevo_arch

    # Obtiene la ruta actual en formato de cadena, desde la carpeta raíz hasta la carpeta actual
    def obtener_ruta_actual_str(self):
        pasos = []
        nodo = self.actual
        while nodo:
            pasos.append(nodo.nombre)
            nodo = nodo.padre
        return "/".join(reversed(pasos))

    # RECORRIDOS DEL ÁRBOL 
    # Si el nodo es None, se inicia desde la raíz. Se imprime la carpeta y sus archivos, y luego se llama recursivamente a las subcarpetas.
    def recorrido_preorden(self, nodo=None, nivel=0):
        if nodo is None:
            nodo = self.raiz
        print("  " * nivel + f"- [Carpeta] {nodo.nombre}/")
        # Recorre los archivos de la carpeta actual y los imprime con sangría según el nivel del árbol
        for arch in nodo.archivos.values():
            print("  " * (nivel + 1) + f"- [Archivo] {arch.nombre} ({arch.tamanio}b)")
        for sub in nodo.subcarpetas.values():
            self.recorrido_preorden(sub, nivel + 1)

    # Recorrido por niveles (BFS) del árbol de carpetas y archivos. Se utiliza una cola para recorrer cada nivel del árbol, imprimiendo las carpetas y archivos con sangría según el nivel.
    def recorrido_por_niveles(self):
        print("\n--- Recorrido por Niveles del Sistema ---")
        cola = deque([(self.raiz, 0)])
        while cola:
            nodo, nivel = cola.popleft()
            print("  " * nivel + f"- [Carpeta] {nodo.nombre}")
            for arch in nodo.archivos.values():
                print("  " * (nivel + 1) + f"- [Archivo] {arch.nombre}")
            for sub in nodo.subcarpetas.values():
                cola.append((sub, nivel + 1))

    #  OPERACIONES BÁSICAS 
    def crear_carpeta(self, nombre):
        if nombre in self.actual.subcarpetas:
            print(f"Error: La carpeta '{nombre}' ya existe.")
            return
        # Creamos la nueva carpeta en memoria y la agregamos a la carpeta actual
        nueva = Carpeta(nombre, padre=self.actual)
        self.actual.subcarpetas[nombre] = nueva

        # Creamos la carpeta físicamente en el disco, asegurándonos de que la ruta exista
        ruta_fisica = os.path.join(self.ruta_master, self.obtener_ruta_relativa(nueva))
        os.makedirs(ruta_fisica, exist_ok=True)
        print(f"Carpeta '{nombre}' creada con éxito en memoria y disco.")

    # Creamos un archivo en la carpeta actual, tanto en memoria como en el disco. Se crea un objeto Archivo y se agrega a la carpeta actual. Luego, se crea el archivo físicamente en el disco con el contenido proporcionado.
    def crear_archivo(self, nombre, contenido):
        nuevo_arch = Archivo(nombre, contenido)
        self.actual.archivos[nombre] = nuevo_arch

        # Refleja la creación del archivo en el disco, asegurándose de que la ruta exista y escribiendo el contenido en el archivo físico
        ruta_carpeta_fisica = os.path.join(self.ruta_master, self.obtener_ruta_relativa(self.actual))
        os.makedirs(ruta_carpeta_fisica, exist_ok=True)
        with open(os.path.join(ruta_carpeta_fisica, nombre), 'w', encoding='utf-8') as f:
            f.write(contenido)
            
        print(f"Archivo '{nombre}' creado con éxito.")

    # Cambia el directorio actual a la carpeta especificada por nombre. Si el nombre es "..", se retrocede al padre. Si el nombre corresponde a una subcarpeta o acceso directo, se cambia a esa carpeta. Se actualiza el historial de navegación y se imprime la ruta actual.
    def cambiar_directorio(self, nombre):
        # Si el nombre es "..", se retrocede al padre. Si el nombre corresponde a una subcarpeta o acceso directo, se cambia a esa carpeta. Se actualiza el historial de navegación y se imprime la ruta actual.
        if nombre == "..":
            carpeta_destino = self.actual.padre
            if carpeta_destino:
                self.actual = carpeta_destino
                self.historial.visitar(self.actual)
                print(f"Regresaste a: {self.obtener_ruta_actual_str()}")
            else:
                print("Ya estás en la raíz Master.")
        elif nombre in self.actual.subcarpetas:
            self.actual = self.actual.subcarpetas[nombre]
            self.historial.visitar(self.actual)
            print(f"Entraste a: {self.obtener_ruta_actual_str()}")
        elif nombre in self.actual.accesos_directos:
            self.actual = self.actual.accesos_directos[nombre]
            self.historial.visitar(self.actual)
            print(f"Acceso directo utilizado. Estás en: {self.obtener_ruta_actual_str()}")
        else:
            print(f"No se encontró la carpeta '{nombre}'.")

    # Obtiene la ruta relativa de una carpeta desde la raíz "Master". Se recorre el árbol hacia arriba hasta llegar a la raíz, almacenando los nombres de las carpetas en una lista. 
    # Luego, se construye la ruta relativa uniendo los nombres en orden inverso.
    def obtener_ruta_relativa(self, carpeta):
        pasos = []
        nodo = carpeta
        while nodo and nodo.nombre != "Master":
            pasos.append(nodo.nombre)
            nodo = nodo.padre
        return os.path.join(*reversed(pasos)) if pasos else ""

    # PILA: PAPELERA DE RECICLAJE 
    # Elimina un elemento (archivo o carpeta) de la carpeta actual y lo envía a la papelera de reciclaje. Si el elemento es un archivo, se elimina físicamente del disco. 
    # Si es una carpeta, se elimina recursivamente del disco. Se guarda el elemento eliminado en la pila de la papelera junto con su tipo y ubicación original.
    def eliminar_elemento(self, nombre):
        if nombre in self.actual.archivos:
            elem = self.actual.archivos.pop(nombre)
            tipo = "archivo"
            ruta_fisica = os.path.join(self.ruta_master, self.obtener_ruta_relativa(self.actual), nombre)
            if os.path.exists(ruta_fisica): os.remove(ruta_fisica)
        elif nombre in self.actual.subcarpetas:
            elem = self.actual.subcarpetas.pop(nombre)
            tipo = "carpeta"
            ruta_fisica = os.path.join(self.ruta_master, self.obtener_ruta_relativa(self.actual), nombre)
            if os.path.exists(ruta_fisica): shutil.rmtree(ruta_fisica)
        else:
            print("Elemento no encontrado.")
            return

        self.papelera.append({"elemento": elem, "tipo": tipo, "ubicacion_padre": self.actual})
        print(f"'{nombre}' enviado a la Papelera de reciclaje.")

    # Restaura el último elemento eliminado de la papelera de reciclaje. Si la papelera está vacía, se muestra un mensaje indicando que no hay elementos para restaurar.
    def restaurar_papelera(self):
        if not self.papelera:
            print("La papelera está vacía.")
            return
        item = self.papelera.pop()
        padre = item["ubicacion_padre"]
        elem = item["elemento"]
        if item["tipo"] == "archivo":
            padre.archivos[elem.nombre] = elem
        else:
            padre.subcarpetas[elem.nombre] = elem
        print(f"Elemento '{elem.nombre}' restaurado con éxito a su carpeta original.")

    # COLA: COLA DE IMPRESIÓN 
    # Envía un archivo a la cola de impresión. Si el archivo existe en la carpeta actual, se agrega a la cola de impresión y se muestra un mensaje indicando que se ha agregado.
    def enviar_a_impresion(self, nombre_archivo):
        if nombre_archivo in self.actual.archivos:
            archivo = self.actual.archivos[nombre_archivo]
            self.cola_impresion.append(archivo)
            print(f"Archivo '{nombre_archivo}' agregado a la cola de impresión.")
        else:
            print("El archivo no existe en esta carpeta.")

    def procesar_impresion(self):
        if not self.cola_impresion:
            print("La cola de impresión está vacía.")
            return
        archivo = self.cola_impresion.popleft()
        print(f"\n[Imprimiendo...] -> Archivo: {archivo.nombre}")
        print(f"Contenido:\n{archivo.contenido}\n-------------------")

    # GRAFOS: ACCESOS DIRECTOS Y DETECCIÓN DE CICLOS (DFS) 
    # Crea un acceso directo (alias) hacia una carpeta destino. Antes de crear el acceso directo, se verifica si la carpeta destino existe y si la creación del acceso directo generaría un ciclo en el grafo.
    def crear_acceso_directo(self, alias, carpeta_destino_nombre):
        if carpeta_destino_nombre in self.actual.subcarpetas:
            destino = self.actual.subcarpetas[carpeta_destino_nombre]
            if self.detectar_ciclo(destino, self.actual):
                print("Error: No se puede crear el acceso directo porque genera un ciclo (bucle).")
            else:
                self.actual.accesos_directos[alias] = destino
                print(f"Enlace directo '{alias}' creado hacia '{carpeta_destino_nombre}'.")
        else:
            print("Carpeta destino no encontrada.")

    def detectar_ciclo(self, inicio, objetivo):
        actual = inicio
        while actual:
            if actual == objetivo:
                return True
            actual = actual.padre
        return False

    # ORDENAMIENTO Y BÚSQUEDA 
    # Ordena los archivos de la carpeta actual utilizando el algoritmo de burbuja según el criterio especificado (nombre o tamaño). 
    # Se recorre la lista de archivos y se intercambian los elementos según el criterio. Al final, se actualiza el diccionario de archivos con la lista ordenada.
    def ordenar_archivos_burbuja(self, criterio="nombre"):
        archivos_lista = list(self.actual.archivos.values())
        n = len(archivos_lista)
        for i in range(n):
            for j in range(0, n - i - 1):
                if criterio == "nombre" and archivos_lista[j].nombre > archivos_lista[j + 1].nombre:
                    archivos_lista[j], archivos_lista[j + 1] = archivos_lista[j + 1], archivos_lista[j]
                elif criterio == "tamanio" and archivos_lista[j].tamanio > archivos_lista[j + 1].tamanio:
                    archivos_lista[j], archivos_lista[j + 1] = archivos_lista[j + 1], archivos_lista[j]
        
        self.actual.archivos = {a.nombre: a for a in archivos_lista}
        print(f"Archivos ordenados por {criterio} mediante Algoritmo Burbuja.")

    # Búsqueda binaria de un archivo por nombre en la carpeta actual. Primero se ordenan los archivos por nombre y luego se realiza la búsqueda binaria.
    # Si se encuentra el archivo, se devuelve el objeto Archivo; de lo contrario, se devuelve None.
    def buscar_archivo_binario(self, nombre):
        self.ordenar_archivos_burbuja("nombre")
        nombres = list(self.actual.archivos.keys())
        
        izq, der = 0, len(nombres) - 1
        while izq <= der:
            medio = (izq + der) // 2
            if nombres[medio] == nombre:
                return self.actual.archivos[nombre]
            elif nombres[medio] < nombre:
                izq = medio + 1
            else:
                der = medio - 1
        return None

# 3- MENÚ INTERACTIVO POR CONSOLA

def main():
    # Inicializa el sistema virtual con la ruta física donde se almacenará la estructura de carpetas y archivos
    # IMPORTANTE: CAMBIAR ESTA RUTA A UNA QUE EXISTA EN TU SISTEMA PARA PROBAR EL PROGRAMA
    # SI NO EXISTE, EL PROGRAMA CREARÁ LA CARPETA "holamundo" EN EL ESCRITORIO DEL USUARIO QUE HAYA EJECUTADO EL PROGRAMA. 
    ruta_desktop = r"C:\Users\josue\Desktop\holamundo"
    sistema = ArchiVirtualSystem(ruta_desktop)

    while True:
        print(f"\n========================================")
        print(f"Ruta Física Master: {sistema.ruta_master}")
        print(f"Ubicación Actual: {sistema.obtener_ruta_actual_str()}")
        print(f"========================================")
        print("1. Listar contenido actual")
        print("2. Crear carpeta")
        print("3. Crear archivo")
        print("4. Cambiar de directorio (cd / '..')")
        print("5. Historial: Atrás / Adelante")
        print("6. Eliminar elemento (Papelera / Pila)")
        print("7. Restaurar último elemento eliminado")
        print("8. Cola de impresión (Enviar y Procesar)")
        print("9. Crear acceso directo")
        print("10. Ordenar archivos")
        print("11. Buscar archivo")
        print("12. Ver árbol completo (Preorden / Niveles)")
        print("13. Salir")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            print("\n--- Contenido ---")
            for name, sub in sistema.actual.subcarpetas.items():
                print(f"  [Carpeta] {sub.nombre}/")
            for name, shortcut in sistema.actual.accesos_directos.items():
                print(f"  [Acceso Directo] {name} -> {shortcut.nombre}")
            for name, arch in sistema.actual.archivos.items():
                print(f"  [Archivo] {arch}")
            if not sistema.actual.subcarpetas and not sistema.actual.archivos and not sistema.actual.accesos_directos:
                print("  (Carpeta vacía)")
            print(f"Tamaño total de carpeta: {sistema.actual.calcular_tamanio()} bytes")

        elif opcion == "2":
            nombre = input("Nombre de la nueva carpeta: ").strip()
            sistema.crear_carpeta(nombre)

        elif opcion == "3":
            nombre = input("Nombre del archivo (ej. notas.txt): ").strip()
            contenido = input("Contenido del archivo:\n")
            sistema.crear_archivo(nombre, contenido)

        elif opcion == "4":
            nombre = input("Carpeta a la que deseas entrar (o '..' para retroceder): ").strip()
            sistema.cambiar_directorio(nombre)

        elif opcion == "5":
            sub_op = input("¿A dónde deseas moverte? [1] Atrás  [2] Adelante: ").strip()
            if sub_op == "1":
                res = sistema.historial.atras()
                if res: sistema.actual = res; print(f"Estás en: {sistema.obtener_ruta_actual_str()}")
                else: print("No hay historial hacia atrás.")
            elif sub_op == "2":
                res = sistema.historial.adelante()
                if res: sistema.actual = res; print(f"Estás en: {sistema.obtener_ruta_actual_str()}")
                else: print("No hay historial hacia adelante.")

        elif opcion == "6":
            nombre = input("Nombre del archivo o carpeta a eliminar: ").strip()
            sistema.eliminar_elemento(nombre)

        elif opcion == "7":
            sistema.restaurar_papelera()

        elif opcion == "8":
            sub_op = input("[1] Enviar archivo a imprimir  [2] Procesar siguiente impresión: ").strip()
            if sub_op == "1":
                nombre = input("Nombre del archivo actual a imprimir: ").strip()
                sistema.enviar_a_impresion(nombre)
            elif sub_op == "2":
                sistema.procesar_impresion()

        elif opcion == "9":
            alias = input("Nombre del acceso directo (alias): ").strip()
            destino = input("Nombre de la carpeta destino existente: ").strip()
            sistema.crear_acceso_directo(alias, destino)

        elif opcion == "10":
            criterio = input("Ordenar por: [nombre] o [tamanio]: ").strip()
            sistema.ordenar_archivos_burbuja(criterio)

        elif opcion == "11":
            nombre = input("Nombre del archivo a buscar: ").strip()
            encontrado = sistema.buscar_archivo_binario(nombre)
            if encontrado:
                print(f"¡Encontrado! -> {encontrado}")
            else:
                print("Archivo no encontrado.")

        elif opcion == "12":
            print("\n--- Árbol en Preorden ---")
            sistema.recorrido_preorden()
            sistema.recorrido_por_niveles()

        elif opcion == "13":
            print("Saliendo de ArchiVirtual. ¡Mucho éxito con tu proyecto!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()