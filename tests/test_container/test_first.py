import operator

import pytest
from koalak.containers import Container, DictContainer, first

from .utils import Person, people_data, people_dict_data


@pytest.mark.skip("lazyfixture")
# @pytest.mark.parametrize("use_function", [True, False])
# @pytest.mark.parametrize("iter_func", [list, iter])
# @pytest.mark.parametrize(
#     "container_type,accessor_function,data",
#     [
#         (Container, getattr, pytest.lazy_fixture("people_data")),
#         (DictContainer, operator.getitem, pytest.lazy_fixture("people_dict_data")),
#     ],
# )
def test_first_without_arguments(
    container_type, accessor_function, data, iter_func, use_function
):
    data = iter_func(data)

    # Determine the appropriate 'first' function based on the test case
    if use_function:
        # Use the function
        first_function = first

    else:
        # Use the method of the container class, first arg will be "self"
        first_function = container_type.first
        data = container_type(data)

    # Perform the test
    result = first_function(data)
    assert accessor_function(result, "name") == "Alice"
    assert accessor_function(result, "age") == 30
    assert accessor_function(result, "tags") == ["friendly", "smart"]


@pytest.mark.skip("lazyfixture")
# @pytest.mark.parametrize("use_function", [True, False])
# @pytest.mark.parametrize("iter_func", [list, iter])
# @pytest.mark.parametrize(
#     "container_type,accessor_function,data",
#     [
#         (Container, getattr, pytest.lazy_fixture("people_data")),
#         (DictContainer, operator.getitem, pytest.lazy_fixture("people_dict_data")),
#     ],
# )
def test_method_first_with_str_argument(
    container_type, accessor_function, data, iter_func, use_function
):
    data = iter_func(data)

    # Determine the appropriate 'first' function based on the test case
    if use_function:
        # Use the function
        first_function = first

    else:
        # Use the method of the container class, first arg will be "self"
        first_function = container_type.first
        data = container_type(data)

    result = first_function(data, name="Alice")
    assert accessor_function(result, "name") == "Alice"
    assert accessor_function(result, "age") == 30
    assert accessor_function(result, "tags") == ["friendly", "smart"]


@pytest.mark.skip("lazyfixture")
# @pytest.mark.parametrize("use_function", [True, False])
# @pytest.mark.parametrize("iter_func", [list, iter])
# @pytest.mark.parametrize(
#     "container_type,accessor_function,data",
#     [
#         (Container, getattr, pytest.lazy_fixture("people_data")),
#         (DictContainer, operator.getitem, pytest.lazy_fixture("people_dict_data")),
#     ],
# )
def test_method_first_with_int_argument(
    container_type, accessor_function, data, iter_func, use_function
):
    data = iter_func(data)

    # Determine the appropriate 'first' function based on the test case
    if use_function:
        # Use the function
        first_function = first

    else:
        # Use the method of the container class, first arg will be "self"
        first_function = container_type.first
        data = container_type(data)

    result = first_function(data, age=35)
    assert accessor_function(result, "name") == "Charlie"
    assert accessor_function(result, "age") == 35
    assert accessor_function(result, "tags") == ["friendly"]


@pytest.mark.skip("lazyfixture")
# @pytest.mark.parametrize("use_function", [True, False])
# @pytest.mark.parametrize("iter_func", [list, iter])
# @pytest.mark.parametrize(
#     "container_type,accessor_function,data",
#     [
#         (Container, getattr, pytest.lazy_fixture("people_data")),
#         (DictContainer, operator.getitem, pytest.lazy_fixture("people_dict_data")),
#     ],
# )
def test_method_first_not_found(
    container_type, accessor_function, data, iter_func, use_function
):
    data = iter_func(data)

    # Determine the appropriate 'first' function based on the test case
    if use_function:
        # Use the function
        first_function = first

    else:
        # Use the method of the container class, first arg will be "self"
        first_function = container_type.first
        data = container_type(data)

    with pytest.raises(ValueError):
        first_function(data, name="Not exists")
