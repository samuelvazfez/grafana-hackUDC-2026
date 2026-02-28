import psycopg2
import time
import os

DB_DSN = os.getenv("DB_DSN", "postgres://admin:FurbitoPG345@pg-timescale:5432/observability")

def mock_bad_conditions():
    """Inyectar datos críticos para forzar la alerta."""
    print("Conectando a la base de datos...")
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    
    # 1. Forzar un IAD de Running a 3.5 en A Coruña (coord_index = 0)
    print("Inyectando IAD crítico (3.5) en A Coruña...")
    query_iad = """
    INSERT INTO meteogalicia.iad_running (time, coord_index, lon, lat, score, label, details)
    VALUES (NOW() + INTERVAL '1 hour', 0, -8.409, 43.362, 3.5, 'No recomendado', '{"mock": true}')
    """
    cur.execute(query_iad)
    
    # 2. Forzar Calidad del Aire AQI a 85 en Vigo (coord_index = 2)
    print("Inyectando AQI malo (85) en Vigo...")
    query_aqi = """
    INSERT INTO raw_air.quality (time, lat, lon, coord_index, european_aqi, pm10, pm2_5, uv_index)
    VALUES (NOW() + INTERVAL '1 hour', 42.240, -8.720, 2, 85, 45.2, 28.5, 4)
    """
    cur.execute(query_aqi)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Datos mockeados correctamente. Disparando comprobación...")
    
    from alerter import check_and_send_alerts
    check_and_send_alerts()

if __name__ == "__main__":
    mock_bad_conditions()
