<p align="center">
  <img src="web/images/hackudc26.png" alt="Galaecia Metrics" width="500"/>
</p>

<p align="center">
  <strong>Plataforma de meteorología deportiva en tiempo real para Galicia</strong><br/>
  Desarrollado durante <a href="https://hackudc.gpul.org/">HackUDC 2026</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Docker-Compose-blue?logo=docker" alt="Docker"/>
  <img src="https://img.shields.io/badge/PostgreSQL-TimescaleDB-336791?logo=postgresql" alt="TimescaleDB"/>
  <img src="https://img.shields.io/badge/Grafana-Dashboard-F46800?logo=grafana" alt="Grafana"/>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License"/>
</p>

---

## Descripción

**Galaecia Metrics** es una plataforma que ingesta, almacena y visualiza datos meteorológicos de múltiples fuentes públicas con enfoque en la **viabilidad deportiva al aire libre** en las principales ciudades de Galicia (A Coruña, Santiago, Vigo, Lugo, Ourense y Pontevedra).

El sistema calcula un **Índice de Aptitud Deportiva (IAD)** personalizado para running que combina temperatura, viento, precipitación y estado del cielo en una puntuación de 0 a 10, indicando si las condiciones son ideales para salir a correr.

### Características principales

- 📊 **Dashboard interactivo** con Grafana: running score, previsión 24h, temperatura, lluvia, viento, nubosidad, polen, AQI y UV
- 🏃 **IAD (Índice de Aptitud Deportiva)** — algoritmo propio que puntúa las condiciones para correr de 0 a 10
- 🔔 **Alertas a Discord** — notificaciones automáticas cuando las condiciones son malas (IAD < 7) o la calidad del aire baja (AQI > 50)
- 🌐 **Landing page** — web estática con Nginx para presentar el proyecto
- 🔄 **Ingesta automática** — scheduler que obtiene y procesa datos periódicamente
- 🏙️ **Filtro por ciudad** — selecciona cualquiera de las 6 ciudades gallegas principales

---

## Arquitectura

```
┌───────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Fuentes API │────▷│    Ingestor      │────▷│ TimescaleDB │
│               │     │    (Python)      │     │ (PostgreSQL)│
│ · MeteoSIX    │     │                  │     └──────┬──────┘
│ · AEMET       │     │ · Fetchers       │            │
│ · Open-Meteo  │     │ · Parsers        │            ▼
│               │     │ · IAD Engine     │     ┌─────────────┐
│               │     │ · Alerter →Discord│     │   Grafana   │
└───────────────┘     └──────────────────┘     │  Dashboard  │
                                               └──────┬──────┘
                                                      │
                                               ┌──────┴──────┐
                                               │    Nginx    │
                                               │  (web app)  │
                                               └─────────────┘
```

### Servicios Docker

| Servicio | Imagen | Puerto | Descripción |
|----------|--------|--------|-------------|
| `postgres` | `timescale/timescaledb:latest-pg16` | `5432` | BD TimescaleDB con esquemas `raw_air`, `raw_aemet`, `meteogalicia` |
| `grafana` | `grafana/grafana-oss:latest` | `3000` | Dashboard interactivo con acceso anónimo habilitado |
| `ingestor` | Build local (`./ingestor`) | — | Scheduler Python que ingesta datos y envía alertas |
| `web` | `nginx:alpine` | `8080` | Landing page estática |

---

## Fuentes de datos

