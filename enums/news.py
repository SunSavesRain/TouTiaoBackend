from enum import Enum

class NewsStatus(str, Enum):
    draft = "draft"
    published = "published"
    offline = "offline"

