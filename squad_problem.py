from pulp import *
from utils import *

class SquadProblem:
    """
    The SquadProblem Class is a class that optimizes the substitution strategy during a sports match, given a group of
    players, positions, time windows and each player's skill for playing in a certain position.
    """

    def __init__(self, sk: SkillMatrix, n_windows: int, match_time: int, min_windows_between_sub: int):
        """
        The Constructor for a SquadProblem instance
        :param sk: a skillmatrix of Class SkillMatrix.
        :param n_windows: the number of time windows in a match.
        :param match_time: The total match duration in minutes.
        :param min_windows_between_sub: The total number of windows that a player should be in the field before being
        allowed to be subbed again. Setting this value too high can increase the complexity of the LP problem.
        """
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
        """
        Construct the LP problem using PuLP.
        """

        # PARAMETERS ---------------------------------------------------------

        sk = self.sk
        players = sk.get_players()
        positions = sk.get_positions()
        skillvalues = self.sk.get_values()
        windows = self.windows
        min_windows_between_sub = self.min_windows_between_sub

        # THE LP formulation -------------------------------------------------

        prob = LpProblem("Squad Substitution Problem", LpMaximize)
        x = self.x

        # The objective function, maximimize the total skills of the team.
        prob += lpSum([skillvalues[p][q] * x[p][q][w] for p in players for q in positions for w in windows])

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

        # We want players to play approximately an equal amount of time.
        T1 = np.floor(len(windows) * len(positions) / len(players))
        T2 = np.ceil(len(windows) * len(positions) / len(players))
        for p in players:
            prob += lpSum([x[p][q][w] for w in windows for q in positions]) >= T1
            prob += lpSum([x[p][q][w] for w in windows for q in positions]) <= T2

        # A player is not allowed to be a substitute two windows in a row
        for p in players:
            for w in windows[:-min_windows_between_sub]:
                prob += lpSum([x[p][q][w + y] for q in positions for y in
                               range(min_windows_between_sub + 1)]) >= min_windows_between_sub
        self.lp_problem = prob

    def solve(self):
        """
        Solve the LP problem.
        :return: An object of class SquadSolution that holds the solution to the LP problem.
        """
        self.lp_problem.solve()
        return SquadSolution(self.lp_problem, self.x, self.sk, self.windows, self.n_windows, self.match_time)

    def update_squad_problem(self):
        """
        Update the squad problem by adding a constraint that forces the next solution to be different from the current solution.
        """
        sk = self.sk
        total = np.sum([value(self.x[p][q][w]) for p in sk.get_players() for q in sk.get_positions() for w in self.windows])
        self.lp_problem += lpSum( [(1 if value(self.x[p][q][w]) > 0 else -1) * self.x[p][q][w]
                                 for p in sk.get_players() for q in sk.get_positions() for w in self.windows]) <= total - 1

class SquadSolution():
    """
    A class to hold and process the results of an LP problem created by solving a SquadProblem object.
    """

    def __init__(self, lp_problem: pulp.LpProblem, x: LpVariable, sk: SkillMatrix, windows: int, n_windows: int, match_time: int):
        """
        Constructor of the SquadSolution object.
        :param lp_problem: A PuLP LP problem
        :param x: the x variables corresponding to the PuLP.LpProblem instance.
        :param sk: a skillmatrix of class SkillMatrix.
        :param windows: a List with the window indices.
        :param n_windows: the number of time windows.
        :param match_time: The total duration of the match in minutes.
        """
        self.x = x
        self.lp_problem = lp_problem
        self.sk = sk
        self.windows = windows

        window_minutes_ = [(i*(match_time/n_windows),(i+1)*(match_time/n_windows)) for i in range(n_windows)]
        window_minutes = [str(x[0]).rjust(4) + ' - ' + str(x[1]).rjust(4) for x in window_minutes_]
        window_starts = [str(x[0]).rjust(4) for x in window_minutes_]

        players = sk.get_players()
        positions = sk.get_positions()
        windows = self.windows
        solution_per_time = np.array([[[self.x[p][q][w].varValue for p in players] for q in positions] for w in windows])
        solution_per_position = np.array([[[self.x[p][q][w].varValue for w in windows] for p in players] for q in positions])

        df_substitutions = get_substitution_dataframe(solution_per_position, sk, windows)
        df_substitutions['minutes'] = [window_starts[i] for i in df_substitutions['window']]
        self.df_substitutions = df_substitutions

        df_squad = get_squad_dataframe(solution_per_time, sk, windows)
        df_squad['minutes'] = [window_minutes[i] for i in df_squad['window']]
        self.df_squad = df_squad

    def get_lp_status(self):
        """
        :return: the status of the PuLP instance.
        """
        return self.lp_problem.status

    def write_solution_to_txt_file(self, file_name):
        """
        Write the solution and some statistics to a single text file.
        :param file_name: The file name of the text file to be creaed.
        """
        tfile = open(file_name, 'w')
        tfile.write('Optimal score: {:.2f}'.format(pulp.value(self.lp_problem.objective)))
        tfile.write('\n\n')
        tfile.write(self.df_squad.to_string())
        tfile.write('\n\n')
        tfile.write(self.df_substitutions.to_string())
        for p in self.sk.get_player_names():
            tfile.write('\n\n')
            tfile.write(p + ': ')
            tfile.write(' - '.join((self.df_squad[self.df_squad['player'] == p][['position', 'score']]).apply(
                lambda x: '{} ({})'.format(x[0], str(x[1])), axis=1).tolist()))
        tfile.close()

    def write_squad_dataframe_to_csv(self,file_name):
        """
        Write the long DataFrame with all the player's positions at each time window to csv.
        :param file_name: The file name of the csv file to be creaed.
        """
        self.df_squad.to_csv(file_name, index = False)

    def write_substitutions_dataframe_to_csv(self, file_name):
        """
        Write the DataFrame with the substitutions to be performed to a csv file.
        :param file_name: The file name of the csv file to be creaed.
        """
        self.df_substitutions.to_csv(file_name, index = False)

