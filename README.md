# Network Assistant (Python)

Herramienta de consola para diagnosticar la red y el equipo en Windows, pensada para soporte TI: reúne en un menú los comandos que se usan a diario y agrega un **diagnóstico automático por capas** y un **reporte HTML**.

## Funciones

| Opción | Qué hace |
| --- | --- |
| 1. Información del PC | Sistema, CPU, RAM, discos, tiempo encendido |
| 2. Información de red | Adaptadores (IPv4/IPv6/MAC/velocidad), gateway, DNS e IP pública; detecta IP APIPA y CGNAT |
| 3. Ping | Pérdida de paquetes y latencia media |
| 4. Traceroute | Ruta hasta el destino e interpretación de saltos sin respuesta |
| 5. DNS Lookup | Resolución con tiempo de respuesta, búsqueda inversa (PTR) y registros MX, NS, TXT… |
| 6. Tabla ARP | Equipos vistos en la red local |
| 7. Tabla de rutas | Rutas IPv4 del equipo |
| 8. Diagnóstico automático | Prueba adaptador → gateway → internet → DNS → HTTPS y dice **qué capa falla y qué hacer** |
| 9. Reporte HTML | Guarda todo en `reports/` y lo abre en el navegador |
| 10. Prueba de puertos TCP | Revisa puertos comunes o los que indiques |

## Uso

Doble clic en `NetworkAssistant.cmd` (crea el entorno e instala `psutil` la primera vez), o:

```bash
pip install -r requirements.txt
python main.py             # menú
python main.py --reporte   # solo genera el reporte (para tareas programadas)
```

## Conceptos aplicados

Troubleshooting por capas (modelo OSI/TCP-IP), ICMP, DNS, enrutamiento, ARP, sockets TCP, parseo de salidas de comandos en Windows en español e inglés, validación de entradas para evitar inyección de comandos y reportes HTML.
