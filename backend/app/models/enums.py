import enum

class DataSourceType(str, enum.Enum):
    REAL_PUBLIC = "REAL_PUBLIC"
    SYNTHETIC = "SYNTHETIC"
    USER_UPLOADED = "USER_UPLOADED"

class WellType(str, enum.Enum):
    ACTIVE = "ACTIVE"
    HISTORICAL = "HISTORICAL"
    EXPLORATORY = "EXPLORATORY"

class WellStatus(str, enum.Enum):
    DRILLING = "DRILLING"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    SUSPENDED = "SUSPENDED"

class EventSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EventType(str, enum.Enum):
    MUD_LOSS = "MUD_LOSS"
    STUCK_PIPE = "STUCK_PIPE"
    KICK = "KICK"
    TORQUE_SPIKE = "TORQUE_SPIKE"
    WELL_CONTROL = "WELL_CONTROL"
    EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE"

class UserRole(str, enum.Enum):
    ENGINEER = "ENGINEER"
    ADMIN = "ADMIN"