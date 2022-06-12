# TODO: implement real shit here
from sqlalchemy import create_engine as _create_engine

#from core.wiring.resolve import resolve


#db_path = resolve("db_path")
db_path = 'output.db'

db_engine = None

def create_engine():
    global db_engine

    db_engine = _create_engine('sqlite:///'+db_path, \
                                #connect_args={'timeout': 15}, \
                                echo=False)
    
    from model.general import sql_bases

    # create all currently existing metadata for declared bases
    (*map(lambda x: x.metadata.create_all(db_engine), sql_bases), )

    return db_engine


def get_engine():
    global db_engine
    return db_engine
