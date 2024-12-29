from datetime import date
from enum import StrEnum, auto, unique
from typing import Optional
from attrs import define, field, validators
from logic.competitor.player import Player
from logic.utils import converter_str_title, converter_str_upper, validator_pos_z_int


def validator_birthdate(_, __, value: date) -> None:
	"""
	Validates the birthdate of a fencer. The birthdate must meet the following criteria:
    	- It must be a valid date object.
        - It must not be more than 127 years ago.
        - It must not be in the future.

	:param _: Unused field (required by attrs validator signature).
    :param __: Unused attribute (required by attrs validator signature).
    :param value: The birthdate to validate.
    :raises TypeError: If the value is not a date object.
    :raises ValueError: If the birthdate is unrealistic.
	"""
	if not isinstance(value, date):
		raise TypeError("Birthdate must be a valid date object.")

	today = date.today()
	max_age = today.replace(year=today.year - 127)

	if (value > today) or (value < max_age):
		raise ValueError(f"Date of birth {value} is invalid. It must be a realistic date in the past.")


@unique
class Gender(StrEnum):
	"""
	Enumeration for the gender of a fencer.

    Values:
        - MALE: The fencer is a male.
        - FEMALE: The fencer is a female.
        - OTHER: The fencer identifies as other.
	"""
	MALE = auto()
	FEMALE = auto()
	OTHER = auto()


@define(kw_only=True)
class Fencer(Player):
	"""
	Represents a fencer in a fencing tournament.

	Attributes:
        lastname: The last name of the fencer.
        firstname: The first name of the fencer.
        birthdate: The birthdate of the fencer.
        gender: The gender of the fencer.
        club: The club the fencer is affiliated with.
        licence: The fencing licence number of the fencer.
        rank: The fencer's rank before the current tournament.
    """
	lastname: str = field(default='', converter=converter_str_upper, validator=validators.instance_of(str))
	firstname: str = field(default='', converter=converter_str_title, validator=validators.instance_of(str))
	birthdate: Optional[date] = field(default=None, validator=validators.optional(validator_birthdate))
	gender: Optional[Gender] = field(default=None, validator=validators.optional(validators.instance_of(Gender)))
	club: Optional[str] = field(
		default=None,
		converter=converter_str_upper,
		validator=validators.optional(validators.instance_of(str))
	)
	licence: Optional[int] = field(default=None, validator=validators.optional(validator_pos_z_int))
	rank: int = field(default=0, validator=validator_pos_z_int)
