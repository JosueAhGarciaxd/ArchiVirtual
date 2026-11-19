import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path

class VentanaPrincipal(tk.Tk):
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

    def _construir_interfaz(self):
        encabezado = ttk.Frame(self, padding=(16, 12))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="ArchiVirtual", style="Titulo.TLabel").pack(side="left")
        ttk.Label(encabezado, text="Sistema de archivos virtual", style="Sub.TLabel").pack(side="left", padx=12)

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

        cuerpo = ttk.Panedwindow(self, orient="horizontal")
        cuerpo.pack(fill="both", expand=True, padx=12, pady=8)

        panel_izq = ttk.Frame(cuerpo, padding=6)
        panel_centro = ttk.Frame(cuerpo, padding=6)
        panel_der = ttk.Frame(cuerpo, padding=10)
        cuerpo.add(panel_izq, weight=1)
        cuerpo.add(panel_centro, weight=3)
        cuerpo.add(panel_der, weight=1)

        ttk.Label(panel_izq, text="DIRECTORIOS", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 7))
        self.arbol = ttk.Treeview(panel_izq, show="tree", selectmode="browse")
        self.arbol.pack(fill="both", expand=True)
        self.arbol.bind("<<TreeviewSelect>>", self._seleccion_arbol)
        self._ids_carpetas = {}

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

        self.estado_var = tk.StringVar()
        ttk.Label(self, textvariable=self.estado_var, relief="sunken", anchor="w", padding=(10, 5)).pack(fill="x", side="bottom")

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

    def _insertar_subcarpetas(self, padre_id, carpeta):
        for sub in sorted(carpeta.subcarpetas.values(), key=lambda x: x.nombre.lower()):
            iid = self.arbol.insert(padre_id, "end", text=f"📁 {sub.nombre}", open=(sub is self.sistema.actual))
            self._ids_carpetas[iid] = sub
            self._insertar_subcarpetas(iid, sub)

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

    def _seleccion_arbol(self, _event=None):
        seleccion = self.arbol.selection()
        if not seleccion:
            return
        carpeta = self._ids_carpetas.get(seleccion[0])
        if carpeta and carpeta is not self.sistema.actual:
            self.sistema.navegar_a(carpeta)
            self.actualizar_vista()

    def _seleccionado(self):
        seleccion = self.lista.selection()
        if not seleccion:
            return None
        valores = self.lista.item(seleccion[0], "values")
        return valores[0], valores[1]

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

    def crear_carpeta(self):
        nombre = simpledialog.askstring("Nueva carpeta", "Nombre de la carpeta:", parent=self)
        if nombre is None:
            return
        self._ejecutar(lambda: self.sistema.crear_carpeta(nombre))

    def crear_archivo(self):
        nombre = simpledialog.askstring("Nuevo archivo", "Nombre (por ejemplo notas.txt):", parent=self)
        if nombre is None:
            return
        contenido = self._dialogo_contenido("Contenido inicial del archivo")
        if contenido is None:
            return
        self._ejecutar(lambda: self.sistema.crear_archivo(nombre, contenido))

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

        def aceptar(_event=None):
            resultado["contenido"] = caja.get("1.0", "end-1c")
            ventana.destroy()
            return "break"

        def cancelar(_event=None):
            ventana.destroy()
            return "break"

        ttk.Button(pie, text="Cancelar", command=cancelar).pack(side="right", padx=(6, 0))
        ttk.Button(pie, text="Guardar", command=aceptar).pack(side="right")

        ventana.protocol("WM_DELETE_WINDOW", cancelar)
        ventana.bind("<Control-s>", aceptar)
        ventana.bind("<Control-S>", aceptar)
        caja.focus_set()

        self.wait_window(ventana)
        return resultado["contenido"]

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

    def eliminar(self):
        seleccionado = self._seleccionado()
        if not seleccionado or seleccionado[0] not in ("Archivo", "Carpeta"):
            messagebox.showinfo("Eliminar", "Selecciona un archivo o carpeta.")
            return
        tipo, nombre = seleccionado
        if not messagebox.askyesno("Confirmar eliminación", f"¿Enviar '{nombre}' a la papelera?"):
            return
        self._ejecutar(lambda: self.sistema.eliminar_elemento(nombre, tipo))

    def restaurar(self):
        self._ejecutar(self.sistema.restaurar_papelera)

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

    def ordenar(self):
        criterio = simpledialog.askstring("Ordenar archivos", "Escribe 'nombre' o 'tamanio':", initialvalue="nombre", parent=self)
        if criterio is None:
            return
        criterio = criterio.strip().lower()
        self._ejecutar(lambda: self.sistema.ordenar_archivos_burbuja(criterio))

    def ir_atras(self):
        if self.sistema.navegar_atras():
            self.actualizar_vista()

    def ir_adelante(self):
        if self.sistema.navegar_adelante():
            self.actualizar_vista()

    def subir(self):
        if self.sistema.subir_directorio():
            self.actualizar_vista()

    def enviar_impresion(self):
        seleccionado = self._seleccionado()
        if not seleccionado or seleccionado[0] != "Archivo":
            messagebox.showinfo("Impresión", "Selecciona un archivo.")
            return
        self._ejecutar(lambda: self.sistema.enviar_a_impresion(seleccionado[1]))

    def procesar_impresion(self):
        def procesar():
            archivo = self.sistema.procesar_impresion()
            messagebox.showinfo("Cola de impresión", f"Procesado: {archivo.nombre}\n\nContenido:\n{archivo.contenido[:1000]}")
        self._ejecutar(procesar)

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

    def _ejecutar(self, operacion):
        try:
            operacion()
            self.actualizar_vista()
        except Exception as exc:
            messagebox.showerror("ArchiVirtual", str(exc), parent=self)
