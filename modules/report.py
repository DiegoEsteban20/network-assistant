"""Genera un reporte HTML con la información del PC, la red y el diagnóstico."""

import html
import os
import webbrowser
from datetime import datetime

from .diagnostics import ejecutar_diagnostico
from .network import obtener_adaptadores, obtener_gateway, obtener_dns, obtener_ip_publica, tipo_ip
from .system import obtener_info_sistema
from .utils import C, titulo, pausa

CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")

CSS = """
body{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;color:#1f2937;background:#f8fafc}
h1{color:#0f3d6e;margin-bottom:4px} .sub{color:#64748b;margin-top:0}
h2{color:#0f3d6e;border-bottom:2px solid #cbd5e1;padding-bottom:4px;margin-top:28px}
table{border-collapse:collapse;width:100%;background:#fff} td,th{border:1px solid #e2e8f0;padding:6px 10px;text-align:left}
th{background:#eef2f7} .ok{color:#15803d;font-weight:600} .mal{color:#b91c1c;font-weight:600}
.veredicto{padding:12px 16px;border-radius:8px;font-size:1.05em} .v-ok{background:#dcfce7} .v-mal{background:#fee2e2}
"""


def _e(x):
    return html.escape(str(x if x is not None else "-"))


def _tabla(filas, encabezado=None):
    h = "<table>"
    if encabezado:
        h += "<tr>" + "".join(f"<th>{_e(c)}</th>" for c in encabezado) + "</tr>"
    for f in filas:
        h += "<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>"
    return h + "</table>"


def generar_reporte(abrir=True):
    os.makedirs(CARPETA, exist_ok=True)
    print("\nRecolectando información del equipo...")
    s = obtener_info_sistema()
    print("Recolectando información de red...")
    gw, dns, pub = obtener_gateway(), obtener_dns(), obtener_ip_publica()
    adaptadores = obtener_adaptadores()
    print("Ejecutando diagnóstico...")
    d = ejecutar_diagnostico(mostrar=False)

    ahora = datetime.now()
    ok_global = d["veredicto"].startswith("Conexión OK")
    partes = [f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Reporte de red - {_e(s['hostname'])}</title>"
              f"<style>{CSS}</style></head><body>",
              f"<h1>Reporte de red · {_e(s['hostname'])}</h1><p class='sub'>Generado el {ahora:%d/%m/%Y %H:%M} por Network Assistant</p>",
              f"<div class='veredicto {'v-ok' if ok_global else 'v-mal'}'><b>Diagnóstico:</b> {_e(d['veredicto'])}<br>{_e(d['consejo'])}</div>",
              "<h2>Diagnóstico por capas</h2>",
              _tabla([[_e(p["paso"]), f"<span class='{'ok' if p['ok'] else 'mal'}'>{'OK' if p['ok'] else 'FALLA'}</span>", _e(p["detalle"])]
                      for p in d["pasos"]], ["Prueba", "Estado", "Detalle"]),
              "<h2>Red</h2>",
              _tabla([["Gateway", _e(gw)], ["Servidores DNS", _e(", ".join(dns) or "-")],
                      ["IP pública", _e(f"{pub} ({tipo_ip(pub)})" if pub else "Sin acceso")]]),
              "<h2>Adaptadores</h2>",
              _tabla([[_e(a["nombre"]), "<span class='ok'>Conectado</span>" if a["conectado"] else "<span class='mal'>Desconectado</span>",
                       _e(f"{a['ipv4']}/{a['mascara']}" if a["ipv4"] else "-"), _e(a["mac"]),
                       _e(f"{a['velocidad']} Mbps" if a["velocidad"] else "-")] for a in adaptadores],
                     ["Adaptador", "Estado", "IPv4", "MAC", "Velocidad"]),
              "<h2>Equipo</h2>",
              _tabla([["Sistema", _e(s["sistema"])], ["Procesador", _e(s["procesador"])],
                      ["CPU", _e(f"{s['cpu_uso']}% · {s['cpu_nucleos']} núcleos / {s['cpu_hilos']} hilos")],
                      ["RAM", _e(f"{s['ram_usada_gb']:.1f} de {s['ram_total_gb']:.1f} GB ({s['ram_pct']}%)")],
                      ["Encendido desde", _e(s["encendido_desde"])]]),
              "<h2>Discos</h2>",
              _tabla([[_e(x["unidad"]), _e(f"{x['total_gb']:.1f} GB"), _e(f"{x['libre_gb']:.1f} GB"), _e(f"{x['uso_pct']}%")]
                      for x in s["discos"]], ["Unidad", "Total", "Libre", "Uso"]),
              "</body></html>"]
    ruta = os.path.join(CARPETA, f"Reporte_{s['hostname']}_{ahora:%Y-%m-%d_%H%M%S}.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("".join(partes))
    if abrir:
        webbrowser.open("file:///" + ruta.replace("\\", "/"))
    return ruta, d


def generar_reporte_menu():
    titulo("GENERAR REPORTE")
    ruta, d = generar_reporte()
    print(f"\n{C.OK}Reporte guardado en:{C.END} {ruta}")
    print(f"{C.BOLD}Diagnóstico:{C.END} {d['veredicto']}")
    pausa()
