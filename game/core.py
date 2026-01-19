from agent.core import Agent
from agent.manager import AgentManager
from agent.task import TaskResult
from game.board import Board
from statistic.core import Statistics
from util.config import *
from util.theme import *

import pygame
from enum import Enum


class GameMode(Enum):
    """An enum to hold the different types of game modes the game can have."""
    STEP = 1
    CONTINUOUS = 2


class Game:
    """Handles user input, game cycles and drawing of the game board.

    :ivar _clock (pygame.time.Clock): The game clock.
    :ivar _screen: The game screen.
    :ivar _font (pygame.font.Font): The game font.
    :ivar _running (bool): Whether the game is running.
    :ivar _restart (bool): Whether the game should be restarted, after it stops running.
    :ivar _mode (GameMode): The current game mode.
    :ivar _step_requested (bool): Whether a game step was requested by the user.
    :ivar _step_interval (float): The intervall of time that needs to pass in continuous game mode
        for a game step to happen.
    :ivar _time_since_last_step (float): The amount of time that passed since the last game step.
    :ivar _board (Board): The game board.
    :ivar _agents (list[Agent]): The list of agents that play the game.
    :ivar _agent_manager (AgentManager): The AgentManger for the agents.
    :ivar _clear_vision (bool): Whether the user sees the entire board or only what the agents see.
    """
    def __init__(self):
        pygame.init()
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self._font: pygame.font.Font = pygame.font.SysFont(None, 24)

        self._running: bool = True
        self._restart: bool = False

        self._mode: GameMode = GameMode.STEP

        self._step_requested: bool = False
        self._step_interval: float = 0.1
        self._time_since_last_step: float = 0

        self._board: Board = Board()
        self._agents: list[Agent] = [
            Agent(1),
            Agent(2),
            Agent(3),
            Agent(4),
        ]
        self._agent_manager: AgentManager = AgentManager(self._agents)

        self._clear_vision: bool = False

        self._statistic: Statistics = Statistics()
        self._game_steps: int = 0

    def _setup_game(self) -> None:
        """Sets up the game."""
        self._running = True
        self._board.setup_board(self._agents)

        for agent in self._agents:
            self._agent_manager.update_beliefs(agent, TaskResult())

    def _restart_game(self) -> None:
        """Reset the game state and start a new game."""
        self._restart = False

        self._game_steps = 0

        self._board.reset()
        self._agent_manager.reset()
        for agent in self._agents:
            agent.reset()

    def start_game(self) -> None:
        while True:
            self._setup_game()
            self._run()

            self._statistic.update(
                self._game_steps,
                sum(agent.dead for agent in self._agents),
                len(self._agent_manager.shared_visited)
            )

            if self._statistic.get_cycles() % 50 == 0 and STATISTICS_ENABLED:
                print(self._statistic.get_cycles())

            if not self._restart or self._statistic.get_cycles() >= MAX_CYCLES:
                break

            self._restart_game()

        if STATISTICS_ENABLED:
            self._statistic.create_file()

    def _run(self) -> None:
        """Runs the game-loop."""
        while self._running:
            dt = self._clock.tick(60) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self) -> None:
        """Handles the user inputs."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self._mode == GameMode.STEP:
                    self._step_requested = True
                elif event.key == pygame.K_PLUS and self._mode == GameMode.CONTINUOUS:
                    self._step_interval /= 2
                elif event.key == pygame.K_MINUS and self._mode == GameMode.CONTINUOUS:
                    self._step_interval *= 2
                elif event.key == pygame.K_RETURN:
                    if self._mode == GameMode.STEP:
                        self._mode = GameMode.CONTINUOUS
                    else:
                        self._mode = GameMode.STEP
                        self._time_since_last_step = 0
                elif event.key == pygame.K_c:
                    self._clear_vision = not self._clear_vision
                elif event.key == pygame.K_r:
                    self._running = False
                    self._restart = True

    def _update(self, dt: float) -> None:
        """Updates the game state.

        :param dt: The amount of time between this and the last cycle in seconds.
        """
        if self._mode == GameMode.STEP and self._step_requested:
            self._step_requested = False
            self._game_step()
        elif self._mode == GameMode.CONTINUOUS:
            self._time_since_last_step += dt
            if self._time_since_last_step >= self._step_interval:
                self._game_step()
                self._time_since_last_step = 0

    def _game_step(self) -> None:
        """One-step cycle of the game, following this Order:

        - Agent-Manager creates tasks.
        - All agents bid on the created tasks.
        - Agent-Manager awards a task to each agent.
        - Each agent executes the awarded task.
        - Result of the executed task is handled.
        - Agent perceives information of its cell and updates the shared beliefs.
        """
        self._game_steps += 1

        tasks = self._agent_manager.create_tasks(self._board)

        bids = self._agent_manager.create_bids(tasks)

        awarded_tasks = self._agent_manager.award_tasks(bids)

        if not awarded_tasks:
            self._statistic.increase_stuck_amount()
            self._running = False
            self._restart = True
            return

        for agent in self._agents:
            if agent.agent_id not in awarded_tasks:
                continue

            result = self._board.execute_task(agent, awarded_tasks[agent.agent_id])

            if result.gold:
                self._running = False
                self._restart = True
                return

            self._agent_manager.update_beliefs(agent, result)

    def _draw(self) -> None:
        """Draws the game window."""
        self._screen.fill((255, 255, 255))

        self._draw_board()

        pygame.display.flip()

    def _draw_board(self) -> None:
        """Draws the game board."""
        for cell in self._board.cells:
            rect = pygame.Rect(
                cell.x * TILE_SIZE,
                cell.y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )

            agent = next(
                (agent for agent in self._agents if agent.x == cell.x and agent.y == cell.y and not agent.dead),
                None
            )

            if self._clear_vision:
                if agent:
                    color = AGENT_COLOR
                elif cell.hasWumpus:
                    color = WUMPUS_COLOR
                elif cell.hasDeadWumpus:
                    color = DEAD_WUMPUS_COLOR
                elif cell.hasPit:
                    color = PIT_COLOR
                elif cell.hasGold:
                    color = GOLD_COLOR
                elif cell.hasBreeze and cell.hasStench:
                    color = BRENCH_COLOR
                elif cell.hasBreeze:
                    color = BREEZE_COLOR
                elif cell.hasStench:
                    color = STENCH_COLOR
                else:
                    color = GRAY
            else:
                if agent:
                    color = AGENT_COLOR
                elif (self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("potential_wumpus") or
                      self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("potential_pit")):
                    color = DANGER_COLOR
                elif self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("wumpus"):
                    color = WUMPUS_COLOR
                elif self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("dead_wumpus"):
                    color = DEAD_WUMPUS_COLOR
                elif self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("pit"):
                    color = PIT_COLOR
                elif (cell.x, cell.y) in self._agent_manager.shared_visited:
                    if cell.hasBreeze and cell.hasStench:
                        color = BRENCH_COLOR
                    elif cell.hasBreeze:
                        color = BREEZE_COLOR
                    elif cell.hasStench:
                        color = STENCH_COLOR
                    else:
                        color = GRAY
                else:
                    color = DARK_GRAY

            pygame.draw.rect(self._screen, color, rect)
            pygame.draw.rect(self._screen, (50, 50, 50), rect, 1)

            if agent:
                label = self._font.render(f"{agent.agent_id}", True, BLACK)
                rect = label.get_rect(center=rect.center)
                self._screen.blit(label, rect)
