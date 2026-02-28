"""Configuración centralizada desde variables de entorno."""
import os

# ── Base de datos ─────────────────────────────────────────────────────────────
PGHOST     = os.getenv("PGHOST", "postgres")
PGPORT     = int(os.getenv("PGPORT", "5432"))
PGDATABASE = os.getenv("PGDATABASE", "observability")
PGUSER     = os.getenv("PGUSER", "admin")
PGPASSWORD = os.getenv("PGPASSWORD", "")

# ── MeteoSIX ─────────────────────────────────────────────────────────────────
METEOSIX_BASE_URL  = os.getenv("METEOSIX_BASE_URL", "https://servizos.meteogalicia.gal/apiv5").rstrip("/")
METEOSIX_API_KEY   = os.getenv("METEOSIX_API_KEY", "")
METEOSIX_OPERATION = os.getenv("METEOSIX_OPERATION", "getNumericForecastInfo")
METEOSIX_FORMAT    = os.getenv("METEOSIX_FORMAT", "application/json")
METEOSIX_LANG      = os.getenv("METEOSIX_LANG", "gl")
METEOSIX_COORDS    = os.getenv(
    "METEOSIX_COORDS",
    "-8.409,43.362;-8.546,42.880;-8.720,42.240;-7.556,43.012;-7.864,42.336;-8.644,42.431"
).strip()

# ── AEMET ─────────────────────────────────────────────────────────────────────
AEMET_API_KEY  = os.getenv("AEMET_API_KEY", "")
AEMET_BASE_URL = os.getenv("AEMET_BASE_URL", "https://opendata.aemet.es/opendata")

# ── Cache ─────────────────────────────────────────────────────────────────────
CACHE_DIR         = os.getenv("CACHE_DIR", "/app/cache")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", str(25 * 3600)))  # 25h

# ── Poll ──────────────────────────────────────────────────────────────────────
POLL_METEOSIX_SECONDS = int(os.getenv("POLL_SECONDS", str(6 * 3600)))       # 6h
POLL_AEMET_SECONDS    = int(os.getenv("POLL_AEMET_SECONDS", str(30 * 60)))  # 30min

# ── Alertas ───────────────────────────────────────────────────────────────────
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

