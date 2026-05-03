from app.domain.enums import Role, Permission

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
