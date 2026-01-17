import json

from wumpusGame.board import Board
from wumpusGame.agent import Agent
from wumpusGame.agentManager import AgentManager
from wumpusGame.task import Task
from util.config import WINDOW_SIZE, TILE_SIZE
from util.theme import *

import pygame
from enum import Enum


class GameMode(Enum):
    STEP = 1
    CONTINUOUS = 2


class WumpusGame:
    def __init__(self):
        pygame.init()
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self._font = pygame.font.SysFont(None, 24)

        self._running = True
        self._restart = False

        self._mode = GameMode.STEP
        self._step_requested = False
        self._step_interval = 0.1
        self._time_since_last_step = 0

        self._board: Board = Board()
        self._agents: list[Agent] = [
            Agent(1),
            Agent(2),
            Agent(3),
            Agent(4),
        ]
        self._agent_manager = AgentManager(self._agents)

        self._clear_vision: bool = False

    def start_game(self) -> None:
        """Starts the Hunt der Wumpus Game"""
        self._running = True
        self._board.setup_board(list(self._agents))

        for agent in self._agents:
            percept = self._board.get_percept(agent.x, agent.y)
            self._agent_manager.update_beliefs(agent, percept)

        self._run()

    def _run(self) -> None:
        """Runs the Game-loop"""
        while self._running:
            dt = self._clock.tick(60) / 1000
            self._handle_events()
            self._update(dt)
            self._draw()
        if self._restart:
            self._cleanup()

    def _handle_events(self) -> None:
        """Handles the User Inputs"""
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
        """Updates the Game state"""
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
        tasks = self._agent_manager.create_tasks(self._board)

        bids = self._agent_manager.create_bids(tasks)

        awarded_tasks = self._agent_manager.award_tasks(bids)

        for agent in self._agents:
            if agent.agent_id in awarded_tasks:
                task = Task(type_="MOVE", target=awarded_tasks[agent.agent_id].target)
                result = self._board.execute_task(agent, task)

                if result.dead:
                    agent.dead = True
                    print("someone died")
                elif result.gold:
                    self._running = False
                    self._restart = True

                percept = self._board.get_percept(agent.x, agent.y)
                self._agent_manager.update_beliefs(agent, percept)

    def _draw(self) -> None:
        """Draws the Game Window"""
        self._screen.fill((255, 255, 255))

        self._draw_board()

        pygame.display.flip()

    def _draw_board(self):
        """Draws the Game Board"""
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
                elif cell.hasAliveWumpus:
                    color = WUMPUS_COLOR
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
                elif self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("wumpus"):
                    color = WUMPUS_COLOR
                elif self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("pit"):
                    color = PIT_COLOR
                elif self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("potential_wumpus") or self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("potential_pit"):
                    color = DANGER_COLOR
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


            # if agent:
            #     color = AGENT_COLOR
            # elif not self._clear_vision and self._agent_manager.potential_danger((cell.x, cell.y)):
            #     color = DANGER_COLOR
            # elif cell.hasAliveWumpus and (self._clear_vision or self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("wumpus")):
            #     color = WUMPUS_COLOR
            # elif cell.hasPit and (self._clear_vision or self._agent_manager.shared_beliefs.get((cell.x, cell.y), {}).get("pit")):
            #     color = PIT_COLOR
            # elif not self._clear_vision and (cell.x, cell.y) not in self._agent_manager.shared_visited:
            #     color = DARK_GRAY
            # elif cell.hasGold:
            #     color = GOLD_COLOR
            # elif cell.hasBreeze and cell.hasStench:
            #     color = BRENCH_COLOR
            # elif cell.hasBreeze:
            #     color = BREEZE_COLOR
            # elif cell.hasStench:
            #     color = STENCH_COLOR
            # else:
            #     color = GRAY

            pygame.draw.rect(self._screen, color, rect)
            pygame.draw.rect(self._screen, (50, 50, 50), rect, 1)

            if agent:
                label = self._font.render(f"{agent.agent_id}", True, BLACK)
                rect = label.get_rect(center=rect.center)
                self._screen.blit(label, rect)

    def _cleanup(self):
        """Clean Up and reset the Game"""
        self._restart = False
        self._board.reset()
        self._agent_manager.reset()
        for agent in self._agents:
            agent.reset()
        self.start_game()
