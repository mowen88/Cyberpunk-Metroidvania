import pygame
from math import ceil, atan2, degrees, pi, sin
from map import Map

class Entity(pygame.sprite.Sprite):
	def __init__(self, game, room, char, pos, groups, obstacle_sprites):
		super().__init__(groups)

		self.game = game
		self.room = room

		self.vel = pygame.math.Vector2()
		self.current_x = 0
		self.char = char

		self.state = 'fall'
		self.alive = True
		self.alpha = 255
		self.frame_index = 0
		self.frame_rate = 0.2
		self.animation_type = 'loop'
		self.jump_counter = 0

		self.moving_left = False
		self.moving_right = False
		self.platform_move_direction = 'stationary'

		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False
		self.on_wall = False
		self.crouching = False
		self.can_stand = None
		self.on_platform = False

		self.invincibility_timer = 0
		self.invincible_cooldown = 80
		self.invincible = False

		# movement
		self.speed = 4
		self.acceleration = self.speed / 12
		self.friction = self.speed / 6
		self.gravity = 0.75
		self.jump_height = 16
		self.max_fall_speed = 16
		self.facing = 1
		self.cyote_timer = 0

		#yoyo
		self.yoyoing = False
		self.can_yoyo = True
		self.send_yoyo = False

		#attacking
		self.attacking = False
		self.can_attack = True
		self.attack_time = None
		self.attack_timer = 0
		self.attack_cooldown = 600
		self.attack_speed = None

		#dashing
		self.dashing = False
		self.can_dash = True
		self.dash_time = None
		self.dash_timer = 0
		self.dash_cooldown = 600
		self.dash_speed_multiplier = 3

		# wall kicking
		self.wall_kicking = False
		self.can_wall_kick = True
		self.wall_kick_time = None
		self.wall_kick_timer = 0
		self.wall_kick_cooldown = 5
		self.wall_slide_speed = 1

		#knocked back
		self.knocked_back = False
		self.can_be_knocked_back = True
		self.knock_back_time = None
		self.knock_back_timer = 0
		self.knock_back_cooldown = 16
		self.knock_back_jump_height = self.knock_back_cooldown / 2

		self.obstacle_sprites = obstacle_sprites
		self.import_imgs()

	def import_imgs(self):
		char_path = f'img/{self.char}/'
		self.animations = {'attack':[],'crawling':[], 'crouching':[], 'run':[], 'idle':[], 'jump':[],'fall':[], 'max_fall':[], 'death':[], 'dashing':[], 'wall_hanging':[]}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = self.game.import_folder(full_path)

	def input(self):
		keys = pygame.key.get_pressed()

		if not self.room.exiting_area:
			if self.game.actions['right']:
				self.moving_right = True

			if self.game.actions['right'] == False:
				self.moving_right = False

			if self.game.actions['left']:
				self.moving_left = True

			if self.game.actions['left'] == False:
				self.moving_left = False

				#show map
			if self.game.actions['m']:
				new_state = Map(self.game, self.room)
				new_state.enter_state()
				self.game.actions['m'] = False

			# attack input
			if self.game.actions['z']:
				self.attack()
				self.game.actions['z'] = False

			if self.game.actions['x']:
				self.yoyo()
				self.game.actions['x'] = False

			# dash input
			if self.game.actions['c']:
				self.dash()
				self.game.actions['c'] = False

			# jump or get-up input
			if self.game.actions['up']:
				if self.crouching:
					self.crouch('up')
				elif self.on_right or self.on_left:
					self.wall_kick()
				else:
					self.jump(self.jump_height)
				self.game.actions['up'] = False

			# crouch input
			if self.game.actions['down']:
				self.crouch('down')
				self.game.actions['down'] = False

			if not (keys[pygame.K_UP] or keys[pygame.K_w]) and self.vel.y < 0:
				# if not holding the jump key, gravity increases while moving up to give variable jump height
				self.gravity = 1.5
			else:
				# set gravity back to normal
				self.gravity = 0.75

			# refresh health for testing
			if self.game.actions['backspace']:
				self.game.current_health = self.game.max_health
				self.game.actions['backspace'] = False

	def moving_left_and_right(self):
		if self.alive and not self.dashing and not self.wall_kicking and not self.on_platform:
				
			if self.moving_right and self.vel.x >= 0:
				self.vel.x += self.acceleration
				self.facing = 1 
			
			elif self.moving_left and self.vel.x <= 0:
				self.vel.x -= self.acceleration
				self.facing = -1
				
			elif self.facing == 1:
				self.vel.x -= self.friction
				if self.vel.x <= 0:
					self.vel.x = 0
			else:
				self.vel.x += self.friction
				if self.vel.x >= 0:
					self.vel.x = 0

		elif self.on_platform:
			if self.platform_move_direction == 'right':
				if self.moving_right and self.vel.x >= 1:
					self.vel.x += self.acceleration
					self.facing = 1
					
				elif self.moving_left and self.vel.x <= 1:
					self.vel.x -= self.acceleration
					self.facing = -1
			
				elif self.facing == 1:
					self.vel.x -= self.friction
					if self.vel.x <= 1:
						self.vel.x = 1
				else:
					self.vel.x += self.friction
					if self.vel.x >= 1:
						self.vel.x = 1

				
			elif self.platform_move_direction == 'left':
				if self.moving_right and self.vel.x >= -1:
					self.vel.x += self.acceleration
					self.facing = 1
			
				elif self.moving_left and self.vel.x <= -1:
					self.vel.x -= self.acceleration
					self.facing = -1

				elif self.facing == 1:
					self.vel.x -= self.friction
					if self.vel.x <= -1:
						self.vel.x = -1
				else:
					self.vel.x += self.friction
					if self.vel.x >= -1:
						self.vel.x = -1

			elif self.platform_move_direction == 'up' or self.platform_move_direction == 'down':
				if self.moving_right and self.vel.x >= 0:
					self.vel.x += self.acceleration
					self.facing = 1 
				
				elif self.moving_left and self.vel.x <= 0:
					self.vel.x -= self.acceleration
					self.facing = -1
					
				elif self.facing == 1:
					self.vel.x -= self.friction
					if self.vel.x <= 0:
						self.vel.x = 0
				else:
					self.vel.x += self.friction
					if self.vel.x >= 0:
						self.vel.x = 0
		else:
			self.platform_move_direction = 'stationary'


	def animate(self, frame_rate):

		inflation = [-10, -10]

		animation = self.animations[self.state]
		
		self.frame_index += frame_rate

		if self.frame_index >= len(animation):
			if self.animation_type == 'loop':
				self.frame_index = 0
			elif self.animation_type == 'end_on_last_frame':
				self.frame_index = len(animation) -1
			else:
				self.kill()
						
		right_img = animation[int(self.frame_index)]
		if self.facing == 1:
			self.image = right_img
		else:
			left_img = pygame.transform.flip(right_img, True, False)
			self.image = left_img

		if self.on_ground and self.on_right:
			self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
			self.hitbox = self.rect.inflate(inflation)
		elif self.on_ground and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
			self.hitbox = self.rect.inflate(inflation)
		elif self.on_ground:
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
			self.hitbox = self.rect.inflate(inflation)
		elif self.on_ceiling and self.on_right:
			self.rect = self.image.get_rect(topright = self.rect.topright)
			self.hitbox = self.rect.inflate(inflation)
		elif self.on_ceiling and self.on_left:
			self.rect = self.image.get_rect(topleft = self.rect.topleft)
			self.hitbox = self.rect.inflate(inflation)
		elif self.on_ceiling:
			self.rect = self.image.get_rect(midtop = self.rect.midtop)
			self.hitbox = self.rect.inflate(inflation)
		else:
			self.rect = self.image.get_rect(center = self.rect.center)
			self.hitbox = self.rect.inflate(inflation)

		if self.invincible:
			alpha = self.wave_func()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)
	
	def wave_func(self):
		value = sin(pygame.time.get_ticks())
		if value >= 0: return 255
		else: return 0

	def change_state(self, new_state, new_frame_rate, new_animation_type):
		if self.state != new_state:
			self.frame_index = 0
			self.state = new_state
			self.frame_rate = new_frame_rate
			self.animation_type = new_animation_type

	def set_state(self):
		if self.alive:
			if self.dashing:
				self.change_state('dashing', 0.3, 'loop')

			elif self.attacking or self.send_yoyo:
				self.change_state('attack', 0.2, 'end_on_last_frame')
	
			elif self.vel.y >= 1 and (self.on_right or self.on_left):
				self.change_state('wall_hanging', 0.1, 'loop')

			elif self.on_ground:
				if self.on_platform:
					if not self.crouching:
						if self.platform_move_direction == 'right':
							if self.vel.x == 1 or self.on_right or self.on_left:
								self.change_state('idle', 0.1, 'loop')	
							else:
								self.change_state('run', 0.2, 'loop')
						elif self.platform_move_direction == 'left':
							if self.vel.x == -1 or self.on_right or self.on_left:
								self.change_state('idle', 0.1, 'loop')	
							else:
								self.change_state('run', 0.2, 'loop')

						if self.platform_move_direction == 'up' or self.platform_move_direction == 'down':
							if (self.vel.x == 0 or self.on_right or self.on_left) and (self.vel.y >= -1 and self.vel.y <= 1):
								self.change_state('idle', 0.1, 'loop')	
							else:
								self.change_state('run', 0.2, 'loop')


					else:
						if self.platform_move_direction == 'right':
							if self.vel.x == 1 or self.on_right or self.on_left:
								self.change_state('crouching', 0.3, 'end_on_last_frame')
							else:
								self.change_state('crawling', 0.2, 'loop')
						elif self.platform_move_direction == 'left':
							if self.vel.x == -1 or self.on_right or self.on_left:
								self.change_state('crouching', 0.1, 'end_on_last_frame')
							else:
								self.change_state('crawling', 0.2, 'loop')

						if self.platform_move_direction == 'up' or self.platform_move_direction == 'down':
							if (self.vel.x == 0 or self.on_right or self.on_left) and (self.vel.y >= -1 and self.vel.y <= 1):
								self.change_state('crouching', 0.1, 'end_on_last_frame')	
							else:
								self.change_state('crawling', 0.2, 'loop')

				
				else:
					if not self.crouching:
						if self.vel.x == 0 or self.on_right or self.on_left:
							self.change_state('idle', 0.1, 'loop')
						else:
							self.change_state('run', 0.2, 'loop')
					else:
						if self.vel.x == 0 or self.on_right or self.on_left:
							self.change_state('crouching', 0.3, 'end_on_last_frame')
						else:
							self.change_state('crawling', 0.2, 'loop')

			else:
				if self.vel.y < 0:
					self.change_state('jump', 0.2, 'end_on_last_frame')
					
				elif self.vel.y < self.max_fall_speed:
					self.change_state('fall', 0.2, 'end_on_last_frame')
				
				else:
					self.change_state('max_fall', 0.3, 'loop')
				
		else:
			self.change_state('death', 0.2, 'loop')

	def apply_gravity(self):
		if not self.on_platform:
			self.vel.y += self.gravity
			self.rect.y += self.vel.y
			if self.vel.y > self.max_fall_speed:
				self.vel.y = self.max_fall_speed

	def apply_acceleration(self):
		if self.on_platform:
			if self.platform_move_direction == 'right':
				if self.vel.x >= self.speed + 1:
					self.vel.x = self.speed + 1
				if self.vel.x <= - self.speed + 1:
					self.vel.x = - self.speed + 1

			elif self.platform_move_direction == 'left':
				if self.vel.x >= self.speed - 1:
					self.vel.x = self.speed - 1
				if self.vel.x <= -self.speed - 1:
					self.vel.x = -self.speed - 1

			elif self.platform_move_direction == 'up' or self.platform_move_direction == 'down':
				if self.vel.x >= self.speed:
					self.vel.x = self.speed
				if self.vel.x <= - self.speed:
					self.vel.x = - self.speed
		else:
			if self.vel.x >= self.speed:
				self.vel.x = self.speed
			if self.vel.x <= - self.speed:
				self.vel.x = - self.speed

	def crouch(self, up_or_down):
		if up_or_down == 'down':
			self.crouching = True
		elif self.can_stand:
			self.crouching = False

	def jump(self, height):
		if self.cyote_timer < 6:
			self.vel.y = -height
			self.jump_counter = 1
		elif self.jump_counter == 1:
			self.jump_counter = 0
			self.vel.y = -height

	def dash(self):
		if self.can_dash and not self.crouching:
			self.dashing = True
			self.can_dash = False
			self.dash_time = pygame.time.get_ticks()

	def yoyo(self):
		if self.can_yoyo and not (self.dashing or self.crouching or self.attacking or self.on_left or self.on_right):
			self.room.create_yoyo()
			self.send_yoyo = True
			self.yoyoing = True
			self.can_yoyo = False

	def attack(self):
		if self.can_attack and not (self.yoyoing or self.crouching or self.dashing or self.on_left or self.on_right):
			self.attack_speed = self.get_distance_direction_and_angle(self)[3]
			self.room.create_attack()
			self.attacking = True
			self.can_attack = False

	def wall_slide(self):
		if not self.on_ground and not self.attacking and self.vel.y > 1 and self.on_right or \
		not self.on_ground and  not self.attacking and self.vel.y > 1 and self.on_left:
			self.vel.y = self.wall_slide_speed
			self.can_wall_kick = True

	def wall_kick(self):
		if self.can_wall_kick:
			self.wall_kicking = True
			self.can_wall_kick = False
			#self.wall_kick_time = pygame.time.get_ticks()

	def knock_back(self):
		if self.can_be_knocked_back:
			self.knocked_back = True
			self.can_be_knocked_back = False
			self.knock_back_time = pygame.time.get_ticks()


	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		
		if self.alive:
			if self.invincible:
				self.invincibility_timer += 1
				if self.invincibility_timer >= self.invincible_cooldown:
					self.invincible = False
					self.invincibility_timer = 0

			if self.dashing:
				self.dash_timer += 1
				self.vel.x = self.facing * self.speed * self.dash_speed_multiplier
				if self.vel.y > 0:
					self.vel.y = 0
				if self.dash_timer > 10:
					self.dashing = False
					self.dash_timer = 0

			if self.can_dash == False:
				if current_time - self.dash_time >= self.dash_cooldown:
					self.can_dash = True

			if self.wall_kicking:
				self.wall_kick_timer += 1
				self.vel.x = -self.facing * self.speed
				self.vel.y = -10
				if self.wall_kick_timer > self.wall_kick_cooldown:
					self.wall_kicking = False
					self.wall_kick_timer = 0

			if self.knocked_back:
				self.knock_back_timer += 1
				#self.knock
				self.vel.x = self.facing * -self.speed
				self.jump(self.knock_back_jump_height)
				if self.knock_back_timer > self.knock_back_cooldown:
					self.knocked_back = False
					self.knock_back_timer = 0

			if self.can_be_knocked_back == False:
				if current_time - self.knock_back_time >= self.knock_back_cooldown:
					self.can_be_knocked_back = True

			if self.can_wall_kick == False:
				#if current_time - self.wall_kick_time >= self.wall_kick_cooldown:
				if self.on_right or self.on_left:
					self.can_wall_kick = True

	# the player's own x collisions to include 'on_right' and 'on_left' booleans
	def x_collisions(self):
		if self.alive:
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.vel.x > 0:
					
						self.hitbox.right = sprite.hitbox.left
						self.on_right = True
						self.current_x = self.hitbox.right
						if self.vel.y == 1:
							self.on_wall = True

					elif self.vel.x < 0:
						
						self.hitbox.left = sprite.hitbox.right
						self.on_left = True
						self.current_x = self.hitbox.left
						if self.vel.y == 1:
							self.on_wall = True
						
			if self.on_right and (self.hitbox.right > self.current_x or self.vel.x <= 0):
				self.on_right = False
				self.on_wall = False

			if self.on_left and (self.hitbox.left < self.current_x or self.vel.x >= 0):
				self.on_left = False
				self.on_wall = False
			
	def y_collisions(self):
		if self.alive:
			for sprite in self.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.vel.y > 0:
						self.hitbox.bottom = sprite.hitbox.top
						self.vel.y = 0
						self.on_ground = True
						self.cyote_timer = 0

					elif self.vel.y < 0:
						self.hitbox.top = sprite.hitbox.bottom
						self.vel.y = 0
						self.on_ceiling = True

			if self.on_ground and self.vel.y < -1 or self.vel.y > 1:
				self.on_ground = False

			if self.on_ceiling and self.vel.y > 0:
				self.on_ceiling = False

	def hit_spikes(self):
		if self.alive:
			for sprite in self.room.spike_sprites:
				if sprite.hitbox.colliderect(self):
					self.alive = False
					self.die()

	def get_distance_direction_and_angle(self, target):
		vel_x = self.vel.x
		enemy_vec = pygame.math.Vector2(self.rect.center)
		target_vec = pygame.math.Vector2(target.rect.center)
		distance = (target_vec - enemy_vec).magnitude()
		
		if (target_vec - enemy_vec) != pygame.math.Vector2(0,0):
		    direction = (target_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2(1,1)
			
		dx = self.rect.centerx - (target.rect.x)
		dy = self.rect.centery - (target.rect.y)

		radians = atan2(-dx, dy)
		radians %= 2*pi
		angle = int(degrees(radians))

		return(distance, direction, angle, vel_x)

	def death_fade_away(self):
		if not self.alive:
			self.image.set_alpha(self.alpha)

	def die(self):
		self.alive = False
		self.jump_counter = 1
		self.jump(self.jump_height)
		self.vel.x = 0

	def timers(self):
		self.cyote_timer += 1

		if not self.on_ground:
			self.crouching = False
		
		if not self.alive:
			self.alpha -= 255/75

		if self.alpha <= 0:
			self.kill()

	def crouch_clearance(self):
		collider = pygame.Rect(self.hitbox.x, self.hitbox.y -25, 25, 25)
		for sprite in self.obstacle_sprites:
			if sprite.hitbox.colliderect((collider)):
				self.can_stand = False

	def collide_platforms(self):
		#collided = pygame.sprite.spritecollide(self.room.target, self.room.trick_platform_sprites, False)
		for platform in self.room.moving_platform_sprites:
			if platform.hitbox.colliderect(self.hitbox): 
				if self.hitbox.bottom <= platform.hitbox.top + 16 and self.vel.y > 0:
					self.hitbox.bottom = platform.hitbox.top +1
					self.vel.y = 1
					self.cyote_timer = 0
					self.on_ground = True
					self.on_wall = False
					self.on_platform = True
					
					if platform.vel.x == 1:
						self.platform_move_direction = 'right'
					elif platform.vel.x == -1:
						self.platform_move_direction = 'left'
					elif platform.vel.y == 1:
						self.platform_move_direction = 'down'
					elif platform.vel.y == -1:
						self.platform_move_direction = 'up'
					else:
						self.platform_move_direction = 'stationary'

			else:
				self.on_platform = False
		for platform in self.room.moving_platform_sprites:
			if platform.hitbox.colliderect(self.hitbox): 
				if self.hitbox.bottom <= platform.hitbox.top + 20 and self.vel.y > 0:
					self.on_platform = True


	def move(self, speed):
		keys = pygame.key.get_pressed()
		self.hitbox.x += self.vel.x
		self.can_stand = True
		self.crouch_clearance()
		self.timers()
		#self.platform_lateral_movement()
		self.x_collisions()
		self.apply_gravity()
		self.hitbox.y += self.vel.y 
		self.y_collisions()	
		self.collide_platforms()
		self.rect.center = self.hitbox.center

		



		


		

