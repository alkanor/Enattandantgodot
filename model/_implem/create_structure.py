from .create_model import db_engine


bases = []

def create_structure():
    for base in bases:
        base.metadata.create_all(db_engine)

def add_base(base):
    bases.append(base)
