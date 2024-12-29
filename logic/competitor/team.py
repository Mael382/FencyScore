from attrs import define, field, validators
from logic.competitor.fencer import Fencer
from logic.competitor.player import Player
from logic.utils import converter_str_upper


@define(kw_only=True)
class Team(Player):
	"""
	Represents a team of fencers in a fencing tournament.

	Attributes:
        name: The name of the team.
        fencers: A list of `Fencer` objects representing the fencers on the team.
	"""
	name: str = field(default='', converter=converter_str_upper, validator=validators.instance_of(str))
	fencers: list[Fencer] = field(
		factory=list,
		validator=validators.deep_iterable(validators.instance_of(Fencer), validators.instance_of(list))
	)
