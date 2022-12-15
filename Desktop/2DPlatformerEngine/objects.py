import pygame

class Tile(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)