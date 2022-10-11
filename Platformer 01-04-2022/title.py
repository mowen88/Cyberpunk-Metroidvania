import pygame 

from state import State
from gamestate import GameState

class Title(State):
	def __init__(self, game):
		State.__init__(self, game)

	def update(self, actions):
		if actions['select']:
			new_state = GameState(self.game)
			new_state.enter_state()
		self.game.reset_keys()

	def draw(self, display):
		display.fill(self.game.BLACK)
		self.game.draw_text(display, 'Demo state', (self.game.WHITE), (self.game.WIDTH // 2, self.game.HEIGHT // 2))



