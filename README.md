# Network Assistant (Python)

Herramienta de consola para diagnosticar la red y el equipo en Windows, pensada para soporte TI. Reúne en un solo menú los comandos que se usan a diario (ping, traceroute, DNS, ARP, rutas, puertos) y agrega un **diagnóstico automático por capas** que no solo muestra datos, sino que te dice **qué está fallando y qué hacer**, más un reporte HTML.

Funciona en Windows con Python 3.8 o superior. El lanzador crea el entorno e instala lo necesario la primera vez.

---

## Tabla de contenidos
- [Para qué sirve](#para-qué-sirve)
- [Funciones del menú](#funciones-del-menú)
- [El diagnóstico automático](#el-diagnóstico-automático)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Preguntas frecuentes](#preguntas-frecuentes)
- [Conceptos aplicados](#conceptos-aplicados)
- [Aviso](#aviso)

---

## Para qué sirve

En soporte TI te pasas el día abriendo la consola para ver la IP, hacer ping, revisar el DNS o mirar la tabla ARP. Esta herramienta junta todo eso en un menú ordenado, interpreta los resultados en palabras simples y, con una sola opción, hace un **diagnóstico de arriba a abajo**: revisa tu adaptador, la puerta de enlace, la salida a internet, el DNS y la navegación HTTPS, y te dice exactamente en qué punto se corta la conexión. Útil para resolver rápido y para aprender cómo se diagnostica una red por capas.

---

## Funciones del menú

| Opción | Qué hace |
| --- | --- |
| 1. Información del PC | Sistema, CPU, RAM, discos y tiempo encendido |
| 2. Información de red | Adaptadores (IPv4/IPv6/MAC/velocidad), gateway, DNS e IP pública; detecta IP APIPA y CGNAT |
| 3. Ping | Pérdida de paquetes y latencia media |
| 4. Traceroute | Ruta hasta el destino e interpretación de los saltos sin respuesta |
| 5. DNS Lookup | Resolución con tiempo de respuesta, búsqueda inversa (PTR) y registros MX, NS, TXT… |
| 6. Tabla ARP | Equipos vistos en la red local |
| 7. Tabla de rutas | Rutas IPv4 del equipo |
| 8. Diagnóstico automático | Prueba adaptador → gateway → internet → DNS → HTTPS y dice **qué capa falla y qué hacer** |
| 9. Reporte HTML | Guarda todo en `reports/` y lo abre en el navegador |
| 10. Prueba de puertos TCP | Revisa puertos comunes o los que indiques |

---

## El diagnóstico automático

La opción 8 es el corazón de la herramienta. Revisa la conexión en orden, de lo más cercano a lo más lejano:

1. **Adaptador de red** — ¿tienes una IP válida? (detecta APIPA `169.254.x.x` = no hay DHCP, y CGNAT.)
2. **Puerta de enlace** — ¿llegas a tu router?
3. **Internet** — ¿sales a la red? (ping a una IP pública conocida.)
4. **DNS** — ¿se resuelven los nombres? (distingue "no hay internet" de "el DNS está mal".)
5. **HTTPS** — ¿navegas de verdad? (por si el ping está bloqueado pero la web funciona.)

Al final entrega un veredicto claro, por ejemplo *"Conexión OK (ping bloqueado)"* o *"Llegas al router pero no a internet: problema del proveedor o del módem"*, en vez de dejarte interpretando números.

---

## Instalación

Doble clic en **`NetworkAssistant.cmd`**: crea un entorno virtual de Python e instala `psutil` la primera vez. Después abre el menú directamente.

Manual:

```bash
pip install -r requirements.txt
python main.py
```

---

## Uso

```bash
python main.py             # abre el menú interactivo
python main.py --reporte   # solo genera el reporte HTML (para tareas programadas)
```

---

## Estructura del proyecto

```
network-assistant/
├─ main.py                 # menú principal y modo --reporte
├─ modules/
│  ├─ utils.py             # ejecutar comandos, decodificación, validación de entradas
│  ├─ system.py            # información del equipo
│  ├─ network.py           # adaptadores, gateway, DNS, IP pública, tipo de IP
│  ├─ tools.py             # ping, traceroute, DNS, ARP, rutas, puertos
│  ├─ diagnostics.py       # diagnóstico automático por capas
│  └─ report.py            # genera el reporte HTML
├─ NetworkAssistant.cmd    # lanzador para Windows
├─ requirements.txt
└─ reports/                # se crea solo: reportes HTML
```

---

## Preguntas frecuentes

**¿Funciona en español y en inglés de Windows?** Sí. El parseo de los comandos entiende las salidas en ambos idiomas.

**¿Necesita permisos de administrador?** No para lo básico. Algunas lecturas pueden mostrar menos detalle sin permisos elevados.

**¿Puede dañar algo?** No cambia la configuración de red; solo consulta y muestra información.

---

## Conceptos aplicados

Troubleshooting por capas (modelo OSI / TCP-IP), ICMP, DNS, enrutamiento, ARP, sockets TCP, parseo de salidas de comandos en Windows en español e inglés, validación de entradas para evitar inyección de comandos, y generación de reportes HTML.

---

## Aviso

Úsalo en tu propio equipo o donde tengas autorización. Las pruebas de puertos contra equipos ajenos deben hacerse solo con permiso.
