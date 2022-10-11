import pygame

from state import State
from level import Level

class GameState(State):
	def __init__(self, game):
		State.__init__(self, game)
		self.game.level.run()
		self.game.ui.show_health(50, 100)
		self.game.ui.show_current_weapon(self.current_weapon)

