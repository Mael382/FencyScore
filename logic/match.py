from enum import StrEnum, auto, unique
from typing import Optional
from attrs import define, field, setters, validators
from logic.competitor.player import MatchResult, Player
from logic.utils import validator_pos_int, validator_pos_z_int


@define
class Side:
	"""
	TODO
	"""
	player: Player = field(validator=validators.instance_of(Player), on_setattr=setters.frozen)
	score: Optional[int] = field(default=None, validator=validators.optional(validator_pos_z_int))
	result: Optional[MatchResult] = field(
		default=None,
		validator=validators.optional(validators.instance_of(MatchResult))
	)

	def update(
			self,
			*,
			other: 'Side',
			result: Optional[MatchResult] = None,
			score: Optional[int] = None
	) -> None:
		"""
		TODO
		"""
		self._update_score(score)
		self._update_result(other, result)

	def _update_score(self, score: Optional[int]) -> None:
		"""
		TODO
		"""
		self.score = score

	def _update_result(self, other: 'Side', result: Optional[MatchResult]) -> None:
		"""
		TODO
		"""
		if result:
			self.result = result
		elif other.result:
			self._set_result_by_opponent_result(other)
		elif (self.score is not None) and (other.score is not None):
			self._set_result_by_scores(other)
		else:
			self.result = None

	def _set_result_by_opponent_result(self, other: 'Side') -> None:
		"""
		TODO
		"""
		result_map = {
			MatchResult.WIN: MatchResult.LOSS,
			MatchResult.LOSS: MatchResult.WIN,
			MatchResult.DRAW: MatchResult.DRAW
		}
		self.result = result_map[other.result]

	def _set_result_by_scores(self, other: 'Side') -> None:
		"""
		TODO
		"""
		if self.score > other.score:
			self.result = MatchResult.WIN
		elif self.score < other.score:
			self.result = MatchResult.LOSS
		else:
			self.result = MatchResult.DRAW


@unique
class MatchStatus(StrEnum):
	"""
	TODO
	"""
	BLANK = auto()
	VALID = auto()
	INVALID = auto()
	LOCKED = auto()


@define(kw_only=True)
class Match:
	"""
	TODO
	"""
	piste: Optional[int] = field(default=None, validator=validators.optional(validator_pos_int))
	score_max: int = field(validator=validator_pos_int, on_setattr=setters.frozen)
	draw_allowed: bool = field(validator=validators.instance_of(bool), on_setattr=setters.frozen)
	right_side: Side = field(validator=validators.instance_of(Side), on_setattr=setters.frozen)
	left_side: Side = field(validator=validators.instance_of(Side), on_setattr=setters.frozen)
	status: MatchStatus = field(default=MatchStatus.BLANK, validator=validators.instance_of(MatchStatus))

	def __attrs_post_init__(self) -> None:
		if self.left_side.player is self.right_side.player:
			raise ValueError("Match must have two different players.")

	def update_right_side(self, *, result: Optional[MatchResult] = None, score: Optional[int] = None) -> None:
		"""
		TODO
		"""
		self._update_side(self.right_side, self.left_side, result, score)

	def update_left(self, *, result: Optional[MatchResult] = None, score: Optional[int] = None) -> None:
		"""
		TODO
		"""
		self._update_side(self.left_side, self.right_side, result, score)

	def _update_side(
			self,
			self_side: Side,
			other_side: Side,
			self_result: Optional[MatchStatus],
			self_score: Optional[int]
	) -> None:
		"""
		TODO
		"""
		if self.status == MatchStatus.LOCKED:
			raise ValueError("Match is locked and cannot be updated.")

		self_side.update(other=other_side, result=self_result, score=self_score)
		self._update_match_status()

	def _update_match_status(self) -> None:
		"""TODO"""
		if self._is_empty():
			self.status = MatchStatus.BLANK
		elif self._is_invalid():
			self.status = MatchStatus.INVALID
		else:
			self.status = MatchStatus.VALID

	def _is_empty(self) -> bool:
		"""
		TODO
		"""
		return any((
			self.right_side.result is None,
			self.left_side.result is None,
			self.right_side.score is None,
			self.left_side.score is None
		))

	def _is_invalid(self) -> bool:
		"""
		TODO
		"""
		return self._is_invalid_with_draw_allowed() if self.draw_allowed else self._is_invalid_without_draw_allowed()

	def _is_invalid_with_draw_allowed(self) -> bool:
		"""
		TODO
		"""
		return self._is_invalid_with_draw_allowed_by_results() or self._is_invalid_with_draw_allowed_by_scores()

	def _is_invalid_with_draw_allowed_by_results(self) -> bool:
		"""
		TODO
		"""
		return (self.right_side.result == self.left_side.result) and (self.right_side.result != MatchResult.DRAW)

	def _is_invalid_with_draw_allowed_by_scores(self) -> bool:
		"""
		TODO
		"""
		return any((
			(self.right_side.result == MatchResult.WIN) and (self.right_side.score <= self.left_side.score),
			(self.right_side.result == MatchResult.LOSS) and (self.right_side.score >= self.left_side.score),
			(self.right_side.result == MatchResult.DRAW) and (self.right_side.score != self.left_side.score),
			(self.left_side.result == MatchResult.WIN) and (self.left_side.score <= self.right_side.score),
			(self.left_side.result == MatchResult.LOSS) and (self.left_side.score >= self.right_side.score),
			(self.left_side.result == MatchResult.DRAW) and (self.left_side.score != self.right_side.score)
		))

	def _is_invalid_without_draw_allowed(self) -> bool:
		"""
		TODO
		"""
		return self._is_invalid_without_draw_allowed_by_results() or self._is_invalid_without_draw_allowed_by_scores()

	def _is_invalid_without_draw_allowed_by_results(self) -> bool:
		"""
		TODO
		"""
		return any((
			self.right_side.result == self.left_side.result,
			self.right_side.result == MatchResult.DRAW,
			self.left_side.result == MatchResult.DRAW
		))

	def _is_invalid_without_draw_allowed_by_scores(self) -> bool:
		"""
		TODO
		"""
		return any((
			(self.right_side.result == MatchResult.WIN) and (self.right_side.score < self.left_side.score),
			(self.right_side.result == MatchResult.LOSS) and (self.right_side.score > self.left_side.score),
			(self.left_side.result == MatchResult.WIN) and (self.left_side.score < self.right_side.score),
			(self.left_side.result == MatchResult.LOSS) and (self.left_side.score > self.right_side.score)
		))

	def record_match(self) -> None:
		"""
		TODO
		"""
		if self.status != MatchStatus.VALID:
			raise ValueError("Cannot record a match that is not in a valid state.")

		self._record_side_of_match(self.right_side, self.left_side)
		self._record_side_of_match(self.left_side, self.right_side)
		self.status = MatchStatus.LOCKED

	@staticmethod
	def _record_side_of_match(self_side: Side, other_side: Side) -> None:
		"""
		TODO
		"""
		self_side.player.add_match(
			opponent=other_side.player,
			self_result=self_side.result,
			touches_scored=self_side.score,
			touches_received=other_side.score
		)
