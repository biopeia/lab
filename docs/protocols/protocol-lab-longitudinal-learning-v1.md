# PROTOCOLO EXPERIMENTAL V1 — APRENDIZAJE LONGITUDINAL EN ORGANISM

**Identificador:** `PROTOCOL-LAB-LONGITUDINAL-LEARNING-V1`  
**Fecha:** 2026-10-17  
**Estado:** Propuesta Técnica — Pendiente de Revisión Metodológica por Claude (Lab)  
**Responsable Técnico:** Antigravity  
**Responsable Científico:** Lab (revisión metodológica independiente: Claude)  
**Dominios Participantes:** Organism, World, Embodiment, Modality, Environment, Lab, Observation.

---

## 1. Misión y Pregunta de Investigación

Determinar experimentalmente si los mecanismos de **plasticidad sináptica Oja** y **retroalimentación somática interoceptiva** de Biopeia, integrados en el runtime causal real de World con MuJoCo, producen modificaciones funcionales reproducibles, durables y adaptativas en Organism, o si sus efectos se limitan a derivas numéricas paramétricas sin valor adaptativo.

### 1.1 Jerarquía Epistémica de Distinciones
El protocolo prohíbe explícitamente equiparar los siguientes cinco niveles de resultado:

```
[Nivel 1] Modificación de parámetros internos
   │      (Variación numérica de pesos w_ij en CognitiveGraph o records en ExperienceLedger)
   ▼
[Nivel 2] Cambio funcional observable
   │      (Diferencia comprobable en las probabilidades de disparo, comandos motores o torques)
   ▼
[Nivel 3] Adquisición de competencias
   │      (Formación de primitivas sensorimotoras robustas con evidencia en CompetenceDevelopmentEngine)
   ▼
[Nivel 4] Retención longitudinal
   │      (Persistencia bit a bit tras interrupción de proceso, cold restore y reanudación multicorte)
   ▼
[Nivel 5] Adaptación ante condiciones diferentes
          (Comportamiento adaptativo ante variabilidad ambiental o perturbaciones mecánicas)
```

Alcanzar un nivel no autoriza a inferir los niveles superiores. Cada nivel requiere pruebas y métricas independientes.

---

## 2. Hipótesis Falsables

- **$H_1$ (Plasticidad no supervisada acotada):**  
  Bajo estimulación aferente sensorial continua, las sinapsis excitatorias sujetas a la regla de aprendizaje de Oja incrementarán su peso $w_{ij}$ desde su valor inicial (0.20) de forma monótona y asintóticamente estable ($w_{ij} \le 1.0$), sin divergencia numérica.  
  *Criterio de falsación:* $w_{ij} = 0.20$ constante, $w_{ij} > 1.0$ (divergencia), o NaN/Inf.

- **$H_2$ (Diferencial funcional observable):**  
  Bajo una sonda de test idéntica $x_{probe}$, el organismo plasticamente modificado exhibirá un vector de activación de nodos y comandos motores estadísticamente diferenciado respecto al organismo control sin plasticidad.  
  *Criterio de falsación:* Salida motora indistinguible del control ($\Delta < 10^{-6}$) a pesar del cambio en pesos.

- **$H_3$ (Efectividad somática e inducción de competencias):**  
  La incorporación causal de retroalimentación somática autorizada (`KinematicSomaticTransductionV1`) genera registros estructurados en `CompetenceDevelopmentEngine.frame_history`, induciendo la creación de primitivas y estadísticas de contingencia diferenciadas respecto a organismos sin retroalimentación.  
  *Criterio de falsación:* `len(frame_history) == 0` o ausencia de primitivas descubiertas.

- **$H_4$ (Durabilidad y no degradación tras restauración multicorte):**  
  Toda modificación sináptica, registro experiencial y estado de desarrollo de competencias acumulado hasta el tick $N$ se preserva exactamente una vez tras interrupción forzosa y restauración en frío desde el corte $N$, sin pérdida de frames ni doble registro.  
  *Criterio de falsación:* Pérdida de frames (e.g. `[1, 3]`), mutación de pesos tras restore o discrepancia de digests.

- **$H_5$ (Plasticidad diferencial dependiente del entorno):**  
  Bajo gradientes variables (inversión de gradiente o extinción), la tasa de cambio de pesos sinápticos reflejará la dinámica del estímulo y no una deriva temporal autónoma.  
  *Criterio de falsación:* Evolución idéntica de pesos con y sin señal externa.

---

## 3. Diseño Factorial 2 × 2 de Grupos Experimentales

Para aislar estrictamente las contribuciones de la plasticidad cognitiva y de la retroalimentación somática, se define la siguiente matriz factorial:

| Grupo | Identificador | Plasticidad Oja (`EdgeLearningInstruction`) | Retroalimentación Somática (`enable_somatic_feedback`) | Propósito Científico |
|---|---|---|---|---|
| **G1** | `CONTROL_INERT` | Deshabilitada (`learning=()`) | Deshabilitada (`somatic_transduction=None`) | Control basal negativo de invariancia. |
| **G2** | `CONTROL_SOMATIC` | Deshabilitada (`learning=()`) | Habilitada (`KinematicSomaticTransductionV1`) | Evalúa adquisición de competencias puramente motora/somática sin modulación sináptica. |
| **G3** | `CONTROL_PLASTIC` | Habilitada (Oja rate $\eta = 0.05$) | Deshabilitada (`somatic_transduction=None`) | Evalúa potenciación sináptica puramente aferente sin feedback corporal. |
| **G4** | `EXPERIMENTAL_FULL` | Habilitada (Oja rate $\eta = 0.05$) | Habilitada (`KinematicSomaticTransductionV1`) | Acoplamiento sensorimotor completo. |

