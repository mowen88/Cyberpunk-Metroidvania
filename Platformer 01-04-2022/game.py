import pygame, sys, json
from pygame import mixer
from menu import *
from ui import UI
from settings import *
from level import Level

class Game():
	def __init__(self):
		pygame.init()

		#sound
		mixer.init()
		pygame.mixer.music.load('audio/Detox.mp3')
		pygame.mixer.music.set_volume(0.2)
		pygame.mixer.music.play(-1, 0.2, 5000)

		self.landing_fx = pygame.mixer.Sound('audio/sfx/landing_grunt.wav') 
		self.landing_fx.set_volume(0.2)
		self.melee_fx = pygame.mixer.Sound('audio/sfx/woosh.wav') 
		self.melee_fx.set_volume(0.2)
		self.save_fx = pygame.mixer.Sound('audio/sfx/save.wav') 
		self.save_fx.set_volume(0.2)
		self.blaster_fx = pygame.mixer.Sound('audio/sfx/blaster.wav')
		self.blaster_fx.set_volume(0.3)
		self.railgun_fx = pygame.mixer.Sound('audio/sfx/railgun.wav')
		self.railgun_fx.set_volume(0.3)
		self.collect_fx = pygame.mixer.Sound('audio/sfx/collect.wav')
		self.collect_fx.set_volume(0.3)
		self.neobit_fx = pygame.mixer.Sound('audio/sfx/neobit.wav')
		self.neobit_fx.set_volume(0.2)
		self.jetpack_fx = pygame.mixer.Sound('audio/sfx/engine.wav')
		self.jetpack_fx.set_volume(0.2)
		self.load_fx = pygame.mixer.Sound('audio/sfx/load.wav')
		self.load_fx.set_volume(0.3)
		self.unload_fx = pygame.mixer.Sound('audio/sfx/unload.wav')
		self.unload_fx.set_volume(0.3)
		self.double_jump_fx = pygame.mixer.Sound('audio/sfx/electroshot.wav')
		self.double_jump_fx.set_volume(0.5)


		with open('progress_data.txt') as progress_file:
			load_data = json.load(progress_file)

		with open('map_data.txt') as map_file:
			levels_visited = json.load(map_file)

		with open('neobit_data.txt') as neobit_file:
			neobit_data = json.load(neobit_file)

		with open('health_data.txt') as health_file:
			health_data = json.load(health_file)

		with open('extra_healths_data.txt') as extra_healths_file:
			extra_healths_collected = json.load(extra_healths_file)

		self.load_gun_data()
		self.load_pickup_data()
		self.load_map_data()
		self.load_extra_healths_data()

		self.running = True
		self.playing = False
		self.actions = {'left': False, 'right': False, 'up': False, 'down': False, 'return': False, 'back': False, 'm': False, \
		'space': False, 'tab': False, 'z': False, 'x': False, 'escape': False, 'l': False, 'd': False, 'i': False, 'y': False, 'n': False}

		self.display = pygame.Surface((WIDTH, HEIGHT))
		self.screen = pygame.display.set_mode(((WIDTH, HEIGHT)))

		self.font_name = 'font/failed attempt.ttf'
		self.BLACK = (0,0,0)
		self.WHITE = (255, 255, 255)

		self.clock = pygame.time.Clock()

		# states
		self.main_menu = MainMenu(self)
		self.options = OptionsMenu(self)
		self.quit = QuitMenu(self)
		self.reset = ResetMenu(self)
		self.level = Level(self, load_data['save_point'], 0, load_data['block_position'], 0, False, self.screen, self.create_level, self.update_neobits, self.update_health)	

		self.current_menu = self.main_menu

		# constant player data
		if neobit_data:
			self.neobits = neobit_data['neobits']
		else:
			self.neobits = 0

		self.start_health = 50
		if health_data:
			self.max_health = health_data['max_health']
		else:
			self.max_health = self.start_health

		self.current_health = self.max_health
		self.ui = UI(self.screen)
		
	
	def update_neobits(self, amount):
		self.neobits += amount

	def update_health(self, max_health_increment, current_health_increment):
		self.max_health += max_health_increment
		self.current_health += current_health_increment
			
	def create_level(self, new_level, entry_pos, new_block_position, current_gun, gun_showing):
		self.level = Level(self, new_level, entry_pos, new_block_position, current_gun, gun_showing, self.screen, self.create_level, self.update_neobits, self.update_health)
		self.level.gun_equipped()

	def game_loop(self):
		while self.playing:
			self.check_events()
			if self.level.player.alive and self.actions['up'] and not self.level.player.hold and not self.level.player.hovering and \
			not (self.level.player.on_elevator and self.level.player.vel.x == 0) and not (self.level.player.going_up or self.level.player.going_down):
				self.level.player.jump()
			elif self.actions['space'] and self.level.player.alive:
				self.level.show_map()
			elif self.actions['tab']:
				self.level.player.change_gun()
				self.level.show_new_gun()
			elif self.actions['z'] and not self.level.player.hold:
				self.level.show_gun()
			elif self.actions['d']:
				self.level.player.dash()
			elif self.actions['i']:
				self.level.show_inventory()
			if not self.level.player.alive:
				if self.actions['y']:
					self.level.load_point()
					self.neobits = 0
					# self.max_health = load_data['max_health']
					self.current_health = self.max_health
				elif self.actions['n']:
					self.playing = False
					self.level.load_point()

			self.level.run()
			self.ui.show_health(self.current_health, self.max_health)
			self.ui.show_neobits(self.neobits)

			if self.level.map_showing and self.actions['escape']:
				self.playing = False
				self.level.load_point()
	
			self.reset_keys()
			self.clock.tick(60)
			pygame.display.update()

	def check_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.level.load_point()
				self.quit_and_dump_data()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					self.actions['return'] = True
				if event.key == pygame.K_BACKSPACE:
					self.actions['back'] = True
				if event.key == pygame.K_UP:
					self.actions['up'] = True
				if event.key == pygame.K_DOWN:
					self.actions['down'] = True
				if event.key == pygame.K_SPACE:
					self.actions['space'] = True
				if event.key == pygame.K_TAB:
					self.actions['tab'] = True
				if event.key == pygame.K_m:
					self.actions['m'] = True
				if event.key == pygame.K_z:
					self.actions['z'] = True
				if event.key == pygame.K_x:
					self.actions['x'] = True
				if event.key == pygame.K_l:
					self.actions['l'] = True
				if event.key == pygame.K_d:
					self.actions['d'] = True
				if event.key == pygame.K_i:
					self.actions['i'] = True
				if event.key == pygame.K_y:
					self.actions['y'] = True
				if event.key == pygame.K_n:
					self.actions['n'] = True
				if event.key == pygame.K_ESCAPE:
					self.actions['escape'] = True

	def draw_text(self, text, size, pos):
		font = pygame.font.Font(self.font_name, size)
		text_surf = font.render(text, True, self.WHITE)
		text_rect = text_surf.get_rect(center = pos)
		self.display.blit(text_surf, text_rect)

	def reset_keys(self):
		for action in self.actions:
			self.actions[action] = False

	def load_gun_data(self):
		with open('gun_data.txt') as gun_file:
			saved_gun_data = json.load(gun_file)
			gun_data.clear()
			gun_data.update(saved_gun_data)

	def load_pickup_data(self):
		with open('pickup_data.txt') as pickup_file:
			saved_pickup_data = json.load(pickup_file)
			pickup_data.clear()
			pickup_data.update(saved_pickup_data)

	def load_map_data(self):
		with open('map_data.txt') as map_file:
			saved_levels_visited = json.load(map_file)
			levels_visited.clear()
			levels_visited.update(saved_levels_visited)

	def load_extra_healths_data(self):
		with open('extra_healths_data.txt') as extra_healths_file:
			saved_extra_healths_collected = json.load(extra_healths_file)
			extra_healths_collected.clear()
			extra_healths_collected.update(saved_extra_healths_collected)

	def quit_and_dump_data(self):
		with open('progress_data.txt', 'w') as progress_file:
			json.dump(load_data, progress_file)
		with open('map_data.txt', 'w') as map_file:
			json.dump(levels_visited, map_file)
		with open('extra_healths_data.txt', 'w') as extra_healths_file:
			json.dump(extra_healths_collected, extra_healths_file)	
		with open('pickup_data.txt', 'w') as pickup_file:
			json.dump(pickup_data, pickup_file)	
		with open('gun_data.txt', 'w') as gun_file:
			json.dump(gun_data, gun_file)
		with open('neobit_data.txt', 'w') as neobit_file:
			json.dump(neobit_data, neobit_file)	
		with open('health_data.txt', 'w') as health_file:
			json.dump(health_data, health_file)	
		
		self.running = False
		self.playing = False
		self.current_menu.run_display = False

if __name__ == "__main__":
	g = Game()
	while g.running:
		g.current_menu.display_menu()
		g.game_loop()





