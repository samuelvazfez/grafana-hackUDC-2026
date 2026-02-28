# Galicia Deporte Seguro (HackUDC 2026)

Proyecto desarrollado para el reto de **Grafana Labs en HackUDC 2026**, cuyo objetivo es transformar datos abiertos complejos en **historias visuales claras, accionables y centradas en el usuario**.

Nuestra propuesta convierte datos meteorológicos brutos en una recomendación comprensible para la ciudadanía:

> **“¿Es buen momento para entrenar hoy, y qué deporte debería hacer?”**

---

## 💡 1. Finalidad del Proyecto

La información meteorológica abierta suele presentarse en forma de variables técnicas:
- Velocidad del viento (km/h)
- Precipitación (mm/h)
- Temperatura
- Estado del cielo

Pero estos datos, aislados, no responden a la pregunta real del usuario.

### 🎯 Nuestra solución: IAD — Índice de Aptitud Deportiva

Creamos el **IAD (Índice de Aptitud Deportiva)**, un algoritmo dinámico que:

- Consume previsiones oficiales de **MeteoSIX (MeteoGalicia)**
- Evalúa condiciones según el tipo de deporte
- Devuelve una puntuación de **0 a 10**
- Clasifica el estado como:
  - 🟢 Óptimo
  - 🟡 Aceptable
  - 🔴 Desaconsejado

---

### 🧠 Inteligencia contextual por deporte

No existe un clima universalmente “bueno”. Depende del deporte:

- 🏃 **Running**
  - Penaliza temperaturas > 20 °C
  - Penaliza humedad elevada
- 🚴 **Ciclismo de carretera**
  - Penaliza viento fuerte (seguridad)
  - Tolera mejor temperaturas medias-altas
- 🚵 **MTB**
  - Penalización menor por lluvia leve
  - Penalización mayor por tormentas

El IAD aplica **pesos específicos por variable y deporte**, recalculados cada vez que se actualiza la previsión.

---

## 🧱 2. Arquitectura Técnica

El sistema está diseñado bajo un modelo de **separación clara entre ingestión, almacenamiento y visualización**.

### 🔄 Flujo de datos
```
MeteoSIX API
↓
ETL Python (ingestor)
↓
TimescaleDB (PostgreSQL + Timescale)
↓
Grafana (Dashboards + Alerting)
```

---

### 🔹 Componentes

#### 🐍 Ingestor (Python ETL)
- Llama a MeteoSIX (API REST con API_KEY)
- Implementa caché local (TTL ~26h)
- Inserta:
  - `raw_weather` (JSON completo)
  - Tablas derivadas horarias normalizadas
- Diseñado para ejecución continua (24/7)

#### 🗄️ TimescaleDB
- Base de datos PostgreSQL con extensión Timescale
- `raw_weather` como hypertable
- Preparado para tablas derivadas (`weather_hourly`, `iad_scores`)
- Índices temporales optimizados

#### 📊 Grafana
- Dashboards interactivos
- Alertas en tiempo real
- Integración con Discord (webhook)
- Provisioning automático

---

## 🚀 3. Cómo Ejecutar el Proyecto

Todo el sistema está contenerizado.

### Requisitos
- Docker
- Docker Compose

---

### 🧩 Paso 1 — Configurar entorno

Edita el archivo `.env`:

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=******
POSTGRES_DB=observability

METEOSIX_API_KEY=******
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```
### 🐳 Paso 2 — Levantar la pila completa
```bash
docker compose up --build -d
```

### 📊 Paso 3 — Acceder a los Dashboards
- Abre tu navegador en [http://localhost:3000](http://localhost:3000)
- Usuario: `admin` | Contraseña: `******`
- Dirígete a **Dashboards** y verás provisionados automáticamente:
  - `IAD Running — Galicia`
  - `¿Dónde entreno hoy? — Galicia`

### 🔔 4. Sistema de Alertas

El sistema permite:

Alertas automáticas si el IAD baja de umbral

Notificaciones vía Discord Webhook

Monitorización de salud del ETL

---

## 🔭 5. Trabajo a Futuro

El proyecto está diseñado para ser modular y escalable. A continuación se detallan las principales líneas de evolución propuestas:

---

### 🌊 Integración de Deportes Acuáticos

Extender el IAD a surf, paddle surf o kayak mediante la integración de APIs marítimas oficiales:

- Puertos del Estado (red de boyas REDEXT)
- AEMET Marítima
- Modelos de oleaje (WAM / SWAN)

Variables adicionales a evaluar:
- Altura de ola
- Periodo
- Dirección del oleaje
- Temperatura del agua
- Mareas

Esto permitiría generar un **IAD-Surf** específico por costa gallega.

---

### 🌫️ Integración de Calidad del Aire

Incorporar el Índice de Calidad del Aire (ICA) de la Xunta de Galicia para:

- Penalizar el IAD en episodios contaminantes
- Proteger la salud cardiovascular
- Diferenciar impacto en deportes aeróbicos intensos

Esto añadiría una dimensión sanitaria al sistema.

---

### 🤖 Bot Conversacional (Telegram / Discord)

Desarrollar una interfaz conversacional donde el usuario pueda preguntar:

> “¿Es seguro salir en bici hoy por la tarde en Santiago?”

El bot leería directamente desde TimescaleDB y devolvería:
- IAD actual
- Motivo de penalización
- Recomendación alternativa

---

### 🚨 Integración de Alertas Oficiales (CAP AEMET)

Parseo automático de avisos meteorológicos oficiales en formato CAP.

Regla propuesta:
- Si existe alerta naranja o roja → IAD = 0
- Generación automática de notificación push

Esto permitiría convertir el sistema en una herramienta de prevención real.

---

### 📊 Machine Learning y Ajuste Dinámico de Pesos

Fase avanzada:

- Ajustar automáticamente los pesos del IAD
- Analizar históricos meteorológicos
- Aprender qué condiciones correlacionan con cancelaciones reales de eventos deportivos

Esto permitiría evolucionar de un modelo heurístico a uno adaptativo.

---

## 📝 6. Diario de Trabajo

### Día 1

- Brainstorming del concepto IAD
- Definición de arquitectura
- Integración inicial con MeteoSIX
- Diseño de modelo RAW en TimescaleDB

---

### Día 2

- Implementación ETL completo
- Normalización de datos horarios
- Creación de dashboards en Grafana
- Sistema de alertas vía Discord Webhook

---

### Día 3

- Ajuste fino de pesos del IAD
- Mejora visual de dashboards
- Preparación demo final
- Documentación y presentación