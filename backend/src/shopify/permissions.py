ALL_PERMISSIONS = {"sale": [], "inventory": [], "stock_port": [], "debt_tracker": []}

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
    permission_str = ""
    for header, group in permissions.items():
        group_str = " ".join(f"{header}:{perm}" for perm in group)
        permission_str += " " + group_str
    return permission_str.strip()
