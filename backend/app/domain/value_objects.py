from app.domain.enums import ApprovalArea, Permission, RiskLevel, Role

ROLE_PERMISSIONS: dict[Role, list[Permission]] = {
    Role.ENGINEER: [
        Permission.CREATE_CHANGE,
    ],
    Role.TECH_LEAD: [
        Permission.CREATE_CHANGE,
        Permission.REVIEW_TECH,
    ],
    Role.OPS_REVIEWER: [
        Permission.REVIEW_OPS,
    ],
    Role.SECURITY_REVIEWER: [
        Permission.REVIEW_SECURITY,
    ],
    Role.ADMIN: [
        Permission.CREATE_CHANGE,
        Permission.REVIEW_TECH,
        Permission.REVIEW_OPS,
        Permission.REVIEW_SECURITY,
        Permission.MANAGE_USERS,
        Permission.VIEW_ALL,
        Permission.CANCEL_ANY,
    ],
}


# Función auxiliar: mapea un rol al área de aprobación que puede cubrir.
ROLE_TO_AREA: dict[Role, ApprovalArea] = {
    Role.TECH_LEAD: ApprovalArea.TECH,
    Role.OPS_REVIEWER: ApprovalArea.OPS,
    Role.SECURITY_REVIEWER: ApprovalArea.SECURITY,
}


# Función auxiliar: áreas requeridas por nivel de riesgo.
RISK_REQUIRED_AREAS: dict[RiskLevel, list[ApprovalArea]] = {
    RiskLevel.LOW: [ApprovalArea.TECH],
    RiskLevel.MEDIUM: [ApprovalArea.TECH, ApprovalArea.OPS],
    RiskLevel.HIGH: [ApprovalArea.TECH, ApprovalArea.OPS, ApprovalArea.SECURITY],
}
