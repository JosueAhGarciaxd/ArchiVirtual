# ArchiVirtual

Primera versión de escritorio con Python y Tkinter.

## Requisitos
- Python 3.10 o superior (Tkinter normalmente viene incluido).
- No requiere instalar paquetes externos.

## Ejecutar
Desde la carpeta `ArchiVirtual`, abre una terminal y ejecuta:

```bash
python main.py
```

## Estructura
- `core/`: modelos y lógica del sistema de archivos.
- `interfaz/`: ventanas y controles Tkinter.
- `almacenamiento/Master/`: directorio físico administrado por ArchiVirtual.

## Funcionalidades incluidas
- Explorador de directorios con árbol y vista de contenido.
- Navegación atrás, adelante y subir.
- Crear carpetas y archivos.
- Abrir y editar archivos de texto.
- Eliminar a una papelera interna en disco y restaurar el último elemento.
- Búsqueda binaria y ordenamiento burbuja.
- Cola de impresión simulada.
- Accesos directos con comprobación de ciclos.
- Visualización textual de recorridos del árbol, pila, cola e historial.

## Consideraciones
Esta es una primera versión educativa. La papelera y los accesos directos se mantienen en memoria durante la ejecución; sus elementos eliminados sí se mueven a `.papelera_archivirtual` dentro de Master. Al cerrar y volver a abrir, la pila de papelera no se reconstruye todavía.

El sistema administra su propia carpeta `almacenamiento/Master`. No selecciones carpetas del sistema operativo como raíz de pruebas.
