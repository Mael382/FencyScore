from typing import Callable, Final
from attrs import validators
from functools import lru_cache

# Constants
CACHE_SIZE: Final[int] = 128


def create_string_converter(transform_func: Callable[[str], str]) -> Callable[[str], str]:
	"""
	Creates a string converter function that applies a transformation to stripped string inputs and caches the results.

	Args:
        transform_func: A callable that transforms a string.

    Returns:
        A cached callable that strips and applies the transformation to a string.
	"""

	def pre_process(value: str) -> str:
		return transform_func(value.strip())

	@lru_cache(maxsize=CACHE_SIZE)
	def converter(value: str) -> str:
		return pre_process(value)

	return converter


# String converters
converter_str_upper: Callable[[str], str] = create_string_converter(str.upper)
"""TODO"""  # TODO
converter_str_title: Callable[[str], str] = create_string_converter(str.title)
"""TODO"""  # TODO

# Integer validators
validator_pos_int: Callable[[..., ..., ...], None] = validators.and_(validators.instance_of(int), validators.gt(0))
"""TODO"""  # TODO
validator_pos_z_int: Callable[[..., ..., ...], None] = validators.and_(validators.instance_of(int), validators.ge(0))
"""TODO"""  # TODO
