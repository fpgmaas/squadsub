## The Squad Substitution Optimization Problem

![](etc/walle_eve_soccer.png)

### Problem definition

During a football match, players can be substituted. Different players have different skills, so not every substitution is beneficial to the team performance. This raises the question; which *player* should play at which *position* at which *time* such that the team performance is optimal? In this repository, a solution approach is proposed and implemented.

Obviously, the optimal strategy would be to create one optimal squad and have that squad play during the entire match, but that would mean some players do not get to play at all. Therefore, we make the assumption of fairness; players should play an approximately equal amount of time. We also assume that players are not allowed to change positions on the pitch without substituting in between, since that could lead to a lot of confusion on the pitch.

 
### Solution approach

This problem can be solved by modelling it as a Linear Programming problem. The input for this LP is the skillmatrix, containing the skills of a set of players at a set of positions.

|          | Position 1 | Position 2 | Position 3 |
| -------- | ---------- | ---------- | ---------- |
| Player 1 | 5          | 3          | 3          |
| Player 2 | 1          | 5          | 5          |
| Player 3 | 3          | 3          | 3          |
| Player 4 | 2          | 5          | 2          |

To model this problem, the match is split up into *w* periods of equal length. The decision variables for this LP problem can then be defined as *x<sub>pqw</sub>* , where *x<sub>pqw</sub>* is 1 if player *p* plays at position *q* during time window *w* and 0 otherwise. The entire formulation can be found [here.](https://github.com/flo12392/squadsub/blob/master/formulation/formulation.pdf)

### How to run?

- First, edit the file in *data/skillmatrix.csv* so it contains the skillmatrix of your team.
- Make sure you have [PuLP](https://pythonhosted.org/PuLP/main/installing_pulp_at_home.html) installed.
- run *main.py*
- When the script is done running, the solutions to your problem can be found in the *results* folder. An example of a resulting file can be found [here](https://github.com/flo12392/squadsub/blob/master/results/example_result.txt).