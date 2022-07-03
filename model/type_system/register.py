
types = {}

# python types singleton to avoid redefining same parametrized types and try avoiding complex errors
def register_type(typename, depends_on):
    def sub(f):
        def called_f(*args, **argv):
            dependancies = (typename, *depends_on(*args, **argv), )
            print(f"Dependancies in type register {dependancies}")
            
            if dependancies in types: # ignore created type as already existing, to avoid incoherencies and create kind of type singleton
                return types[dependancies]
            
            # otherwise register the freshly created type
            types[dependancies] = f(*args, **argv)
            return types[dependancies]

        return called_f
    return sub
