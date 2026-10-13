"""Utilidades comunes: consola, colores, ejecución de comandos del sistema."""

import os
import platform
import subprocess

ES_WINDOWS = platform.system() == "Windows"

# Activa los colores ANSI en la consola de Windows 10/11
if ES_WINDOWS:
    os.system("")


class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    ERR = "\033[91m"
    INFO = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    END = "\033[0m"


def limpiar():
    os.system("cls" if ES_WINDOWS else "clear")


def pausa():
    input(f"\n{C.DIM}Presiona ENTER para volver al menú...{C.END}")


def titulo(texto):
    print("\n" + "=" * 56)
    print(f"{C.BOLD}{texto.center(56)}{C.END}")
    print("=" * 56)


def subtitulo(texto):
    print("\n" + "-" * 56)
    print(f"{texto.center(56)}")
    print("-" * 56)


def fila(etiqueta, valor):
    print(f"{etiqueta:<18}: {valor}")


def estado(ok, texto_ok="OK", texto_mal="FALLA"):
    if ok is None:
        return f"{C.WARN}N/A{C.END}"
    return f"{C.OK}{texto_ok}{C.END}" if ok else f"{C.ERR}{texto_mal}{C.END}"


def ejecutar(comando, timeout=60):
    """Ejecuta un comando y devuelve (codigo, salida) como texto legible.
    En Windows los comandos de consola escriben en la página de códigos OEM (cp850)."""
    codificacion = "oem" if ES_WINDOWS else "utf-8"
    try:
        r = subprocess.run(comando, capture_output=True, timeout=timeout,
                           shell=isinstance(comando, str))
        salida = (r.stdout or b"") + (r.stderr or b"")
        return r.returncode, salida.decode(codificacion, errors="replace")
    except subprocess.TimeoutExpired:
        return -1, "Tiempo de espera agotado."
    except FileNotFoundError:
        return -1, f"Comando no encontrado: {comando[0] if isinstance(comando, list) else comando}"


def powershell(script, timeout=30):
    return ejecutar(["powershell", "-NoProfile", "-Command", script], timeout=timeout)


def objetivo_valido(texto):
    """Evita que se inyecten comandos: solo IPs, dominios y nombres de host."""
    import re
    return bool(re.fullmatch(r"[A-Za-z0-9.\-:_]{1,253}", texto or ""))
