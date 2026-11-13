# Importamos las librerías necesarias
# os: para interactuar con el sistema operativo (navegar directorios, listar archivos, etc.)
# shutil: para operaciones de alto nivel con archivos y directorios (copiar, mover,
import os
import shutil

def mostrar_menu():
    print("\n--- GESTOR DE ARCHIVOS ---")
    print(f"Directorio actual: {os.getcwd()}")
    print("1. Listar archivos y carpetas")
    print("2. Cambiar de directorio (cd)")
    print("3. Crear carpeta")
    print("4. Crear o editar archivo de texto")
    print("5. Leer archivo de texto")
    print("6. Eliminar archivo o carpeta")
    print("7. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()
        
        try:
            if opcion == "1":
                # Listar contenido
                elementos = os.listdir('.')
                print("\nContenido:")
                for el in elementos:
                    tipo = "[DIR]" if os.path.isdir(el) else "[FILE]"
                    print(f"  {tipo} {el}")
                    
            elif opcion == "2":
                # Cambiar de directorio
                nueva_ruta = input("Introduce la ruta o '..' para retroceder: ")
                os.chdir(nueva_ruta)
                
            elif opcion == "3":
                # Crear carpeta
                nombre = input("Nombre de la nueva carpeta: ")
                os.makedirs(nombre, exist_ok=True)
                print(f"Carpeta '{nombre}' creada con éxito.")
                
            elif opcion == "4":
                # Crear/Escribir archivo
                nombre = input("Nombre del archivo (ej. notas.txt): ")
                contenido = input("Escribe el contenido del archivo:\n")
                with open(nombre, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                print("Archivo guardado correctamente.")
                
            elif opcion == "5":
                # Leer archivo
                nombre = input("Nombre del archivo a leer: ")
                if os.path.exists(nombre) and os.path.isfile(nombre):
                    with open(nombre, 'r', encoding='utf-8') as f:
                        print("\n--- Contenido ---")
                        print(f.read())
                        print("-----------------")
                else:
                    print("El archivo no existe.")
                    
            elif opcion == "6":
                # Eliminar
                nombre = input("Nombre del archivo o carpeta a eliminar: ")
                if os.path.isdir(nombre):
                    shutil.rmtree(nombre) # Borra carpetas con contenido
                    print(f"Carpeta '{nombre}' eliminada.")
                elif os.path.isfile(nombre):
                    os.remove(nombre) # Borra archivos
                    print(f"Archivo '{nombre}' eliminado.")
                else:
                    print("No se encontró el elemento.")
                    
            elif opcion == "7":
                print("¡Saliendo del gestor de archivos. Adiós!")
                break
            else:
                print("Opción inválida, intenta de nuevo.")
                
        except Exception as e:
            print(f"[ERROR]: {e}")

if __name__ == "__main__":
    main()