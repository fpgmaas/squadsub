## The Squad Substitution Optimization Problem

<img src="etc/soccer-ball-ss-img.jpg" alt="drawing" width="300"/>

### Problem definition

During a football match, players can be substituted. Different players have different skills, so not every substitution is beneficial to the team performance. This raises the question; which *player* should play at which *position* at which *time* such that the team performance is optimal? In this repository, a solution approach is proposed and implemented.

 
### Solution approach

This problem can be solved by modelling it as a Linear Programming problem. The input for this LP is the skillmatrix, containing the skills of a set of players at a set of positions.

|          | Position 1 | Position 2 | Position 3 |
| -------- | ---------- | ---------- | ---------- |
| Player 1 | 5          | 3          | 3          |
| Player 2 | 1          | 5          | 5          |
| Player 3 | 3          | 3          | 3          |
| Player 4 | 2          | 5          | 2          |

Obviously, the optimal strategy would be to create one optimal squad and have that squad play during the entire match, but that would mean some players do not get to play at all. Therefore, we also include equality constraints in the model; players should play an approximately equal amount of time. We also assume that players are not allowed to change positions on the pitch without substituting in between, since that could lead to a lot of confusion on the pitch.

The entire formulation can be found [here.](https://github.com/flo12392/squadsub/blob/master/formulation/formulation.pdf)

### How to run?

- First, edit the file in *data/skillmatrix.csv* so it contains the skillmatrix of your team.
- Make sure you have [PuLP](https://pythonhosted.org/PuLP/main/installing_pulp_at_home.html) installed.
- run *main.py*
- When the script is done running, the solutions to your problem can be found in the *results* folder.