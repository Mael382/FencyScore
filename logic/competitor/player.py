from abc import ABC
from itertools import count
from attrs import define, field, setters, validators
from logic.utils import validator_pos_int, validator_pos_z_int


id_generator: count = count(start=1)
"""ID generator."""


@define(init=False, kw_only=True)
class Player(ABC):
	"""
	Represents a player in a fencing tournament.

	Attributes:
        id: A unique identifier for the player.
        victories: The number of matches won by the player.
        draws: The number of matches drawn by the player.
        touches_scored: The total touches scored by the player.
        touches_received: The total touches received by the player.
        opponents: A set of IDs representing opponents faced.
        exempted: Whether the player has been exempted from a round.
	"""
	id: int = field(factory=id_generator.__next__, on_setattr=setters.frozen)
	victories: int = field(default=0, validator=validator_pos_z_int)
	draws: int = field(default=0, validator=validator_pos_z_int)
	touches_scored: int = field(default=0, validator=validator_pos_z_int)
	touches_received: int = field(default=0, validator=validator_pos_z_int)
	opponents: set[int] = field(
		factory=set,
		validator=validators.deep_iterable(validator_pos_int, validators.instance_of(set))
	)
	exempted: bool = field(default=False, validator=validators.instance_of(bool))

	@property
	def result(self) -> tuple[int, int]:
		"""Gives the player's result."""
		return self.victories, self.draws

	@property
	def indicator(self) -> int:
		"""Computes the player's indicator."""
		return self.touches_scored - self.touches_received

	@property
	def score(self) -> tuple[tuple[int, int], int, int]:
		"""Gives the player's score."""
		return self.result, self.indicator, self.touches_scored

	def record_match(self, *, result: str, scored: int, received: int, opponent: int) -> None:
		"""
		Records the result of a match for the player.

		:param result: The result of the match (`win`, `loss` or `draw`).
		:param scored: Touches scored in the match.
		:param received: Touches received in the match.
		:param opponent: The ID of the opponent.
		:raises ValueError: If the touches are negative or if the opponent is already recorded.
		"""
		if (scored < 0) or (received < 0):
			raise ValueError("Touches must be non-negative.")
		if opponent in self.opponents:
			raise ValueError(f"Match against player {opponent} is already recorded.")

		if result == "win":
			self.victories += 1
		elif result == "draw":
			self.draws += 1

		self.touches_scored += scored
		self.touches_received += received
		self.opponents.add(opponent)

	def reset_stats(self) -> None:
		"""Resets all the player's statistics."""
		self.victories = 0
		self.draws = 0
		self.touches_scored = 0
		self.touches_received = 0
		self.opponents.clear()
		self.exempted = False
