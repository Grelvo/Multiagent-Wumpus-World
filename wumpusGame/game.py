from wumpusGame.board import Board
from agents.baseAgent import BaseAgent
from agents.explorerAgent import ExplorerAgent
from util.config import WINDOW_SIZE, TILE_SIZE, LEADERBOARD_WIDTH
from util.theme import WUMPUS_COLOR, GOLD_COLOR, PIT_COLOR, BREEZE_COLOR, STENCH_COLOR, AGENT_COLOR, BLACK, GRAY, DARK_GRAY

import pygame
from enum import Enum


class GameMode(Enum):
    STEP = 1
    CONTINUOUS = 2


class WumpusGame:
    def __init__(self):
        pygame.init()
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode((WINDOW_SIZE + LEADERBOARD_WIDTH, WINDOW_SIZE))
        self._font = pygame.font.SysFont(None, 24)

        self._running = True

        self._mode = GameMode.STEP
        self._step_requested = False
        self._step_interval = 0.1
        self._time_since_last_step = 0

        self._board: Board = Board()
        self._agents: dict[BaseAgent, int] = {
            ExplorerAgent(1): 0,
            ExplorerAgent(2): 0,
            ExplorerAgent(3): 0,
            ExplorerAgent(4): 0,
        }
        self._selected_agent_id: int | None = None

    def start_game(self) -> None:
        """Starts the Hunt der Wumpus Game"""
        self._running = True
        self._board.setup_board(list(self._agents.keys()))
        self._run()

    def _run(self) -> None:
        """Runs the Game-loop"""
        while self._running:
            dt = self._clock.tick(60) / 1000
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
                if pygame.K_0 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_0 - 1
                    if 0 <= num < len(self._agents):
                        if self._selected_agent_id == num:
                            self._selected_agent_id = None
                        else:
                            self._selected_agent_id = num
                    print(self._selected_agent_id)

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
        for agent in self._agents.keys():
            if agent.dead:
                continue

            x, y = agent.decide_next_move(self._board)
            agent.x, agent.y = x, y
            agent.visited.append((x, y))

            cell = self._board.grid[x][y]
            if cell.hasWumpus or cell.hasPit:
                # Agent Died
                agent.dead = True

            if cell.hasGold:
                # Agent Wins
                agent.score += 1
                self._running = False

    def _draw(self) -> None:
        """Draws the Game Window"""
        self._screen.fill((255, 255, 255))

        self._draw_board()
        self._draw_leaderboard()

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
                (agent for agent in self._agents.keys() if agent.x == cell.x and agent.y == cell.y and not agent.dead),
                None
            )
            if agent:
                color = AGENT_COLOR
            elif (self._selected_agent_id is not None
                  and (cell.x, cell.y) not in list(self._agents.keys())[self._selected_agent_id].visited):
                color = DARK_GRAY
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
                color = GRAY

            pygame.draw.rect(self._screen, color, rect)
            pygame.draw.rect(self._screen, (50, 50, 50), rect, 1)

            if agent:
                label = self._font.render(f"{agent.agent_id}", True, BLACK)
                rect = label.get_rect(center=rect.center)
                self._screen.blit(label, rect)

    def _draw_leaderboard(self):
        """Draws the Leaderboard"""

        start_x = WINDOW_SIZE + 20
        start_y = 20
        spacing = 40

        rect = pygame.Rect(WINDOW_SIZE, 0, LEADERBOARD_WIDTH, 50)
        label = self._font.render("Leaderboard", True, BLACK)
        rect = label.get_rect(center=rect.center)
        self._screen.blit(label, rect)

        for index, agent in enumerate(sorted(self._agents, key=lambda a: -a.score)):
            label = self._font.render(f"{agent.agent_id}: {agent.score}", True, BLACK)
            self._screen.blit(label, (start_x, start_y + spacing * (index + 2)))

    def _cleanup(self):
        """Clean Up and reset the Game"""
        self._board.reset()
        for agent in self._agents:
            agent.reset()
        self.start_game()
