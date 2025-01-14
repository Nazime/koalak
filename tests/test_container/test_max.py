import operator

import pytest
from koalak import containers
from koalak.containers import Container, DictContainer, first

from .utils import Person, people_data, people_dict_data


# TODO: fix the problem with lazy fixture!
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
def test_method_max_with_int_argument(
    container_type, accessor_function, data, iter_func, use_function
):
    data = iter_func(data)

    # Determine the appropriate 'first' function based on the test case
    if use_function:
        # Use the function
        function = containers.max

    else:
        # Use the method of the container class, first arg will be "self"
        function = container_type.max
        data = container_type(data)

    result = function(data, "age")
    assert accessor_function(result, "name") == "Charlie"
    assert accessor_function(result, "age") == 35
