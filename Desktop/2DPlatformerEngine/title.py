from state import State
from zone import Zone

class Title(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.title_surf = self.game.font.render(str('Title Screen'), True, self.game.YELLOW)
		self.title_rect = self.title_surf.get_rect()
		self.title_rect = self.title_surf.get_rect(center = (self.game.WIDTH * 0.5, self.game.HEIGHT * 0.5))

	def update(self, actions):
		if actions['return']:
			new_state = Zone(self.game)
			new_state.enter_state()
		self.game.reset_keys()

	def render(self, display):
		display.fill((self.game.MAGENTA))
		display.blit(self.title_surf, self.title_rect)
