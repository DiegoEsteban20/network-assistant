"""Información de red: adaptadores, gateway, DNS e IP pública."""

import json
import re
import socket
import urllib.request

import psutil

from .utils import ES_WINDOWS, titulo, subtitulo, fila, pausa, estado, ejecutar, powershell

AF_LINK = getattr(psutil, "AF_LINK", -1)


def obtener_adaptadores():
    stats = psutil.net_if_stats()
    lista = []
    for nombre, direcciones in psutil.net_if_addrs().items():
        st = stats.get(nombre)
        a = {"nombre": nombre, "conectado": bool(st and st.isup),
             "velocidad": st.speed if st else 0, "ipv4": None, "mascara": None,
             "ipv6": None, "mac": None}
        for d in direcciones:
            if d.family == socket.AF_INET:
                a["ipv4"], a["mascara"] = d.address, d.netmask
            elif d.family == socket.AF_INET6 and not a["ipv6"]:
                a["ipv6"] = d.address.split("%")[0]
            elif d.family == AF_LINK:
                a["mac"] = d.address
        if a["ipv4"] and a["ipv4"].startswith("127."):
            continue  # loopback
        lista.append(a)
    # Primero los conectados con IP
    return sorted(lista, key=lambda x: (not x["conectado"], x["ipv4"] is None, x["nombre"]))


def obtener_gateway():
    if ES_WINDOWS:
        _, salida = ejecutar(["route", "print", "-4"])
        m = re.search(r"^\s*0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", salida, re.M)
    else:
        _, salida = ejecutar(["ip", "route"])
        m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", salida)
    return m.group(1) if m else None


def obtener_dns():
    if ES_WINDOWS:
        _, salida = powershell("(Get-DnsClientServerAddress -AddressFamily IPv4 | "
                               "Where-Object ServerAddresses).ServerAddresses | ConvertTo-Json")
        try:
            datos = json.loads(salida.strip() or "[]")
            datos = [datos] if isinstance(datos, str) else datos
            return list(dict.fromkeys(datos))
        except json.JSONDecodeError:
            return re.findall(r"\d+\.\d+\.\d+\.\d+", salida)
    try:
        with open("/etc/resolv.conf") as f:
            return re.findall(r"^nameserver\s+(\S+)", f.read(), re.M)
    except OSError:
        return []


def obtener_ip_publica(timeout=5):
    for url in ("https://api.ipify.org", "https://ifconfig.me/ip"):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                ip = r.read().decode().strip()
                if re.fullmatch(r"[\d.:a-fA-F]+", ip):
                    return ip
        except Exception:
            continue
    return None


def tipo_ip(ip):
    if not ip:
        return ""
    if ip.startswith("169.254."):
        return "APIPA: no recibió IP del DHCP"
    if re.match(r"^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)", ip):
        return "privada"
    if re.match(r"^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.", ip):
        return "CGNAT"
    return "pública"


def network_info():
    titulo("INFORMACIÓN DE RED")
    fila("Hostname", socket.gethostname())
    gw = obtener_gateway()
    fila("Gateway", gw or "No encontrado")
    dns = obtener_dns()
    fila("Servidores DNS", ", ".join(dns) if dns else "No encontrados")
    print("Consultando IP pública...", end="\r")
    pub = obtener_ip_publica()
    fila("IP pública", f"{pub} ({tipo_ip(pub)})" if pub else "Sin acceso a internet")

    subtitulo("ADAPTADORES DE RED")
    for a in obtener_adaptadores():
        print(f"\nAdaptador: {a['nombre']}")
        fila("  Estado", estado(a["conectado"], "CONECTADO", "DESCONECTADO"))
        if a["velocidad"]:
            fila("  Velocidad", f"{a['velocidad']} Mbps")
        if a["ipv4"]:
            fila("  IPv4", f"{a['ipv4']} / {a['mascara']}  ({tipo_ip(a['ipv4'])})")
        if a["ipv6"]:
            fila("  IPv6", a["ipv6"])
        if a["mac"]:
            fila("  MAC", a["mac"])
    pausa()
