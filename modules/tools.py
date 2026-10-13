"""Herramientas: ping, traceroute, DNS lookup, ARP, rutas y prueba de puertos."""

import re
import socket
import time

from .utils import ES_WINDOWS, C, titulo, fila, pausa, estado, ejecutar, objetivo_valido


def pedir_objetivo(mensaje="Ingrese IP o dominio: "):
    destino = input(f"\n{mensaje}").strip()
    if not objetivo_valido(destino):
        print(f"{C.ERR}Destino no válido. Usa solo una IP o un dominio (ej. 8.8.8.8 o google.com).{C.END}")
        return None
    return destino


# ------------------------------------------------------------------ PING
def hacer_ping(destino, cantidad=4, timeout_ms=1000):
    """Devuelve dict con ok, perdida_pct, promedio_ms, salida."""
    if ES_WINDOWS:
        cmd = ["ping", "-n", str(cantidad), "-w", str(timeout_ms), destino]
    else:
        cmd = ["ping", "-c", str(cantidad), "-W", str(max(1, timeout_ms // 1000)), destino]
    _, salida = ejecutar(cmd, timeout=cantidad * (timeout_ms / 1000) + 10)
    respuestas = len(re.findall(r"TTL=|ttl=", salida))
    perdida = round(100 * (cantidad - min(respuestas, cantidad)) / cantidad)
    tiempos = [float(t) for t in re.findall(r"(?:tiempo|time)[=<]\s*([\d.]+)\s*ms", salida, re.I)]
    promedio = round(sum(tiempos) / len(tiempos), 1) if tiempos else None
    return {"ok": respuestas > 0, "perdida_pct": perdida, "promedio_ms": promedio, "salida": salida}


def ping():
    destino = pedir_objetivo()
    if destino:
        cantidad = input("Cantidad de paquetes [4]: ").strip()
        cantidad = int(cantidad) if cantidad.isdigit() and 0 < int(cantidad) <= 100 else 4
        print(f"\nHaciendo ping a {destino}...\n")
        r = hacer_ping(destino, cantidad)
        print(r["salida"].strip())
        print()
        fila("Resultado", estado(r["ok"], "RESPONDE", "SIN RESPUESTA"))
        fila("Pérdida", f"{r['perdida_pct']}%")
        if r["promedio_ms"] is not None:
            fila("Latencia media", f"{r['promedio_ms']} ms")
    pausa()


# ------------------------------------------------------------------ TRACEROUTE
def hacer_traceroute(destino, saltos=20):
    if ES_WINDOWS:
        cmd = ["tracert", "-d", "-h", str(saltos), "-w", "800", destino]
    else:
        cmd = ["traceroute", "-n", "-m", str(saltos), "-w", "1", destino]
    return ejecutar(cmd, timeout=saltos * 4 + 15)[1]


def traceroute():
    destino = pedir_objetivo()
    if destino:
        print(f"\nTrazando ruta a {destino} (máx. 20 saltos, puede tardar)...\n")
        salida = hacer_traceroute(destino)
        print(salida.strip())
        perdidos = len(re.findall(r"\*\s+\*\s+\*", salida))
        if perdidos:
            print(f"\n{C.WARN}{perdidos} salto(s) no respondieron. Es normal si un router filtra ICMP; "
                  f"si todos los saltos finales fallan, el corte está después del último que respondió.{C.END}")
    pausa()


# ------------------------------------------------------------------ DNS
TIPOS_DNS = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]


def resolver(nombre):
    """Resolución con el DNS del sistema. Devuelve (ips, ms) o ([], None)."""
    inicio = time.perf_counter()
    try:
        infos = socket.getaddrinfo(nombre, None)
    except socket.gaierror:
        return [], None
    ms = round((time.perf_counter() - inicio) * 1000, 1)
    return list(dict.fromkeys(i[4][0] for i in infos)), ms


def dns_lookup():
    destino = pedir_objetivo("Ingrese dominio (o IP para búsqueda inversa): ")
    if destino:
        titulo(f"DNS LOOKUP: {destino}")
        if re.fullmatch(r"[\d.]+", destino):
            try:
                fila("Nombre (PTR)", socket.gethostbyaddr(destino)[0])
            except (socket.herror, socket.gaierror):
                fila("Nombre (PTR)", "Sin registro PTR")
        else:
            ips, ms = resolver(destino)
            fila("Resolución", estado(bool(ips), "OK", "NO RESUELVE"))
            if ips:
                fila("Tiempo", f"{ms} ms")
                for ip in ips:
                    fila("  Dirección", ip)
            tipo = input(f"\nVer otro tipo de registro {'/'.join(TIPOS_DNS)} (Enter = no): ").strip().upper()
            if tipo in TIPOS_DNS:
                print()
                print(ejecutar(["nslookup", f"-type={tipo}", destino], timeout=15)[1].strip())
    pausa()


# ------------------------------------------------------------------ ARP / RUTAS
def tabla_arp():
    titulo("TABLA ARP")
    print(ejecutar(["arp", "-a"] if ES_WINDOWS else ["ip", "neigh"])[1].strip())
    print(f"\n{C.DIM}Muestra qué IPs de tu red local se han comunicado con este equipo y su MAC.{C.END}")
    pausa()


def tabla_rutas():
    titulo("TABLA DE RUTAS")
    print(ejecutar(["route", "print", "-4"] if ES_WINDOWS else ["ip", "route"])[1].strip())
    pausa()


# ------------------------------------------------------------------ PUERTOS
PUERTOS_COMUNES = {21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP",
                   110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB", 3389: "RDP", 8080: "HTTP-alt"}


def probar_puerto(host, puerto, timeout=2):
    inicio = time.perf_counter()
    try:
        with socket.create_connection((host, puerto), timeout=timeout):
            return True, round((time.perf_counter() - inicio) * 1000, 1)
    except OSError:
        return False, None


def test_puertos():
    destino = pedir_objetivo("Ingrese IP o dominio del equipo: ")
    if destino:
        texto = input("Puertos separados por coma (Enter = puertos comunes): ").strip()
        if texto:
            puertos = [int(p) for p in re.findall(r"\d+", texto) if 0 < int(p) < 65536][:50]
        else:
            puertos = list(PUERTOS_COMUNES)
        titulo(f"PUERTOS TCP EN {destino}")
        for p in puertos:
            ok, ms = probar_puerto(destino, p)
            servicio = PUERTOS_COMUNES.get(p, "")
            extra = f"  ({ms} ms)" if ok else ""
            print(f"{p:>6}  {servicio:<9} {estado(ok, 'ABIERTO', 'cerrado/filtrado')}{extra}")
        print(f"\n{C.DIM}Usa esta prueba solo en equipos propios o con autorización.{C.END}")
    pausa()
