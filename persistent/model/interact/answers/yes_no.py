from .answer_statement import AnswerStatement
from enum import Enum


class YesNo(Enum):

    YES = AnswerStatement.GET_CREATE("YES")
    NO = AnswerStatement.GET_CREATE("NO")
