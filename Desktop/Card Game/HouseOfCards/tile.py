import pygame, random

class Tile(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf = pygame.Surface((48, 48))):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)

class LeverRocker(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = pygame.image.load(surf).convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)

class CollisionTile(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf = pygame.Surface((48, 48))):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)

class Exit(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf, number):
		super().__init__(groups)
		self.game = game
		self.number = number
		self.image = pygame.image.load(surf).convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-40, -40)

class Spike(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf = pygame.Surface((48, 48))):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-5, -5)

class Lever(pygame.sprite.Sprite):
	def __init__(self, game, room, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.room = room
		self.image_type = pygame.image.load(surf).convert_alpha()
		self.image = pygame.image.load(surf).convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)

		self.rotate = 0
		self.on = False
		self.can_collide = True

	def rotate_sprite(self):
		if self.room.lever_on:
			self.rotate += 2
			if self.rotate >= 18:
				self.rotate = 18
		elif not self.room.lever_on:
			if self.rotate != 0:
				self.rotate -= 2
				if self.rotate <= 0:
					self.rotate = 0
		
		self.image = pygame.transform.rotate(self.image_type, self.rotate)
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(center = self.rect.center)
		self.hitbox.center = self.rect.center

	def update(self):
		if self.hitbox.colliderect(self.room.yoyo_sprite):
			if self.can_collide:
				self.room.lever_on = not self.room.lever_on
				self.can_collide = False
		else:
			self.can_collide = True

		self.rotate_sprite()
		self.rect.center = self.hitbox.center
		
