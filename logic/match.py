from enum import StrEnum, auto, unique
from typing import Optional
from attrs import define, field, setters, validators
from logic.competitor.player import MatchResult, Player
from logic.utils import validator_pos_int, validator_pos_z_int


@define
class Side:
	"""
	Represents a side in a match.

	Attributes:
		player: Side's player.
		score: Player's score.
		result: Player's result.
	"""
	player: Player = field(validator=validators.instance_of(Player), on_setattr=setters.frozen)
	score: Optional[int] = field(default=None, validator=validators.optional(validator_pos_z_int))
	result: Optional[MatchResult] = field(
		default=None,
		validator=validators.optional(validators.instance_of(MatchResult))
	)

	def update(self, *, other: 'Side', result: Optional[MatchResult] = None, score: Optional[int] = None) -> None:
		"""
		Update the side's data.

		Args:
			other: The opposing side.
			result: The new result.
			score: The new score.
		"""
		self._set_score(score)
		self._set_result(other, result)

	def _set_score(self, score: Optional[int]) -> None:
		"""Sets the score for this side."""
		self.score = score

	def _set_result(self, other: 'Side', result: Optional[MatchResult]) -> None:
		"""Sets the result for this side."""
		if result:
			self.result = result
		elif other.result:
			self._set_result_by_opponent_result(other)
		elif (self.score is not None) and (other.score is not None):
			self._set_result_by_scores(other)
		else:
			self.result = None

	def _set_result_by_opponent_result(self, other: 'Side') -> None:
		"""Sets result based on opponent's result."""
		result_map = {
			MatchResult.WIN: MatchResult.LOSS,
			MatchResult.LOSS: MatchResult.WIN,
			MatchResult.DRAW: MatchResult.DRAW
		}
		self.result = result_map[other.result]

	def _set_result_by_scores(self, other: 'Side') -> None:
		"""Sets result based on scores."""
		if self.score > other.score:
			self.result = MatchResult.WIN
		elif self.score < other.score:
			self.result = MatchResult.LOSS
		else:
			self.result = MatchResult.DRAW


@unique
class MatchStatus(StrEnum):
	"""
	Enumeration of status for matches.

	Values:
    	PENDING: Match hasn't started yet.
        VALID: Match results are valid and can be recorded.
        INVALID: Match results are invalid and cannot be recorded.
        LOCKED: Match recorded and unchangeable.
	"""
	PENDING = auto()
	VALID = auto()
	INVALID = auto()
	LOCKED = auto()


