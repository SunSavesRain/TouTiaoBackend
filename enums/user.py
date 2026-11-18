from enum import Enum

class Gender(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserStatus(str, Enum):
    active = "active"
    disabled = "disabled"