class Attack(pygame.sprite.Sprite):
	def __init__(self, game, room, sprite, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.room = room
		self.sprite = sprite
		self.image_type = pygame.image.load(surf).convert_alpha()
		self.image = pygame.image.load(surf).convert_alpha()
		self.rotate = 180
		self.vel = pygame.math.Vector2()
		

		if self.sprite.facing == 1:
			self.rect = self.image.get_rect(midleft = (self.sprite.hitbox.midright[0] + 5, self.sprite.hitbox.midright[1]))
		else:
			self.rect = self.image.get_rect(midright = (self.sprite.hitbox.midleft[0] - 5, self.sprite.hitbox.midleft[1]))
		self.hitbox = self.rect.inflate(0, 0)


	def rotate_sprite(self):
		self.rotate += 15
		if self.rotate <= 90:
			self.rotate = 90
		self.image = pygame.transform.rotate(self.image_type, self.rotate)
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(center = self.rect.center)
		self.vel = pygame.math.Vector2()
		self.hitbox.center = self.rect.center


	def update(self):
		self.rect = self.hitbox
		
		if self.sprite.facing == 1:
			self.rect = self.image.get_rect(midleft = (self.sprite.hitbox.midright[0] + 5, self.sprite.hitbox.midright[1]))

		else:
			self.rect = self.image.get_rect(midright = (self.sprite.hitbox.midleft[0] - 5, self.sprite.hitbox.midleft[1]))

		self.rotate_sprite()

		if self.sprite.frame_index >= len(self.sprite.animations[self.sprite.state]) -1 or self.sprite.dashing:
			self.sprite.attacking = False
			self.sprite.can_attack = True
			self.kill()

class Yoyo(pygame.sprite.Sprite):
	def __init__(self, game, room, sprite, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.room = room
		self.sprite = sprite
		self.image_type = pygame.image.load(surf).convert_alpha()
		self.image = pygame.image.load(surf).convert_alpha()
		self.rotate = 0

		self.speed = 15
		self.acceleration = self.speed/7.5
		self.vel = pygame.math.Vector2()
		self.state = 'throwing'

		if self.sprite.facing == 1:
			self.rect = self.image.get_rect(midleft = self.sprite.hitbox.midright)
			self.vel.x = self.speed
			
		else:
			self.rect = self.image.get_rect(midright = self.sprite.hitbox.midleft)
			self.vel.x = -self.speed
	
		self.hitbox = self.rect.inflate(-10, -10)

		self.start_pos = self.room.player.get_distance_direction_and_angle(self.sprite)[0]
		self.start_pos += self.sprite.hitbox.x

	def collide_blocks(self):
		for sprite in self.room.obstacle_sprites:
			if sprite.hitbox.colliderect(self):
				self.state = 'returning'

	def rotate_sprite(self):
		self.rotate += 10
		self.image = pygame.transform.rotate(self.image_type, self.rotate)
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(center = self.rect.center)
		self.hitbox.center = self.rect.center
				
	def update(self):
		self.collide_blocks()
		if not self.sprite.can_yoyo:
			if self.hitbox.x > self.start_pos + (self.speed * 20):
				self.vel.x -= self.acceleration
				if self.vel.x <= 0:
					self.state = 'returning'

			elif self.hitbox.x < self.start_pos - (self.speed * 20):
				self.vel.x += self.acceleration
				if self.vel.x >= 0:
					self.state = 'returning'

			if self.state == 'returning':
				self.vel = -self.room.player.get_distance_direction_and_angle(self)[1] * self.acceleration
				self.acceleration += 1 
				if self.hitbox.colliderect(self.sprite):
					self.kill()
					self.sprite.can_yoyo = True
					self.sprite.yoyoing = False
					self.sprite.send_yoyo = False

		self.hitbox.x += self.vel.x
		self.hitbox.y += self.vel.y
		self.rect = self.hitbox
	
		self.rotate_sprite()

		if self.sprite.frame_index >= (len(self.sprite.animations[self.sprite.state]) -1):
			self.sprite.send_yoyo = False

class CutsceneCollider(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, number):
		super().__init__(groups)
		self.game = game
		self.image = pygame.image.load(f'img/tiles/cutscene_colliders/{number}.png')
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.number = number
		self.rect = self.image.get_rect(topleft = (pos[0], pos[1] -self.image.get_height()))

class AnimatedTile(pygame.sprite.Sprite):
	def __init__(self, game, room, pos, groups, path):
		super().__init__(groups)

		#self.sprite_type = sprite_type
		self.game = game
		self.room = room
		self.frames = self.game.import_folder(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = pos)

	def animate(self):
		self.frame_index += 0.15
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.animate()

class Particle(AnimatedTile):
	def __init__(self, game, room, pos, groups, path):
		super().__init__(game, room, pos, groups, path)

	def animate(self):
		self.frame_index += 0.2
		if self.frame_index >= len(self.frames) -1:
			self.kill()
		self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.animate()


class Coin(AnimatedTile):
	def __init__(self, game, room, pos, groups, path):
		super().__init__(game, room, pos, groups, path)

		self.vel = pygame.math.Vector2()
		self.vel.x = random.uniform(-2,2)
		self.bounce_height = random.uniform(-10,-6)
		self.state = 'bouncing'
		self.acceleration = 0

		self.bounce()
		

	def collide_obstacles(self):
		for sprite in self.room.obstacle_sprites:
			if self.state == 'bouncing':
				if sprite.rect.colliderect(self.rect):
					if self.rect.bottom > sprite.rect.top:
						self.rect.bottom = sprite.rect.top
						self.bounce()

	def bounce(self):
		self.vel.y = self.bounce_height
		self.bounce_height += 2

	def apply_gravity(self):
		self.vel.y += 0.5
		if self.vel.y > 12:
			self.vel.y = 12

	def zoom_to_player(self):
		position = self.room.player.get_distance_direction_and_angle(self)[1]
		distance = self.room.player.get_distance_direction_and_angle(self)[0]
		if self.bounce_height >= 0 and self.room.target.alive:
			self.state = 'go_to_player'
			self.acceleration += 0.5
			self.vel = -position * self.acceleration
			
	def update_player_coins(self):
		if self.rect.colliderect(self.room.player.hitbox):
			if self.state == 'go_to_player':
				Particle(self.game, self.room, self.room.player.hitbox.center, [self.room.visible_sprites, self.room.active_sprites], 'img/particles/coin_collect/')
				self.kill()
				self.game.data['coins'] += 1
				print(self.game.data['coins'])

	def update(self):
		self.animate()
		self.update_player_coins()
		self.collide_obstacles()
		self.zoom_to_player()
		self.rect.x += self.vel.x
		self.apply_gravity()
		self.rect.y += self.vel.y

class Platform(pygame.sprite.Sprite):
	def __init__(self, game, room, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.room = room
		self.image = pygame.image.load(surf).convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)

	def collide_platforms(self):
		#collided = pygame.sprite.spritecollide(self.room.target, self.room.trick_platform_sprites, False)
		if self.hitbox.colliderect(self.room.target.hitbox): 
			if self.room.target.hitbox.bottom <= self.hitbox.top + 16 and self.room.target.vel.y >= 0:
					self.on_platform = True
					self.room.target.cyote_timer = 0
					self.room.target.vel.y = 0
					self.room.target.hitbox.bottom = self.hitbox.top +1
					self.room.target.on_ground = True
					self.room.target.on_wall = False

	def update(self):
		self.collide_platforms()

class MovingPlatform(pygame.sprite.Sprite):
	def __init__(self, game, room, pos, groups, surf, platform_type):
		super().__init__(groups)
		self.game = game
		self.room = room
		self.platform_type = platform_type
		
		self.image = pygame.image.load(surf).convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))

		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,0)
		self.timer = 0

		self.vel = pygame.math.Vector2()

	def horizontal(self):
		if self.timer < 300:
			self.vel = pygame.math.Vector2(-1,0)
			
		elif self.timer <= 600:
			self.vel = pygame.math.Vector2(1,0)
			
		else:
			self.timer = 0

	def vertical(self):
		if self.timer <= 300:
			self.vel = pygame.math.Vector2(0, 1)

		elif self.timer <= 600:
			self.vel = pygame.math.Vector2(0, -1)
		else:
			self.timer = 0

	def move(self):
		self.timer += 1
		if self.platform_type == 'down_up':
			self.vertical()
		elif self.platform_type == 'up_down':
			self.vertical()
			self.vel *= -1
		elif self.platform_type == 'left_right':
			self.horizontal()
		elif self.platform_type == 'right_left':
			self.horizontal()
			self.vel *= -1
			

			# if self.timer <= 300:
			# 	self.vel = pygame.math.Vector2(1, 0)

			# elif self.timer >300 and self.timer <=600:
			# 	self.vel = pygame.math.Vector2(0, 1)
		
			# elif self.timer >600 and self.timer <= 900:
			# 	self.vel = pygame.math.Vector2(-1, 0)

			# elif self.timer > 900 and self.timer <= 1200:
			# 	self.vel = pygame.math.Vector2(0, -1)

	

		self.hitbox.x += self.vel.x
		self.hitbox.y += self.vel.y
		self.rect.center = self.hitbox.center

	def update(self):
		self.move()
		
