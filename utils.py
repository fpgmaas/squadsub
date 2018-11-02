import pandas as pd
import numpy as np
from itertools import product

class SkillMatrix():

    def __init__(self, skillmatrix):
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
    return df_substitutions

def get_squad_dataframe(solution_per_time,sk,windows):
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
    return df_squad

def write_result_to_file(file_name, objective_score, df_squad, df_substitutions, player_names):
    tfile = open(file_name, 'w')
    tfile.write('Optimal score: {:.2f}'.format(objective_score))
    tfile.write('\n\n')
    tfile.write(df_squad.to_string())
    tfile.write('\n\n')
    tfile.write(df_substitutions.to_string())
    for p in player_names:
        tfile.write('\n\n')
        tfile.write(p + ': ')
        tfile.write(' - '.join((df_squad[df_squad['player'] == p][['position', 'score']]).apply(
            lambda x: '{} ({})'.format(x[0], str(x[1])), axis=1).tolist()))
    tfile.close()