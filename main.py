import pandas as pd
import numpy as np
from pulp import *

# SETTINGS --------------------------------------------------------------

skillmatrix = pd.read_csv('skillmatrix.csv', sep=',',header=0, index_col = 0)
players = list(range(skillmatrix.shape[0]))
positions = list(range(skillmatrix.shape[1]))
print(skillmatrix)

n_windows = 4
match_time = 90
windows = list(range(n_windows))

# LINEAR OPTIMIZATION -------------------------------------------------

prob = LpProblem("Squad Substitution Problem",LpMaximize)

# Initialize the decision variables. x[p][q][w] is 1 if player p plays on position q during timewindow w.
x = LpVariable.dicts("Choice",(players,positions,windows),0,1,LpInteger)

# The objective function, maximimize the total skills of the team.
prob += lpSum([skillmatrix.values[p][q] * x[p][q][w] for p in players for q in positions for w in windows])

# During every timewindow, there should be exactly as many players in the field as there are available positions
for w in windows:
    prob += lpSum([x[p][q][w] for p in players for q in positions]) == len(positions)

# We want players to play approximately an equal amount of time.
T1 = np.floor(len(windows)*len(positions)/len(players))
T2 = np.ceil(len(windows)*len(positions)/len(players))
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

# A player is not allowed to change places in the pitch while he/she is in play. The player is only allowed to play in different positions if he is substituted in between.
for q_star in positions:
    for p in players:
        for w in windows[:-1]:
            prob += lpSum([x[p][q][w + 1] for q in positions if q != q_star] + [x[p][q_star][w]]) <= 1

prob.solve()

solution_per_player = np.array([[[x[p][q][w].varValue for w in windows] for q in positions] for p in players])
solution_per_time = np.array([[[x[p][q][w].varValue for p in players] for q in positions] for w in windows])


# To get a second solution

total = np.sum([value(x[p][q][w]) for p in players for q in positions for w in windows])
prob += lpSum([(1 if value(x[p][q][w])>0 else -1) * x[p][q][w] for p in players for q in positions for w in windows]) <= total-1
prob.solve()

solution_per_player = np.array([[[x[p][q][w].varValue for w in windows] for q in positions] for p in players])
solution_per_time = np.array([[[x[p][q][w].varValue for p in players] for q in positions] for w in windows])
solution_per_position = np.array([[[x[p][q][w].varValue for w in windows] for p in players] for q in positions])