### Invariantes de Comparabilidad Compartida
- Todos los grupos comparten:
  - Idéntica arquitectura cognitiva inicial (`CognitiveGraph` con 2 nodos: `opaque.scalar.signal` y `concept.resource`, peso inicial $w_0 = 0.20$).
  - Idéntica morfología física de Embodiment (`ActiveArticulatedMorphology` de bisagra articulada 1-DoF).
  - Idéntica configuración física de MuJoCo (Euler, 0.01s timestep, 50 iteraciones).
  - Idéntico campo escalar de Environment (`IdentifiedFiniteScalarField` con gradiente espacial conocido).
  - Mismos límites de kernel cognitivo (`KernelLimits`).

---

## 4. Escenarios Ambientales de Evaluación

1. **E1 — Campo Estable (Estímulo Persistente):**
   - Campo escalar continuo con fuente constante en $(1.0, 0.0, 0.0)$.
   - Estímulo sensorimotor ininterrumpido durante 20–50 ciclos.
   - Evalúa convergencia de Oja y saturación de pesos.

2. **E2 — Campo Variable (Dinámica y Extinción):**
   - **Fase A (Ciclos 1–20):** Campo activo alto ($I = 1.0$).
   - **Fase B (Ciclos 21–40):** Extinción del estímulo ($I = 0.0$).
   - **Fase C (Ciclos 41–60):** Reaparición en orientación invertida.
   - Evalúa persistencia de pesos vs decaimiento pasivo, y adaptabilidad a cambios ambientales.

3. **E3 — Perturbación Mecánica Corporal:**
   - Aplicación de resistencia articular variable (cambio acotado en amortiguación de articulación o torque de carga) conforme a contratos de Embodiment.
   - Evalúa si el desarrollo de competencias distingue resistencia mecánica real de variabilidad sensorial.

---

## 5. Protocolo de Continuidad Multicorte e Interrupción

Para validar el criterio de durabilidad (Fase 3):
- Sesión total planificada: 30 ciclos.
- Interrupciones forzosas planificadas en:
  - **Tick 10:** Corte 10 confirmado $\to$ Aborto de proceso $\to$ Cold restore $\to$ Ejecución 10–20.
  - **Tick 20:** Corte 20 confirmado $\to$ Aborto de proceso $\to$ Cold restore $\to$ Ejecución 20–30.
- Comparación contra sesión control ininterrumpida de 30 ciclos:
  - Verificación de identidad estricta: `frame_history`, `experience_records`, `graph.edges[0].weight`, `horizon_counts`, `horizon_stats`.
  - Discrepancia tolerable: exactamente $0$ (determinismo estricto garantizado por contrato).

---

## 6. Métricas y Criterios de Aceptación/Inconclusión

### 6.1 Métricas Formales
1. **Diferencial Sináptico:** $\Delta w = w_{final} - w_0$.
2. **Deriva Control:** $\Delta w_{control} = |w_{control, final} - w_0|$ (debe ser exactamente 0.0).
3. **Diferencial Funcional Motor:** Magnitud de torque proyectado bajo sonda normalizada:
   $$D_{func} = \| \tau(G4, x_{probe}) - \tau(G1, x_{probe}) \|$$
4. **Índice de Madurez de Primitivas:** Número de primitivas en `primitives` y recuentos de uso en `use_counts`.
5. **Tasa de Integridad de Frame:** Ratio de frames recuperados sobre frames comprometidos:
   $$R_{frames} = \frac{N_{restored}}{N_{committed}} \equiv 1.0$$

### 6.2 Criterios de Decisión
- **Éxito Técnico:**
  - $R_{frames} = 1.0$ en todos los multicortes.
  - $\Delta w_{control} = 0.0$ estricto.
  - $\Delta w_{plastic} > 0.0$ con estabilidad acotada.
  - Transducción cinemática 100% delegada a Modality sin violaciones de finitud.
- **Inconclusión:**
  - Si $\Delta w_{plastic} > 0.0$ pero $D_{func} = 0.0$ (modificación interna sin consecuencia funcional observable).
  - Si se generan primitivas en el motor de competencias pero nunca son reutilizadas en la selección de acciones.
- **Fallo:**
  - Pérdida de frames en restore ($R_{frames} < 1.0$).
  - Divergencia numérica o NaN en pesos.
  - Fallo en la verificación de contratos de checkpoints de World.

---

## 7. Gobernanza, Custodia y Revisión Independiente

1. **Custodia en Lab:**  
   Los datos brutos de las ejecuciones (manifests de World, journals, checkpoints binarios de participantes, hashes sha256 y logs de ejecución) se almacenan en el directorio de evidencias de Lab (`repos/lab/`).
2. **Revisión Metodológica:**  
   Este protocolo (D1) y los dossiers de resultados subsecuentes (D2–D6) se someten a la revisión independiente de Claude en Lab/Docs antes de emitir conclusiones científicas sobre el aprendizaje de Organism.
3. **Ejecuciones Preliminares:**  
   Los pilotos iniciales (20 ciclos) se etiquetan estrictamente como `EXPLORATORY_INSTRUMENTATION_PILOT`.
