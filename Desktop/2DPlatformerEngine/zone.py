import pygame, os, csv
from state import State
from camera import Camera
from objects import Tile

class Zone(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.surf = pygame.display.get_surface()

		self.rendered_sprites = Camera(self.game, self)
		self.updated_sprite = pygame.sprite.Group()

		self.create_zone()

	def create_zone(self):
		layouts = {
		'blocks':self.game.import_csv(f'zones/{self.game.zone}/{self.game.zone}_blocks.csv')
		}

		images = {
		'blocks':self.game.import_folder(f'imgs/tiles/blocks')
		}

		for style, layout in layouts.items():
			for row_index, row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * self.game.TILESIZE
						y = row_index * self.game.TILESIZE

						if style == 'blocks':
							surf = images['blocks'][int(col)]
							Tile(self.game, (x,y), [self.rendered_sprites, self.updated_sprite], surf)

	def update(self, actions):
		self.updated_sprite.update()

	def render(self, display):
		self.rendered_sprites.offset_draw()
	
