import pygame
from settings import *
from player import Player

class UI:
	def __init__(self, surf):

		self.display_surf = surf
		self.gun_list = []
		self.offset = 60

		self.neobit = pygame.image.load('img/pickups/neobits/ui_neobit_img.png').convert_alpha()
		self.neobit = pygame.transform.scale(self.neobit, (self.neobit.get_width() * SCALE, self.neobit.get_height() * SCALE))
		self.neobit_rect = self.neobit.get_rect(topleft = (24, 60))

		self.font = pygame.font.Font(UI_FONT, 24)

	def show_health(self, current, full):
		self.health_bar = pygame.Surface((current * SCALE, 24))
		self.health_bar.fill(GREEN)
		self.health_bar_border = pygame.Surface((full * SCALE + 6, self.health_bar.get_height() +6))

		self.display_surf.blit(self.health_bar_border,(24,24))
		self.display_surf.blit(self.health_bar,(27,27))
		
	def show_neobits(self, amount):
		self.display_surf.blit(self.neobit, self.neobit_rect)
		neobit_amount_surf = self.font.render(str(amount), True, 'WHITE')
		neobit_amount_rect = neobit_amount_surf.get_rect(midleft = (self.neobit_rect.right + 6, self.neobit_rect.centery))
		self.display_surf.blit(neobit_amount_surf, neobit_amount_rect)



	