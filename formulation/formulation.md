## Formulation of the Squad Substitution Optimization problem

The Squad Substitution Optimization Problem, where we want to optimize the substitution strategy during a sports match given a set of players, positions and a number of time windows can be defined by the formulation given below. First, define the following variables and parameters:

- $x_{pqw}$ is equal to $1$ if player $p$ plays at position $q$ during time window $w$, and $0$ otherwise.
- $a_{pq}$ is the competence level of player p for playing at position q
- $P$ is the set of players
- $Q$ is the set of positions
- $W$ is the set of time windows
- $T_{1} = \lfloor \frac{|W| * |Q|}{|P|} \rfloor$, the minimum number of time windows a player should be on the pitch
- $T_{2} = \lceil \frac{|W| * |Q|}{|P|} \rceil$, the maximum number of time windows a player should be on the pitch
- $m$ is the minimum number of time windows a player should be on the pitch between subsequent substitution.

$$
max \sum_{p \in P} \sum_{q \in Q} \sum_{w \in W} a_{pq} * x_{pqw}\label{ref1}
$$

$$
subject \; to \nonumber
$$

$$
\sum_{q \in Q} x_{pqw} \le 1,  \; \forall p \in P, \forall w \in W\label{ref2}
$$

$$
\sum_{p \in P} x_{pqw} = 1,  \; \forall q \in Q, \forall w \in W\label{ref3}
$$

$$
x_{pq^{*}w} + \sum_{q \in Q, q \ne q^{*}} x_{pqw+1} \le 1, \; \forall p \in P, \forall q^{*} \in Q, \forall w \in \{1,2, \dots, {|W|-1}\}\label{ref4}
$$

$$
\sum_{w \in W} \sum_{q \in Q} x_{pqw} \ge T_{1},  \; \forall p \in P\label{ref5}
$$

$$
\sum_{w \in W} \sum_{q \in Q} x_{pqw} \le T_{2},  \; \forall p \in P\label{ref6}
$$

$$
\sum_{y \in \{0,1,\dots,m\}} \sum_{q \in Q} x_{pqw+y} \ge m,  \; \forall p \in P, \forall w \in \{1,2,\dots,|W|-m\}\label{ref7}
$$

$$
x_{pqw} \in \{0,1\}, \; \forall p \in P, \forall q \in Q, \forall w \in W\label{ref8}
$$

Here, The objective function $\ref{ref1}$ maximizes the sum of the skills of players that are on the pitch each time window. Constraint $\ref{ref2}$ ensures that every player occupies at most one position during every time window, i.e. they are either on the pitch or they are a substitute. Constraint $\ref{ref3}$ states that every position should be filled by exactly one player during every time window. Furthermore, Constraint $\ref{ref4}$ prohibits players from changing positions on the pitch in subsequent time windows; a player can only play on another position if he is substituted in between. Constraints $\ref{ref5}$ and $\ref{ref6}$ aim to balance the amount of times each player is substituted. Constraint $\ref{ref7}$ ensures that there is a minimum amount of time windows between subsequent substitutions of a single player. Lastly, Constraint $\ref{ref8}$ states that the $x$-variables can only take binary values.