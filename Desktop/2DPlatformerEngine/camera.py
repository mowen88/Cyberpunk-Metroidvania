import pygame, csv

class Camera(pygame.sprite.Group):
	def __init__(self, game, room):
		super().__init__()
		self.game = game
		self.room = room
		self.surf = pygame.display.get_surface()
		self.zone_size = self.get_zone_size()

		self.offset = pygame.math.Vector2()

	def get_zone_size(self):
		with open(f'zones/{self.game.zone}/{self.game.zone}_blocks.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		size = (cols * self.game.TILESIZE, rows * self.game.TILESIZE)

		return size


	def screenshake(self):
		pass

	def blur(self):
		pass


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

	def offset_draw(self):
		self.keyboard_control()
		# self.bg_rect = self.bg_surf.get_rect(topleft = (0,0))
		# bg_offset_pos = self.bg_rect.topleft - (self.offset * 0.5)
		# self.display_surf.blit(self.bg_surf, bg_offset_pos)
		# self.bg_surf.set_alpha(255)
		self.surf.fill((self.game.CYAN))

		# self.offset[1] += (target[1] - self.offset[1] - self.display_surf.get_height() *0.5)/self.scroll_delay * (15/9)
		# self.offset[0] += (target[0] - self.offset[0] - self.display_surf.get_width() *0.5)/self.scroll_delay

		# keeps the camera within the outer bounds of the current room
		if self.offset[0] <= 0:
			self.offset[0] = 0
		elif self.offset[0] >= self.zone_size[0] - (self.game.WIDTH):
			self.offset[0] = self.zone_size[0] - (self.game.WIDTH)
		if self.offset[1] <= 0:
			self.offset[1] = 0
		elif self.offset[1] >= self.zone_size[1] - (self.game.HEIGHT):
			self.offset[1] = self.zone_size[1] - (self.game.HEIGHT)


		for sprite in self.sprites():
			offset = sprite.rect.topleft - self.offset
			self.surf.blit(sprite.image, offset)
