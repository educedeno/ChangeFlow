# Discovery - ChangeFlow
## Resumen ejecutivo

ChangeFlow es una plataforma interna para formalizar, revisar y registrar solicitudes de cambios técnicos antes de su ejecución. Actualmente, los cambios se coordinan por Slack o se aplican directamente por ingenieros sin revisión formal, lo que ha generado incidentes operativos por falta de evaluación de impacto, ausencia de plan de rollback y falta de comunicación con soporte.

El objetivo del MVP es establecer un flujo estructurado de aprobación que garantice trazabilidad, control de riesgo y registro de resultados — sin ejecutar cambios automáticamente desde la plataforma.

---

## Contexto del negocio

### Proceso actual (AS-IS)

- Los ingenieros solicitan cambios técnicos vía Slack o los ejecutan directamente.
- No existe revisión formal antes de aplicar cambios en producción.
- No se evalúa el impacto operativo ni se define un plan de rollback.
- El equipo de soporte no siempre es informado antes de la ejecución.
- Los incidentes ocurridos se deben a cambios aplicados sin validación previa.

### Herramientas actuales

- **Slack**: canal principal de comunicación de cambios (informal).
- Sin sistema de tickets técnicos dedicado para change management.

### Pasos manuales identificados

1. Ingeniero decide que necesita un cambio técnico.
2. Lo comunica (o no) por Slack.
3. Lo ejecuta directamente, sin aprobación formal.
4. No queda registro estructurado del resultado.
5. En caso de fallo, no hay plan de rollback documentado.

### Problema principal

> El riesgo operativo es alto. No existe visibilidad sobre quién pidió el cambio, qué sistema afecta, qué riesgo tiene, quién lo aprobó, cuándo se ejecutará, cuál es el plan de rollback y qué pasó después de ejecutarlo.

---

## Usuarios y roles

| Rol | Responsabilidad | Permisos |
|---|---|---|
| **Engineer** | Crea solicitudes de cambio técnico | Crear, editar en DRAFT, cancelar antes de aprobación |
| **Tech Lead** | Revisa impacto técnico | Aprobar/rechazar cambios LOW y MEDIUM; solicitar cambios |
| **Operations Reviewer** | Valida impacto operativo y ventanas de ejecución | Aprobar/rechazar en revisión OPS |
| **Security Reviewer** | Revisa cambios críticos o sensibles | Aprobar/rechazar en revisión SECURITY |
| **Admin** | Visibilidad total del sistema | Reasignar solicitudes, cancelar en cualquier estado |

### Restricciones por rol

- Solo el solicitante (Engineer) o un Admin puede cancelar una solicitud antes de que sea aprobada.
- Una solicitud en estado EXECUTED no puede volver a estado de revisión.
- Un cambio no puede ejecutarse si no está aprobado.

---

## Reglas de negocio

### Clasificación de riesgo

Los cambios se clasifican en tres niveles que determinan el flujo de aprobación:

| Nivel | Descripción | Aprobaciones requeridas |
|---|---|---|
| **LOW** | Cambios internos de bajo impacto (ej: dashboard interno) | Tech Lead |
| **MEDIUM** | Cambios con impacto moderado | Tech Lead + Operations Reviewer |
| **HIGH** | Cambios críticos o sensibles en producción | Tech Lead + Operations Reviewer + Security Reviewer |

> "No todos los cambios tienen el mismo riesgo. Cambiar un dashboard interno no es igual que tocar una integración productiva."

### Plan de rollback

- Todo cambio **MEDIUM** o **HIGH** debe incluir un plan de rollback documentado.
- Si no tiene plan de rollback, la solicitud **no puede avanzar** en el flujo.

### Ejecución del cambio (MVP)

- En el MVP, **la plataforma no ejecuta cambios reales**. Solo registra aprobación, agenda y resultado.
- Un cambio puede marcarse como: `SCHEDULED`, `EXECUTED`, o `FAILED`.
- Si la ejecución falla, debe registrarse el motivo.

### Restricciones operativas

- Un cambio **no puede ejecutarse** si no está aprobado.
- Solo el solicitante o un Admin puede cancelar antes de aprobación.
- Una solicitud ejecutada **no puede volver** a estado de revisión.
- Si la ejecución falla, debe registrarse el motivo del fallo.

---

## Flujo de estados (ciclo de vida)

```
DRAFT → SUBMITTED → TECH_REVIEW → OPS_REVIEW → SECURITY_REVIEW →
APPROVED → SCHEDULED → EXECUTED
              ↘ CHANGES_REQUESTED
              ↘ REJECTED
              ↘ CANCELLED
              ↘ FAILED
```

> No todos los cambios pasan por todos los reviews. El flujo depende del nivel de riesgo asignado.

---

## Eventos del sistema y notificaciones

### Eventos

