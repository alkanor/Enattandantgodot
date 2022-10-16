from persistent.datastructure.alias import ALIAS
from persistent.datastructure.list import LIST
from .answer_statement import AnswerStatement


MultipleAnswersStatement = ALIAS(LIST(AnswerStatement), "MultipleAnswers")
