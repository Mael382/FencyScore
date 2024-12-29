from enum import StrEnum, auto, unique
from typing import Optional
from attrs import define, field, setters, validators
from logic.competitor.player import Player
from logic.utils import validator_pos_int, validator_pos_z_int


@unique
class PlayerStatus(StrEnum):
	"""
	Enumeration for the status of a player in a match.

	Values:
        - WIN: The player won the match.
        - LOSS: The player lost the match.
        - DRAW: The match ended in a draw.
	"""
	WIN = auto()
	LOSS = auto()
	DRAW = auto()


@define
class Side:
	"""
	Represents one side of a match in a fencing tournament.

	Attributes:
		player: The player on this side.
		score: The current score of the player.
		player_status: The current status of the player.
	"""
	player: Player = field(validator=validators.instance_of(Player), on_setattr=setters.frozen)
	score: Optional[int] = field(default=None, validator=validators.optional(validator_pos_z_int))
	player_status: Optional[PlayerStatus] = field(
		default=None,
		validator=validators.optional(validators.instance_of(PlayerStatus))
	)

	def update(
			self,
			*,
			other: 'Side',
			player_status: Optional[PlayerStatus] = None,
			score: Optional[int] = None
	) -> None:
		"""
		Updates the score and player's status for this side.

		:param other: The opponent's side.
		:param player_status: The new player's status. If `None`, it will be determined from the opponent's status or
        scores.
		:param score: The new score. If `None`, resets the score.
		"""
		self._update_score(score)
		self._update_player_status(other, player_status)

	def _update_score(self, score: Optional[int]) -> None:
		"""
		Updates the score.

		:param score: The new score. If `None`, resets the score.
		"""
		self.score = score

	def _update_player_status(self, other: 'Side', player_status: Optional[PlayerStatus]) -> None:
		"""
		Updates the player's status.

		:param other: The opponent's side.
        :param player_status: The new player's status. If `None`, it will be determined from the opponent's status or
        scores.
		"""
		if player_status is not None:
			self.player_status = player_status
		elif other.player_status is not None:
			self._set_player_status_from_opponent(other)
		elif (self.score is not None) and (other.score is not None):
			self._set_player_status_from_scores(other)
		else:
			self.player_status = None

	def _set_player_status_from_opponent(self, other: 'Side') -> None:
		"""
		Sets the player's status based on the opponent's status.

		:param other: The opponent's side.
		"""
		player_status_mapping = {
			PlayerStatus.WIN: PlayerStatus.LOSS,
			PlayerStatus.LOSS: PlayerStatus.WIN,
			PlayerStatus.DRAW: PlayerStatus.DRAW
		}
		self.player_status = player_status_mapping[other.player_status]

	def _set_player_status_from_scores(self, other: 'Side') -> None:
		"""
		Sets the player's status based on scores.

		:param other: The opponent's side.
		"""
		if self.score > other.score:
			self.player_status = PlayerStatus.WIN
		elif self.score < other.score:
			self.player_status = PlayerStatus.LOSS
		else:
			self.player_status = PlayerStatus.DRAW


@unique
class MatchStatus(StrEnum):
	"""
	Enumeration for the status of a match.

	Values:
		- EMPTY: The match is incomplete.
		- VALID: The match is valid.
		- INVALID: The match is invalid.
		- LOCKED: The match is locked.
	"""
	EMPTY = auto()
	VALID = auto()
	INVALID = auto()
	LOCKED = auto()


