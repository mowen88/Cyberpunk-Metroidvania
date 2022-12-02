from state import State
from room import Room

class Title(State):
	def __init__(self, game):
		State.__init__(self, game)

	def update(self, actions):
		if actions['return']:
			new_state = Room(self.game)
			new_state.enter_state()
		self.game.reset_keys()

	def render(self, display):
		display.fill((self.game.BLACK))
		self.game.draw_text(display, 'Title Screen', (245,245,245), 30, (self.game.WIDTH // 2, self.game.HEIGHT // 2))
