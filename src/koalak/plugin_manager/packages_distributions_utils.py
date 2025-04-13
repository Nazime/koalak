import importlib.metadata
import os
import types
from importlib.metadata import PathDistribution

__all__ = "module_to_distribution"

# TODO: clean and test this code!

_map_modules_to_distribution = {}
_seen_root_packages_names = set()


def module_to_package_distribution_name(module: types.ModuleType | str) -> str:
    """All this module is here for this function,"""
    # Declare global variables for caching
    global _map_modules_to_distribution
    global _seen_root_packages_names

    # Normalize argument
    if isinstance(module, types.ModuleType):
        module_name = module.__name__
    else:
        module_name = module

    # get root package
    root_package_name = module_name.split(".")[0]

    # Check if we already parsed the root_package
    if root_package_name in _seen_root_packages_names:
        return _map_modules_to_distribution[module_name]

    # Get all modules from all distributions for that given package
    distributions_names = importlib.metadata.packages_distributions()[root_package_name]
    distributions_names = list(set(distributions_names))
    for distribution_name in distributions_names:
        distribution = importlib.metadata.distribution(distribution_name)
        modules = get_modules_from_distribution(distribution, root_package_name)
        for module in modules:
            _map_modules_to_distribution[module] = distribution_name

    # add to cache
    _seen_root_packages_names.add(root_package_name)
    return _map_modules_to_distribution[module_name]


def get_modules_from_distribution(
    distribution: PathDistribution, root_package_name
) -> list[str]:
    # If distribution is installed in 'editable' mode, check the editable file
    #  ex: "venv/lib/python3.13/site-packages/__editable__.koalak-0.3.4.pth
    if is_editable_distribution(distribution):
        editable_filename = [
            str(e) for e in distribution.files if str(e).startswith("__editable__")
        ]
        if len(editable_filename) != 1:
            raise ValueError(
                f"distribution.files for '{distribution.name}' expect to have one file starting with __editable__ not {len(editable_filename)}"
            )
        editable_filename = editable_filename[0]
        editable_filepath = distribution.locate_file(editable_filename)
        with open(editable_filepath) as f:
            src_filepath = f.read().strip()
        return get_modules_from_root_package(src_filepath)
    else:
        return get_modules_from_distribution_files(distribution, root_package_name)


def get_modules_from_root_package(directory: str) -> list[str]:
    """Return all modules from a given filepath that represent a root dir"""
    modules = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(".py"):
                continue

            # Create the module path by removing the .py extension
            module_path = os.path.relpath(os.path.join(root, file), directory)
            module_name = _clean_modulename(module_path)

            # Add the module to the list
            modules.append(module_name)
    return modules


def get_modules_from_distribution_files(
    distribution: PathDistribution, root_package_name: str
) -> list[str]:
    modules = []
    for file in distribution.files:
        file = str(file)
        if not file.endswith(".py"):
            continue

        if not file.startswith(root_package_name):
            continue
        module_name = _clean_modulename(file)
        modules.append(module_name)
    return modules


def is_editable_distribution(dist):
    # Look for the __editable__ marker file in the distribution files
    for file in dist.files:
        if file.name.startswith("__editable__"):
            return True  # It's an editable install
    return False


def _clean_modulename(module_name: str) -> str:
    module_name = module_name.removesuffix(".py")
    module_name = module_name.replace("/", ".").replace("\\", ".")
    # Handle __init__.py as a package
    if module_name.endswith("__init__"):
        # If it's __init__.py, treat it as a package, not a module
        module_name = module_name.removesuffix(".__init__")
    return module_name
