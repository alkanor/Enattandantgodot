from persistent.datastructure.alias import ALIAS
from persistent.datastructure.list import LIST
from .answer_statement import AnswerEnumAlias


MultipleAnswersStatement = ALIAS(LIST(AnswerEnumAlias), "MultipleAnswers")

#TODO: wire it
