from typing import Iterator
from attrs import define, field, validators
from logic.competitor.fencer import Fencer
from logic.competitor.player import Player
from logic.utils import converter_str_upper


@define(kw_only=True, eq=False)
class Team(Player):
	"""
	Represents a fencing team in a tournament.
	Extends the class `Player`.

	Attributes:
        name: Official name.
        fencers: Team members.
	"""

	# Team identity
	name: str = field(default='', converter=converter_str_upper, validator=validators.instance_of(str))

	# Team composition
	fencers: list[Fencer] = field(
		factory=list,
		validator=validators.deep_iterable(validators.instance_of(Fencer), validators.instance_of(list))
	)

	def __str__(self) -> str:
		return f"{self.name} ({' | '.join(str(fencer) for fencer in self.fencers)})"

	def __iter__(self) -> Iterator[Fencer]:
		return iter(self.fencers)

	def __len__(self) -> int:
		return len(self.fencers)

	def __getitem__(self, item: int) -> Fencer:
		return self.fencers[item]

	def __delitem__(self, key: int) -> None:
		del self.fencers[key]

	def add_fencer(self, fencer: Fencer) -> None:
		"""
		Adds a new fencer to the team.

		Args:
            fencer: The fencer to add.

        Raises:
            ValueError: If the fencer is already in the team.
		"""
		if fencer in self.fencers:
			raise ValueError(f"{fencer} is already a member of {self}.")

		self.fencers.append(fencer)

	def remove_fencer(self, fencer: Fencer | int) -> None:
		"""
		Removes a fencer from the team by either reference or index.

		Args:
            fencer: The fencer instance or index to remove.

        Raises:
            ValueError: If the fencer is not in the team.
            IndexError: If the provided index is out of range.
		"""
		if isinstance(fencer, int):
			try:
				del self[fencer]
			except IndexError:
				raise IndexError(f"Index {fencer} is out of range for {self}.")
		elif isinstance(fencer, Fencer):
			try:
				self.fencers.remove(fencer)
			except ValueError:
				raise ValueError(f"{fencer} is not a member of {self}.")
