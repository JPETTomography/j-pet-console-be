from enum import Enum, unique
@unique
class Role(Enum):
    SHIFTER = 'Shifter'
    COORDINATOR = 'Coordinator'
    ADMIN = 'Admin'
@unique
class Status(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DAMAGED = "damaged"
    IN_REPAIR = "in-repair"
    COMMISSIONED = "commissioned"
    DECOMMISSIONED = "decommissioned"

@unique
class ExperimentStatus(Enum):
    DRAFT = "draft"
    ONGOING = "ongoing"
    CLOSED = "closed"
    ARCHIVED = "archived"