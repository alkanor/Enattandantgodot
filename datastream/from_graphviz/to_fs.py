import os


def Graphviz_to_fs(graphviz_obj, fs_path, view=False, format='svg'):
    fname = os.path.basename(fs_path)
    dirname = os.path.dirname(fs_path)
    graphviz_obj.render(directory=dirname, filename=fname, view=view, format=format)
    return fs_path
