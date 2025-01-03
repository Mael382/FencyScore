from abc import ABC
from enum import StrEnum, auto, unique
from itertools import count
from typing import ClassVar, Optional
from attrs import define, field, setters, validators
from logic.utils import validator_pos_int, validator_pos_z_int


@unique
class MatchResult(StrEnum):
	"""
	TODO
	"""
	WIN = auto()
	LOSS = auto()
	DRAW = auto()


@define(kw_only=True, init=False, eq=False)
class Player(ABC):
	"""
    Represents a player in a tournament with ID and performance tracking.

    Attributes:
        id: Unique identifier.
        victories: Number of matches won.
        draws: Number of matches drawn.
        touches_scored: Total touches scored.
        touches_received: Total touches received.
        opponents: Opponent IDs faced.
        exempted: Whether the player has been exempted in a round.
    """
	# Class-level ID generator
	_id_generator: ClassVar[count[int]] = count(start=1)

	# Identity
	id: int = field(factory=_id_generator.__next__, on_setattr=setters.frozen)

	# Match statistics
	victories: int = field(default=0, validator=validator_pos_z_int, repr=False)
	draws: int = field(default=0, validator=validator_pos_z_int, repr=False)

	# Touch statistics
	touches_scored: int = field(default=0, validator=validator_pos_z_int, repr=False)
	touches_received: int = field(default=0, validator=validator_pos_z_int, repr=False)

	# Tournament tracking
	opponents: set[int] = field(
		factory=set,
		validator=validators.deep_iterable(validator_pos_int, validators.instance_of(set)),
		repr = False
	)
	exempted: bool = field(default=False, validator=validators.instance_of(bool), repr=False)

	# Cache score
	_cached_score: Optional[tuple[tuple[int, int], int, int]] = field(default=None, repr=False)

	@property
	def result(self) -> tuple[int, int]:
		"""Player's result as a tuple of (victories, draws)."""
		return self.victories, self.draws

	@property
	def indicator(self) -> int:
		"""Player's touch indicator (touches scored - touches received)."""
		return self.touches_scored - self.touches_received

	@property
	def score(self) -> tuple[tuple[int, int], int, int]:
		"""Player's score as a tuple of ((victories, draws), indicator, touches scored)."""
		if not self._cached_score:
			self._cached_score = (self.result, self.indicator, self.touches_scored)
		return self._cached_score

	def __lt__(self, other: 'Player') -> bool:
		return self.score < other.score

	def add_match(
		self,
		*,
		opponent: 'Player',
		self_result: MatchResult,
		touches_scored: int,
		touches_received: int
	) -> None:
		"""
		Records the result of a match against an opponent.

        Args:
            opponent: The opposing player.
            self_result: The result for this player (`WIN`, `LOSS` or `DRAW`).
            touches_scored: Touches scored by this player.
            touches_received: Touches received by this player.

        Raises:
            ValueError: If touches are negative or opponents have already faced each other.
		"""
		if opponent.id in self.opponents:
			raise ValueError(f"{self} already faced {opponent}.")
		if self.id in opponent.opponents:
			raise ValueError(f"{opponent} already faced {self}.")
		if (touches_scored < 0) or (touches_received < 0):
			raise ValueError("Touches must be non-negative.")

		result_map = {
			MatchResult.WIN: (MatchResult.WIN, MatchResult.LOSS),
			MatchResult.LOSS: (MatchResult.LOSS, MatchResult.WIN),
			MatchResult.DRAW: (MatchResult.DRAW, MatchResult.DRAW),
		}
		self_result, opponent_result = result_map[self_result]

		self._add_side_of_match(opponent.id, self_result, touches_scored, touches_received)
		opponent._add_side_of_match(self.id, opponent_result, touches_received, touches_scored)

	def _add_side_of_match(
		self,
		opponent_id: int,
		self_result: MatchResult,
		touches_scored: int,
		touches_received: int
	) -> None:
		"""Updates the player's statistics."""
		if self_result == MatchResult.WIN:
			self.victories += 1
		elif self_result == MatchResult.DRAW:
			self.draws += 1

		self.touches_scored += touches_scored
		self.touches_received += touches_received
		self.opponents.add(opponent_id)
		self._cached_score = None

	def add_bye(self) -> None:
		"""
		Marks the player as exempted for one round.

		Raises:
			ValueError: If the player has already been exempted.
		"""
		if self.exempted:
			raise ValueError(f"{self} has already been exempted.")

		self.exempted = True

	def reset(self) -> None:
		"""Resets the player's statistics."""
		self.victories = 0
		self.draws = 0
		self.touches_scored = 0
		self.touches_received = 0
		self.opponents.clear()
		self.exempted = False
		self._cached_score = None
