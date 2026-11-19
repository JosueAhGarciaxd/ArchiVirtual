# Importaciones de módulos necesarios para la interfaz gráfica
# tkinter: para crear la ventana principal y los widgets de la interfaz
# ttk: para utilizar widgets con estilo moderno
# messagebox: para mostrar cuadros de diálogo de información, advertencia y error
# simpledialog: para solicitar entradas simples al usuario
# filedialog: para abrir cuadros de diálogo de selección de archivos y directorios
# pathlib: para manejar rutas de archivos y directorios
# core.sistema: para importar la clase ArchiVirtualSystem que gestiona la lógica del sistema
# interfaz.ventana_principal: para importar la clase VentanaPrincipal que maneja la interfaz gráfica de usuario
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path

# Clase VentanaPrincipal que representa la ventana principal de la aplicación ArchiVirtual
class VentanaPrincipal(tk.Tk):
    # Inicializa la ventana principal y configura la interfaz gráfica
    def __init__(self, sistema):
        super().__init__()
        self.sistema = sistema
        self.title("ArchiVirtual | Explorador de archivos")
        self.geometry("1120x700")
        self.minsize(850, 550)
        self.configure(bg="#f3f5f8")
        self._configurar_estilos()
        self._construir_interfaz()
        self.actualizar_vista()

    # Configura los estilos de los widgets utilizando ttk.Style
    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Treeview", rowheight=27, font=("Segoe UI", 10), background="white", fieldbackground="white")
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("TButton", font=("Segoe UI", 9), padding=6)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 17, "bold"), background="#f3f5f8", foreground="#182230")
        estilo.configure("Sub.TLabel", font=("Segoe UI", 9), background="#f3f5f8", foreground="#64748b")

    # Construye la interfaz gráfica de la ventana principal, incluyendo encabezado, barra de herramientas, paneles y lista de elementos
    def _construir_interfaz(self):
        encabezado = ttk.Frame(self, padding=(16, 12))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="ArchiVirtual", style="Titulo.TLabel").pack(side="left")
        ttk.Label(encabezado, text="Sistema de archivos virtual", style="Sub.TLabel").pack(side="left", padx=12)

        # Barra de herramientas con botones para navegar, subir, actualizar y mostrar la ruta actual
        barra = ttk.Frame(self, padding=(12, 4))
        barra.pack(fill="x")
        self.btn_atras = ttk.Button(barra, text="← Atrás", command=self.ir_atras)
        self.btn_atras.pack(side="left", padx=3)
        self.btn_adelante = ttk.Button(barra, text="Adelante →", command=self.ir_adelante)
        self.btn_adelante.pack(side="left", padx=3)
        ttk.Button(barra, text="↑ Subir", command=self.subir).pack(side="left", padx=3)
        ttk.Button(barra, text="⟳ Actualizar", command=self.actualizar_vista).pack(side="left", padx=3)
        self.ruta_var = tk.StringVar()
        ruta = ttk.Entry(barra, textvariable=self.ruta_var, state="readonly")
        ruta.pack(side="left", fill="x", expand=True, padx=(12, 5))

        # Panel de acciones con botones para crear carpetas y archivos, editar, eliminar, restaurar, buscar, ordenar y ver estructuras
        acciones = ttk.Frame(self, padding=(12, 5))
        acciones.pack(fill="x")
        ttk.Button(acciones, text="+ Carpeta", command=self.crear_carpeta).pack(side="left", padx=3)
        ttk.Button(acciones, text="+ Archivo", command=self.crear_archivo).pack(side="left", padx=3)
        ttk.Button(acciones, text="Editar / abrir", command=self.abrir_archivo).pack(side="left", padx=3)
        ttk.Button(acciones, text="Eliminar", command=self.eliminar).pack(side="left", padx=3)
        ttk.Button(acciones, text="Restaurar papelera", command=self.restaurar).pack(side="left", padx=3)
        ttk.Button(acciones, text="Buscar", command=self.buscar).pack(side="left", padx=3)
        ttk.Button(acciones, text="Ordenar", command=self.ordenar).pack(side="left", padx=3)
        ttk.Button(acciones, text="Estructuras", command=self.ver_estructuras).pack(side="right", padx=3)

        # Panel principal dividido en tres secciones: árbol de directorios, lista de contenido y propiedades del elemento seleccionado
        cuerpo = ttk.Panedwindow(self, orient="horizontal")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=8)

        # Panel izquierdo: árbol de directorios
        panel_izq = ttk.Frame(cuerpo, padding=6)
        panel_centro = ttk.Frame(cuerpo, padding=6)
        panel_der = ttk.Frame(cuerpo, padding=10)
        cuerpo.add(panel_izq, weight=1)
        cuerpo.add(panel_centro, weight=3)
        cuerpo.add(panel_der, weight=1)

        # Panel izquierdo: árbol de directorios
        ttk.Label(panel_izq, text="DIRECTORIOS", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 7))
        self.arbol = ttk.Treeview(panel_izq, show="tree", selectmode="browse")
        self.arbol.pack(fill="both", expand=True)
        self.arbol.bind("<<TreeviewSelect>>", self._seleccion_arbol)
        self._ids_carpetas = {}

        # Panel central: lista de contenido
        ttk.Label(panel_centro, text="CONTENIDO", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 7))
        columnas = ("tipo", "nombre", "tamanio")
        self.lista = ttk.Treeview(panel_centro, columns=columnas, show="headings", selectmode="browse")
        self.lista.heading("tipo", text="Tipo")
        self.lista.heading("nombre", text="Nombre")
        self.lista.heading("tamanio", text="Tamaño")
        self.lista.column("tipo", width=105, stretch=False)
        self.lista.column("nombre", width=240)
        self.lista.column("tamanio", width=100, anchor="e", stretch=False)
        self.lista.pack(fill="both", expand=True)
        self.lista.bind("<Double-1>", self.doble_clic)
        self.lista.bind("<<TreeviewSelect>>", self.actualizar_propiedades)

        # Panel derecho: propiedades del elemento seleccionado y operaciones disponibles
        ttk.Label(panel_der, text="PROPIEDADES", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 12))
        self.prop_nombre = tk.StringVar(value="Ningún elemento seleccionado")
        self.prop_tipo = tk.StringVar(value="—")
        self.prop_tamanio = tk.StringVar(value="—")
        ttk.Label(panel_der, text="Nombre").pack(anchor="w")
        ttk.Label(panel_der, textvariable=self.prop_nombre, wraplength=170).pack(anchor="w", pady=(2, 12))
        ttk.Label(panel_der, text="Tipo").pack(anchor="w")
        ttk.Label(panel_der, textvariable=self.prop_tipo).pack(anchor="w", pady=(2, 12))
        ttk.Label(panel_der, text="Tamaño").pack(anchor="w")
        ttk.Label(panel_der, textvariable=self.prop_tamanio).pack(anchor="w", pady=(2, 12))
        ttk.Separator(panel_der).pack(fill="x", pady=10)
        ttk.Label(panel_der, text="Operaciones").pack(anchor="w")
        ttk.Button(panel_der, text="Enviar a impresión", command=self.enviar_impresion).pack(fill="x", pady=4)
        ttk.Button(panel_der, text="Procesar impresión", command=self.procesar_impresion).pack(fill="x", pady=4)
        ttk.Button(panel_der, text="Crear acceso directo", command=self.crear_acceso).pack(fill="x", pady=4)

        # Pie de la ventana: barra de estado que muestra información sobre el contenido actual y la papelera
        self.estado_var = tk.StringVar()
        ttk.Label(self, textvariable=self.estado_var, relief="sunken", anchor="w", padding=(10, 5)).pack(fill="x", side="bottom")

        # Inicializa la vista del sistema y actualiza la interfaz
    def _refrescar_arbol(self):
        self.arbol.delete(*self.arbol.get_children())
        self._ids_carpetas.clear()
        raiz_id = self.arbol.insert("", "end", text="📁 Master", open=True, values=())
        self._ids_carpetas[raiz_id] = self.sistema.raiz
        self._insertar_subcarpetas(raiz_id, self.sistema.raiz)
        for iid, carpeta in self._ids_carpetas.items():
            if carpeta is self.sistema.actual:
                self.arbol.selection_set(iid)
                self.arbol.see(iid)
                break

    # Inserta recursivamente las subcarpetas en el árbol de directorios
    def _insertar_subcarpetas(self, padre_id, carpeta):
        for sub in sorted(carpeta.subcarpetas.values(), key=lambda x: x.nombre.lower()):
            iid = self.arbol.insert(padre_id, "end", text=f"📁 {sub.nombre}", open=(sub is self.sistema.actual))
            self._ids_carpetas[iid] = sub
            self._insertar_subcarpetas(iid, sub)

    # Actualiza la vista de la interfaz gráfica con la información actual del sistema, incluyendo la ruta actual, el contenido de la carpeta y las propiedades del elemento seleccionado
    # Esta función también actualiza la barra de estado con información sobre el número de elementos, el tamaño total, la cantidad de elementos en la papelera y la cola de impresión.
    # Además, resetea las propiedades del elemento seleccionado a valores predeterminados si no hay ningún elemento seleccionado.
    def actualizar_vista(self):
        self.ruta_var.set(self.sistema.obtener_ruta_actual_str())
        self._refrescar_arbol()
        self.lista.delete(*self.lista.get_children())
        for tipo, elemento, *extra in self.sistema.listar_elementos():
            if tipo == "Acceso directo":
                alias, destino = elemento, extra[0]
                self.lista.insert("", "end", values=(tipo, f"{alias} → {destino.nombre}", "—"), tags=("directo",))
            elif tipo == "Carpeta":
                self.lista.insert("", "end", values=(tipo, elemento.nombre, "—"), tags=("carpeta",))
            else:
                self.lista.insert("", "end", values=(tipo, elemento.nombre, f"{elemento.tamanio} bytes"), tags=("archivo",))
        self.lista.tag_configure("carpeta", foreground="#9a6700")
        self.lista.tag_configure("archivo", foreground="#245b9e")
        total = self.sistema.actual.calcular_tamanio()
        self.estado_var.set(f"{len(self.lista.get_children())} elemento(s)   |   Tamaño total: {total} bytes   |   Papelera: {len(self.sistema.papelera)}   |   Cola de impresión: {len(self.sistema.cola_impresion)}")
        self.prop_nombre.set("Ningún elemento seleccionado")
        self.prop_tipo.set("—")
        self.prop_tamanio.set("—")

    # Maneja la selección de un elemento en el árbol de directorios y navega a la carpeta correspondiente si es diferente a la actual
    # Si no hay selección, la función retorna sin hacer nada. Si la carpeta seleccionada es diferente a la actual, se navega a ella y se actualiza la vista.
    # Si la carpeta seleccionada es la misma que la actual, no se realiza ninguna acción.
    def _seleccion_arbol(self, _event=None):
        seleccion = self.arbol.selection()
        if not seleccion:
            return
        carpeta = self._ids_carpetas.get(seleccion[0])
        if carpeta and carpeta is not self.sistema.actual:
            self.sistema.navegar_a(carpeta)
            self.actualizar_vista()

    # Devuelve el tipo y nombre del elemento seleccionado en la lista de contenido, o None si no hay selección
    # Esta función obtiene la selección actual de la lista de contenido y, si hay un elemento seleccionado, devuelve una tupla con el tipo y nombre del elemento. Si no hay selección, retorna None.
    # Si hay un elemento seleccionado, el nombre se devuelve tal como aparece en la lista, incluyendo cualquier información adicional (por ejemplo, alias de acceso directo).
    # Si no hay selección, la función retorna None.    
    def _seleccionado(self):
        seleccion = self.lista.selection()
        if not seleccion:
            return None
        valores = self.lista.item(seleccion[0], "values")
        return valores[0], valores[1]

    # Actualiza las propiedades del elemento seleccionado en el panel derecho de la interfaz gráfica
    # Esta función obtiene el elemento actualmente seleccionado en la lista de contenido y actualiza las variables
    # de propiedades (nombre, tipo y tamaño) en el panel derecho. Si no hay ningún elemento seleccionado, la función retorna sin hacer nada.
    # Si el elemento seleccionado es un archivo, se obtiene su tamaño en bytes; si es una carpeta, se calcula su tamaño total. Si el elemento es un acceso directo, se muestra un mensaje indicando que se trata de un acceso a otra carpeta.
    def actualizar_propiedades(self, _event=None):
        seleccionado = self._seleccionado()
        if not seleccionado:
            return
        tipo, nombre = seleccionado
        nombre = nombre.split(" → ")[0]
        self.prop_nombre.set(nombre)
        self.prop_tipo.set(tipo)
        if tipo == "Archivo":
            archivo = self.sistema.actual.archivos.get(nombre)
            self.prop_tamanio.set(f"{archivo.tamanio} bytes" if archivo else "—")
        elif tipo == "Carpeta":
            carpeta = self.sistema.actual.subcarpetas.get(nombre)
            self.prop_tamanio.set(f"{carpeta.calcular_tamanio()} bytes" if carpeta else "—")
        else:
            self.prop_tamanio.set("Acceso a otra carpeta")

    # Funciones para crear carpetas y archivos, abrir archivos, eliminar elementos, restaurar papelera, buscar archivos, ordenar archivos, navegar entre carpetas, enviar a impresión, procesar impresión, crear accesos directos y ver estructuras de datos
    def crear_carpeta(self):
        nombre = simpledialog.askstring("Nueva carpeta", "Nombre de la carpeta:", parent=self)
        if nombre is None:
            return
        self._ejecutar(lambda: self.sistema.crear_carpeta(nombre))

    # Función para crear un nuevo archivo en la carpeta actual del sistema
    def crear_archivo(self):
        nombre = simpledialog.askstring("Nuevo archivo", "Nombre (por ejemplo notas.txt):", parent=self)
        if nombre is None:
            return
        contenido = self._dialogo_contenido("Contenido inicial del archivo")
        if contenido is None:
            return
        self._ejecutar(lambda: self.sistema.crear_archivo(nombre, contenido))

    # Función para mostrar un cuadro de diálogo que permite al usuario editar el contenido de un archivo
    # Esta función crea una ventana emergente con un área de texto donde el usuario puede modificar
    def _dialogo_contenido(self, titulo, inicial=""):
        ventana = tk.Toplevel(self)
        ventana.title(titulo)
        ventana.geometry("620x440")
        ventana.minsize(480, 320)
        ventana.transient(self)
        ventana.grab_set()

        # El pie se coloca primero y queda anclado abajo para que los botones
        # nunca desaparezcan cuando el usuario cambia el tamaño de la ventana.
        pie = ttk.Frame(ventana, padding=(12, 10))
        pie.pack(side="bottom", fill="x")
        ttk.Separator(ventana).pack(side="bottom", fill="x")

        area = ttk.Frame(ventana, padding=10)
        area.pack(side="top", fill="both", expand=True)
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)

        caja = tk.Text(area, wrap="word", font=("Consolas", 10), undo=True)
        barra = ttk.Scrollbar(area, orient="vertical", command=caja.yview)
        caja.configure(yscrollcommand=barra.set)
        caja.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        caja.insert("1.0", inicial)

        resultado = {"contenido": None}

        # Función para aceptar los cambios realizados en el área de texto y cerrar la ventana de diálogo
        def aceptar(_event=None):
            resultado["contenido"] = caja.get("1.0", "end-1c")
            ventana.destroy()
            return "break"

        # Función para cancelar los cambios realizados en el área de texto y cerrar la ventana de diálogo
        def cancelar(_event=None):
            ventana.destroy()
            return "break"

        # Configuración de los botones "Cancelar" y "Guardar" en el pie de la ventana de diálogo
        ttk.Button(pie, text="Cancelar", command=cancelar).pack(side="right", padx=(6, 0))
        ttk.Button(pie, text="Guardar", command=aceptar).pack(side="right")

        # Configuración de eventos para cerrar la ventana con el botón de cerrar o con Ctrl+S
        # El evento "WM_DELETE_WINDOW" se activa cuando el usuario intenta cerrar la ventana con el botón de cerrar (X) en la esquina superior derecha. En este caso, se llama a la función cancelar para descartar los cambios y cerrar la ventana.
        # Los eventos "<Control-s>" y "<Control-S>" se activan cuando el usuario presiona Ctrl+S (mayúscula o minúscula) mientras la ventana de diálogo está activa. En este caso, se llama a la función aceptar para guardar los cambios y cerrar la ventana.
        ventana.protocol("WM_DELETE_WINDOW", cancelar)
        ventana.bind("<Control-s>", aceptar)
        ventana.bind("<Control-S>", aceptar)
        caja.focus_set()

        self.wait_window(ventana)
        return resultado["contenido"]

    # Función para abrir un archivo seleccionado en la lista de contenido y permitir al usuario editar su contenido
    # Esta función verifica si hay un archivo seleccionado en la lista de contenido. Si no hay selección o si el elemento seleccionado no es un archivo, se muestra un mensaje de información al usuario. Si hay un archivo seleccionado, se intenta leer su contenido utilizando el método leer_archivo del sistema.
    # Si ocurre un error al leer el archivo (por ejemplo, un error de decodificación o un error de entrada/salida), se muestra un mensaje de error al usuario. Si la lectura del archivo es exitosa, se abre un cuadro de diálogo para que el usuario pueda editar el contenido del archivo.
    # Si el usuario realiza cambios y guarda el contenido, se llama al método guardar_archivo del sistema para actualizar el archivo con el nuevo contenido. La función actualizar_vista se llama después de guardar los cambios para reflejar la actualización en la interfaz gráfica.
    # Si el usuario cancela la edición, no se realizan cambios en el archivo y la función retorna sin hacer nada.
    def abrir_archivo(self):
        seleccionado = self._seleccionado()
        if not seleccionado or seleccionado[0] != "Archivo":
            messagebox.showinfo("ArchiVirtual", "Selecciona un archivo para abrir.")
            return
        archivo = self.sistema.actual.archivos[seleccionado[1]]
        try:
            contenido = self.sistema.leer_archivo(archivo)
        except (UnicodeDecodeError, OSError) as exc:
            messagebox.showerror("No se puede abrir", str(exc))
            return
        nuevo = self._dialogo_contenido(f"Editar: {archivo.nombre}", contenido)
        if nuevo is not None:
            self._ejecutar(lambda: self.sistema.guardar_archivo(archivo, nuevo))

    # Función que maneja el doble clic en un elemento de la lista de contenido
    # Esta función obtiene el elemento seleccionado en la lista de contenido y realiza una acción según su tipo. Si el elemento es una carpeta, se cambia al directorio correspondiente. Si es un archivo, se abre para su edición. Si es un acceso directo, se navega a la carpeta destino del acceso directo.
    # Si no hay ningún elemento seleccionado, la función retorna sin hacer nada.
    # Si el elemento seleccionado es un acceso directo, se extrae el alias del nombre del elemento (que tiene el formato "alias → destino") y se utiliza para cambiar al directorio correspondiente.
    # Si ocurre algún error durante la ejecución de la acción (por ejemplo, si el archivo no se puede abrir), se muestra un mensaje de error al usuario.
    # Si el elemento seleccionado es una carpeta, se utiliza el método cambiar_directorio del sistema para navegar a la carpeta seleccionada. Si es un archivo, se llama a la función abrir_archivo para permitir al usuario editar su contenido. Si es un acceso directo, se navega a la carpeta destino utilizando el alias extraído del nombre del acceso directo.
    # Si el elemento seleccionado es un acceso directo, se extrae el alias del nombre del elemento (que tiene el formato "alias → destino") y se utiliza para cambiar al directorio correspondiente.
    # Si ocurre algún error durante la ejecución de la acción (por ejemplo, si el archivo no se puede abrir), se muestra un mensaje de error al usuario.
    # Si el elemento seleccionado es una carpeta, se utiliza el método cambiar_directorio del sistema para navegar a la carpeta seleccionada. Si es un archivo, se llama a la función abrir_archivo para permitir al usuario editar su contenido. Si es un acceso directo, se navega a la carpeta destino utilizando el alias extraído del nombre del acceso directo.
    def doble_clic(self, _event=None):
        seleccionado = self._seleccionado()
        if not seleccionado:
            return
        tipo, nombre = seleccionado
        if tipo == "Carpeta":
            self._ejecutar(lambda: self.sistema.cambiar_directorio(nombre))
        elif tipo == "Archivo":
            self.abrir_archivo()
        elif tipo == "Acceso directo":
            alias = nombre.split(" → ")[0]
            self._ejecutar(lambda: self.sistema.cambiar_directorio(alias))

    # Función para eliminar un elemento seleccionado (archivo o carpeta) en la lista de contenido
    # Esta función verifica si hay un elemento seleccionado en la lista de contenido. Si no hay selección o si el elemento seleccionado no es un archivo o carpeta, se muestra un mensaje de información al usuario. Si hay un elemento seleccionado, se solicita confirmación al usuario antes de eliminarlo.
    # Si el usuario confirma la eliminación, se llama al método eliminar_elemento del sistema para eliminar el elemento seleccionado. La función actualizar_vista se llama después de la eliminación para reflejar los cambios en la interfaz gráfica.
    # Si el usuario cancela la eliminación, no se realizan cambios y la función retorna sin hacer nada. La función utiliza un bloque try-except para manejar cualquier excepción que pueda ocurrir durante la eliminación del elemento, mostrando un mensaje de error al usuario si es necesario.
    def eliminar(self):
        seleccionado = self._seleccionado()
        if not seleccionado or seleccionado[0] not in ("Archivo", "Carpeta"):
            messagebox.showinfo("Eliminar", "Selecciona un archivo o carpeta.")
            return
        tipo, nombre = seleccionado
        if not messagebox.askyesno("Confirmar eliminación", f"¿Enviar '{nombre}' a la papelera?"):
            return
        self._ejecutar(lambda: self.sistema.eliminar_elemento(nombre, tipo))

    # Función para restaurar los elementos eliminados de la papelera
    # Esta función llama al método restaurar_papelera del sistema para restaurar los elementos
    # eliminados de la papelera. La función actualizar_vista se llama después de la restauración para reflejar los cambios en la interfaz gráfica.
    def restaurar(self):
        self._ejecutar(self.sistema.restaurar_papelera)

    # Función para buscar un archivo por nombre exacto en la carpeta actual utilizando búsqueda binaria
    # Esta función solicita al usuario que ingrese el nombre exacto del archivo que desea buscar
    # en la carpeta actual. Si el usuario proporciona un nombre, se llama al método buscar_archivo_binario del sistema
    # para realizar la búsqueda. La función actualizar_vista se llama después de la búsqueda para reflejar los cambios en la interfaz gráfica.
    # Si el archivo se encuentra, se muestra un mensaje de información con el nombre y tamaño del archivo encontrado.
    # Si el archivo no se encuentra, se muestra un mensaje de información indicando que no se encontró el archivo en la carpeta actual. Si el usuario no proporciona un nombre, la función retorna sin hacer nada.
    def buscar(self):
        nombre = simpledialog.askstring("Búsqueda binaria", "Nombre exacto del archivo en esta carpeta:", parent=self)
        if not nombre:
            return
        encontrado = self.sistema.buscar_archivo_binario(nombre)
        self.actualizar_vista()
        if encontrado:
            messagebox.showinfo("Resultado", f"Encontrado: {encontrado.nombre}\nTamaño: {encontrado.tamanio} bytes")
        else:
            messagebox.showinfo("Resultado", "No se encontró el archivo en esta carpeta.")

    # Función para ordenar los archivos en la carpeta actual según un criterio especificado por el usuario
    # Esta función solicita al usuario que ingrese un criterio de ordenamiento, ya sea "nombre" o "tamanio". Si el usuario proporciona un criterio válido, se llama al método ordenar_archivos_burbuja del sistema para ordenar los archivos en la carpeta actual según el criterio especificado.
    # La función actualizar_vista se llama después de la ordenación para reflejar los cambios en la interfaz gráfica. Si el usuario no proporciona un criterio o proporciona un criterio inválido, la función retorna sin hacer nada.
    def ordenar(self):
        criterio = simpledialog.askstring("Ordenar archivos", "Escribe 'nombre' o 'tamanio':", initialvalue="nombre", parent=self)
        if criterio is None:
            return
        criterio = criterio.strip().lower()
        self._ejecutar(lambda: self.sistema.ordenar_archivos_burbuja(criterio))

    # Funciones para navegar entre carpetas, enviar archivos a impresión, procesar la cola de impresión, crear accesos directos y ver estructuras de datos
    # Estas funciones permiten al usuario navegar hacia atrás y adelante en el historial de navegación, subir un nivel en la jerarquía de carpetas, enviar archivos a la cola de impresión, procesar la cola de impresión, crear accesos directos a carpetas y ver las estructuras de datos utilizadas por el sistema.
    # Cada función realiza la acción correspondiente y luego actualiza la vista de la interfaz gráfica para reflejar los cambios realizados en el sistema.
    # La función ir_atras navega hacia atrás en el historial de navegación, la función ir_adelante navega hacia adelante, y la función subir permite al usuario subir un nivel en la jerarquía de carpetas. La función enviar_impresion envía un archivo seleccionado a la cola de impresión, mientras que la función procesar_impresion procesa el siguiente archivo en la cola de impresión.
    # La función crear_acceso permite al usuario crear un acceso directo a una carpeta específica, y la función ver_estructuras muestra las estructuras de datos utilizadas por el sistema, incluyendo el árbol de directorios, la pila de papelera, la cola de impresión y el historial de navegación.
    def ir_atras(self):
        if self.sistema.navegar_atras():
            self.actualizar_vista()

    # Función para navegar hacia adelante en el historial de navegación del sistema
    # Esta función verifica si es posible navegar hacia adelante en el historial de navegación del sistema.
    # Si es posible, se llama al método navegar_adelante del sistema para realizar la navegación hacia adelante y luego se actualiza la vista de la interfaz gráfica para reflejar los cambios realizados en el sistema.
    # Si no es posible navegar hacia adelante (por ejemplo, si ya se encuentra en la última carpeta visitada), la función retorna sin hacer nada.
    # La función ir_adelante permite al usuario avanzar en el historial de navegación, similar a la función ir_atras que permite retroceder en el historial.
    # En resumen, esta función facilita la navegación hacia adelante en la jerarquía de carpetas del sistema, mejorando la experiencia del usuario al explorar el sistema de archivos virtual.
    def ir_adelante(self):
        if self.sistema.navegar_adelante():
            self.actualizar_vista()

    # Función para subir un nivel en la jerarquía de carpetas del sistema
    # Esta función verifica si es posible subir un nivel en la jerarquía de carpetas del sistema.
    # Si es posible, se llama al método subir_directorio del sistema para realizar la acción de subir un nivel y luego se actualiza la vista de la interfaz gráfica para reflejar los cambios realizados en el sistema.
    # Si no es posible subir un nivel (por ejemplo, si ya se encuentra en la carpeta raíz), la función retorna sin hacer nada.
    # La función subir permite al usuario moverse hacia arriba en la estructura de carpetas del sistema, facilitando la navegación y exploración de los directorios.
    def subir(self):
        if self.sistema.subir_directorio():
            self.actualizar_vista()

    # Función para enviar un archivo seleccionado a la cola de impresión del sistema
    # Esta función verifica si hay un archivo seleccionado en la lista de contenido. Si no hay selección o si el elemento seleccionado no es un archivo, se muestra un mensaje de información al usuario.
    # Si hay un archivo seleccionado, se llama al método enviar_a_impresion del sistema para enviar el archivo a la cola de impresión. La función actualizar_vista se llama después de enviar el archivo para reflejar los cambios en la interfaz gráfica.
    # Si el usuario no selecciona un archivo o selecciona un elemento que no es un archivo, la función retorna sin hacer nada. La función enviar_impresion permite al usuario enviar archivos a la cola de impresión del sistema, facilitando la gestión de documentos para su impresión.   
    def enviar_impresion(self):
        seleccionado = self._seleccionado()
        if not seleccionado or seleccionado[0] != "Archivo":
            messagebox.showinfo("Impresión", "Selecciona un archivo.")
            return
        self._ejecutar(lambda: self.sistema.enviar_a_impresion(seleccionado[1]))

    # Función para procesar el siguiente archivo en la cola de impresión del sistema
    # Esta función llama al método procesar_impresion del sistema para procesar el siguiente archivo en la cola de impresión. Si hay un archivo en la cola, se muestra un mensaje de información con el nombre del archivo procesado y una vista previa de su contenido (los primeros 1000 caracteres).
    # La función actualizar_vista se llama después de procesar el archivo para reflejar los cambios en la interfaz gráfica. Si no hay archivos en la cola de impresión, se muestra un mensaje de información indicando que la cola está vacía.
    def procesar_impresion(self):
        def procesar():
            archivo = self.sistema.procesar_impresion()
            messagebox.showinfo("Cola de impresión", f"Procesado: {archivo.nombre}\n\nContenido:\n{archivo.contenido[:1000]}")
        self._ejecutar(procesar)

    # Función para crear un acceso directo a una carpeta específica en el sistema
    # Esta función obtiene la lista de subcarpetas en la carpeta actual del sistema.
    # Si no hay subcarpetas, se muestra un mensaje de información al usuario indicando que no hay subcarpetas disponibles para crear un acceso directo.
    # Si hay subcarpetas, se solicita al usuario que ingrese el nombre exacto de la carpeta destino para el acceso directo. Luego, se solicita al usuario que ingrese un alias para el acceso directo.
    # Si el usuario proporciona un nombre de carpeta destino y un alias, se llama al método crear_acceso_directo del sistema para crear el acceso directo. La función actualizar_vista se llama después de crear el acceso directo para reflejar los cambios en la interfaz gráfica.
    def crear_acceso(self):
        carpetas = list(self.sistema.actual.subcarpetas.keys())
        if not carpetas:
            messagebox.showinfo("Acceso directo", "No hay subcarpetas en esta ubicación.")
            return
        destino = simpledialog.askstring("Acceso directo", "Nombre exacto de la carpeta destino:\n" + ", ".join(carpetas), parent=self)
        if not destino:
            return
        alias = simpledialog.askstring("Acceso directo", "Nombre del alias:", parent=self)
        if not alias:
            return
        self._ejecutar(lambda: self.sistema.crear_acceso_directo(alias, destino))

    # Función para mostrar las estructuras de datos utilizadas por el sistema en una ventana separada
    # Esta función crea una ventana emergente que muestra las estructuras de datos utilizadas por el sistema, incluyendo el árbol de directorios, la pila de papelera, la cola de impresión y el historial de navegación.
    # La ventana contiene pestañas para cada estructura de datos, y cada pestaña muestra la información correspondiente en un área de texto. La función utiliza el método recorrido_preorden para mostrar el árbol de directorios en preorden, el método recorrido_por_niveles para mostrar el árbol en niveles (BFS), y muestra la pila de papelera, la cola de impresión y el historial de navegación en formato legible.
    def ver_estructuras(self):
        ventana = tk.Toplevel(self)
        ventana.title("Estructuras de datos | ArchiVirtual")
        ventana.geometry("760x570")
        pestañas = ttk.Notebook(ventana)
        pestañas.pack(fill="both", expand=True, padx=10, pady=10)
        vistas = [
            ("Árbol - Preorden", self.sistema.recorrido_preorden()),
            ("Árbol - Niveles (BFS)", self.sistema.recorrido_por_niveles()),
            ("Pila - Papelera", [f"{i+1}. {x['nombre_original']} ({x['tipo']})" for i, x in enumerate(reversed(self.sistema.papelera))] or ["Pila vacía"]),
            ("Cola - Impresión", [f"{i+1}. {a.nombre}" for i, a in enumerate(self.sistema.cola_impresion)] or ["Cola vacía"]),
            ("Lista doble - Historial", self._obtener_historial())
        ]
        for titulo, lineas in vistas:
            marco = ttk.Frame(pestañas, padding=8)
            pestañas.add(marco, text=titulo)
            texto = tk.Text(marco, wrap="none", font=("Consolas", 10), state="normal")
            texto.pack(fill="both", expand=True)
            texto.insert("1.0", "\n".join(lineas))
            texto.configure(state="disabled")

    # Función para obtener el historial de navegación del sistema en formato legible
    # Esta función recorre la lista doblemente enlazada que representa el historial de navegación del sistema y construye una lista de elementos que representan cada carpeta visitada. La carpeta actual se indica con un prefijo "→ ", mientras que las demás carpetas se muestran sin prefijo.
    # Si el historial está vacío, la función retorna una lista con un solo elemento que indica que el historial está vacío. La función se utiliza para mostrar el historial de navegación en la pestaña correspondiente de la ventana de estructuras de datos.
    def _obtener_historial(self):
        nodo = self.sistema.historial.actual
        while nodo.anterior:
            nodo = nodo.anterior
        elementos = []
        while nodo:
            prefijo = "→ " if nodo is self.sistema.historial.actual else "  "
            elementos.append(prefijo + ("Master" if nodo.carpeta is self.sistema.raiz else nodo.carpeta.nombre))
            nodo = nodo.siguiente
        return elementos or ["Historial vacío"]

    # Función para ejecutar una operación y actualizar la vista de la interfaz gráfica
    # Esta función recibe una operación (función) como argumento y la ejecuta dentro de un bloque try-except para manejar posibles excepciones. Si la operación se ejecuta correctamente, se llama a la función actualizar_vista para reflejar los cambios en la interfaz gráfica.
    # Si ocurre una excepción durante la ejecución de la operación, se muestra un mensaje de error al usuario utilizando un cuadro de diálogo de error. Esta función se utiliza para encapsular la ejecución de operaciones que pueden modificar el estado del sistema y garantizar que la interfaz gráfica se mantenga actualizada y que los errores se manejen adecuadamente. 
    def _ejecutar(self, operacion):
        try:
            operacion()
            self.actualizar_vista()
        except Exception as exc:
            messagebox.showerror("ArchiVirtual", str(exc), parent=self)
