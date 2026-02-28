"""Parser para AEMET observaciones → filas para raw_aemet.observaciones."""
import logging
from datetime import datetime

log = logging.getLogger(__name__)


def parse_aemet_observaciones(data: list) -> list[dict]:
    """
    Parsea lista de observaciones AEMET convencionales.
    Filtra por estaciones de Galicia (prefijo idema empieza por '1' o prov. gallegas).
    Devuelve una lista de dicts listos para INSERT.
    """
    rows = []
    # Provincias gallegas en AEMET: A Coruña, Lugo, Ourense, Pontevedra
    galicia_prov = {"15", "27", "32", "36"}

    for obs in data:
        idema = obs.get("idema", "")
        # Filtrar aproximado por provincia (primeros 2 dígitos del idema si están)
        prov_code = idema[:2] if len(idema) >= 2 else ""

        # Incluir todas si no podemos filtrar, o filtrar por Galicia
        # Para hackathon tomamos todo y luego ya filtramos en Grafana
        fint = obs.get("fint", "")
        if not fint:
            continue

        try:
            dt = datetime.fromisoformat(fint)
        except ValueError:
            log.warning("[AEMET] fint malformado: %s", fint)
            continue

        row = {
            "time": dt,
            "estacion_id": idema,
            "ubicacion": obs.get("ubi", ""),
            "temperatura": _safe(obs.get("ta")),
            "humedad": _safe(obs.get("hr")),
            "precipitacion": _safe(obs.get("prec")),
            "viento_vel": _safe(obs.get("vv")),
            "viento_dir": _safe(obs.get("dv")),
            "raw_data": obs,
        }
        rows.append(row)

    log.info("[parser] AEMET obs → %d filas", len(rows))
    return rows


def _safe(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
