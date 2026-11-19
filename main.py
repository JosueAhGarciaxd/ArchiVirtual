from pathlib import Path
from core.sistema import ArchiVirtualSystem
from interfaz.ventana_principal import VentanaPrincipal

def main():
    base = Path(__file__).resolve().parent
    ruta_master = base / "almacenamiento" / "Master"
    sistema = ArchiVirtualSystem(ruta_master)
    app = VentanaPrincipal(sistema)
    app.mainloop()

if __name__ == "__main__":
    main()