class TrickPlatform(AnimatedTile):
	def __init__(self, game, room, pos, groups, path):
		super().__init__(game, room, pos, groups, path)
		self.game = game
		self.room = room
		self.frames = self.game.import_folder(path)
		self.on_platform = False
		self.frame_rate = 0.2
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,5)

	def collide_platforms(self):
		#collided = pygame.sprite.spritecollide(self.room.target, self.room.trick_platform_sprites, False)
		if self.hitbox.colliderect(self.room.target.hitbox): 
			if self.room.target.hitbox.bottom <= self.hitbox.top + 16 and self.room.target.vel.y >= 0:
				if self.frame_index < 8:
					self.on_platform = True
					self.room.target.cyote_timer = 0
					self.room.target.vel.y = 0
					self.room.target.hitbox.bottom = self.hitbox.top +1
					self.room.target.on_ground = True
					self.room.target.on_wall = False

	def animate(self):
		if self.on_platform:
			self.frame_index += self.frame_rate
			if self.frame_index >= len(self.frames) -1:
				self.on_platform = False
				self.frame_index = 0
				
			self.frame_index += self.frame_rate
			self.image = self.frames[int(self.frame_index)]

		else:
			self.frame_index = 0

	def update(self):
		self.collide_platforms()
		self.animate()

class Interact(pygame.sprite.Sprite):
	def __init__(self, game, room, pos, groups):
		super().__init__(groups)
		self.game = game
		self.room = room
		self.image = self.game.font.render(str('Press space to interact'), True, self.game.BLACK)
		self.rect = self.image.get_rect(center = pos)









		





		



