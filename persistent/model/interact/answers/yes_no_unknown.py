from .answer_statement import craft_answer_for_session, AnswerStatement


class YesNoUnknown(AnswerStatement):

    @classmethod
    @craft_answer_for_session
    def YES(cls):
        pass

    @classmethod
    @craft_answer_for_session
    def NO(cls):
        pass

    @classmethod
    @craft_answer_for_session
    def UNKNOWN(cls):
        pass
