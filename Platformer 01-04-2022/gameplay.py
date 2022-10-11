import pygame

from settings import *
from ui import UI
from level import Level

class GamePlay():
	def __init__(self, game):
		self.game = game
# constant player data
		self.save_point = load_data['save_point']
		self.max_health = 100
		self.current_health = 50
		self.current_weapon = None
		self.pickups_collected = None

		self.ui = UI(self.game.screen)
		self.level = Level(0, 0, (200, 400), 0, False, self.game.screen, self.create_level)

	def create_level(self, new_level, entry_pos, new_block_position, current_gun, gun_showing):
		self.level = Level(new_level, entry_pos, new_block_position, current_gun, gun_showing, self.game.screen, self.create_level)
		self.level.gun_equipped()

	def check_input(self):
		if self.game.actions['up']:
			self.game.level.player.jump()
		elif self.game.actions['space']:
			self.game.level.paused()
		elif self.game.actions['tab']:
			self.game.level.player.change_gun()
			self.game.level.show_new_gun()
		elif self.game.actions['z']:
			self.game.level.show_gun()
		self.level.run()
		self.game.ui.show_health(50, 100)
		self.game.ui.show_current_weapon(self.current_weapon)
		if self.game.level.game_paused and self.game.actions['escape']:
			self.game.playing = False
			self.level = Level(self.save_point, 0, self.level.block_position, 0, False, self.game.screen, self.create_level)