| Evento | Descripción |
|---|---|
| `CHANGE_CREATED` | Se creó una nueva solicitud |
| `CHANGE_SUBMITTED` | El engineer envió la solicitud para revisión |
| `TECH_REVIEW_REQUIRED` | Requiere revisión del Tech Lead |
| `OPS_REVIEW_REQUIRED` | Requiere revisión de Operations |
| `SECURITY_REVIEW_REQUIRED` | Requiere revisión de Security |
| `CHANGE_APPROVED` | El cambio fue aprobado |
| `CHANGE_REJECTED` | El cambio fue rechazado |
| `CHANGE_SCHEDULED` | Se agendó la ventana de ejecución |
| `CHANGE_EXECUTED` | El cambio fue marcado como ejecutado |
| `CHANGE_FAILED` | La ejecución fue marcada como fallida |

### Notificaciones esperadas

- Al enviar el cambio → se notifica al primer aprobador (Tech Lead).
- Al requerir Operations → se notifica a Operations Reviewer.
- Al requerir Security → se notifica a Security Reviewer.
- Al aprobar o rechazar → se notifica al solicitante.
- Al agendar → se notifica a stakeholders.
- Si falla → se notifica al solicitante y al Tech Lead.

---

## Fuera de alcance del MVP

Los siguientes elementos **no forman parte del MVP**:

- Ejecución real de cambios desde la plataforma.
- Integración con CI/CD real.
- Conexión con Jira.
- Rollback automático.
- Calendario real de ventanas de cambio.
- Integración con Slack real.

---

## Riesgos, supuestos y preguntas abiertas

### Supuestos

- Los usuarios accederán a la plataforma vía web.
- La clasificación de riesgo es asignada por el Engineer al crear la solicitud.
- Los aprobadores son notificados por la plataforma (mecanismo a definir).
- No se requiere autenticación SSO para el MVP.

### Riesgos identificados

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Engineers clasifiquen mal el riesgo (subestimen) | Alto | Validación por Tech Lead; posibilidad de reclasificación |
| Falta de adopción del flujo formal | Alto | Comunicación interna; involucrar líderes técnicos desde el inicio |
| Ambigüedad en la definición de "sistema crítico" | Medio | Definir criterios de clasificación antes del lanzamiento |
| Notificaciones no llegan o se ignoran | Medio | Definir canal de notificación confiable |

### Preguntas abiertas

1. ¿Quién tiene permiso para reclasificar el riesgo de una solicitud ya enviada?
2. ¿Puede un Tech Lead también ser Engineer (solicitar cambios)?
3. ¿Cuál es el SLA esperado por nivel de revisión?
4. ¿La agenda de ejecución (`SCHEDULED`) la define el Engineer o el Operations Reviewer?
5. ¿Qué sistema de notificaciones se usará en el MVP (email, notificación interna)?
6. ¿Se requiere historial de versiones de una solicitud si se piden cambios (`CHANGES_REQUESTED`)?


## Requerimientos funcionales

**RF-01.** El sistema debe permitir que un Engineer cree solicitudes de cambio técnico.

**RF-02.** El sistema debe permitir enviar una solicitud desde `DRAFT` hacia revisión.

**RF-03.** El sistema debe clasificar los cambios por riesgo: `LOW`, `MEDIUM` y `HIGH`.

**RF-04.** El sistema debe asignar aprobadores según el nivel de riesgo.

**RF-05.** Un cambio `LOW` requiere aprobación de Tech Lead.

**RF-06.** Un cambio `MEDIUM` requiere aprobación de Tech Lead y Operations Reviewer.

**RF-07.** Un cambio `HIGH` requiere aprobación de Tech Lead, Operations Reviewer y Security Reviewer.

**RF-08.** Todo cambio `MEDIUM` o `HIGH` debe incluir un plan de rollback.

**RF-09.** El sistema debe impedir ejecutar un cambio que no esté aprobado.

**RF-10.** El sistema debe permitir que el solicitante o un Admin cancelen una solicitud antes de aprobación.

**RF-11.** El sistema debe registrar el resultado de la ejecución del cambio como `SCHEDULED`, `EXECUTED` o `FAILED`.

**RF-12.** Si la ejecución falla, el sistema debe registrar el motivo del fallo.

**RF-13.** Una solicitud ejecutada no puede volver a estado de revisión.

**RF-14.** El sistema debe registrar auditoría de acciones: creación, envío, revisión, aprobación, rechazo, ejecución y fallo.

**RF-15.** El sistema debe notificar a los stakeholders cuando cambie el estado de una solicitud.

## Requerimientos no funcionales

**RNF-01.** El sistema debe garantizar trazabilidad completa de cada cambio técnico.

**RNF-02.** El sistema debe evitar que se salte el flujo formal de aprobación.

**RNF-03.** El sistema debe mantener registro histórico de solicitudes, aprobaciones y ejecuciones.

**RNF-04.** El sistema debe separar responsabilidades por rol.

**RNF-05.** El MVP no debe ejecutar cambios reales en producción.

**RNF-06.** El sistema debe registrar eventos relevantes para auditoría.
