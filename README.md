## The Squad Substitution Optimization Problem

### Problem definition

Almost everyone on the planet is familiar with the concept of *team sports*; two teams are expected to participate in a competitive match against each other before they are allowed to head inside the clubhouse for a drink with their teammates. A team usually consists of more players than there are actually allowed to play simultaneously. Therefore, a part of the team takes place in the dugout and they can enter play by switching places with another player that is active on the court; a so-called *substitution*.

However, this leads to a difficult problem: A team usually plays in a formation with a number of positions, where every position has a different role on the pitch. Simultaneously, every player has different preferences and/or competences for playing in certain positions. So the question to be answered is; which *player* plays at which *position* at which *time* such that the team performance is optimal? 

### Solution approach

This problem can be solved by modelling it as a Linear Programming problem. The input for this LP

|          | Position 1 | Position 2 | Position 3 |
| -------- | ---------- | ---------- | ---------- |
| Player 1 | 5          | 3          | 3          |
| Player 2 | 1          | 5          | 5          |
| Player 3 | 3          | 3          | 3          |
| Player 4 | 2          | 5          | 2          |

Obviously, the optimal strategy would be to create one optimal squad and have that squad play during the entire match, but that would mean some players do not get to play at all. Therefore, we also include equality constraints in the model; players should play an approximately equal amount of time.

The entire formulation can be found [here.](https://github.com/flo12392/squadsub/blob/master/formulation/formulation.pdf)

### How to run?

