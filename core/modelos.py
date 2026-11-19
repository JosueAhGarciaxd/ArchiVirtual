# Archivo: core/modelos.py
# Descripción: Este archivo contiene las clases que representan los modelos de datos del sistema ArchiVirtual, incluyendo archivos, carpetas y el historial de navegación. Estas clases encapsulan la información y el comportamiento de los elementos del sistema de archivos virtual.
# datetime: funcionalidad para manejar fechas y horas, utilizada para registrar la fecha de creación de archivos y carpetas.
from datetime import datetime

# La clase Archivo representa un archivo en el sistema, con atributos como nombre, contenido, ruta, tamaño y fecha de creación.
class Archivo:
    def __init__(self, nombre, contenido="", ruta=None):
        self.nombre = nombre
        self.contenido = contenido
        self.ruta = ruta
        self.tamanio = len(contenido.encode("utf-8"))
        self.fecha_creacion = datetime.now()

    def __str__(self):
        return f"{self.nombre} ({self.tamanio} bytes)"

# La clase Carpeta representa una carpeta en el sistema, con atributos como nombre, carpeta padre, ruta, subcarpetas, archivos, accesos directos y fecha de creación. También incluye un método para calcular el tamaño total de la carpeta.
class Carpeta:
    def __init__(self, nombre, padre=None, ruta=None):
        self.nombre = nombre
        self.padre = padre
        self.ruta = ruta
        self.subcarpetas = {}
        self.archivos = {}
        self.accesos_directos = {}
        self.fecha_creacion = datetime.now()

    # Método para calcular el tamaño total de la carpeta, sumando el tamaño de todos los archivos y subcarpetas contenidos en ella.
    # El método recorre recursivamente las subcarpetas y suma sus tamaños, junto con el tamaño de los archivos en la carpeta actual.
    # Devuelve el tamaño total en bytes.
    # Este método es útil para obtener información sobre el espacio ocupado por una carpeta y sus contenidos en el sistema de archivos virtual.
    # En resumen, calcular_tamanio proporciona una forma de medir el tamaño total de una carpeta y sus elementos asociados en el sistema ArchiVirtual.
    def calcular_tamanio(self):
        total = sum(a.tamanio for a in self.archivos.values())
        total += sum(c.calcular_tamanio() for c in self.subcarpetas.values())
        return total

    def __str__(self):
        return f"{self.nombre}/"

# La clase NodoHistorial representa un nodo en la lista doblemente enlazada que forma el historial de navegación del sistema. Cada nodo contiene una referencia a la carpeta visitada, así como referencias al nodo siguiente y al nodo anterior en la lista.
class NodoHistorial:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.siguiente = None
        self.anterior = None

# La clase HistorialNavegacion implementa una lista doblemente enlazada para gestionar el historial de navegación del sistema. Permite visitar nuevas carpetas, navegar hacia atrás y hacia adelante en el historial.
class HistorialNavegacion:
    # Lista doblemente ligada para navegar atrás y adelante.
    def __init__(self, carpeta_inicial):
        self.actual = NodoHistorial(carpeta_inicial)

    # Visita una nueva carpeta y actualiza el historial de navegación.
    # Este método crea un nuevo nodo en la lista doblemente enlazada para representar la carpeta visitada. El nodo actual se actualiza para apuntar a la nueva carpeta, y cualquier tramo futuro en el historial se elimina.
    # La función visitar permite al usuario registrar la navegación a una nueva carpeta en el historial, facilitando la capacidad de retroceder y avanzar en la jerarquía de carpetas del sistema.
    def visitar(self, carpeta):
        nuevo = NodoHistorial(carpeta)
        nuevo.anterior = self.actual
        # Una nueva navegación elimina el tramo futuro.
        self.actual.siguiente = nuevo
        self.actual = nuevo

    # Navega hacia atrás en el historial de navegación, si es posible.
    # Este método verifica si hay un nodo anterior en la lista doblemente enlazada. Si es así, actualiza el nodo actual para apuntar al nodo anterior y devuelve la carpeta correspondiente. Si no hay un nodo anterior (es decir, si ya se encuentra en la primera carpeta visitada), devuelve None.
    # La función atras permite al usuario retroceder en el historial de navegación, facilitando la exploración de carpetas previamente visitadas en el sistema de archivos virtual.
    def atras(self):
        if self.actual.anterior:
            self.actual = self.actual.anterior
            return self.actual.carpeta
        return None

    # Navega hacia adelante en el historial de navegación, si es posible.
    # Este método verifica si hay un nodo siguiente en la lista doblemente enlazada. Si es así, actualiza el nodo actual para apuntar al nodo siguiente y devuelve la carpeta correspondiente. Si no hay un nodo siguiente (es decir, si ya se encuentra en la última carpeta visitada), devuelve None.
    # La función adelante permite al usuario avanzar en el historial de navegación, facilitando la exploración de carpetas previamente visitadas en el sistema de archivos virtual.
    def adelante(self):
        if self.actual.siguiente:
            self.actual = self.actual.siguiente
            return self.actual.carpeta
        return None
