from .answer_statement import craft_answer_for_session, Statement
from enum import Enum


class YesNo(Statement, Enum):

    YES = craft_answer_for_session("YES")
    NO = craft_answer_for_session("NO")