| API | Datos | Frecuencia |
|-----|-------|------------|
| [MeteoSIX](https://www.meteogalicia.gal/web/RSS/rssIndex.action) (MeteoGalicia) | Previsión numérica: temperatura, precipitación, estado del cielo | Cada 6h |
| [AEMET OpenData](https://opendata.aemet.es/) | Observaciones reales: temperatura, humedad, viento, precipitación | Cada 30min |
| [Open-Meteo Forecast](https://open-meteo.com/) | Previsión horaria: temp, sens. térmica, viento, rachas, visibilidad, nubes | Cada 30min |
| [Open-Meteo Air Quality](https://open-meteo.com/) | AQI europeo, PM10, PM2.5, índice UV, polen (gramíneas, abedul, olivo…) | Cada 30min |

### Ciudades monitorizadas

| Índice | Ciudad | Coordenadas |
|--------|--------|-------------|
| 0 | A Coruña | -8.409, 43.362 |
| 1 | Santiago de Compostela | -8.546, 42.880 |
| 2 | Vigo | -8.720, 42.240 |
| 3 | Lugo | -7.556, 43.012 |
| 4 | Ourense | -7.864, 42.336 |
| 5 | Pontevedra | -8.644, 42.431 |

---

## IAD — Índice de Aptitud Deportiva

El IAD es un score compuesto de **0 a 10** que evalúa las condiciones para running basándose en sub-scores ponderados:

| Factor | Peso | Ideal (puntuación 10) | Peor caso (puntuación 0) |
|--------|------|----------------------|--------------------------|
| 🌡️ Temperatura | 30% | 10-20 °C | < 0 °C o > 40 °C |
| 💨 Viento | 25% | < 15 km/h | > 40 km/h |
| 🌧️ Precipitación | 30% | 0 mm | > 10 mm |
| ☁️ Estado del cielo | 15% | Despejado/sunny | Tormenta/nieve |

**Etiquetas resultantes:**

| Score | Etiqueta |
|-------|----------|
| ≥ 8.0 | Perfecto |
| ≥ 6.0 | Bueno |
| ≥ 4.0 | Aceptable |
| ≥ 2.0 | Malo |
| < 2.0 | No recomendado |

---

## Instalación y uso

### Prerrequisitos

- [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clonar el repositorio

```bash
git clone https://github.com/samuelvazfez/grafana-hackUDC-2026.git
cd grafana-hackUDC-2026
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y completa al menos:

```env
POSTGRES_PASSWORD=tu_contraseña_segura
GRAFANA_PASSWORD=tu_contraseña_grafana

# API Keys (obtener gratis en las webs correspondientes)
METEOSIX_API_KEY=tu_key_meteosix
AEMET_API_KEY=tu_key_aemet

# Opcional: alertas a Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

> **Nota:** Las APIs de Open-Meteo no requieren API key.

### 3. Arrancar los servicios

```bash
docker compose up --build -d
```

### 4. Acceder

| Servicio | URL |
|----------|-----|
| 🌐 Landing page | [http://localhost:8080](http://localhost:8080) |
| 📊 Dashboard (con UI Grafana) | [http://localhost:3000](http://localhost:3000) |
| 📊 Dashboard (modo kiosko, sin UI) | [http://localhost:3000/d/running-galicia-v2?kiosk](http://localhost:3000/d/running-galicia-v2?kiosk) |

---

## Estructura del proyecto

```
grafana-hackUDC-2026/
├── docker-compose.yml          # Orquestación de servicios
├── .env.example                # Variables de entorno (plantilla)
│
├── ingestor/                   # Servicio de ingesta de datos (Python)
│   ├── Dockerfile
│   ├── app.py                  # Main loop — scheduler de ingesta
│   ├── config.py               # Configuración desde variables de entorno
│   ├── db.py                   # Pool de conexiones PostgreSQL
│   ├── cache.py                # Caché local en disco
│   ├── iad.py                  # Motor de cálculo del IAD
│   ├── alerter.py              # Sistema de alertas a Discord
│   ├── fetchers/               # Módulos de obtención de datos
│   │   ├── meteosix.py         #   └─ MeteoGalicia (MeteoSIX v5)
│   │   ├── aemet.py            #   └─ AEMET OpenData
│   │   └── air.py              #   └─ Open-Meteo (forecast + AQI + pollen)
│   └── parsers/                # Módulos de transformación de datos
│       ├── meteosix.py         #   └─ Parser MeteoSIX
│       ├── aemet.py            #   └─ Parser AEMET
│       └── air.py              #   └─ Parser Open-Meteo
│
├── postgres/                   # Configuración de base de datos
│   └── initdb/                 # Scripts de inicialización (orden alfanumérico)
│       ├── 000_setup.sql       #   └─ Extensiones y esquemas
│       ├── 001_air.sql         #   └─ Tablas de calidad del aire y forecast
│       ├── 002_aemet.sql       #   └─ Tablas de observaciones AEMET
│       ├── 003_meteogalicia.sql#   └─ Tablas MeteoSIX + IAD
│       └── 005_grafana_user.sql#   └─ Usuario de solo lectura para Grafana
│
├── grafana/                    # Configuración de Grafana
│   └── provisioning/
│       ├── dashboards/
│       │   ├── dashboards.yaml #   └─ Configuración de provisioning
│       │   └── running.json    #   └─ Dashboard principal
│       └── datasources/
│           └── timescaledb.yaml#   └─ Conexión a TimescaleDB
│
└── web/                        # Landing page (Nginx)
    ├── index.html
    ├── styles.css
    ├── main.js
    └── images/
```

---

## Sistema de alertas

El ingestor evalúa umbrales cada **5 minutos** y envía notificaciones a Discord:

| Alerta | Condición | Severidad |
|--------|-----------|-----------|
| 🔴 No salgas hoy | IAD < 5.0 | Crítica |
| 🟡 Condiciones regulares | IAD entre 5.0 y 7.0 | Warning |
| 💨 Calidad del aire mala | AQI > 50 | Warning |

Para configurar las alertas, crea un **Webhook** en tu servidor de Discord y pega la URL en la variable `DISCORD_WEBHOOK_URL` del `.env`.

---

## Tecnologías

- **Python 3.12** — ingestor, parsers, alerter
- **PostgreSQL 16 + TimescaleDB** — base de datos temporal optimizada
- **Grafana OSS** — visualización de dashboards
- **Nginx** — servidor web estático
- **Docker & Docker Compose** — orquestación de contenedores
- **APIs públicas** — MeteoSIX, AEMET OpenData, Open-Meteo

---

## Licencia

Este proyecto está licenciado bajo la **MIT License**. Ver [LICENSE](LICENSE) para más detalles.

### ¿Por qué MIT?

Se ha elegido la licencia **MIT** por las siguientes razones:

1. **Máxima apertura** — Permite a cualquiera usar, modificar y distribuir el código sin restricciones, ideal para un proyecto nacido en un hackathon comunitario.
2. **Compatibilidad** — MIT es compatible con prácticamente todas las demás licencias open source (GPL, Apache, BSD…), facilitando que otros proyectos integren partes de este código.
3. **Simplicidad** — Es una de las licencias más cortas y fáciles de entender, sin cláusulas complejas.
4. **Sin copyleft** — A diferencia de GPL, no obliga a que los trabajos derivados mantengan la misma licencia, dando total libertad a la comunidad.
5. **Estándar en hackathons** — Es la licencia más utilizada en proyectos de hackathon y open source en general (React, Node.js, Rails, jQuery…).

---

## Equipo

- Alejandro Quintela Río
- Samuel Vázquez Fernández
- Jacobo Estévez Rouco
- Andrés Paz Paredes
