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
converter_str_lower: Callable[[str], str] = create_string_converter(str.lower)
"""Converts the provided string to lower case."""
converter_str_upper: Callable[[str], str] = create_string_converter(str.upper)
"""Converts the provided string to upper case."""
converter_str_capital: Callable[[str], str] = create_string_converter(str.capitalize)
"""Converts the provided string to capital case."""
converter_str_title: Callable[[str], str] = create_string_converter(str.title)
"""Converts the provided string to title case."""

# Integer validators
validator_pos_int: Callable[[..., ..., ...], None] = validators.and_(validators.instance_of(int), validators.gt(0))
"""Validates the provided value to be a positive integer."""
validator_pos_z_int: Callable[[..., ..., ...], None] = validators.and_(validators.instance_of(int), validators.ge(0))
"""Validates the provided value to be a non-negative integer."""
validator_neg_int: Callable[[..., ..., ...], None] = validators.and_(validators.instance_of(int), validators.lt(0))
"""Validates the provided value to be a negative integer."""
validator_neg_z_int: Callable[[..., ..., ...], None] = validators.and_(validators.instance_of(int), validators.le(0))
"""Validates the provided value to be a non-positive integer."""