@define(kw_only=True)
class Match:
	"""
	Represents a match in a fencing tournament.

	Attributes:
		piste: The piste (strip) number.
        score_max: Maximum score allowed for the match.
        draw_allowed: Whether a draw is allowed in the match.
        right: The right side of the match.
        left: The left side of the match.
        match_status: The current status of the match.
	"""
	piste: Optional[int] = field(default=None, validator=validators.optional(validator_pos_int))
	score_max: int = field(validator=validator_pos_int, on_setattr=setters.frozen)
	draw_allowed: bool = field(validator=validators.instance_of(bool), on_setattr=setters.frozen)
	right: Side = field(validator=validators.instance_of(Side), on_setattr=setters.frozen)
	left: Side = field(validator=validators.instance_of(Side), on_setattr=setters.frozen)
	match_status: MatchStatus = field(default=MatchStatus.EMPTY, validator=validators.instance_of(MatchStatus))

	def __attrs_post_init__(self) -> None:
		"""
		Initializes the match by validating the sides. Ensures that the player on each side is different.

		:raises ValueError: If both sides have the same player.
		"""
		if self.left.player is self.right.player:
			raise ValueError("Match must have two different players.")

	def update_right(self, *, player_status: Optional[PlayerStatus] = None, score: Optional[int] = None) -> None:
		"""
		Updates the right-side.

        :param player_status: The new player's status. If `None`, it will be determined from the left-side player's
        status or scores.
        :param score: The new score. If `None`, resets the score.
        :raises ValueError: If the match is locked.
		"""
		self._update_side(self.right, self.left, player_status, score)

	def update_left(self, *, player_status: Optional[PlayerStatus] = None, score: Optional[int] = None) -> None:
		"""
		Updates the left-side.

		:param player_status: The new player's status. If `None`, it will be determined from the right-side player's
		status or scores.
        :param score: The new score. If `None`, resets the score.
        :raises ValueError: If the match is locked.
		"""
		self._update_side(self.left, self.right, player_status, score)

	def _update_side(
			self,
			self_side: Side,
			other_side: Side,
			player_status: Optional[PlayerStatus] = None,
			score: Optional[int] = None
	) -> None:
		"""
		Updates one side of the match.

		:param self_side: The side to update.
        :param other_side: The opponent's side.
        :param player_status: The new player's status.
        :param score: The new score.
        :raises ValueError: If the match is locked.
		"""
		if self.match_status != MatchStatus.LOCKED:
			raise ValueError("Match is locked and cannot be updated.")

		self_side.update(other=other_side, player_status=player_status, score=score)
		self._update_match_status()

	def _update_match_status(self) -> None:
		"""Updates the match's status."""
		if self._is_empty():
			self.status = MatchStatus.EMPTY
		elif self._is_invalid():
			self.status = MatchStatus.INVALID
		else:
			self.status = MatchStatus.VALID

	def _is_empty(self) -> bool:
		"""
		Checks if the match is empty.

		:return: `True` if the match is incomplete, otherwise `False`.
		"""
		return any((
			self.right.player_status is None,
			self.left.player_status is None,
			self.right.score is None,
			self.left.score is None
		))

	def _is_invalid(self) -> bool:
		"""
		Checks if the match is invalid.

		:return: `True` if the match is invalid, otherwise `False`.
		"""
		return self._is_invalid_with_draw_allowed() if self.draw_allowed else self._is_invalid_without_draw_allowed()

	def _is_invalid_with_draw_allowed(self) -> bool:
		"""
		Checks if the match is invalid when draws are allowed.

		:return: `True` if the match is invalid, otherwise `False`.
		"""
		return (
			self._is_invalid_with_draw_allowed_by_player_status()
			or self._is_invalid_with_draw_allowed_by_score()
		)

	def _is_invalid_with_draw_allowed_by_player_status(self) -> bool:
		"""
		Checks if player statuses are invalid when draws are allowed.

		:return: `True` if a player's status is invalid, otherwise `False`.
		"""
		return (self.right.player_status == self.left.player_status) and (self.right.player_status != PlayerStatus.DRAW)

	def _is_invalid_with_draw_allowed_by_score(self) -> bool:
		"""
		Checks if scores are invalid when draws are allowed.

		:return: `True` if a score is invalid, otherwise `False`.
		"""
		return any((
			(self.right.player_status == PlayerStatus.WIN) and (self.right.score <= self.left.score),
			(self.right.player_status == PlayerStatus.LOSS) and (self.right.score >= self.left.score),
			(self.right.player_status == PlayerStatus.DRAW) and (self.right.score != self.left.score),
			(self.left.player_status == PlayerStatus.WIN) and (self.left.score <= self.right.score),
			(self.left.player_status == PlayerStatus.LOSS) and (self.left.score >= self.right.score),
			(self.left.player_status == PlayerStatus.DRAW) and (self.left.score != self.right.score)
		))

	def _is_invalid_without_draw_allowed(self) -> bool:
		"""
		Checks if the match is invalid when draws are disallowed.

		:return: `True` if the match is invalid, otherwise `False`.
		"""
		return (
			self._is_invalid_without_draw_allowed_by_player_status()
			or self._is_invalid_without_draw_allowed_by_score()
		)

	def _is_invalid_without_draw_allowed_by_player_status(self) -> bool:
		"""
		Checks if player statuses are invalid when draws are disallowed.

		:return: `True` if a player's status is invalid, otherwise `False`.
		"""
		return (
			(self.right.player_status == self.left.player_status)
			or (self.right.player_status == PlayerStatus.DRAW)
			or (self.left.player_status == PlayerStatus.DRAW)
		)

	def _is_invalid_without_draw_allowed_by_score(self) -> bool:
		"""
		Checks if scores are invalid when draws are disallowed.

		:return: `True` if a score is invalid, otherwise `False`.
		"""
		return any((
			(self.right.player_status == PlayerStatus.WIN) and (self.right.score < self.left.score),
			(self.right.player_status == PlayerStatus.LOSS) and (self.right.score > self.left.score),
			(self.left.player_status == PlayerStatus.WIN) and (self.left.score < self.right.score),
			(self.left.player_status == PlayerStatus.LOSS) and (self.left.score > self.right.score)
		))

	def record_match(self) -> None:
		"""
		Finalizes the match by recording the results for both players.

		:raises ValueError: If the match is not in a valid state for recording.
		"""
		if self.status != MatchStatus.VALID:
			raise ValueError("Cannot record a match that is not in a valid state.")

		self._record_match_for_side(self.right, self.left)
		self._record_match_for_side(self.left, self.right)
		self.match_status = MatchStatus.LOCKED

	@staticmethod
	def _record_match_for_side(self_side: Side, other_side: Side) -> None:
		"""
		Records the match results for one side.

		:param self_side: The side whose results are to be recorded.
		:param other_side: The opponent's side.
		"""
		self_side.player.record_match(
			result=self_side.player_status.value,
			scored=self_side.score,
			received=other_side.score,
			opponent=other_side.player.id
		)
