from sqlalchemy.orm import sessionmaker


def create_session():
    from .db_engine import db_engine, create_engine

    if not db_engine:
        create_engine()
        from .db_engine import db_engine
        assert(db_engine)
    
    return sessionmaker(bind=db_engine, expire_on_commit=False)()


if __name__ == "__main__":
    create_session()
