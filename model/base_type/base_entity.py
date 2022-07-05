from sqlalchemy.orm.exc import UnmappedInstanceError

from model.base import BaseAndMetaFromAttrDict


def BasicEntity(tablename, columns_dict, ToInherit=None, slug=None):
    if ToInherit:
        if isinstance(ToInherit, list):
            bases = ToInherit
        else:
            bases = [ToInherit]
    else:
        bases = [BaseAndMetaFromAttrDict(columns_dict)[0]]

    every_repr = [b for b in bases if "__repr__" in b.__dict__]

    class _BasicEntity(*bases):

        __tablename__ = tablename
        __slug__ = slug

        def __init__(self, *args, **argv):
            cur_dict = argv
            for base in bases[::-1]:
                if base != bases[0]: # in this case construct the object possibly with args
                    base.__init__(self, *args, **cur_dict)
                else: # the default sql alchemy constructor does not like non-argv arguments so remove it
                    base.__init__(self, **cur_dict)
                cur_dict = {k: v for k, v in self.__dict__.items() if k[0] != '_'} # replace the current dict with the attributes set in base constructors

        @classmethod
        def GET(cls, session, **argv):
            filtered_result = session.query(cls)
            for colname in columns_dict:
                filtered_result = filtered_result.filter(getattr(cls, colname) == argv[colname] if argv.get(colname) else True)

            result = list(filtered_result.all())
            if len(result) == 1:
                return result[0]
            else:
                return None if not result else result

        @classmethod
        def GET_ONE(cls, session, **argv):
            filtered_result = session.query(cls)
            for colname in columns_dict:
                filtered_result = filtered_result.filter(getattr(cls, colname) == argv[colname] if argv.get(colname) else True)

            result = list(filtered_result.all())
            return result[0]

        @classmethod
        def GET_CREATE(cls, session, *args, **argv):
            existing = cls.GET(session, **argv)
            if existing:
                return existing
            newobj = cls(*args, **argv)
            session.add(newobj)
            session.commit()
            for k, v in argv.items():
                if not hasattr(newobj, k):
                    setattr(newobj, k, v)
            return newobj

        @classmethod
        def NEW(cls, session, *args, **argv):
            newobj = cls(*args, **argv)
            session.add(newobj)
            session.commit()
            return newobj

        @classmethod
        def DELETE(cls, session, **argv):
            existing = cls.GET(session, **argv)
            if existing is None:
                return
            try:
                session.delete(existing)
            except UnmappedInstanceError:
                for x in existing:
                    session.delete(x)
            session.commit()

        @classmethod
        def GET_COND(cls, session, condition):
            return session.query(cls).filter(condition).all()

        def __repr__(self):
            if every_repr:
                return "\n".join([repr_cls.__dict__['__repr__'](self) for repr_cls in every_repr])
            else:
                textual = ' - '.join(map(lambda x: x + " " + repr(getattr(self, x)), columns_dict))
                return f'{self.__tablename__} : [{textual}]'

    return _BasicEntity
