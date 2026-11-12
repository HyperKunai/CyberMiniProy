import sys
import argon2.exceptions
if not hasattr(argon2.exceptions, "InvalidHashError"):
    argon2.exceptions.InvalidHashError = getattr(argon2.exceptions, "InvalidHash", Exception)

import json
from pathlib import Path
from seguridad import verificar_clave
from datetime import datetime

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "inventario.json"
USUARIOS = RAIZ / "usuarios.json"
LOG = RAIZ / "auditoria.jsonl"


def cargar_inventario():
    if not DATOS.exists():
        print("Error: El archivo de inventario no existe.")
        return None
    try:
        return json.loads(DATOS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("Error: El archivo de inventario contiene datos JSON inválidos.")
        return None


def guardar_inventario(productos):
    DATOS.write_text(json.dumps(productos, indent=2, ensure_ascii=False), encoding="utf-8")


def registrar_evento(usuario, accion, resultado, **detalles):
    evento = {
        "fecha_hora": datetime.now().isoformat() if 'datetime' in globals() else "",
        "usuario": usuario if usuario else "sin_sesion",
        "accion": accion,
        "resultado": resultado
    }
    for clave, valor in detalles.items():
        evento[clave] = valor

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")


def autenticar(nombre, clave):
    if not USUARIOS.exists():
        print("Error: El archivo de usuarios no existe.")
        return None
    
    try:
        usuarios = json.loads(USUARIOS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("Error: El archivo de usuarios está corrupto.")
        return None

    for usuario in usuarios:
        if usuario["usuario"] == nombre:
            if usuario["clave"] == clave:
                registrar_evento(nombre, "login", "exitoso")
                return {"usuario": nombre, "rol": usuario["rol"]}
            else:
                registrar_evento(nombre, "login", "fallido", motivo="password_incorrecto")
                print("Credenciales incorrectas.")
                return None

    registrar_evento(nombre, "login", "fallido", motivo="usuario_inexistente")
    print("Credenciales incorrectas.")
    return None

def consultar_inventario(sesion):
    if not sesion:
        print("Acceso denegado: Se requiere iniciar sesión.")
        registrar_evento("sin_sesion", "consultar", "rechazado", motivo="sin_sesion")
        return False

    productos = cargar_inventario()
    if productos is None:
        return False
        
    for producto in productos:
        print(producto["id"], producto["nombre"], producto["cantidad"])
    return True


def modificar_cantidad(sesion, identificador, entrada):
    if not sesion:
        print("Acceso denegado: Se requiere iniciar sesión.")
        registrar_evento("sin_sesion", "modificar", "rechazado", motivo="sin_sesion")
        return False

    if sesion.get("rol") != "admin":
        print(f"Acceso denegado: El usuario '{sesion['usuario']}' con rol '{sesion['rol']}' no tiene permisos para modificar inventario.")
        registrar_evento(sesion["usuario"], "modificar", "rechazado", motivo="permiso_insuficiente")
        return False

    try:
        cantidad = int(entrada)
    except ValueError:
        print("Error: La cantidad debe ser un número entero válido.")
        return False

    if not (0 <= cantidad <= 1000):
        print("Error: La cantidad debe estar entre 0 y 1000.")
        return False

    productos = cargar_inventario()
    if productos is None:
        return False

    for producto in productos:
        if producto["id"] == identificador:
            anterior = producto["cantidad"]
            producto["cantidad"] = cantidad
            guardar_inventario(productos)
            registrar_evento(
                sesion["usuario"], "modificar", "exitoso",
                producto=identificador, anterior=anterior, nueva=cantidad
            )
            print("Cantidad actualizada.")
            return True

    print(f"Error: El identificador '{identificador}' no existe en el inventario.")
    return False

def main():
    print("Inventario académico — BASE CON DEBILIDADES")
    print("Estudiante:", input("Escriba su nombre: "))
    sesion = None
    while True:
        if sesion is None:
            nombre = input("Usuario (o salir): ")
            if nombre == "salir":
                break
            sesion = autenticar(nombre, input("Contraseña de prueba: "))
            continue
        print("1. Consultar | 2. Modificar | 3. Cerrar sesión | 0. Salir")
        opcion = input("Opción: ")
        if opcion == "1":
            consultar_inventario(sesion)
        elif opcion == "2":
            identificador = input("ID del producto: ")
            entrada = input("Nueva cantidad: ")
            modificar_cantidad(sesion, identificador, entrada)
        elif opcion == "3":
            sesion = None
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()