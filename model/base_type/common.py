
class CommonMethodBase:

    @classmethod
    def GET(cls, session, id):
        return session.query(cls).filter_by(id=id).one_or_none()

    @classmethod
    def GET_CREATE(cls, session, id):
        existing = cls.GET(session, id)
        return existing if existing else cls.NEW(session, id)

    @classmethod
    def NEW(cls, session, id):
        newobj = cls(id=id)
        session.add(newobj)
        session.commit()
        return newobj

    @classmethod
    def DELETE(cls, session, id):
        existing = cls.GET(session, id)
        if existing is None:
            return
        session.delete(existing)
        session.commit()

    @classmethod
    def GET_COND(cls, session, condition):
        return session.query(cls).filter(condition).all()

    def __repr__(self):
        return f'{self.id}'
