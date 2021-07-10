from importlib import import_module
from types import ModuleType
from os import listdir


def import_modules_from_dir(path_to_dir: str) -> list[ModuleType]:
    """
    Return list of imported modules in `path_to_dir`, not recursive,
    import all but `__init__.py` and `__main__.py`.

    Args:
    path_to_dir -- path to dir with modules from root of project

    if project tree is
    ```
    root
    ├──dir1
    │  ├──subdir
    │  │  ├──module1
    │  │  ├──module2
    ├──dir2
    ├──README.md
    ...
    ```

    path to dir should be `dir1/subdir` or `dir1/subdir/`
    """

    modules = []
    path_to_dir = path_to_dir if path_to_dir.endswith("/") else path_to_dir + "/"
    files = listdir(path_to_dir)
    for file in files:
        if not file.endswith(".py") or file in ("__init__.py", "__main__.py"):
            continue

        module = import_module(path_to_dir.replace("/", ".") + file[:-3])
        modules.append(module)
    return modules
