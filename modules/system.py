"""Información del equipo: sistema operativo, CPU, RAM y discos."""

import getpass
import platform
import socket
from datetime import datetime

import psutil

from .utils import titulo, subtitulo, fila, pausa


def obtener_info_sistema():
    ram = psutil.virtual_memory()
    arranque = datetime.fromtimestamp(psutil.boot_time())
    discos = []
    for p in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(p.mountpoint)
        except (PermissionError, OSError):
            continue
        discos.append({
            "unidad": p.mountpoint, "sistema": p.fstype,
            "total_gb": u.total / 1024 ** 3, "usado_gb": u.used / 1024 ** 3,
            "libre_gb": u.free / 1024 ** 3, "uso_pct": u.percent,
        })
    return {
        "hostname": socket.gethostname(),
        "usuario": getpass.getuser(),
        "sistema": f"{platform.system()} {platform.release()}",
        "version": platform.version(),
        "arquitectura": platform.machine(),
        "procesador": platform.processor() or "No informado",
        "cpu_uso": psutil.cpu_percent(interval=1),
        "cpu_nucleos": psutil.cpu_count(logical=False),
        "cpu_hilos": psutil.cpu_count(logical=True),
        "ram_total_gb": ram.total / 1024 ** 3,
        "ram_usada_gb": ram.used / 1024 ** 3,
        "ram_libre_gb": ram.available / 1024 ** 3,
        "ram_pct": ram.percent,
        "encendido_desde": arranque.strftime("%d/%m/%Y %H:%M"),
        "discos": discos,
    }


def system_info():
    i = obtener_info_sistema()
    titulo("INFORMACIÓN DEL PC")
    fila("Hostname", i["hostname"])
    fila("Usuario", i["usuario"])
    fila("Sistema", i["sistema"])
    fila("Versión", i["version"])
    fila("Arquitectura", i["arquitectura"])
    fila("Procesador", i["procesador"])
    fila("Encendido desde", i["encendido_desde"])

    subtitulo("CPU Y MEMORIA")
    fila("Uso de CPU", f"{i['cpu_uso']}%")
    fila("Núcleos / hilos", f"{i['cpu_nucleos']} / {i['cpu_hilos']}")
    fila("RAM total", f"{i['ram_total_gb']:.2f} GB")
    fila("RAM en uso", f"{i['ram_usada_gb']:.2f} GB ({i['ram_pct']}%)")
    fila("RAM disponible", f"{i['ram_libre_gb']:.2f} GB")

    subtitulo("ALMACENAMIENTO")
    for d in i["discos"]:
        print(f"\nUnidad {d['unidad']} ({d['sistema']})")
        fila("  Total", f"{d['total_gb']:.2f} GB")
        fila("  Libre", f"{d['libre_gb']:.2f} GB")
        fila("  Uso", f"{d['uso_pct']}%")
    pausa()
