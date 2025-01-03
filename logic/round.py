from collections import defaultdict, deque
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
	Represents a round in a tournament.

	Attributes:
		rank: Round's number.
		score_max: Maximum score allowed.
		draw_allowed: Whether draws are allowed.
		players: Players participating.
		matches: Matches generated.
		bye: Player who gets a bye.
	"""
	rank: int = field(validator=validator_pos_int)
	score_max: int = field(validator=validator_pos_int)
	draw_allowed: bool = field(validator=validators.instance_of(bool))
	players: list[Player] = field(
		validator=validators.deep_iterable(validators.instance_of(Player), validators.instance_of(list))
	)
	matches: list[Match] = field(
		init=False,
		validator=validators.deep_iterable(validators.instance_of(Match), validators.instance_of(deque))
	)
	bye: Optional[Player] = field(init=False, validator=validators.optional(validators.instance_of(Player)))

	def __attrs_post_init__(self) -> None:
		self.players.sort()
		players, bye = self._separate_players()
		groups = self._group_players(players)
		grouped_matches = self._match_groups(groups)
		matches = self._ungroup_matches(grouped_matches)

		object.__setattr__(self, "matches", matches)
		object.__setattr__(self, "bye", bye)

	def _separate_players(self) -> tuple[list[Player], Optional[Player]]:
		"""Separates competing players and the exempt player."""
		competing_players = self.players.copy()
		exempt_player = None

		if len(self.players) % 2 != 0:
			for i, player in enumerate(reversed(competing_players), start=1):
				if not player.exempted:
					exempt_player = competing_players.pop(-i)
					break

		return competing_players, exempt_player

	@staticmethod
	def _group_players(players: list[Player]) -> list[deque[Player]]:
		"""Groups players based on their results."""
		groups = defaultdict(deque)
		for player in players:
			groups[player.result].append(player)

		grouped_players = deque(groups[key] for key in sorted(groups.keys(), reverse=True))

		for i in range(len(grouped_players) - 1):
			if len(grouped_players[i]) % 2 != 0:
				grouped_players[i].append(grouped_players[i + 1].popleft())

		return list(grouped_players)

	def _match_groups(self, groups: list[deque[Player]]) -> deque[deque[Match]]:
		"""Creates matches within and across groups."""
		return self._merge_groups(groups, deque(), 0)

	def _merge_groups(
		self,
		groups: list[deque[Player]],
		grouped_matches: deque[deque[Match]],
		start: int
	) -> deque[deque[Match]]:
		"""Creates matches and merge groups if necessary."""
		for i, group in enumerate(groups[start:]):
			group_matches = self._match_group(group)
			if group_matches:
				grouped_matches.append(group_matches)
			elif (j := start + i) < len(groups):
				groups[j] += groups.pop(j + 1)
				return self._merge_groups(groups, grouped_matches, j)
			elif len(groups) > 1:
				groups[-1] = groups[-2] + groups.pop()
				grouped_matches.pop()
				return self._merge_groups(groups, grouped_matches, j - 1)
			else:
				raise ValueError("Unable to match all players.")

		return grouped_matches

	def _match_group(self, group: deque[Player]) -> deque[Match]:
		"""Creates matches within a single group of players."""
		matching_graph = self._group_to_matching_graph(group)
		couples = min_weight_matching(matching_graph)
		matches = deque()

		if len(couples) == len(group) % 2:
			for couple in couples:
				matches.append(Match(
					score_max=self.score_max,
					draw_allowed=self.draw_allowed,
					right_side=couple[0],
					left_side=couple[1]
				))

		return matches

	def _group_to_matching_graph(self, group: deque[Player]) -> Graph:
		"""Converts a group of players into a weighted graph for matching."""
		graph = Graph()
		graph.add_nodes_from(group)

		for (i, player1), (j, player2) in combinations(enumerate(group), 2):
			if player2.id not in player1.opponents:
				graph.add_edge(player1, player2, weight=self._matching_distance(i, j, len(group)))

		return graph

	@staticmethod
	def _matching_distance(rank1: int, rank2: int, size: int) -> int:
		"""Distance metric for optimal matching."""
		return abs(abs(rank1 - rank2) - size // 2)

	@staticmethod
	def _ungroup_matches(grouped_matches: deque[deque[Match]]) -> list[Match]:
		"""Ungroups matches."""
		matches = []

		for group_matches in grouped_matches:
			matches.extend(group_matches)

		return matches
