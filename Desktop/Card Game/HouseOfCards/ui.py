import pygame

class UI:
	def __init__(self, game):

		self.game = game
	
		self.health_icon_img = pygame.image.load('img/ui/health_icon.png').convert_alpha()
		self.health_bar_img = pygame.image.load('img/ui/health_bar.png').convert_alpha()
		self.coin_icon_img = pygame.image.load('img/ui/coin_icon.png').convert_alpha()
		self.health_icon_img = pygame.transform.scale(self.health_icon_img, (self.health_icon_img.get_width() * self.game.SCALE, self.health_icon_img.get_height() * self.game.SCALE))
		self.health_bar_img = pygame.transform.scale(self.health_bar_img, (self.health_bar_img.get_width() * self.game.SCALE, self.health_bar_img.get_height() * self.game.SCALE))
		self.coin_icon_img = pygame.transform.scale(self.coin_icon_img, (self.coin_icon_img.get_width() * self.game.SCALE, self.coin_icon_img.get_height() * self.game.SCALE))



		self.pos = (self.game.WIDTH * 0.02, self.game.HEIGHT * 0.02)
		self.offset = 50
		print(self.offset)

	def coin_display(self):
		self.coin_text_img = self.game.font.render(str(self.game.data['coins']), True, self.game.WHITE)
		self.game.screen.blit(self.coin_icon_img, (self.game.WIDTH - self.coin_icon_img.get_width(), self.game.HEIGHT - (self.coin_icon_img.get_height() * 2)))
		self.game.screen.blit(self.coin_text_img, (self.game.WIDTH - self.coin_icon_img.get_width() * 0.55, self.game.HEIGHT - (self.coin_icon_img.get_height() * 1.7)))

	def health_display(self):

		for box in range(self.game.max_health):
			box *= self.offset
			self.game.screen.blit(self.health_bar_img, ((box + self.offset, self.pos[1])))
		for box in range(self.game.current_health):
			box *= self.offset
			self.game.screen.blit(self.health_icon_img, ((box + self.offset, self.pos[1])))

		
	def render(self):
		self.health_display()
		self.coin_display()

