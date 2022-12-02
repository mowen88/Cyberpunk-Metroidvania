import pygame, csv


class Camera(pygame.sprite.Group):
	def __init__(self, game, room):
		super().__init__()
		self.game = game
		self.room = room
		self.display_surf = pygame.display.get_surface()

		self.offset = pygame.math.Vector2()

		self.scroll_delay = 16
		self.screen_transition_speed = 16 # ensure this is equal to or less than scroll delay above
		self.scroll_speed = 16

		self.transition = False
		
	
		# #get size (length and width) of room in pixels fpr bg surf
		with open(f'rooms/{self.game.current_room}/{self.game.current_room}_blocks.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		self.room_size = (cols * self.game.TILESIZE, rows * self.game.TILESIZE)


	def keyboard_control(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_a]:
			self.offset[0] -= 4
		if keys[pygame.K_d]:
			self.offset[0] += 4
		if keys[pygame.K_w]:
			self.offset[1] -= 4
		if keys[pygame.K_s]:
			self.offset[1] += 4

	def screenshake(self):
		pass

	def blur(self):
		pass

	def offset_draw(self, target):
		# self.bg_rect = self.bg_surf.get_rect(topleft = (0,0))
		# bg_offset_pos = self.bg_rect.topleft - (self.offset * 0.5)
		# self.display_surf.blit(self.bg_surf, bg_offset_pos)
		self.display_surf.fill((self.game.WHITE))

		#if not self.room.cutscene_running:
		if self.room.target.facing == 1:
			self.offset[0] += (target[0] - self.offset[0] - self.display_surf.get_width() *0.4)/self.scroll_delay
		else:
			self.offset[0] += (target[0] - self.offset[0] - self.display_surf.get_width() *0.6)/self.scroll_delay
		self.offset[1] += (target[1] - self.offset[1] - self.display_surf.get_height() *0.5)/self.scroll_delay * (15/9)

		# keeps the camera within the outer bounds of the current room
		if self.offset[0] <= 0:
			self.offset[0] = 0
		elif self.offset[0] >= self.room_size[0] - (self.game.WIDTH):
			self.offset[0] = self.room_size[0] - (self.game.WIDTH)
		if self.offset[1] <= 0:
			self.offset[1] = 0
		elif self.offset[1] >= self.room_size[1] - (self.game.HEIGHT):
			self.offset[1] = self.room_size[1] - (self.game.HEIGHT)

		# if self.offset[0] <= room_pos[0]:
		# 	self.offset[0] += (self.display_surf.get_width()/self.screen_transition_speed)
		# 	if self.offset[0] >= room_pos[0]:
		# 		self.offset[0] = room_pos[0]

		# elif self.offset[0] >= room_size[0] - self.display_surf.get_width():
		# 	self.offset[0] -= (self.display_surf.get_width()/self.screen_transition_speed)
		# 	if self.offset[0] <= room_size[0] - self.display_surf.get_width():
		# 		self.offset[0] = room_size[0] - self.display_surf.get_width()

		# if self.offset[1] <= room_pos[1]:
		# 	self.offset[1] += self.display_surf.get_height()/self.screen_transition_speed
		# 	if self.offset[1] >= room_pos[1]:
		# 		self.offset[1] = room_pos[1]

		# elif self.offset[1] >= room_size[1] - self.display_surf.get_height():
		# 	self.offset[1] -= self.display_surf.get_height()/self.screen_transition_speed
		# 	if self.offset[1] <= room_size[1] - self.display_surf.get_height():
		# 		self.offset[1] = room_size[1] - self.display_surf.get_height()
	
	# else:
	# 	self.keyboard_control()

		# seperate blits to layer target on top of other sprites

		for sprite in self.sprites():
			offset = sprite.rect.topleft - self.offset
			self.display_surf.blit(sprite.image, offset)
			






		
