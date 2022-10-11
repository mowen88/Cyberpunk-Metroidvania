import pygame
from settings import *

class LayerCameraGroup(pygame.sprite.Group):
	def __init__(self, game, bg, level_length, level_height):
		super().__init__()
		self.game = game
		self.display_surf = pygame.display.get_surface()
		self.offset = pygame.math.Vector2(100,150)
		self.level_length = level_length
		self.level_height = level_height

		# upload bg image
		self.bg = bg
		self.bg_surf = pygame.image.load(f'levels/bg/{self.bg}.png').convert_alpha()
		self.bg_surf = pygame.transform.scale(self.bg_surf, (self.level_length, self.level_height))

		# centre the camera
		self.half_width = self.display_surf.get_width() // 2
		self.half_height = self.display_surf.get_height() // 2

		# camera
		left = CAMERA_BORDERS['left']
		top = CAMERA_BORDERS['top']
		width = self.display_surf.get_width() - (CAMERA_BORDERS['left'] * 2)
		height = self.display_surf.get_height() - (CAMERA_BORDERS['top'] * 2)

		self.camera_rect = pygame.Rect(left, top, width, height)

	def offset_draw(self, player):
		
		#below is to create a camera box around the player to move the oll instead of the player moving the scroll if wanted
		# # get cam position
		if player.rect.left < self.camera_rect.left:
			self.camera_rect.left = player.rect.left
		if player.rect.right > self.camera_rect.right:
			self.camera_rect.right = player.rect.right
		if player.rect.bottom + 21 < self.camera_rect.top:
			self.camera_rect.top = player.rect.bottom + 21
		if player.rect.bottom > self.camera_rect.bottom:
			self.camera_rect.bottom = player.rect.bottom
		# cam offset
		self.offset = pygame.math.Vector2(self.camera_rect.left - CAMERA_BORDERS['left'], self.camera_rect.top - CAMERA_BORDERS['top'])

		if self.offset[0] <= 0:
			self.offset[0] = 0
		elif self.offset[0] >= self.level_length - WIDTH:
			self.offset[0] = self.level_length - WIDTH

		if self.offset[1] <= 0:
			self.offset[1] = 0
		elif self.offset[1] >= self.level_height - HEIGHT:
			self.offset[1] = self.level_height - HEIGHT


		# seperate blits to layer player on top of other sprites
		self.bg_rect = self.bg_surf.get_rect(topleft = (0, 0))
		bg_offset_pos = self.bg_rect.topleft - self.offset
		self.display_surf.blit(self.bg_surf, bg_offset_pos)

		for sprite in self.game.level.second_layer_sprites:
			offset = sprite.rect.topleft - self.offset
			self.display_surf.blit(sprite.image, offset)

		for sprite in self.sprites():
			if sprite not in self.game.level.second_layer_sprites:
				offset = sprite.rect.topleft - self.offset
				self.display_surf.blit(sprite.image, offset)

		



		

		

		


			
			