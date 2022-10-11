import pygame
from settings import *
from support import import_folder
from entities import Entity

class GunUpgrade(Entity):
	def __init__(self, pos, groups, gun_upgrade_sprites, player):
		super().__init__(groups)

		self.import_assets('weapons')
		self.facing = 1
		self.state = 'gun'
		self.frame_index = 0
		self.frame_rate = 0.2

		self.image = self.animations['gun'][self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-20, -20)

		self.gun_upgrade_sprites = gun_upgrade_sprites
		self.player = player

	def import_assets(self, name):
		char_path = f'img/{name}/'
		self.animations = {'gun': []}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = import_folder(full_path)

	def if_collected(self):
		for sprite in self.gun_upgrade_sprites:
			if sprite.rect.colliderect(self.player.rect):
				print(list(gun_data.keys())[self.player.gun_index])

	def update(self):
		self.animate('loop')
		self.if_collected()


		