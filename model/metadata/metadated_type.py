def metaclass_for_metadata(MetadataClass, commit=True):

    class _To_Inherit():

        __metadataclass__ = MetadataClass

        @classmethod
        def GET(cls, session, **argv):
            metadata = MetadataClass.GET(session, **argv)
            if not metadata:
                return None
            else:
                return cls(session, metadata)
        
        @classmethod
        def GET_CREATE(cls, session, **argv):
            base_obj = cls.GET(session, **argv)
            if base_obj:
                return base_obj
            else:
                return cls.NEW(session, **argv)

        @classmethod
        def NEW(cls, session, **argv):
            new_metadata = MetadataClass.NEW(session, **argv)
            new_obj = cls(session, new_metadata)
            if ccommit:
                session.add(new_obj)
                session.commit()
            return new_obj

        @classmethod
        def DELETE(cls, session, element=None, **argv):
            to_delete = element
            if to_delete:
                assert(to_delete.__class__ == cls or element.__class__ == MetadataClass)
                if to_delete.__class__ != cls:
                    if not element.id:
                        return
                    to_delete = cls.GET(session, id=element.id)
            else:
                to_delete = cls.GET(session, **argv)
                if to_delete is None:
                    return
            to_delete.clear(session)
                
        @classmethod
        def GET_COND(cls, session, condition):
            from_metadata = MetadataClass.GET_COND(session, condition)
            return list([cls(session, m) for m in from_metadata])

    return _To_Inherit
