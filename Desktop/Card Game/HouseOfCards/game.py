
import os, time, pygame, csv, json
from os import walk
from csv import reader
from title import Title
from room import Room
from dialogue import Dialogue


class Game():
	def __init__(self):

		pygame.init()
		self.SCALE = 2.5
		self.TILESIZE = 16 * self.SCALE
		self.HEIGHT = 288 * self.SCALE
		self.WIDTH = self.HEIGHT/9*15
		self.FPS = 60
		self.BLACK = ((29, 17, 26))
		self.WHITE = ((255, 248, 232)) 
		self.BLUE = ((76, 76, 228))
		self.RED = ((255, 75, 75))
		self.clock = pygame.time.Clock()
		#self.monitor_info = pygame.display.Info()
		#self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN|pygame.SCALED)
		self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

		self.running, self.playing = True, True
		self.actions = {'F4': False, 'left': False, 'right': False, 'up': False, 'down': False, 'return': False, 'backspace': False,\
		 'space': False, 'x': False, 'z': False, 'c': False, 'm': False, 'escape': False} 
		
		with open('data_dicts/dialogue.txt') as f: self.dialog_dict = eval(f.read())

		self.cutscene_data = {0:(pygame.Rect(300, 400, 20, 100))}
		self.cutscenes_completed = []
		self.current_room = 'test'
		
		self.room_transition_speed = 20
		self.spawn_point = 0

		self.data = {'max_health': 5, 'coins': 0}

		self.start_health = 5
		if self.data['max_health']:
			self.max_health = self.data['max_health']
		else:   
			self.max_health = self.start_health

		self.current_health = self.max_health


		self.stack = []
		self.font = pygame.font.Font('font/MonoAManoRegular-45jx.ttf', 25)

		self.load_states()
		self.get_room_pos_and_sizes()

		#self.room = 0
		#self.current_room = self.room_dict[self.current_zone][self.room][1]
		#self.room_pos = selfcurrent_room.topleft
		#self.room_size = (self.current_room.right - self.current_room.left, self.current_room.bottom - self.current_room.top)


	def get_room_pos_and_sizes(self):

		self.room_dict = {
		'jail':{1: 'courtroom'},
		'courtroom':{1:'jail', 2:'hallway'},
		'hallway':{1:'pantry', 2:'courtroom', 3:'pantry'},
		'pantry':{1:'hallway', 2:'courtroom', 3: 'jail', 4: 'kitchen'},
		'kitchen':{1:'jail', 2:'courtroom', 4:'pantry'}
		}


	def get_room_number(self, val):
	    for key, value in self.room_dict.items():
	        if val == value:
	            return key
	    return "room doesn't exist"

	def game_loop(self):
		self.clock.tick(self.FPS)
		self.show_fps = str(int(self.clock.get_fps()))
		self.get_events()
		self.update()
		self.render()

	def get_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
				self.playing = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.actions['escape'] = True
					self.running = False
					self.playing = False
				elif event.key == pygame.K_F4:
					self.actions['F4'] = True
				elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
					self.actions['left'] = True
				elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					self.actions['right'] = True
				elif event.key == pygame.K_UP or event.key == pygame.K_w:
					self.actions['up'] = True
				elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
					self.actions['down'] = True
				elif event.key == pygame.K_RETURN:
					self.actions['return'] = True
				elif event.key == pygame.K_BACKSPACE:
					self.actions['backspace'] = True
				elif event.key == pygame.K_SPACE:
					self.actions['space'] = True
				elif event.key == pygame.K_x:
					self.actions['x'] = True
				elif event.key == pygame.K_z:
					self.actions['z'] = True
				elif event.key == pygame.K_c:
					self.actions['c'] = True
				elif event.key == pygame.K_m:
					self.actions['m'] = True

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					self.actions['left'] = False
				elif event.key == pygame.K_F4:
					self.actions['F4'] = False
				elif event.key == pygame.K_RIGHT:
					self.actions['right'] = False
				elif event.key == pygame.K_UP:
					self.actions['up'] = False
				elif event.key == pygame.K_DOWN:
					self.actions['down'] = False
				elif event.key == pygame.K_RETURN:
					self.actions['return'] = False
				elif event.key == pygame.K_BACKSPACE:
					self.actions['backspace'] = False
				elif event.key == pygame.K_SPACE:
					self.actions['space'] = False
				elif event.key == pygame.K_x:
					self.actions['x'] = False
				elif event.key == pygame.K_z:
					self.actions['z'] = False
				elif event.key == pygame.K_c:
					self.actions['c'] = False
				elif event.key == pygame.K_m:
					self.actions['m'] = False

	def update(self):
		self.stack[-1].update(self.actions)

	def render(self):
		self.stack[-1].render(self.screen)
		pygame.display.flip()

	def load_states(self):
		self.title_screen = Title(self)
		self.stack.append(self.title_screen)

	def draw_text(self, surf, text, colour, size, pos):
		text_surf = self.font.render(text, True, colour, size)
		text_rect = text_surf.get_rect(center = pos)
		surf.blit(text_surf, text_rect)

	def import_csv(self, path):
		room_map = []
		with open(path) as map:
			room = reader(map, delimiter=',')
			for row in room:
				room_map.append(list(row))

		return room_map

	def import_folder(self, path):
		surf_list = []

		for _, __, img_files in walk(path):
			for img in img_files:
				full_path = path + '/' + img
				img_surf = pygame.image.load(full_path).convert_alpha()
				img_surf = pygame.transform.scale(img_surf,(img_surf.get_width() * self.SCALE, img_surf.get_height() * self.SCALE))
				surf_list.append(img_surf)

		return surf_list

	def reset_keys(self):
		for key_pressed in self.actions:
			self.actions[key_pressed] = False
		
if __name__ == "__main__":
	g = Game()
	while g.running:
		g.game_loop()




