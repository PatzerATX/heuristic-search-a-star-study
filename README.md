# A* Search Variants: Empirical Analysis of Heuristic Pathfinding Strategies

## Abstract
This project presents an implementation and empirical analysis of multiple A* search variants in stochastic gridworld environments. The study evaluates how algorithmic modifications—specifically search direction, replanning strategies, and heuristic adaptation—affect computational efficiency while preserving optimality. Results focus on node expansion behavior, path cost, and the impact of tie-breaking strategies.

---

## 1. Introduction
Heuristic search is a fundamental component of artificial intelligence, particularly in pathfinding and planning problems. While the standard A* algorithm guarantees optimal solutions under admissible and consistent heuristics, variations such as Repeated Forward A*, Repeated Backward A*, and Adaptive A* introduce different trade-offs in efficiency and information reuse.

This project investigates these trade-offs through controlled experimentation in partially observable grid environments.

---

## 2. Problem Formulation

- Environment: 2D gridworld with stochastic obstacles  
- State space: discrete cells in a bounded grid  
- Actions: 4-connected movement (up, down, left, right)  
- Cost model: uniform step cost  
- Objective: compute a shortest path from start to goal  

The agent initially has incomplete knowledge of blocked cells and must update its internal model through repeated planning.

---

## 3. Algorithms

### 3.1 Forward A*
Performs standard A* search from start to goal using the Manhattan distance heuristic.

### 3.2 Repeated Forward A*
Replans from the agent’s current position whenever a blocked cell is encountered during execution.

### 3.3 Repeated Backward A*
Performs search from goal to start, updating knowledge of obstacles during execution.

### 3.4 Adaptive A*
Updates heuristic values based on previous search results:

h(s) = g(goal) - g(s)

This allows subsequent searches to reuse information and reduce node expansions.

---

## 4. Experimental Design

- Grid size: typically 51 × 51  
- Obstacle probability: 0.3  
- Multiple randomized trials per configuration  
- Start and goal selected from unblocked cells  

### Evaluation Metrics:
- Number of expanded nodes  
- Path length (optimality check)  
- Search efficiency across repeated runs  

### Tie-breaking strategies:
- High-g preference  
- Low-g preference  

---

## 5. Results and Observations

Key findings include:

- Tie-breaking strategies significantly influence search space exploration.
- Repeated Backward A* may expand more nodes due to delayed discovery of critical obstacles near the start.
- Adaptive A* reduces redundant exploration by leveraging updated heuristic values.
- All variants maintain optimal path cost under consistent heuristics, but differ substantially in computational efficiency.

---

## 6. Visualization

The system includes visualization tools to display:

- Grid environments  
- Expanded nodes during search  
- Final solution paths  
- Start and goal states  

---

## 7. Implementation Details

- Language: Python  
- Libraries: NumPy, Matplotlib  
- Data representation: 2D grid (0 = free, 1 = blocked)  
- Heuristic: Manhattan distance  

---

## 8. Reproducibility

Experiments can be reproduced by running:

python main.py

Additional functionality includes:
- saving generated grid environments  
- loading predefined test cases  
- exporting visualizations as images  

---

## 9. Future Work

- Extension to weighted or dynamic environments  
- Integration with real-world map data  
- Parallelization of search strategies  
- Comparison with learning-based approaches  

---

## 10. Conclusion

This project demonstrates that while A* guarantees optimality, algorithmic variations significantly impact efficiency. In particular, Adaptive A* highlights the benefits of incorporating prior search knowledge, suggesting a bridge between classical search and learning-based methods.

---

## Keywords
A*, heuristic search, pathfinding, adaptive search, gridworld, artificial intelligence

## Game Update

A game function was added to the project where the user and an AI agent race to a finishing point. Game functions include maze walls, visibility of cells revealed as each actor progresses, and action cells that contain various effects that hurt or harm each agent.
