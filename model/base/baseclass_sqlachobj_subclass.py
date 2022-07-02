def baseclass_for_sqlalchemy_with_subclass(SubClass, sub_ormobj_name=None, commit=True):
    class _To_Inherit:

        __metadataclass__ = SubClass

        @classmethod
        def GET(cls, session, **argv):
            if 'id' in argv and len(argv) == 1:
                fullobj_exist = session.query(cls).filter_by(**argv).one_or_none()
                return fullobj_exist

            target_obj_exist = session.query(cls.__metadataclass__).filter_by(**argv).one_or_none()
            if target_obj_exist:
                fullobj_exist = session.query(cls).filter(
                    getattr(cls, sub_ormobj_name) == target_obj_exist).one_or_none()
                if fullobj_exist:
                    return fullobj_exist
                return cls(session, target_obj_exist)
            return None

        @classmethod
        def GET_CREATE(cls, session, **argv):
            base_obj = cls.GET(session, **argv)
            if base_obj:
                if commit and base_obj.id is None:  # check if the subclass has no related persistent data (id == none) and commit if available
                    session.add(base_obj)
                    session.commit()
                return base_obj
            else:
                return cls.NEW(session, **argv)

        @classmethod
        def NEW(cls, session, **argv):
            new_subobj = SubClass.NEW(session, **argv)
            new_obj = cls(session, new_subobj)
            if commit:
                session.add(new_obj)
                session.commit()
            return new_obj

        @classmethod
        def DELETE(cls, session, element=None, **argv):
            to_delete = element
            if to_delete:
                assert (to_delete.__class__ == cls or element.__class__ == SubClass)
                if to_delete.__class__ != cls:
                    if not element.id:
                        return
                    to_delete = session.query(cls).filter(getattr(cls, sub_ormobj_name) == element).one_or_none()
            else:
                to_delete = cls.GET(session, **argv)

            if not to_delete:
                return
            to_delete.clear(session)

        @classmethod
        def GET_COND(cls, session, condition):
            from_subobj = SubClass.GET_COND(session, condition)
            return list([cls(session, m) for m in from_subobj])

    return _To_Inherit
