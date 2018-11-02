import numpy as np
from pulp import *
from utils import *

class SquadProblem:

    def __init__(self, sk: SkillMatrix, n_windows: int, match_time: int, min_windows_between_sub: int):
        self.sk = sk
        self.n_windows = n_windows
        self.match_time = match_time
        self.windows = list(range(n_windows))
        self.n_solutions = 10
        self.min_windows_between_sub = min_windows_between_sub
        # Initialize the decision variables. x[p][q][w] is 1 if player p plays on position q during timewindow w.
        self.x = LpVariable.dicts("Choice", (sk.get_players(), sk.get_positions(), self.windows), 0, 1, LpInteger)

        # Create the LP problem
        self.lp_problem = None
        self._construct_problem()

    def _construct_problem(self):
        sk = self.sk
        players = sk.get_players()
        positions = sk.get_positions()
        skillvalues = self.sk.get_values()
        windows = self.windows
        min_windows_between_sub = self.min_windows_between_sub

        # LINEAR OPTIMIZATION -------------------------------------------------

        prob = LpProblem("Squad Substitution Problem", LpMaximize)
        x = self.x

        # The objective function, maximimize the total skills of the team.
        prob += lpSum([skillvalues[p][q] * x[p][q][w] for p in players for q in positions for w in windows])

        # During every timewindow, there should be exactly as many players in the field as there are available positions
        for w in windows:
            prob += lpSum([x[p][q][w] for p in players for q in positions]) == len(positions)

        # We want players to play approximately an equal amount of time.
        T1 = np.floor(len(windows) * len(positions) / len(players))
        T2 = np.ceil(len(windows) * len(positions) / len(players))
        for p in players:
            prob += lpSum([x[p][q][w] for w in windows for q in positions]) >= T1
            prob += lpSum([x[p][q][w] for w in windows for q in positions]) <= T2

        # Every player should occupy at most 1 position in the pitch during any given timewindow.
        for p in players:
            for w in windows:
                prob += lpSum([x[p][q][w] for q in positions]) <= 1

        # Every position should be filled by exactly one player during every time window.
        for q in positions:
            for w in windows:
                prob += lpSum([x[p][q][w] for p in players]) == 1

        # A player is not allowed to change places in the pitch while he/she is in play.
        # The player is only allowed to play in different positions if he is substituted in between.
        for q_star in positions:
            for p in players:
                for w in windows[:-1]:
                    prob += lpSum([x[p][q][w + 1] for q in positions if q != q_star] + [x[p][q_star][w]]) <= 1

        # A player is not allowed to be a substitute two windows in a row
        for p in players:
            for w in windows[:-min_windows_between_sub]:
                prob += lpSum([x[p][q][w + y] for q in positions for y in
                               range(min_windows_between_sub + 1)]) >= min_windows_between_sub
        self.lp_problem = prob

    def solve(self):
        self.lp_problem.solve()
        return SquadSolution(self.lp_problem, self.x, self.sk, self.windows)

    def update_squad_problem(self):
        sk = self.sk
        total = np.sum([value(self.x[p][q][w]) for p in sk.get_players() for q in sk.get_positions() for w in self.windows])
        self.lp_problem += lpSum( [(1 if value(self.x[p][q][w]) > 0 else -1) * self.x[p][q][w]
                                 for p in sk.get_players() for q in sk.get_positions() for w in self.windows]) <= total - 1

class SquadSolution():

    def __init__(self, lp_problem: pulp.LpProblem, x: LpVariable, sk: SkillMatrix, windows: int):
        self.x = x
        self.lp_problem = lp_problem
        self.sk = sk
        self.windows = windows

    def get_lp_status(self):
        return self.lp_problem.status

    def write_solution_to_file(self, file_name):
        sk = self.sk
        players = sk.get_players()
        positions = sk.get_positions()
        player_names = sk.get_player_names()
        windows = self.windows
        solution_per_time = np.array([[[self.x[p][q][w].varValue for p in players] for q in positions] for w in windows])
        solution_per_position = np.array([[[self.x[p][q][w].varValue for w in windows] for p in players] for q in positions])
        df_substitutions = get_substitution_dataframe(solution_per_position, sk, windows)
        df_squad = get_squad_dataframe(solution_per_time, sk, windows)
        write_result_to_file(file_name, pulp.value(self.lp_problem.objective), df_squad, df_substitutions, player_names)

