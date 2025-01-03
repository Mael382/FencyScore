from datetime import date
from enum import StrEnum, auto, unique
from functools import lru_cache
from typing import Final, Optional
from attrs import define, field, validators
from logic.competitor.player import Player
from logic.utils import converter_str_title, converter_str_upper, validator_pos_z_int

# Constants
MAX_AGE: Final[int] = 128


@lru_cache(maxsize=1)
def get_max_age_date() -> date:
	"""Maximum valid birthdate for a fencer."""
	today = date.today()
	return today.replace(year=today.year - MAX_AGE)


def validator_birthdate(_, __, value: date) -> None:
	"""
	Validates the provided birthdate.

    Args:
    	_: Unused parameter for instance.
        __: Unused parameter for attribute.
        value: The birthdate to validate.

    Raises:
        ValueError: If the birthdate is in the future or exceeds the maximum age.
	"""
	if value > (today := date.today()):
		raise ValueError(f"Birthdate {value} cannot be in the future (today: {today}).")
	if value < (max_age_date := get_max_age_date()):
		raise ValueError(f"Birthdate {value} is too old (limit: {max_age_date}).")


@unique
class Gender(StrEnum):
	"""
	Enumeration of gender categories for fencers.

    Values:
    	HOMME: Male fencer.
        FEMME: Female fencer.
        AUTRE: Other gender identity.
	"""
	HOMME: Final = auto()  # Male
	FEMME: Final = auto()  # Female
	AUTRE: Final = auto()  # Other

	def __str__(self) -> str:
		return self.value.title()


@define(kw_only=True, eq=False)
class Fencer(Player):
	"""
	Represents a fencer in a tournament.
	Extends the class `Player`.

	Attributes:
		lastname: Family name.
		firstname: Given name.
		birthdate: Date of birth.
		gender: Gender category.
		club: Affiliated fencing club.
		licence: Official fencing license number.
		rank: Initial tournament ranking.
	"""

	# Personal information
	lastname: str = field(default='', converter=converter_str_upper, validator=validators.instance_of(str))
	firstname: str = field(default='', converter=converter_str_title, validator=validators.instance_of(str))
	birthdate: Optional[date] = field(default=None, validator=validators.optional(validator_birthdate))
	gender: Optional[Gender] = field(default=None, validator=validators.optional(validators.instance_of(Gender)))

	# Club affiliation and licensing
	club: Optional[str] = field(
		default=None,
		converter=converter_str_upper,
		validator=validators.optional(validators.instance_of(str))
	)
	licence: Optional[int] = field(default=None, validator=validators.optional(validator_pos_z_int))

	# Competition details
	rank: int = field(default=0, validator=validator_pos_z_int)

	def __str__(self) -> str:
		return f"{self.lastname} {self.firstname}"
