import json

ALL_PERMISSIONS = {
    "sales": [],
    "inventory": [
        # Write permissions
        "can_add_new_product",
        "can_delete_product",
        # Read permissions
        "can_view_inventory_value",
        "can_view_cogs",
    ],
    "orders": [],
    "tracker": [],
    "analytics": [
        "can_view_profits",
        "can_view_loss",
    ],
}

# permissions_str = "sale:view_audit sale:view_history inventory:update_quantity"


def parse_permission_str(permission_str: str):
    if permission_str == "*":
        return ALL_PERMISSIONS
    permission_group = {}
    permissions = permission_str.split(" ")
    headers = set((permission.split(":")[0].strip() for permission in permissions))
    for header in headers:
        # permission_group = {
        #   'sale' : ['view_audit', 'view_history'],
        #   'inventory' : ['update_quantity']
        # }
        permission_group[header] = [
            permission.split(":")[1].strip()
            for permission in permissions
            if permission.startswith(header)
        ]
    return permission_group


def create_permission_str(permissions: dict[str, list]):
    if permissions == "*":
        return "*"
    permission_str = ""
    for header, group in permissions.items():
        group_str = " ".join(f"{header}:{perm}" for perm in group)
        permission_str += " " + group_str
    return permission_str.strip()
