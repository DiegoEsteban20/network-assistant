"""Diagnóstico automático por capas: adaptador, gateway, internet, DNS y web."""

import time
import urllib.request

from .network import obtener_adaptadores, obtener_gateway, obtener_dns, tipo_ip
from .tools import hacer_ping, resolver
from .utils import C, titulo, pausa, estado

DESTINOS_INTERNET = ["8.8.8.8", "1.1.1.1"]
DOMINIO_PRUEBA = "www.google.com"
URL_PRUEBA = "https://www.google.com/generate_204"


def probar_web(url=URL_PRUEBA, timeout=6):
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status < 400, round((time.perf_counter() - inicio) * 1000)
    except Exception:
        return False, None


def ejecutar_diagnostico(mostrar=True):
    """Devuelve una lista de pasos {paso, ok, detalle} y un veredicto."""
    pasos = []

    def registrar(paso, ok, detalle):
        pasos.append({"paso": paso, "ok": ok, "detalle": detalle})
        if mostrar:
            print(f"  {estado(ok):<20} {paso}: {detalle}")

    if mostrar:
        print(f"\n{C.INFO}Revisando la conexión capa por capa...{C.END}\n")

    # 1. Adaptador
    activos = [a for a in obtener_adaptadores() if a["conectado"] and a["ipv4"]]
    if not activos:
        registrar("Adaptador de red", False, "Ningún adaptador conectado con IPv4")
    else:
        a = activos[0]
        apipa = a["ipv4"].startswith("169.254.")
        registrar("Adaptador de red", not apipa,
                  f"{a['nombre']} {a['ipv4']}/{a['mascara']}" + (" (APIPA: el DHCP no respondió)" if apipa else ""))

    # 2. Gateway
    gw = obtener_gateway()
    if not gw:
        registrar("Gateway", False, "No hay puerta de enlace predeterminada")
        r_gw = None
    else:
        r_gw = hacer_ping(gw, 4)
        registrar("Gateway", r_gw["ok"],
                  f"{gw} · pérdida {r_gw['perdida_pct']}%" + (f" · {r_gw['promedio_ms']} ms" if r_gw["promedio_ms"] is not None else ""))

    # 3. Internet por IP
    r_net = None
    for ip in DESTINOS_INTERNET:
        r_net = hacer_ping(ip, 4)
        if r_net["ok"]:
            break
    registrar("Internet (IP)", r_net["ok"],
              f"{ip} · pérdida {r_net['perdida_pct']}%" + (f" · {r_net['promedio_ms']} ms" if r_net["promedio_ms"] is not None else ""))

    # 4. DNS
    dns = obtener_dns()
    ips, ms = resolver(DOMINIO_PRUEBA)
    registrar("DNS", bool(ips),
              (f"{DOMINIO_PRUEBA} -> {ips[0]} en {ms} ms" if ips else f"No resuelve {DOMINIO_PRUEBA}") +
              (f" · servidores: {', '.join(dns)}" if dns else ""))
    dns_cgnat = [d for d in dns if tipo_ip(d) == "CGNAT"]

    # 5. Web (HTTPS)
    ok_web, ms_web = probar_web()
    registrar("Navegación HTTPS", ok_web, f"respuesta en {ms_web} ms" if ok_web else "no se pudo abrir una página HTTPS")

    # Veredicto: la primera capa que falla es la causa más probable
    veredicto, consejo = "Conexión OK", "Todas las pruebas pasaron."
    if not activos:
        veredicto, consejo = "Sin conexión física o WiFi", "Revisa el cable o la conexión WiFi y que el adaptador esté habilitado."
    elif activos[0]["ipv4"].startswith("169.254."):
        veredicto, consejo = "Sin IP del DHCP", "Reinicia el router o ejecuta: ipconfig /release y luego ipconfig /renew."
    elif not r_net["ok"] and ok_web:
        veredicto, consejo = "Conexión OK (ping bloqueado)", "La navegación funciona; esta red bloquea ICMP, por eso el ping falla."
    elif (not gw or (r_gw and not r_gw["ok"])) and not r_net["ok"]:
        veredicto, consejo = "No llega al router", "Revisa el cable/WiFi, que el router esté encendido y que el adaptador tenga la puerta de enlace correcta."
    elif not r_net["ok"]:
        veredicto, consejo = "El router no tiene salida a internet", "Revisa las luces del módem/ONT o llama a tu proveedor."
    elif not ips:
        veredicto, consejo = "Falla de DNS", "Hay internet pero no resuelve nombres. Prueba DNS 8.8.8.8 y 1.1.1.1 en el adaptador."
    elif not ok_web:
        veredicto, consejo = "Navegación bloqueada", "Hay DNS e internet, pero HTTPS falla: revisa proxy, firewall o antivirus."
    elif r_net["perdida_pct"] >= 25 or (r_net["promedio_ms"] or 0) > 150:
        veredicto, consejo = "Conexión inestable", "Hay pérdida de paquetes o latencia alta. Prueba por cable y revisa quién está usando la red."
    if dns_cgnat and veredicto.startswith("Conexión OK"):
        consejo += f" Ojo: tu DNS {dns_cgnat[0]} está en rango CGNAT; si fallan sitios puntuales, usa DNS públicos."

    if mostrar:
        color = C.OK if veredicto.startswith("Conexión OK") else C.ERR
        print(f"\n{C.BOLD}Diagnóstico:{C.END} {color}{veredicto}{C.END}")
        print(f"{C.BOLD}Qué hacer:{C.END} {consejo}")
    return {"pasos": pasos, "veredicto": veredicto, "consejo": consejo}


def diagnostico_automatico():
    titulo("DIAGNÓSTICO AUTOMÁTICO")
    ejecutar_diagnostico(mostrar=True)
    pausa()
