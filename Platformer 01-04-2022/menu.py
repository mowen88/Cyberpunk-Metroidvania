import pygame, json

from ui import UI
from level import Level
from settings import *

class Menu():
	def __init__(self, game):
		self.game = game
		self.center_x = WIDTH //2
		self.center_y = HEIGHT // 2
		self.run_display = True
		self.cursor_rect = pygame.Rect(0,0, 30, 30)
		self.offset = - 120

	def draw_cursor(self):
		self.image = pygame.image.load('img/ui/cursor.png').convert_alpha()
		self.rect = self.image.get_rect(center = (self.cursor_rect.x, self.cursor_rect.y))
		self.game.display.blit(self.image, self.rect)
		

	def blit_screen(self):
		self.game.screen.blit(self.game.display, (0, 0))
		pygame.display.update()
		self.game.reset_keys()

class MainMenu(Menu):
	def __init__(self, game):
		Menu.__init__(self, game)
		self.state = "Continue"

		self.continue_x = self.center_x
		self.continue_y = self.center_y + 30

		self.reset_x = self.center_x
		self.reset_y = self.center_y + 60

		self.options_x = self.center_x
		self.options_y = self.center_y + 90

		self.quit_x = self.center_x
		self.quit_y = self.center_y + 120

		self.cursor_rect.midtop = (self.continue_x + self.offset, self.continue_y)

	def display_menu(self):
		self.run_display = True
		while self.run_display:
			self.game.check_events()
			self.check_input()
			self.game.display.fill(self.game.BLACK)
			self.game.draw_text('Main Menu', 50, (WIDTH // 2, HEIGHT // 2 - 30))
			self.game.draw_text('Continue', 30, (self.continue_x, self.continue_y))
			self.game.draw_text('Reset', 30, (self.reset_x, self.reset_y))
			self.game.draw_text('Options', 30, (self.options_x, self.options_y))
			self.game.draw_text('Quit', 30, (self.quit_x, self.quit_y))
			self.draw_cursor()
			self.blit_screen()

	def move_cursor(self):
		if self.game.actions['down']:
			if self.state == 'Continue':
				self.cursor_rect.midtop = (self.reset_x + self.offset, self.reset_y)
				self.state = 'Reset'
			elif self.state == 'Reset':
				self.cursor_rect.midtop = (self.options_x + self.offset, self.options_y)
				self.state = 'Options'
			elif self.state == 'Options':
				self.cursor_rect.midtop = (self.quit_x + self.offset, self.quit_y)
				self.state = 'Quit'
			elif self.state == 'Quit':
				self.cursor_rect.midtop = (self.continue_x + self.offset, self.continue_y)
				self.state = 'Continue'

		if self.game.actions['up']:
			if self.state == 'Continue':
				self.cursor_rect.midtop = (self.quit_x + self.offset, self.quit_y)
				self.state = 'Quit'
			elif self.state == 'Quit':
				self.cursor_rect.midtop = (self.options_x + self.offset, self.options_y)
				self.state = 'Options'
			elif self.state == 'Options':
				self.cursor_rect.midtop = (self.reset_x + self.offset, self.reset_y)
				self.state = 'Reset'
			elif self.state == 'Reset':
				self.cursor_rect.midtop = (self.continue_x + self.offset, self.continue_y)
				self.state = 'Continue'

	def check_input(self):
		self.move_cursor()
		if self.game.actions['return']:
			if self.state == 'Continue':
				self.game.playing = True
			elif self.state == 'Reset':
				self.game.current_menu = self.game.reset
				# self.game.current_menu = self.game.reset
			elif self.state == 'Options':
				self.game.current_menu = self.game.options
			elif self.state == 'Quit':
				self.game.current_menu = self.game.quit
			self.run_display = False

class ResetMenu(Menu):
	def __init__(self, game):
		Menu.__init__(self, game)
		self.state = 'ok'
		self.ok_x = self.center_x
		self.ok_y = self.center_y + 30
		self.cancel_x = self.center_x
		self.cancel_y = self.center_y + 60
		self.cursor_rect.midtop = (self.ok_x + self.offset, self.ok_y)

	def display_menu(self):
		self.run_display = True
		while self.run_display:
			self.game.check_events()
			self.check_input()
			self.game.display.fill(self.game.BLACK)
			self.game.draw_text('Reset all data and start new game?', 50, (WIDTH // 2, HEIGHT // 2 - 30))
			self.game.draw_text('OK', 30, (self.ok_x, self.ok_y))
			self.game.draw_text('Cancel', 30, (self.cancel_x, self.cancel_y))
			self.draw_cursor()
			self.blit_screen()

	def check_input(self):
		if self.game.actions['back']:
			self.game.current_menu = self.game.main_menu
			self.run_display = False

		elif self.game.actions['up'] or self.game.actions['down']:
			if self.state == 'ok':
				self.state = 'cancel'
				self.cursor_rect.midtop = (self.cancel_x + self.offset, self.cancel_y)
			elif self.state == 'cancel':
				self.state = 'ok'
				self.cursor_rect.midtop = (self.ok_x + self.offset, self.ok_y)

		elif self.game.actions['return']:
			if self.state == 'ok':
				self.game.neobits = 0
				self.game.max_health = self.game.start_health
				self.game.current_health = self.game.max_health
				gun_data.clear()
				saved_gun_data.clear()
				pickup_data.clear()
				saved_pickup_data.clear()
				levels_visited.clear()
				saved_levels_visited.clear()
				extra_healths_collected.clear()
				saved_extra_healths_collected.clear()
				extra_healths_collected.update({})
				load_data.update({'save_point': 0, 'gun_showing': False, 'current_gun': 0})
				pickup_data.update({'double_jump': False, 'wall_jump': False, 'dash': False, 'hovering': False, 'can_swim': False, 'tracker': False})
				neobit_data.update({'neobits': 0})
				health_data.update({'max_health': self.game.max_health})
				with open('progress_data.txt', 'w') as progress_file:
					json.dump(load_data, progress_file)
				self.game.level.load_point()

				self.game.current_menu = self.game.main_menu
				self.run_display = False
			elif self.state == 'cancel':
				self.game.current_menu = self.game.main_menu
				self.run_display = False


class OptionsMenu(Menu):
	def __init__(self, game):
		Menu.__init__(self, game)
		self.state = 'Volume'
		self.vol_x = self.center_x
		self.vol_y = self.center_y + 30
		self.controls_x = self.center_x
		self.controls_y = self.center_y + 60
		self.cursor_rect.midtop = (self.vol_x + self.offset, self.vol_y)

	def display_menu(self):
		self.run_display = True
		while self.run_display:
			self.game.check_events()
			self.check_input()
			self.game.display.fill(self.game.BLACK)
			self.game.draw_text('Options', 50, (WIDTH // 2, HEIGHT // 2 - 30))
			self.game.draw_text('Volume', 30, (self.vol_x, self.vol_y))
			self.game.draw_text('Controls', 30, (self.controls_x, self.controls_y))
			self.draw_cursor()
			self.blit_screen()

	def check_input(self):
		if self.game.actions['back']:
			self.game.current_menu = self.game.main_menu
			self.run_display = False

		elif self.game.actions['up'] or self.game.actions['down']:
			if self.state == 'Volume':
				self.state = 'Controls'
				self.cursor_rect.midtop = (self.controls_x + self.offset, self.controls_y)
			elif self.state == 'Controls':
				self.state = 'Volume'
				self.cursor_rect.midtop = (self.vol_x + self.offset, self.vol_y)

		elif self.game.actions['return']:
			# create controls and volume menus
			pass

class QuitMenu(Menu):
	def __init__(self, game):
		Menu.__init__(self, game)
		Menu.__init__(self, game)
		self.state = 'ok'
		self.ok_x = self.center_x
		self.ok_y = self.center_y + 30
		self.cancel_x = self.center_x
		self.cancel_y = self.center_y + 60
		self.cursor_rect.midtop = (self.ok_x + self.offset, self.ok_y)

	def display_menu(self):
		self.run_display = True
		while self.run_display:
			self.game.check_events()
			self.check_input()
			self.game.display.fill(self.game.BLACK)
			self.game.draw_text('Quit game?', 50, (WIDTH // 2, HEIGHT // 2 - 30))
			self.game.draw_text('OK', 30, (self.ok_x, self.ok_y))
			self.game.draw_text('Cancel', 30, (self.cancel_x, self.cancel_y))
			self.draw_cursor()
			self.blit_screen()

	def check_input(self):
		if self.game.actions['back']:
			self.game.current_menu = self.game.main_menu
			self.run_display = False

		elif self.game.actions['up'] or self.game.actions['down']:
			if self.state == 'ok':
				self.state = 'cancel'
				self.cursor_rect.midtop = (self.cancel_x + self.offset, self.cancel_y)
			elif self.state == 'cancel':
				self.state = 'ok'
				self.cursor_rect.midtop = (self.ok_x + self.offset, self.ok_y)

		elif self.game.actions['return']:
			if self.state == 'ok':
				self.game.quit_and_dump_data()
			elif self.state == 'cancel':
				self.game.current_menu = self.game.main_menu
				self.run_display = False

class PauseMenu(Menu):
	def __init__(self, game):
		Menu.__init__(self, game)
		self.state = 'Resume'
		self.resume_x = self.center_x
		self.resume_y = self.center_y + 30
		self.quit_x = self.center_x
		self.quit_y = self.center_y + 60
		self.cursor_rect.midtop = (self.resume_x + self.offset, self.resume_y)

	def display_menu(self):
		self.run_display = True
		while self.run_display:
			self.game.check_events()
			self.check_input()
			self.game.display.fill(self.game.BLACK)
			self.game.draw_text('Paused', 50, (WIDTH // 2, HEIGHT // 2 - 30))
			self.game.draw_text('Resume', 30, (self.resume_x, self.resume_y))
			self.game.draw_text('Quit', 30, (self.quit_x, self.quit_y))
			self.draw_cursor()
			self.blit_screen()

	def check_input(self):
		if self.game.BACK:
			self.run_display = False

		elif self.game.UP or self.game.DOWN:
			if self.state == 'Resume':
				self.state = 'Quit'
				self.cursor_rect.midtop = (self.quit_x + self.offset, self.quit_y)
			elif self.state == 'Quit':
				self.state = 'Resume'
				self.cursor_rect.midtop = (self.resume_x + self.offset, self.resume_y)

		elif self.game.GO:
			if self.state == 'Resume':
				self.run_display = False
			elif self.state == 'Quit':
				self.game.running = False
				self.game.current_menu = self.game.main_menu


			# create controls and volume menus
			pass













