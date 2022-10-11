from .response_statement import ResponseStatement
from enum import Enum


class YesNo(Enum):

    YES = ResponseStatement.GET_CREATE("YES")
    NO = ResponseStatement.GET_CREATE("NO")
