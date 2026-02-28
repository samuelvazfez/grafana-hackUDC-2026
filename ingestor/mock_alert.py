"""Script para mockear datos de IAD y probar las alertas de Discord."""
import sys
import os
import argparse
from datetime import datetime, timedelta

# Asegurar que encuentre db.py y variables de entorno
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import get_conn
import psycopg2.extras

def mock_bad_weather(sport="running", coord_index=0, minutes_ahead=60):
    """Inserta un IAD crítico (score 1.0) para que el alerter lo detecte."""
    target_time = datetime.now() + timedelta(minutes=minutes_ahead)
    
    print(f"Mocking {sport} bad weather for coord {coord_index} at {target_time}...")
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Primero nos aseguramos de que no de error por FK (no tenemos FK pero por si acaso)
            # Insertamos el IAD crítico
            query = """
            INSERT INTO meteogalicia.iad_scores 
                (time, coord_index, sport, score, label, details)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Detalles inflados (mucho viento, mucha lluvia)
            bad_details = {
                "temp": 3.0, "wind": 85.0, "precip": 45.0, "sky": "STORM",
                "temp_score": 0.5, "wind_score": 0.0, "precip_score": 0.0, "sky_score": 0.0
            }
            
            psycopg2.extras.execute_values(cur, """
            INSERT INTO meteogalicia.iad_scores 
                (time, coord_index, sport, lon, lat, score, label, details)
            VALUES %s
            """, [(
                target_time, coord_index, sport, -8.409, 43.362, 
                1.5, "No recomendado", psycopg2.extras.Json(bad_details)
            )])
            
        conn.commit()
    print("¡Datos mockeados exitosamente! Espera hasta 5 minutos a que el ingestor envíe la alerta o ejecuta alerter.py manualmente.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sport", default="running", choices=["running", "cycling", "mtb"])
    parser.add_argument("--coord", type=int, default=0, help="0=Coruña, 1=Santiago, ...")
    parser.add_argument("--minutes", type=int, default=30)
    args = parser.parse_args()
    
    mock_bad_weather(args.sport, args.coord, args.minutes)
