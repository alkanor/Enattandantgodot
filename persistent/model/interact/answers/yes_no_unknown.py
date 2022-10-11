from .response_statement import ResponseStatement
from enum import Enum


class YesNoUnknown(Enum):

    YES = ResponseStatement.GET_CREATE("YES")
    NO = ResponseStatement.GET_CREATE("NO")
    UNKNOWN = ResponseStatement.GET_CREATE("UNKNOWN")
