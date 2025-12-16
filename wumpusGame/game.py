from wumpusGame.board import Board
from agents.baseAgent import BaseAgent
from agents.explorerAgent import ExplorerAgent
from util.config import WINDOW_SIZE, TILE_SIZE
from util.theme import WUMPUS_COLOR, GOLD_COLOR, PIT_COLOR, BREEZE_COLOR, STENCH_COLOR, AGENT_COLOR

import pygame
from enum import Enum
from copy import copy


class GameMode(Enum):
    STEP = 1
    CONTINUOUS = 2


class WumpusGame:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

        self._running = True

        self._mode = GameMode.STEP
        self._step_requested = False
        self._step_interval = 0.1
        self._time_since_last_step = 0

        self._board: Board = Board()
        self._agents: list[BaseAgent] = []

    def start_game(self) -> None:
        """Starts the Hunt der Wumpus Game"""
        self._running = True
        self._agents = [
            ExplorerAgent(),
            ExplorerAgent(),
            ExplorerAgent(),
            ExplorerAgent(),
        ]
        self._board.setup_board(self._agents)
        self._run()

    def _run(self) -> None:
        """Runs the Game-loop"""
        while self._running:
            dt = self.clock.tick(60) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()
        self._cleanup()

    def _handle_events(self) -> None:
        """Handles the User Inputs"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self._mode == GameMode.STEP:
                    self._step_requested = True
                if event.key == pygame.K_RETURN:
                    if self._mode == GameMode.STEP:
                        self._mode = GameMode.CONTINUOUS
                    else:
                        self._mode = GameMode.STEP
                        self._time_since_last_step = 0

    def _update(self, dt: float) -> None:
        """Updates any other"""
        if self._mode == GameMode.STEP and self._step_requested:
            self._step_requested = False
            self._game_step()
        elif self._mode == GameMode.CONTINUOUS:
            self._time_since_last_step += dt
            if self._time_since_last_step >= self._step_interval:
                self._game_step()
                self._time_since_last_step = 0

    def _game_step(self) -> None:
        """One Step in the Game"""
        for agent in copy(self._agents):
            x, y = agent.decide_next_move(self._board)
            agent.x, agent.y = x, y
            agent.visited.append((x, y))

            cell = self._board.grid[x][y]
            if cell.hasWumpus or cell.hasPit:
                # Agent Died
                self._agents.remove(agent)

            if cell.hasGold:
                # Agent Wins
                self._running = False

    def _draw(self) -> None:
        """Draws the Game Window"""
        self.screen.fill((255, 255, 255))

        agent_positions = [[agent.x, agent.y] for agent in self._agents]
        for cell in self._board.cells:
            rect = pygame.Rect(
                cell.x * TILE_SIZE,
                cell.y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )

            if [cell.x, cell.y] in agent_positions:
                color = AGENT_COLOR
            #elif (cell.x, cell.y) not in self._agents[0].visited:
            #    color = (127, 127, 127)
            elif cell.hasWumpus:
                color = WUMPUS_COLOR
            elif cell.hasPit:
                color = PIT_COLOR
            elif cell.hasGold:
                color = GOLD_COLOR
            elif cell.hasBreeze:
                color = BREEZE_COLOR
            elif cell.hasStench:
                color = STENCH_COLOR
            else:
                color = (200, 200, 200)

            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

        pygame.display.flip()

    def _cleanup(self):
        self.start_game()
