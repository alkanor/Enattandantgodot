from persistent.datastructure.enum import ENUM


def craft_enum_for_states(name, values):
    def sub(session):
        return ENUM(name, values, session)
    return sub
