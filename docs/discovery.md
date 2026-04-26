# Discovery - ChangeFlow

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

## Estados del flujo principal

Flujo sugerido:

```text
DRAFT -> SUBMITTED -> TECH_REVIEW -> OPS_REVIEW -> SECURITY_REVIEW -> APPROVED -> SCHEDULED -> EXECUTED
                         \-> CHANGES_REQUESTED
                         \-> REJECTED
                         \-> CANCELLED
                         \-> FAILED