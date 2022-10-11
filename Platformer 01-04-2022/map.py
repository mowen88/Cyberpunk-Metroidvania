import pygame

from settings import *

class Map():
	def __init__(self, game, current_level, level_length, level_height, surf):
		self.game = game
		self.gun_list = []
		self.pickup_list = []
		self.current_room = current_level
		self.display_surf = surf

		# list of room positions on map - index 0 in list is room rect, the following rects are the passageways from that room connecting
		self.room_w = 60
		self.room_h = 33
		self.passage_size = [12, 24]

		self.rooms = {
				'0': [(390,130,self.room_w*2,self.room_h), (390, 130,self.passage_size[1],self.passage_size[0])],
				'1': [(320,130,self.room_w,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'2': [(320,173,self.room_w*2,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'3': [(520,130,self.room_w,self.room_h*2 + 10),(390, 130,self.passage_size[0],self.passage_size[1])],
				'4': [(450,173,self.room_w,self.room_h*4 +(10*3)),(390, 130,self.passage_size[1],self.passage_size[0])],
				'5': [(390,345,self.room_w*2,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'6': [(520,345,self.room_w,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'7': [(520,260,self.room_w,self.room_h*2 +10),(390, 130,self.passage_size[1],self.passage_size[0])],
				'8': [(380,216,self.room_w,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'9': [(250,260,self.room_w*3 + 10,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'10': [(320,303,self.room_w,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'11': [(260,345,self.room_w*2,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'12': [(520,216,self.room_w*3 + 40,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'13': [(590,260,self.room_w + 10,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'14': [(670,260,self.room_w + 10,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])],
				'15': [(250,173,self.room_w,self.room_h*2),(390, 130,self.passage_size[1],self.passage_size[0])],
				'16': [(250,130,self.room_w,self.room_h),(390, 130,self.passage_size[1],self.passage_size[0])]
				}

		
		self.marker_pos = list(self.rooms.values())[self.current_room][0]

		# player marker
		self.marker_surf = pygame.image.load('img/ui/marker.png').convert_alpha()
		self.rect = pygame.Rect((self.marker_pos))
		self.marker_rect = self.marker_surf.get_rect(center = (self.rect.center))
		self.icon_rect = self.marker_surf.get_rect(center = (WIDTH //2 - 120, HEIGHT - 192))

		self.font = pygame.font.Font(FONT, 40)
		self.small_font = pygame.font.Font(UI_FONT, 20)

		self.text_surf = self.font.render('Paused', True, 'WHITE')
		self.text_rect = self.text_surf.get_rect(center = (WIDTH //2, HEIGHT // 2 - 168))
		
		self.inventory_text_surf = self.small_font.render('Inventory', True, 'WHITE')
		self.inventory_text_rect = self.inventory_text_surf.get_rect(center = (166, HEIGHT - 168))

		self.position_text_surf = self.small_font.render('You are here:', True, 'WHITE')
		self.position_text_rect = self.position_text_surf.get_rect(center = (176, 120))

		self.exit_text_surf = self.small_font.render('Press ESC for main menu', True, 'WHITE')
		self.exit_text_rect = self.exit_text_surf.get_rect(center = (WIDTH // 2 + 249, 90))

		self.backdrop_surf = pygame.Surface((WIDTH - 204, HEIGHT -128))
		self.backdrop_rect = self.backdrop_surf.get_rect(center = (WIDTH // 2, HEIGHT //2))

		# border
		self.backdrop_border_surf = pygame.Surface(((self.backdrop_surf.get_width() - 12), (self.backdrop_surf.get_height()) - 12))
		self.backdrop_border_rect = self.backdrop_border_surf.get_rect(center = (WIDTH // 2, HEIGHT //2))

		self.slot_size = 60
		self.slot_number = 8
		self.offset = self.backdrop_border_surf.get_width() // self.slot_number


	def show_rooms(self):
		for rect in range(len(list(self.rooms.values())[0])):
			for num in list(self.rooms.keys()):
				#for rect in (len(list(self.rooms.values())[0])):
				if num in list(levels_visited.keys()) and 'tracker' in list(pickup_data.keys()):
					if pickup_data['tracker'] == True:
						pygame.draw.rect(self.display_surf, PURPLE, self.rooms[num][rect])
					
				else:
					pygame.draw.rect(self.display_surf, PURPLE, self.rooms[str(self.current_room)][rect])
					

	def slots(self):
		for slot in range(self.slot_number):
			slot *= self.offset
			pygame.draw.rect(self.display_surf, GREY, (slot + 126, HEIGHT - 149, self.slot_size,self.slot_size))	

	def show_guns(self):
		for num in list(gun_data.keys()):
			if num in gun_data.keys():
				path = gun_data[num]['gun_img']
				self.gun_list.append(path)
				self.image = pygame.image.load(path).convert_alpha()
				self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE, self.image.get_height() * SCALE))
				if num == '0':
					self.rect = self.image.get_rect(center = (156, HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)
				elif num =='1':
					self.rect = self.image.get_rect(center = (156 + (self.offset), HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)
				elif num == '2':
					self.rect = self.image.get_rect(center = (156 + (self.offset * 2), HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)

	def show_pickups(self):
		for num in list(pickup_data.keys()):
			if num in pickup_data.keys():
				path = f'img/pickups/ui_icons/{num}.png'
				self.pickup_list.append(path)
				self.image = pygame.image.load(path).convert_alpha()
				self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE, self.image.get_height() * SCALE))
				if num == 'double_jump':
					self.rect = self.image.get_rect(center = (156 + (self.offset * 3), HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)
				elif num =='hovering':
					self.rect = self.image.get_rect(center = (156 + (self.offset * 4), HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)
				elif num == 'wall_jump':
					self.rect = self.image.get_rect(center = (156 + (self.offset * 5), HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)
				elif num == 'dash':
					self.rect = self.image.get_rect(center = (156 + (self.offset * 6), HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)
				elif num == 'can_swim':
					self.rect = self.image.get_rect(center = (156 + (self.offset * 7), HEIGHT - 149 + ( self.slot_size // 2)))
					self.display_surf.blit(self.image, self.rect)


	def run(self):
		self.display_surf.blit(self.backdrop_surf, self.backdrop_rect)	
		pygame.draw.rect(self.display_surf, NEON_BLUE, (self.backdrop_border_rect), 3)	
		self.show_rooms()
		self.display_surf.blit(self.marker_surf, self.marker_rect)
		self.display_surf.blit(self.text_surf, self.text_rect)
		self.display_surf.blit(self.exit_text_surf, self.exit_text_rect)
		self.display_surf.blit(self.inventory_text_surf, self.inventory_text_rect)
		self.display_surf.blit(self.position_text_surf, self.position_text_rect)
		# self.display_surf.blit(self.marker_surf, self.icon_rect)
		self.slots()
		self.show_guns()
		self.show_pickups()

	




		





	