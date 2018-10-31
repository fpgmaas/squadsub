import pandas as pd
import numpy as np
from itertools import product

def get_substitution_dataframe(solution_per_position, positions, windows) -> pd.DataFrame:
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
    return df_substitutions

def get_squad_dataframe(solution_per_time,players,positions,windows):
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
    return df_squad
