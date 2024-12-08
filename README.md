# Pacman AI Contest Team

This project is an implementation for the **Pacman AI Contest**, which revolves around developing intelligent agents to compete in a strategic game of Pacman. This README provides an overview of the project, features of the AI agents, and instructions to run and customize the implementation.

---

## **Overview**

The project implements a team of two specialized AI agents for the game:

1. **OffensiveReflexAgent**: Focuses on scoring points by consuming food and capsules on the opponent's side of the map.
2. **DefensiveReflexAgent**: Specializes in protecting the team's food and deterring invaders.

These agents utilize advanced strategies like **Monte Carlo simulation**, dynamic feature weighting, and patrol-based decision-making to enhance their gameplay.

The implementation builds upon UC Berkeley's Pacman Projects ([link](http://ai.berkeley.edu/project_overview.html)).

---

## **Features**

### **Offensive Agent**
The **OffensiveReflexAgent** is designed to:
- Navigate into enemy territory and consume food and capsules.
- Use capsules to temporarily disable enemies, allowing safe navigation.
- Dynamically adjust its strategy based on game state:
  - **Attack Mode**: Actively seeks food and capsules.
  - **Return Mode**: Prioritizes returning to the team's side when carrying significant points or facing high risk.

Key Features:
- **Food Distance**: Calculates the shortest path to the nearest food.
- **Opponent Avoidance**: Maintains distance from enemies unless they are scared.
- **Monte Carlo Simulation**:
  - Simulates multiple future game states to evaluate and choose the best action.
  - Considers both short-term rewards and long-term consequences.

---

### **Defensive Agent**
The **DefensiveReflexAgent** is responsible for:
- Protecting the team's resources and deterring invaders.
- Chasing and intercepting enemy Pacman in the team's half of the map.
- Patrolling high-priority areas to proactively prevent theft.

Key Features:
- **Dynamic Patrols**:
  - Focuses on areas where food has recently been stolen.
  - Adjusts patrol routes based on the opponent's behavior and game state.
- **Enemy Tracking**:
  - Pursues and intercepts opponents when they invade the team's territory.
- **Food Protection**:
  - Prioritizes defending critical food resources, especially when the team has fewer resources remaining.

---

### **Monte Carlo Simulation**
Monte Carlo simulation is a statistical method used by the **OffensiveReflexAgent** to evaluate potential actions. It works as follows:
1. **Simulate Game States**: Generate multiple possible outcomes for each action by playing out random sequences of future moves.
2. **Calculate Rewards**: Evaluate the desirability of each outcome based on features such as points scored, safety, and proximity to key objectives.
3. **Select the Best Action**: Choose the action with the highest average reward.

This allows the agent to account for uncertainty and make more robust decisions.

---

## **Getting Started**

### **Prerequisites**
- **Python 3.8**: Ensure you have Python 3.8 installed on your system.

### **Installation**
1. Clone this repository.
2. Navigate to the project directory.

---

### **How to Run**
To run the contest, use the following command:
```bash
python capture.py -r my_team -b baselineTeam
