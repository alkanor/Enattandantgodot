
def metaclass_for_sqlalchemy_with_subclass(SubClass, sub_ormobj_name=None, commit=True):

    class _To_Inherit():

        __metadataclass__ = SubClass

        @classmethod
        def GET(cls, session, **argv):
            does_exist = session.query(cls.__metadataclass__).filter_by(**argv).one_or_none()
            if does_exist:
                return cls(session, does_exist)
            else:
                return cls(session, **argv)

        @classmethod
        def GET_FROM_SUB(cls, session, **argv):
            subobj = cls.GET(session, **argv)
            if not subobj:
                return None

            if sub_ormobj_name:
                print(sub_ormobj_name, getattr(subobj, sub_ormobj_name))
                print("IS EXIST")
                print(subobj)
                does_exist = session.query(cls).filter(getattr(subobj, sub_ormobj_name) == subobj).one_or_none()
                if does_exist:
                    return does_exist

            return subobj
        
        @classmethod
        def GET_CREATE(cls, session, **argv):
            base_obj = cls.GET_FROM_SUB(session, **argv)
            print("BASCASE")
            if base_obj:
                print("NEXTCSE")
                print(base_obj)
                if commit and base_obj.id is None: # check if the subclass has no related persistent data (id == none) and commit if available
                    #session.add(base_obj.metadata)
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
                assert(to_delete.__class__ == cls or element.__class__ == SubClass)
                if to_delete.__class__ != cls:
                    if not element.id:
                        return
                    to_delete = cls.GET_FROM_SUB(session, id=element.id)
            else:
                to_delete = cls.GET_FROM_SUB(session, **argv)
                print("DELETING")
                print(to_delete)
                if to_delete is None:
                    return
            to_delete.clear(session)
                
        @classmethod
        def GET_COND(cls, session, condition):
            from_subobj = SubClass.GET_COND(session, condition)
            return list([cls(session, m) for m in from_subobj])

    return _To_Inherit