@define(kw_only=True)
class Match:
	"""
	Represents a match between two players in a tournament.

	Attributes:
		piste: Strip's number.
		score_max: Maximum score allowed.
		draw_allowed: Whether draws are allowed.
		right_side: Right side of the match.
		left_side: Left side of the match.
		status: Match's status.
	"""
	piste: Optional[int] = field(default=None, validator=validators.optional(validator_pos_int))
	score_max: int = field(validator=validator_pos_int, on_setattr=setters.frozen)
	draw_allowed: bool = field(validator=validators.instance_of(bool), on_setattr=setters.frozen)
	right_side: Side = field(validator=validators.instance_of(Side), on_setattr=setters.frozen)
	left_side: Side = field(validator=validators.instance_of(Side), on_setattr=setters.frozen)
	status: MatchStatus = field(default=MatchStatus.PENDING, validator=validators.instance_of(MatchStatus))

	def __attrs_post_init__(self) -> None:
		if self.left_side.player is self.right_side.player:
			raise ValueError("Match must have two different players.")

	def update_right_side(self, *, result: Optional[MatchResult] = None, score: Optional[int] = None) -> None:
		"""
		Updates the right side's data.

		Args:
			result: The new result.
			score: The new score.
		"""
		self._update_side(self.right_side, self.left_side, result, score)

	def update_left(self, *, result: Optional[MatchResult] = None, score: Optional[int] = None) -> None:
		"""
		Updates the left side's data.

		Args:
			result: The new result.
			score: The new score.
		"""
		self._update_side(self.left_side, self.right_side, result, score)

	def _update_side(
		self,
		self_side: Side,
		other_side: Side,
		self_result: Optional[MatchStatus],
		self_score: Optional[int]
	) -> None:
		"""Updates data on this side."""
		if self.status == MatchStatus.LOCKED:
			raise ValueError("Match is locked and cannot be updated.")

		self_side.update(other=other_side, result=self_result, score=self_score)
		self._update_match_status()

	def _update_match_status(self) -> None:
		"""Updates the match's status."""
		if self._is_incomplete():
			self.status = MatchStatus.PENDING
		elif self._is_invalid():
			self.status = MatchStatus.INVALID
		else:
			self.status = MatchStatus.VALID

	def _is_incomplete(self) -> bool:
		"""Checks if the match is incomplete."""
		return any((
			self.right_side.result is None,
			self.left_side.result is None,
			self.right_side.score is None,
			self.left_side.score is None
		))

	def _is_invalid(self) -> bool:
		"""Checks if the match is invalid."""
		return self._is_invalid_with_draw_allowed() if self.draw_allowed else self._is_invalid_without_draw_allowed()

	def _is_invalid_with_draw_allowed(self) -> bool:
		"""Checks if the match is invalid with a draw allowed."""
		return self._is_invalid_with_draw_allowed_by_results() or self._is_invalid_with_draw_allowed_by_scores()

	def _is_invalid_with_draw_allowed_by_results(self) -> bool:
		"""Checks if results are invalid with a draw allowed."""
		return self.right_side.result == self.left_side.result != MatchResult.DRAW

	def _is_invalid_with_draw_allowed_by_scores(self) -> bool:
		"""Checks if scores are invalid with a draw allowed."""
		return any((
			(self.right_side.result == MatchResult.WIN) and (self.right_side.score <= self.left_side.score),
			(self.right_side.result == MatchResult.LOSS) and (self.right_side.score >= self.left_side.score),
			(self.right_side.result == MatchResult.DRAW) and (self.right_side.score != self.left_side.score),
			(self.left_side.result == MatchResult.WIN) and (self.left_side.score <= self.right_side.score),
			(self.left_side.result == MatchResult.LOSS) and (self.left_side.score >= self.right_side.score),
			(self.left_side.result == MatchResult.DRAW) and (self.left_side.score != self.right_side.score)
		))

	def _is_invalid_without_draw_allowed(self) -> bool:
		"""Checks if the match is invalid without allowing a draw."""
		return self._is_invalid_without_draw_allowed_by_results() or self._is_invalid_without_draw_allowed_by_scores()

	def _is_invalid_without_draw_allowed_by_results(self) -> bool:
		"""Checks if results are invalid without allowing a draw."""
		return any((
			self.right_side.result == self.left_side.result,
			self.right_side.result == MatchResult.DRAW,
			self.left_side.result == MatchResult.DRAW
		))

	def _is_invalid_without_draw_allowed_by_scores(self) -> bool:
		"""Checks if scores are invalid without allowing a draw."""
		return any((
			(self.right_side.result == MatchResult.WIN) and (self.right_side.score < self.left_side.score),
			(self.right_side.result == MatchResult.LOSS) and (self.right_side.score > self.left_side.score),
			(self.left_side.result == MatchResult.WIN) and (self.left_side.score < self.right_side.score),
			(self.left_side.result == MatchResult.LOSS) and (self.left_side.score > self.right_side.score)
		))

	def record_match(self) -> None:
		"""
		Records the result of the match.

		Raises:
            ValueError: If the match is not in a valid state.
		"""
		if self.status != MatchStatus.VALID:
			raise ValueError("Cannot record a match that is not in a valid state.")

		self._record_side_of_match(self.right_side, self.left_side)
		self._record_side_of_match(self.left_side, self.right_side)
		self.status = MatchStatus.LOCKED

	@staticmethod
	def _record_side_of_match(self_side: Side, other_side: Side) -> None:
		"""Records the result of the match for a single side."""
		self_side.player.add_match(
			opponent=other_side.player,
			self_result=self_side.result,
			touches_scored=self_side.score,
			touches_received=other_side.score
		)
