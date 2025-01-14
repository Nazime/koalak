import csv
from copy import deepcopy as builtin_deepcopy
from operator import getitem, setitem
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

ContainerKey = Union[str, List[str], Tuple[str], Callable[[Any], Any]]


T = TypeVar("T")


def normalize_to_list(value: Any) -> list:
    """
    Converts a value to a list if it is not already a list.

    Args:
        value (any): The value to normalize to a list.

    Returns:
        list: The value as a list, or the value itself if it's already a list.
    """
    return [value] if not isinstance(value, list) else value


class Container(Generic[T]):
    get = getattr
    set = setattr

    def __init__(
        self, data: List[T] = None, copy: bool = None, deepcopy=None, name: str = None
    ):
        if copy and deepcopy:
            raise ValueError("Can have only copy or deepcopy not both")
        if copy is None:
            copy = True
        if deepcopy is None:
            deepcopy = False

        if data is None:
            data = []
            copy = False

        if copy:
            data = list(data)
        elif deepcopy:
            data = builtin_deepcopy(data)

        self._data = data
        self.name = name

    # ================ #
    # MODIFIER METHODS #
    # ================ #
    def add(self, obj: T) -> None:
        self._data.append(obj)

    def extend(self, other: Iterable[T]) -> None:
        self._data.extend(other)

    def update_first(
        self, filter_query: Dict[str, Any], update_query: Dict[str, Any]
    ) -> T:
        """
        Update the first item matching the filter query with the update query.

        Args:
            filter_query (dict): A dictionary containing key-value pairs that are used to filter the list of dictionaries.
            update_query (dict): A dictionary containing key-value pairs that will be used to update the first matching dictionary.

        Returns:
            None.
        """

        for d in self.search(**filter_query):
            for key, value in update_query.items():
                self.set(d, key, value)
            return d
        raise ValueError("Not found")

    def update(
        self, filter_query: Dict[str, Any], update_query: Dict[str, Any]
    ) -> None:
        for d in self.search(**filter_query):
            for key, value in update_query.items():
                self.set(d, key, value)

    def delete_first(self, positional_criteria: dict = None, **criteria):
        """
        Delete the first dictionary in the list that matches the filter criteria.

        Args:
            positional_criteria: A dictionary containing the filter criteria for the dictionary to be deleted.
            **kwargs: The filter criteria for the dictionary to be deleted.

        Raises:
            ValueError: If both `params` and `**kwargs` are passed as arguments.
            ValueError: If no filter criteria is specified.
        """

        criteria = self._normalize_positional_and_keyword_criteria(
            positional_criteria, **criteria
        )

        for d in self.search(**criteria):
            self._data.remove(d)
            return
        raise ValueError("Not found")

    def delete(self, positional_criteria: dict = None, **criteria):
        criteria = self._normalize_positional_and_keyword_criteria(
            positional_criteria, **criteria
        )
        if not criteria:
            self._data = []
            return

        matched = list(self.search(**criteria))
        # FIXME: not optimized at ALL!!!
        self.data = [e for e in self if e not in matched]

    def clear(self) -> None:
        """
        Clears all items from the container.
        """
        self._data.clear()

    # ============= #
    # QUERY METHODS #
    # ============= #

    def filter(self, **criteria):
        # FIXME: what's the difference between filter and search!
        data = []
        for item in self.search(**criteria):
            data.append(item)
        return Container(data, copy=False)

    def first(self, pos_criteria: Dict = None, **criteria) -> T:
        criteria = self._normalize_positional_and_keyword_criteria(
            pos_criteria, **criteria
        )
        for item in self.search(**criteria):
            return item
        raise ValueError("No match found")

    def count(self, pos_criteria: Dict = None, **criteria) -> int:
        criteria = self._normalize_positional_and_keyword_criteria(
            pos_criteria, **criteria
        )
        if not criteria and isinstance(self._data, list):
            return len(self._data)
        count = 0
        for _ in self.search(**criteria):
            count += 1
        return count

    def count_values(self, key: ContainerKey):
        key_func = self._get_key_func(key)
        result = {}
        for e in self:
            value = key_func(e)
            if value not in result:
                result[value] = 0
            result[value] += 1
        return result

    def distinct(self, key, **criteria) -> List[Any]:
        # use list and set to keep the order
        key_func = self._get_key_func(key)
        results = []
        seen = set()
        for item in self.search(**criteria):
            value = key_func(item)
            if value not in seen:
                results.append(value)
                seen.add(value)
        return results

    def sum(self, key: ContainerKey, pos_criteria: Dict = None, **criteria) -> Any:
        criteria = self._normalize_positional_and_keyword_criteria(
            pos_criteria, **criteria
        )
        key_func = self._get_key_func(key)
        return sum(key_func(e) for e in self.search(**criteria))

    def mean(self, key):
        # TODO: implement me
        pass

    def max(self, key: Optional[ContainerKey] = None) -> T:
        """
        Returns the item with the maximum value based on the provided key.

        Args:
            key: A ContainerKey to determine the value used for comparison. If None,
                 compares the items themselves.

        Returns:
            The item with the maximum value.
        """

        key_func = self._get_key_func(key)
        return max(self._data, key=key_func)

    def min(self, key: Optional[ContainerKey] = None) -> T:
        """
        Returns the item with the minimum value based on the provided key.

        Args:
            key: A ContainerKey to determine the value used for comparison. If None,
                 compares the items themselves.

        Returns:
            The item with the minimum value.
        """
        key_func = self._get_key_func(key)
        return min(self._data, key=key_func)

    def sort(self, key: Optional[ContainerKey] = None, reverse: bool = None) -> None:
        """
        Sorts the items in the container based on the provided key.

        Args:
            key: A ContainerKey to determine the value used for sorting. If None,
                 sorts based on the items themselves.
            reverse: If True, sort in descending order; otherwise, ascending.

        """
        if reverse is None:
            reverse = False
        key_func = self._get_key_func(key)
        self._data.sort(key=key_func, reverse=reverse)

    def groupby(self, key: ContainerKey) -> Iterable[Tuple[Any, "Container[T]"]]:
        result = {}
        key_func = self._get_key_func(key)
        for item in self:
            group_key = key_func(item)
            if group_key not in result:
                result[group_key] = Container(name=f"groupby[{key}={group_key}])")
            result[group_key].add(item)
        return result

    def search(
        self,
        pos_criteria: Dict = None,
        *,
        search=None,
        searchable_fields=None,
        **criteria,
    ) -> Iterable[T]:
        """
        Searches through an iterable of objects based on specified criteria.

        Args:
            iterable (iter): An iterable of objects to search through.
            **kwargs: Search criteria in the form of key-value pairs, where the key
                      is the attribute name and the value is the criteria.

        Returns:
            iter: A generator of objects matching the search criteria.
        """

        criteria = self._normalize_positional_and_keyword_criteria(
            pos_criteria, **criteria
        )
        # FIXME: search and searchable_fields not in criteria?
        # Clean criteria
        cleaned_criteria = []
        for key, value in criteria.items():
            if value is None:
                continue
            if "__" in key:
                key, operator = key.split("__", maxsplit=1)
            else:
                operator = "default"
            value = normalize_to_list(value)
            cleaned_criteria.append((key, value, operator))

        for item in self._data:
            if search:
                if searchable_fields is None:
                    searchable_fields = self._get_searchable_fields(item)
                if not self._search_all_fields(item, search, searchable_fields):
                    continue
            if all(
                self._matches_criteria(item, key, search_value, operator)
                for key, search_value, operator in cleaned_criteria
            ):
                yield item

    def print(self):
        for e in self:
            print(e)

    def show(self, fields):
        # TODO: forgot what this function does
        if not isinstance(fields, list):
            fields = [fields]

        data = []
        for e in self.data:
            entry = {}
            for field in fields:
                if field in e:
                    entry[field] = e[field]
            if entry:
                data.append(entry)
        return self.__class__(data)

    def unique(self):
        # FIXME: works only with dicts
        seen = set()
        result = []
        for d in self:
            d_tuple = tuple(sorted(d.items()))
            if d_tuple in seen:
                continue
            seen.add(d_tuple)
            result.append(d)
        return self.__class__(result)

    # ============= #
    # CLASS METHODS #
    # ============= #
    @classmethod
    def from_csv(cls, filepath):
        with open(filepath) as file:
            reader = csv.DictReader(file)
            return cls(list(reader))

    # ============== #
    # DUNDER METHODS #
    # ============== #
    def __iter__(self) -> Iterable[T]:
        yield from self._data

    def __str__(self) -> str:
        if self.name:
            str_name = self.name
        else:
            str_name = ""
        return f"{Container.__name__}({str_name})"

    def __repr__(self) -> str:
        return self.__str__()

    def __getitem__(self, item) -> T:
        return self._data[item]

    def __len__(self) -> int:
        return len(self._data)

    def __eq__(self, other):
        if isinstance(other, Container):
            return self._data == other._data
        return ValueError("Can not compare different types")

    # =============== #
    # PRIVATE METHODS #
    # =============== #
    def _get_key_func(self, key: Optional[ContainerKey]) -> Callable[[Any], Any]:
        if key is None:
            return lambda x: x
        elif isinstance(key, str):
            return lambda item: self.get(item, key)
        elif isinstance(key, (list, tuple)):
            return lambda item: tuple(self.get(item, k) for k in key)
        elif callable(key):
            return key
        else:
            raise TypeError("Invalid type for 'key' in groupby")

    def _matches_criteria(
        self, item: object, key: str, search_value: any, operator: str
    ) -> bool:
        """
        Checks if an object's attribute matches the specified criteria based on an operator.

        Args:
            item (object): The object to check.
            key (str): The attribute key to check on the object.
            value (any): The value to compare against the object's attribute.
            operator (str): The operator defining how to compare the value with the object's attribute.

        Returns:
            bool: True if the object's attribute matches the criteria, False otherwise.
        """
        item_value = self.get(item, key)
        # debug(item, key, search_value, operator, item_value)
        if operator == "default":
            if isinstance(item_value, list):
                return any(v in item_value for v in search_value)
            else:
                return any(v == item_value for v in search_value)
        elif operator == "not":
            if isinstance(item_value, list):
                return all(v not in item_value for v in search_value)
            else:
                return all(v != item_value for v in search_value)
        elif operator == "eq":
            return search_value == item_value
        elif operator == "ne":
            return search_value != item_value
        elif operator == "lt":
            return item_value < search_value
        elif operator == "le":
            return item_value <= search_value
        elif operator == "gt":
            return item_value > search_value
        elif operator == "ge":
            return item_value >= search_value
        elif operator == "in":
            return item_value in search_value
        elif operator == "nin":
            return item_value not in search_value
        elif operator == "key__":
            raise ValueError
        elif operator == "search__":
            raise ValueError
        else:
            raise ValueError(f"Unsupported operator '{operator}'")

    def _search_all_fields(self, item, search, searchable_fields):
        # TODO: search as list?
        search = search.lower()
        for field_name in searchable_fields:
            field = self.get(item, field_name)
            field_as_str = str(field).lower()
            if search in field_as_str:
                return True
        return False

    def _get_searchable_fields(self, item):
        if isinstance(item, dict):
            return list(item.keys())

        fields_names = []
        for attribute_name in dir(item):
            # remove private attributes
            if attribute_name.startswith("_"):
                continue
            attribute = self.get(item, attribute_name)
            if callable(attribute):
                continue
            fields_names.append(attribute_name)

        return fields_names

    def _normalize_positional_and_keyword_criteria(
        self, positional_criteria, **criteria
    ):
        if positional_criteria is not None and criteria:
            raise ValueError("Cannot use both positional criteria and keyword criteria")
        if positional_criteria is not None:
            criteria = positional_criteria
        return criteria


class DictContainer(Container):
    get = getitem
    set = setitem
