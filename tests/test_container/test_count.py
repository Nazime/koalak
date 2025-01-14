import operator

import pytest
from koalak import containers
from koalak.containers import Container, DictContainer

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
def test_count_without_args(
    container_type, accessor_function, data, iter_func, use_function
):
    data = iter_func(data)

    # Determine the appropriate 'first' function based on the test case
    if use_function:
        # Use the function
        function = containers.count

    else:
        # Use the method of the container class, first arg will be "self"
        function = container_type.count
        data = container_type(data)

    assert function(data) == 3


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
def test_count_with_int_arg(
    container_type, accessor_function, data, iter_func, use_function
):
    data = iter_func(data)

    # Determine the appropriate 'first' function based on the test case
    if use_function:
        # Use the function
        function = containers.count

    else:
        # Use the method of the container class, first arg will be "self"
        function = container_type.count
        data = container_type(data)

    assert function(data, money=50) == 2
