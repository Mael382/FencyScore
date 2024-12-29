from attrs import validators


def converter_str_upper(value: str) -> str:
	"""
	Converts a string to uppercase after stripping leading and trailing whitespace.

	:param value: The string to convert.
	:return: The stripped string in uppercase.
	"""
	return value.strip().upper()


def converter_str_title(value: str) -> str:
	"""
	Converts a string to title case after stripping leading and trailing whitespace.

	:param value: The string to convert.
	:return: The stripped string in title case.
	"""
	return value.strip().title()


validator_pos_int = validators.and_(validators.instance_of(int), validators.gt(0))
"""Validates a positive integers. Ensures that the value is an integer greater than 0."""


validator_pos_z_int = validators.and_(validators.instance_of(int), validators.ge(0))
"""Validates a non-negative integers. Ensures that the value is an integer greater than or equal to 0."""
