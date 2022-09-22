import os


def graphviz_to_fs(graphviz_obj, fs_path, view=False, format='svg'):
    f_name = os.path.basename(fs_path)
    dir_name = os.path.dirname(fs_path)
    graphviz_obj.render(directory=dir_name, filename=f_name, view=view, format=format)
    return fs_path
