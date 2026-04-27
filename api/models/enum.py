from enum import Enum

class StatusOfUser(str, Enum):
    new = "new_user",
    common = "common_user",
    admin = "admin_user" # (руководитель)
