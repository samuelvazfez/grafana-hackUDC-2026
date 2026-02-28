"""Módulo de alertas hacia Discord para notificar condiciones IAD críticas."""
import logging
import json
import urllib.request
from datetime import datetime
from config import DISCORD_WEBHOOK_URL
from db import get_conn

log = logging.getLogger(__name__)

def check_and_send_alerts():
    """Busca scores críticos (IAD < 3) en las próximas 3 horas y envía alerta si no se envió recientemente."""
    if not DISCORD_WEBHOOK_URL:
        log.info("[Alertas] DISCORD_WEBHOOK_URL no configurado, omitiendo alertas.")
        return

    query = """
    WITH critical_scores AS (
        SELECT time, sport,
               CASE coord_index 
                   WHEN 0 THEN 'A Coruña' WHEN 1 THEN 'Santiago' 
                   WHEN 2 THEN 'Vigo' WHEN 3 THEN 'Lugo' 
                   WHEN 4 THEN 'Ourense' WHEN 5 THEN 'Pontevedra' 
               END as zona,
               score, details
        FROM meteogalicia.iad_scores
        WHERE time BETWEEN NOW() AND NOW() + INTERVAL '3 hours'
          AND score < 3.0
    )
    SELECT time, sport, zona, score, details
    FROM critical_scores
    ORDER BY time ASC
    """

    results = []
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                for row in cur.fetchall():
                    results.append({
                        "time": row[0],
                        "sport": row[1],
                        "zona": row[2],
                        "score": float(row[3]),
                        "details": row[4]
                    })
    except Exception as e:
        log.error(f"[Alertas] Error leyendo alertas de BD: {e}")
        return

    if not results:
        log.info("[Alertas] Todo en orden. No hay IAD crítico en las próximas 3h.")
        return

    log.warning(f"[Alertas] ¡Se encontraron {len(results)} condiciones críticas! Enviando aviso a Discord...")
    _send_discord_alert(results)


def _send_discord_alert(critical_rows):
    """Agrupa las alertas y envía un bonito embed a Discord."""
    # Agrupar por zona
    by_zona = {}
    for r in critical_rows:
        z = r["zona"]
        if z not in by_zona:
            by_zona[z] = []
        by_zona[z].append(r)

    embeds = []
    
    for zona, items in by_zona.items():
        description = f"Se han detectado condiciones peligrosas para la práctica deportiva en **{zona}** en las próximas 3 horas.\n\n"
        
        for item in items:
            t_str = item["time"].strftime("%H:%0M")
            sp = {"running": "🏃 Running", "cycling": "🚴 Ciclismo", "mtb": "🚵 MTB"}.get(item["sport"], item["sport"])
            sc = item["score"]
            w = item["details"].get("wind", 0)
            p = item["details"].get("precip", 0)
            temp = item["details"].get("temp", 0)
            
            description += f"**{t_str} - {sp}**\n"
            description += f"IAD: `{sc}/10` 🔴 | 🌡️ {temp}ºC | 💨 {w} km/h | 🌧️ {p} mm\n\n"

        embeds.append({
            "title": f"🚨 Alerta Meteorológica Deportiva: {zona}",
            "description": description,
            "color": 16711680,  # Rojo
        })

    payload = {
        "content": "¡Atención! Condiciones no aptas para el deporte detectadas. ⚠️",
        "embeds": embeds[:10]  # Discord allows max 10 embeds per message
    }

    try:
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "GrafanaHackUDC/1.0"}
        )
        with urllib.request.urlopen(req) as response:
            if response.status in (200, 204):
                log.info("[Alertas] Mensaje enviado a Discord correctamente.")
            else:
                log.error(f"[Alertas] Error mandando a Discord: HTTP {response.status}")
    except Exception as e:
        log.error(f"[Alertas] Excepción al enviar a Discord: {e}")
