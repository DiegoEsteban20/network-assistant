"""Network Assistant: herramienta de consola para diagnóstico de red y del equipo."""

import sys

from modules.utils import C, limpiar
from modules.system import system_info
from modules.network import network_info
from modules.tools import ping, traceroute, dns_lookup, tabla_arp, tabla_rutas, test_puertos
from modules.diagnostics import diagnostico_automatico
from modules.report import generar_reporte_menu, generar_reporte

VERSION = "2.0"

OPCIONES = {
    "1": ("Información del PC", system_info),
    "2": ("Información de red", network_info),
    "3": ("Ping", ping),
    "4": ("Traceroute", traceroute),
    "5": ("DNS Lookup", dns_lookup),
    "6": ("Tabla ARP", tabla_arp),
    "7": ("Tabla de rutas", tabla_rutas),
    "8": ("Diagnóstico automático", diagnostico_automatico),
    "9": ("Generar reporte HTML", generar_reporte_menu),
    "10": ("Prueba de puertos TCP", test_puertos),
}


def menu():
    while True:
        limpiar()
        print("=" * 50)
        print(f"{C.BOLD}{f'NETWORK ASSISTANT v{VERSION}'.center(50)}{C.END}")
        print("=" * 50)
        print()
        for clave, (texto, _) in OPCIONES.items():
            print(f"[{clave}] {texto}")
        print("[0] Salir\n")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "0":
            print("\nSaliendo de Network Assistant...")
            break
        if opcion in OPCIONES:
            try:
                OPCIONES[opcion][1]()
            except KeyboardInterrupt:
                print("\nCancelado.")
            except Exception as e:  # que un error no cierre el programa
                print(f"\n{C.ERR}Error: {e}{C.END}")
                input("\nPresiona ENTER para continuar...")
        else:
            input(f"\n{C.ERR}Opción incorrecta.{C.END} Presiona ENTER...")


if __name__ == "__main__":
    # Modo sin menú: python main.py --reporte (útil para tareas programadas)
    if "--reporte" in sys.argv:
        ruta, d = generar_reporte(abrir=False)
        print(f"{d['veredicto']} -> {ruta}")
    else:
        try:
            menu()
        except KeyboardInterrupt:
            print("\nSaliendo...")
