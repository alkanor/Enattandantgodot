from .state import craft_enum_for_states


_StartedFinished = ["Started", "Finished"]

StartedFinished_for_session = craft_enum_for_states("StartedFinished", _StartedFinished)
