import pandas as pd
import numpy as np
from itertools import product

class SkillMatrix():
    """
    A Class to hold a skillmatrix and return its values or other parameters like the player- and position names.
    """

    def __init__(self, skillmatrix, fairness=False):
        """
        :param skillmatrix: The skillmatrix is expected in shape p x q where p is the number of rows, q is the number of columns,
        and every value [p,q] represents the performance of player p playing at position q.
        :param fairness: A parameter to indicate that all values in a row should be scaled so that the maximum for that
        row is 1. This will make the solution more fair in the sense that players have more equal probabilities of
        substituting equally often.
        """

        if fairness:
            for i in range(skillmatrix.shape[0]):
                skillmatrix.iloc[i] = np.round(skillmatrix.iloc[i] / np.max(skillmatrix.iloc[i]))

        self.players = list(range(skillmatrix.shape[0]))
        self.player_names = skillmatrix.index.tolist()
        self.positions = list(range(skillmatrix.shape[1]))
        self.position_names = skillmatrix.columns.tolist()
        self.values = skillmatrix.values
        self.skillmatrix = skillmatrix

    def get_players(self):
        return self.players

    def get_player_names(self):
        return self.player_names

    def get_positions(self):
        return self.positions

    def get_position_names(self):
        return self.position_names

    def get_values(self):
        return self.values

    def get_skillmatrix(self):
        return self.skillmatrix


def get_substitution_dataframe(solution_per_position, sk, windows) -> pd.DataFrame:
    """
    Convert a solution in the shape [q,p,w] to a DataFrame of the substitutions to be performed at certain time windows,
    where q is the number of positions, p is the number of players, and w is the time window.

    :param solution_per_position: A solution in the shape [q,p,w] where solution_per_position[q,p,w] is 1 if
    player p plays at position q during time window w, and 0 otherwise.
    :param sk: a skillmatrix of class SkillMatrix.
    :param windows: a List of integers representing the different time windows.
    :return: A DataFrame with the substitutions to be performed at certain time windows.
    """
    positions = sk.get_positions()
    player_names = sk.get_player_names()
    # Get a list of the substitutions
    substitutions = []
    for q in positions:
        q_p = [np.where(solution_per_position[q][:, w])[0][0] for w in windows]
        change_windows = [i for i in range(1, len(q_p)) if q_p[i] != q_p[i - 1]]
        for change in change_windows:
            player_out = q_p[change - 1]
            player_in = q_p[change]
            substitutions.append({'window': change, 'player_out': player_out, 'player_in': player_in})
    df_substitutions = pd.DataFrame(substitutions).sort_values('window')
    df_substitutions = df_substitutions.reset_index()
    df_substitutions['player_out'] = [player_names[i] for i in df_substitutions['player_out']]
    df_substitutions['player_in'] = [player_names[i] for i in df_substitutions['player_in']]
    df_substitutions = df_substitutions.drop('index', axis=1)
    return df_substitutions

def get_squad_dataframe(solution_per_time,sk,windows):
    """
    Convert a solution in the shape [w,q,p] to a long DataFrame of all the player's positions at each time window,
    where q is the number of positions, p is the number of players, and w is the time window.

    :param solution_per_time: A solution in the shape [w,q,p] where solution_per_position[w,q,p] is 1 if
    player p plays at position q during time window w, and 0 otherwise.
    :param sk: a skillmatrix of class SkillMatrix.
    :param windows: a List of integers representing the different time windows.
    :return: A long DataFrame with all the player's positions at each time window
    """
    players = sk.get_players()
    positions = sk.get_positions()
    player_names = sk.get_player_names()
    position_names = sk.get_position_names()

    squad = []
    w = 0
    for w in windows:
        for q in positions:
            p = np.where(solution_per_time[w][q])[0][0]
            squad.append({'window': w, 'position': q, 'player': p})

    df_squad = pd.DataFrame(squad)
    player_window_combinations = pd.DataFrame(list(product(players, windows)), columns=['player', 'window'])
    df_squad = pd.merge(df_squad, player_window_combinations, on=['player', 'window'], how='outer')
    df_squad = df_squad.sort_values(['window', 'position'])
    df_squad = df_squad.reset_index()
    df_squad['player'] = [player_names[i] for i in df_squad['player']]
    df_squad['position'] = [position_names[int(i)] if not np.isnan(i) else np.nan for i in df_squad['position']]
    df_squad['position'] = df_squad['position'].fillna('Substitute')
    df_squad['score'] = [sk.skillmatrix[df_squad['position'][i]][df_squad['player'][i]]
                         if df_squad['position'][i] is not 'Substitute' else 0 for i in range(df_squad.shape[0])]
    df_squad = df_squad.drop('index', axis=1)
    return df_squad
