# Importaciones de módulos y clases necesarias para la ejecución del programa
# pathlib: para manejar rutas de archivos y directorios
# core.sistema: para importar la clase ArchiVirtualSystem que gestiona la lógica del sistema
# interfaz.ventana_principal: para importar la clase VentanaPrincipal que maneja la interfaz gráfica de usuario
from pathlib import Path
from core.sistema import ArchiVirtualSystem
from interfaz.ventana_principal import VentanaPrincipal

# Función principal que inicializa el sistema y la interfaz gráfica
def main():
    base = Path(__file__).resolve().parent
    ruta_master = base / "almacenamiento" / "Master"
    sistema = ArchiVirtualSystem(ruta_master)
    app = VentanaPrincipal(sistema)
    app.mainloop()

if __name__ == "__main__":
    main()
