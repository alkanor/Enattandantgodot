from persistent.datastructure import alias
from persistent.base_type.string import String
from persistent.datastructure.list import LIST


AnswerStatement = alias(String, "AnswerEnum")
MultipleAnswersStatement = alias(LIST(AnswerStatement), "MultipleAnswers")
