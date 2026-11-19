from datetime import datetime

class Archivo:
    def __init__(self, nombre, contenido="", ruta=None):
        self.nombre = nombre
        self.contenido = contenido
        self.ruta = ruta
        self.tamanio = len(contenido.encode("utf-8"))
        self.fecha_creacion = datetime.now()

    def __str__(self):
        return f"{self.nombre} ({self.tamanio} bytes)"


class Carpeta:
    def __init__(self, nombre, padre=None, ruta=None):
        self.nombre = nombre
        self.padre = padre
        self.ruta = ruta
        self.subcarpetas = {}
        self.archivos = {}
        self.accesos_directos = {}
        self.fecha_creacion = datetime.now()

    def calcular_tamanio(self):
        total = sum(a.tamanio for a in self.archivos.values())
        total += sum(c.calcular_tamanio() for c in self.subcarpetas.values())
        return total

    def __str__(self):
        return f"{self.nombre}/"


class NodoHistorial:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.siguiente = None
        self.anterior = None


class HistorialNavegacion:
    """Lista doblemente ligada para navegar atrás y adelante."""
    def __init__(self, carpeta_inicial):
        self.actual = NodoHistorial(carpeta_inicial)

    def visitar(self, carpeta):
        nuevo = NodoHistorial(carpeta)
        nuevo.anterior = self.actual
        # Una nueva navegación elimina el tramo futuro.
        self.actual.siguiente = nuevo
        self.actual = nuevo

    def atras(self):
        if self.actual.anterior:
            self.actual = self.actual.anterior
            return self.actual.carpeta
        return None

    def adelante(self):
        if self.actual.siguiente:
            self.actual = self.actual.siguiente
            return self.actual.carpeta
        return None
