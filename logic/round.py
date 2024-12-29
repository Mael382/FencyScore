from collections import defaultdict
from itertools import combinations
from typing import Optional
from attrs import define, field, validators
from networkx import Graph, min_weight_matching
from logic.competitor.player import Player
from logic.match import Match
from logic.utils import validator_pos_int


@define(frozen=True, kw_only=True)
class Round:
	"""
	Represents a round in a fencing tournament.

	Attributes:
		rank: The rank of the round.
		players: The sorted list of players participating in the round.
		matches: The list of matches scheduled in the round.
		bye: The player receiving a bye, if applicable.
	"""
	rank: int = field(validator=validator_pos_int)
	players: list[Player] = field(
		validator=validators.deep_iterable(validators.instance_of(Player), validators.instance_of(list))
	)
	matches: list[Match] = field(
		init=False,
		validator=validators.deep_iterable(validators.instance_of(Match), validators.instance_of(list))
	)
	bye: Optional[Player] = field(init=False, validator=validators.optional(validators.instance_of(Player)))

	def __attrs_post_init__(self) -> None:
		"""Initializes the round by sorting players and setting matches and bye."""
		self.players.sort()
		players, bye = self._separate_players()
		groups = self._group_players(players)
		grouped_matches = self._match_groups(groups)
		matches = self._ungroup_matches(grouped_matches)

		object.__setattr__(self, "matches", matches)
		object.__setattr__(self, "bye", bye)

	def _separate_players(self) -> tuple[list[Player], Optional[Player]]:
		"""
		Separates players into competing players and an exempted player if the total count is odd.

		:return: The list of competing players and the exempted player, if any.
		"""
		competing_players = self.players.copy()
		exempted_player = None

		if len(self.players) % 2 != 0:
			for i, player in enumerate(reversed(competing_players)):
				if not player.exempted:
					exempted_player = competing_players.pop(-1 - i)
					break

		return competing_players, exempted_player

	@staticmethod
	def _group_players(players: list[Player]) -> list[list[Player]]:
		"""
		Groups players by result (victories and draws).

		:param players: The list of players to group.
		:return: The grouped list of players.
		"""
		groups = defaultdict(list)
		for player in players:
			groups[player.result].append(player)

		grouped_players = []
		for key in sorted(groups.keys(), reverse=True):
			grouped_players.append(groups[key])

		for i, group in enumerate(grouped_players[:-1]):
			if len(group) % 2 != 0:
				group.append(grouped_players[i + 1].pop(0))

		return grouped_players

	def _match_groups(self, groups: list[list[Player]]) -> list[set[tuple[Player, Player]]]:
		"""
		Matches players within each group.

		:param groups: The grouped list of players to match.
		:return: The grouped list of matches.
		"""
		return self._merge_groups(groups, [])

	def _merge_groups(
		self,
		groups: list[list[Player]],
		grouped_matches: list[set[tuple[Player, Player]]],
		start: int = 0
	) -> list[set[tuple[Player, Player]]]:
		"""
		Attempts to match players in groups, merging if necessary.

		:param groups: The grouped list of players to match.
		:param grouped_matches: The grouped list of matches.
		:param start: The index to start matching from.
		:return: The grouped list of matches.
		:raises ValueError: If unable to match all players.
		"""
		for i, group in enumerate(groups[start:]):
			group_matches = self._match_group(group)
			if group_matches:
				grouped_matches.append(group_matches)
			elif (j := start + i) < len(groups):
				groups[j] += groups.pop(j + 1)
				return self._merge_groups(groups, grouped_matches, j)
			elif len(groups) > 1:
				groups[-2] += groups.pop()
				return self._merge_groups(groups, grouped_matches[:-1], j - 1)
			else:
				raise ValueError("Unable to match all players.")

		return grouped_matches

	def _match_group(self, group: list[Player]) -> set[tuple[Player, Player]]:
		"""
		Matches a group of players.

		:param group: The group of players to match.
		:return: The group of matches.
		"""
		matching_graph = self._group_to_matching_graph(group)
		matches = min_weight_matching(matching_graph)

		if len(matches) != len(group) % 2:
			return set()

		return matches

	def _group_to_matching_graph(self, group: list[Player]) -> Graph:
		"""
		Converts a grouped list of players into a graph for minimum-weight matching.

		:param group: The group of players to convert.
		:return: The graph of players.
		"""
		graph = Graph()
		graph.add_nodes_from(group)

		for (i, player1), (j, player2) in combinations(enumerate(group), 2):
			if player2.id not in player1.opponents:
				graph.add_edge(player1, player2, weight=self._matching_distance(i, j, len(group)))

		return graph

	@staticmethod
	def _matching_distance(rank1: int, rank2: int, size: int) -> int:
		"""
		Computes the matching distance between two players based on their rank in a group.

		:param rank1: The rank of the first player.
		:param rank2: The rank of the second player.
		:param size: The size of the group of players.
		:return: The matching distance between the two players.
		"""
		return abs(abs(rank1 - rank2) - size // 2)

	@staticmethod
	def _ungroup_matches(grouped_matches: list[set[tuple[Player, Player]]]) -> list[tuple[Player, Player]]:
		"""
		Ungroups matches.

		:param grouped_matches: The grouped list of matches to ungroup.
		:return: The list of matches.
		"""
		matches = []

		for group_matches in grouped_matches:
			matches.extend(group_matches)

		return matches
