import os
import requests
import psycopg2
import logging
from psycopg2.extras import RealDictCursor

# Configuración de log
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("alerter")

DB_DSN = os.getenv("DB_DSN", "postgres://admin:FurbitoPG345@pg-timescale:5432/observability")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

ZONAS = {
    0: "A Coruña",
    1: "Santiago de Compostela",
    2: "Vigo",
    3: "Lugo",
    4: "Ourense",
    5: "Pontevedra"
}

def get_conn():
    return psycopg2.connect(DB_DSN, cursor_factory=RealDictCursor)

def fetch_iad_alerts(conn):
    """
    Busca IADs recientes para running con scores por debajo de 7.
    < 7 -> Warning
    < 5 -> Crítico
    """
    alerts = []
    query = """
    WITH latest_scores AS (
        SELECT DISTINCT ON (coord_index) coord_index, score, label, time
        FROM meteogalicia.iad_running
        WHERE time >= NOW()
        ORDER BY coord_index, time ASC, ts_ingested DESC
    )
    SELECT * FROM latest_scores WHERE score < 7.0;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        for r in rows:
            zona_nombre = ZONAS.get(r['coord_index'], "Desconocido")
            if r['score'] < 5.0:
                alerts.append({
                    "title": f"🔴 No salgas hoy en {zona_nombre}",
                    "description": f"El IAD actual es **{r['score']}**. Las condiciones son muy malas ({r['label']}).",
                    "color": 16711680 # Red
                })
            else:
                alerts.append({
                    "title": f"🟡 El día ya no está tan bueno en {zona_nombre}",
                    "description": f"El IAD ha bajado a **{r['score']}** ({r['label']}).",
                    "color": 16753920 # Orange
                })
    return alerts


def fetch_aqi_alerts(conn):
    """
    Busca valores recientes de calidad de aire con AQI > 50 (Calidad mala).
    """
    alerts = []
    query = """
    WITH latest_aqi AS (
        SELECT DISTINCT ON (coord_index) coord_index, european_aqi, pm10, pm2_5
        FROM raw_air.quality
        WHERE time >= NOW() - INTERVAL '1 hour'
        ORDER BY coord_index, time DESC, ts_ingested DESC
    )
    SELECT * FROM latest_aqi WHERE european_aqi > 50;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        for r in rows:
            zona_nombre = ZONAS.get(r['coord_index'], "Desconocido")
            alerts.append({
                "title": f"💨 Calidad del aire mala en {zona_nombre}",
                "description": f"El índice AQI ha subido a **{r['european_aqi']}**. Se desaconseja hacer ejercicio intenso al aire libre.\nPM10: {r['pm10']} | PM2.5: {r['pm2_5']}",
                "color": 10038562 # Dark Red/Brownish
            })
    return alerts


def send_discord_alert(embeds):
    """Envía los embeds listados a Discord."""
    if not DISCORD_WEBHOOK_URL:
        log.warning("No hay DISCORD_WEBHOOK_URL configurado.")
        return

    payload = {
        "content": "⚠️ **Sistema de Alertas Deportivas Galicia** ⚠️",
        "embeds": embeds
    }

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        resp.raise_for_status()
        log.info("Alerta enviada a Discord con éxito.")
    except Exception as e:
        log.error(f"Error enviando alerta a Discord: {e}")

def check_and_send_alerts():
    """Ejecutado por app.py periodicamente para procesar las alertas."""
    log.info("Comprobando umbrales de alerta...")
    try:
        with get_conn() as conn:
            iad_embeds = fetch_iad_alerts(conn)
            aqi_embeds = fetch_aqi_alerts(conn)
            
            all_embeds = iad_embeds + aqi_embeds
            
            if all_embeds:
                log.info(f"¡Se encontraron {len(all_embeds)} condiciones de alerta! Enviando a Discord...")
                # Discord permite un máximo de 10 embeds por mensaje. Aseguramos no pasarnos.
                for i in range(0, len(all_embeds), 10):
                    send_discord_alert(all_embeds[i:i+10])
            else:
                log.info("Sin alertas críticas. Todo en orden.")
    except Exception as e:
        log.error(f"Fallo al comprobar la base de datos para alertas: {e}")

if __name__ == "__main__":
    check_and_send_alerts()
