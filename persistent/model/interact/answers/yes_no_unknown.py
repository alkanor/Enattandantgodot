from .answer_statement import AnswerStatement
from enum import Enum


class YesNoUnknown(Enum):

    YES = AnswerStatement.GET_CREATE("YES")
    NO = AnswerStatement.GET_CREATE("NO")
    UNKNOWN = AnswerStatement.GET_CREATE("UNKNOWN")
