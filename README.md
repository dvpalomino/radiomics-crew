# RadiomicsCrew

**Sistemas multiagente para metodología en radiómica.** Dos crews construidas con [crewAI](https://github.com/crewAIInc/crewAI): una revisa la literatura leyendo la sección de métodos, la otra simula un panel de expertos que delibera una decisión metodológica y deja constancia del desacuerdo.

![python](https://img.shields.io/badge/python-3.10–3.13-blue) ![license](https://img.shields.io/badge/license-MIT-green)

---

## Para qué sirve

La radiómica arrastra un problema de reproducibilidad conocido: los estudios rara vez declaran cómo discretizan, normalizan o armonizan sus características, y revisarlo a mano —artículo por artículo, sección de métodos por sección de métodos— es lento. Estas dos crews atacan esa fricción.

**`review`** — Revisión de evidencia. Busca en PubMed y Europe PMC, filtra con criterios explícitos y audita la metodología de cada artículo contra un checklist de reporte tipo IBSI, leyendo los métodos y no solo el resumen. Produce una tabla de evidencia y una síntesis organizada por decisión metodológica, no artículo por artículo.

**`panel`** — Panel de expertos. Cinco roles (radiólogo, metodólogo IBSI, bioestadístico, ingeniero de ML, asesor regulatorio) debaten una decisión —por ejemplo, *fixed bin size* frente a *fixed bin number*— coordinados por un chair que preserva el desacuerdo en lugar de promediarlo. Produce un registro de decisión metodológica (estilo ADR).

No resuelve la falta de armonización —eso es un problema de fondo del campo— pero hace ese desorden metodológico rápido de auditar. Ejemplos reales de salida en [`docs/example_output.md`](docs/example_output.md) (review) y [`docs/example_output_panel.md`](docs/example_output_panel.md) (panel).

## Instalación

Requiere Python 3.10–3.13 (crewAI limita a `<3.14`; en Windows, 3.12 es lo más seguro).

```bash
git clone https://github.com/USER/radiomics-crew.git
cd radiomics-crew
python -m venv .venv && source .venv/bin/activate    # Windows: py -3.12 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env      # añade tu clave; .env está gitignorado
pytest -q                 # verifica la instalación sin gastar un token
```

Configura el `.env` con tu proveedor. Con Anthropic:

```bash
ANTHROPIC_API_KEY=sk-ant-...
RC_MODEL=anthropic/claude-haiku-4-5-20251001   # los cuatro workers
RC_MANAGER_MODEL=anthropic/claude-sonnet-5     # el chair del panel
RC_TEMPERATURE=off                             # algunos modelos rechazan temperature
NCBI_EMAIL=tu@correo.org                        # opcional, sube el límite de PubMed
```

Cualquier proveedor soportado por LiteLLM funciona (OpenAI, Gemini, Ollama local): instala el extra correspondiente y ajusta el nombre del modelo. Ver `.env.example`.

## Uso

**Revisión bibliográfica:**

```bash
python -m radiomics_crew review \
  --question "How sensitive are CT radiomic texture features to fixed bin size versus fixed bin number discretisation?" \
  --min-year 2019
```

**Panel de expertos, desde un preset:**

```bash
python -m radiomics_crew panel --preset fbn_vs_fbs_ct
```

**Panel con tu propia pregunta:**

```bash
python -m radiomics_crew panel \
  --question "Are DL-generated masks acceptable as the ROI source for a radiomic signature?" \
  --context "nnU-Net mean Dice 0.87, 10% of cases below 0.6" \
  --option "fully automatic" --option "automatic + review of every case" \
  --option "review triggered by a quality score" \
  --tumour-site pancreatic --modality CT
```

Las salidas caen en `outputs/` como JSON (para diffear) y Markdown (para leer). Presets disponibles en [`examples/presets.yaml`](examples/presets.yaml); más preguntas de ejemplo en [`examples/questions.md`](examples/questions.md).

Empieza por `review`: es más barato y más rápido que `panel`. El `panel` es jerárquico y consume bastante más — revisa el `token_usage` que se imprime al terminar.

## Cómo leer las salidas

En el **review**, mira primero si la tabla de evidencia tiene PMIDs reales (compruébalos en PubMed) antes que la síntesis. La columna de preprocesado revela si el agente leyó los métodos o se quedó en el abstract; muchos `not verifiable from abstract` suelen ser el muro del paywall, no un fallo.

En el **panel**, ve directo a `points_of_disagreement`. Si está poblado, el registro captura tensión real —que es su valor—. Un consenso demasiado limpio suele significar que los agentes no se presionaron lo suficiente.

## Limitaciones

- El cribado no es de grado revisión-sistemática (sin doble cribado independiente, sin PRISMA, sin instrumento formal de riesgo de sesgo). Es un primer paso rápido y auditable que apunta a los artículos correctos; no los sustituye.
- La valoración a texto completo solo alcanza open access; los artículos de pago se marcan como no verificables en lugar de adivinarlos.
- El panel *simula* experiencia, no la tiene. El registro es un punto de partida estructurado para una reunión real, no una opinión clínica ni regulatoria. Nada aquí es un producto sanitario.
- La indexación de PubMed va con retraso; el trabajo muy reciente se recupera de menos.

## Tests

```bash
pytest -q          # sin red, sin clave
ruff check src tests
```

La batería fija los componentes deterministas y varios fallos que llegaron a producirse en runs reales: reparación de JSON truncado, coerción de tipos que un LLM escribe mal, que `temperature` no se envíe a modelos que la rechazan, y que ningún esquema anidado llegue al proveedor.

## Estructura

```
config/          agents.yaml + tasks.yaml por crew — los prompts, versionados
knowledge/       el checklist de reporte tipo IBSI
src/radiomics_crew/
  crews/         review (secuencial), panel (jerárquico)
  tools/         PubMed, Europe PMC, checker IBSI, capa HTTP con caché
  schemas.py     contratos pydantic de cada salida
  parsing.py     validación en proceso (no vía el esquema del proveedor)
examples/        presets y preguntas de ejemplo
```

## Créditos

Patrones de diseño de agentes del curso [*Multi AI Agent Systems with crewAI*](https://www.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai) (DeepLearning.AI / crewAI). La capa de dominio —el checklist, los esquemas, los roles del panel, los modos de fallo que conviene vigilar— es propia.

MIT. No es un producto sanitario. No es consejo clínico.
