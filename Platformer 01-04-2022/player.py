import pygame
from settings import *
from support import import_folder
from tile import Entity, Character, Gun
from particles import Particles

class Player(Character):
	def __init__(self, game, pos, groups, obstacle_sprites, create_melee, create_run_particles, create_jump_particles, create_dash_particles, create_hover_particles, shoot, current_gun, gun_showing):
		super().__init__(groups)
		self.display_surf = pygame.display.get_surface()
		
		self.game = game
		self.current_x = 0
		self.going_down = False
		self.going_up = False
		self.on_elevator = False
		self.liquid_collided = False
		self.can_jump = True
		#self.liquid_collided = False
		# animation setup
		self.import_assets()

		self.image = self.animations['idle'][self.frame_index].convert_alpha()
		self.rect = self.image.get_rect(bottomleft = (pos[0], pos[1] + self.image.get_height() + TILESIZE))

		# movement
		self.speed = None
		self.jump_height = JUMP_HEIGHT
		self.jump_counter = 0
		self.run_in = True
		self.hold = False
		self.hold_timer = 0
		self.facing = 1
		self.state = 'idle'
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False
		self.on_wall = False
		self.invincible = False
		self.invincibility_timer = 0

		#hovering
		self.hovering = False

		#dashing
		self.dashing = False
		self.can_dash = True
		self.dash_time = None
		self.dash_timer = 0
		self.dash_cooldown = 800

		# attacking
		self.create_melee = create_melee
		self.attacking = False
		self.air_attacked = False
		self.attack_cooldown = 300
		self.attack_time = None

		#shooting
		self.gun_showing = gun_showing
		self.can_shoot = True
		self.shoot = shoot
		self.shoot_time = None
		self.gun_index = 0
		self.gun = current_gun
		self.shoot_cooldown = None

		# particles
		self.create_jump_particles = create_jump_particles
		self.create_run_particles = create_run_particles
		self.create_dash_particles = create_dash_particles
		self.create_hover_particles = create_hover_particles
		self.run_particle_timer = 0
		self.dash_particle_timer = 0
		self.hover_particle_timer = 0

		self.obstacle_sprites = obstacle_sprites

	def change_gun(self):
		if self.gun_index < len(list(gun_data.keys()))-1:
			self.gun_index += 1
		else:
			self.gun_index = 0
		self.gun = self.gun_index
	
	def get_state(self):
		if self.alive:
			if self.hold and self.gun_showing:
				self.state = 'collecting_armed'
			elif not self.run_in: 
				if self.dashing:
					self.state = 'dashing'
				elif self.hovering and not self.on_ground:
					self.state = 'hovering'
				elif self.gun_showing:
					self.speed = 3
					if self.hold:
						self.state = 'collecting_armed'
					elif self.vel.x != 0 and self.on_ground  and not self.on_right and not self.on_left:
						self.state = 'run_armed'
					elif self.on_ground:
						self.state = 'idle_armed'
					elif self.vel.y < 0:
						self.state = 'jump_armed'
					else:
						self.state = 'fall_armed'
				else:
					self.speed = 5
					if self.hold:
						self.state = 'collecting'
					elif 'wall_jump' in pickup_data and pickup_data['wall_jump'] == True and \
					self.on_right and self.vel.y >= 1 or 'wall_jump' in pickup_data and pickup_data['wall_jump'] == True and self.on_left and self.vel.y >= 1:
						self.state = 'sliding'
					elif self.attacking:
						self.state = 'attack'
					elif self.vel.y < 0:
						self.state = 'jump'
					elif self.vel.y > 1:
						self.state = 'fall'
					else:
						if self.vel.x != 0 and not self.on_right and not self.on_left:
							self.state = 'run' 
						else:
							self.state = 'idle'
		else:
			self.state = 'death'
			
	def import_assets(self):
		char_path = f'img/player/'
		self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': [], 'dashing': [],'idle_armed': [], 'hovering': [], \
		 'run_armed': [], 'jump_armed': [], 'fall_armed': [], 'death': [], 'collecting_armed': [], 'collecting': [], 'sliding': []}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = import_folder(full_path)

	def input(self):
		if not self.attacking and not self.run_in and not self.dashing and not self.hold:
			keys = pygame.key.get_pressed()
			# move input
			if keys[pygame.K_RIGHT] and not (self.going_up or self.going_down):
				self.vel.x = 1
				self.facing = 1

			elif keys[pygame.K_LEFT] and not (self.going_up or self.going_down):
				self.vel.x = -1
				self.facing = -1

			else:
				self.vel.x = 0

			if keys[pygame.K_x]:
				if self.gun_showing:
					if self.can_shoot and gun_data:
						self.shoot(self.gun)
						self.can_shoot = False
						self.shoot_time = pygame.time.get_ticks()

				elif self.game.actions['x'] and not self.air_attacked and not (self.on_right or self.on_left):
					self.attacking = True
					self.attack_time = pygame.time.get_ticks()
					self.create_melee()

			if keys[pygame.K_LSHIFT] and 'hovering' in pickup_data and pickup_data['hovering'] == True and not self.on_ground:
				self.hovering = True
				self.game.jetpack_fx.play()
				self.create_hover_particles()
				self.vel.y = 1
			else:
				self.hovering = False
				self.game.jetpack_fx.stop()

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if self.attacking:
			if self.on_ground:
				self.vel = pygame.math.Vector2()
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attacking = False

		if self.can_shoot == False:
			if current_time - self.shoot_time >= self.shoot_cooldown:
				self.can_shoot = True

		if self.on_ground:
			self.air_attacked = False
			self.hovering = False

		#get gun cooldown
		if gun_data:
			self.shoot_cooldown = (list(gun_data.values())[self.gun]['cooldown'])

		if self.dashing:
			self.dash_timer += 1
			self.vel.x = self.facing * 6
			if self.dash_timer > 10:
				self.dashing = False
				self.dash_timer = 0

		if self.can_dash == False:
			if current_time - self.dash_time >= self.dash_cooldown:
				self.can_dash = True


	# auto walk into the level to avoid exit collision
	def enter_level(self):
		if self.rect.centerx > self.display_surf.get_width() // 2:
			self.facing = -1
			
		else:
			self.facing = 1
		
		
	# the player's own x collisions to include 'on_right' and 'on_left' booleans
	def x_collisions(self):
		for sprite in self.obstacle_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.vel.x > 0:
					self.rect.right = sprite.rect.left
					self.on_right = True
					self.current_x = self.rect.right
					if self.vel.y == 1:
						self.on_wall = True
		
				elif self.vel.x < 0:
					self.rect.left = sprite.rect.right
					self.on_left = True
					self.current_x = self.rect.left
					if self.vel.y == 1:
						self.on_wall = True
					
		if self.on_right and (self.rect.right > self.current_x or self.vel.x <= 0):
			self.on_right = False
			self.on_wall = False

		if self.on_left and (self.rect.left < self.current_x or self.vel.x >= 0):
			self.on_left = False
			self.on_wall = False

	def y_collisions(self):
		for sprite in self.obstacle_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.vel.y > 0:
					self.rect.bottom = sprite.rect.top
					self.vel.y = 0
					self.on_ground = True
				elif self.vel.y < 0:
					self.rect.top = sprite.rect.bottom
					self.vel.y = 0
					self.on_ceiling = True

		if self.on_ground and self.vel.y < 0 or self.vel.y > 1:
			self.on_ground = False
		if self.on_ceiling and self.vel.y > 0:
			self.on_ceiling = False

	def dash(self):
		if not self.run_in and self.can_dash and 'dash' in pickup_data and pickup_data['dash'] == True:
			self.dashing = True
			self.can_dash = False
			self.dash_time = pygame.time.get_ticks()
		
	# player inputs passed to event queue, as opposed to get key presses
	def jump(self):
		if self.on_ground:
			self.vel.y = - JUMP_HEIGHT
			self.create_jump_particles('jump')
			self.jump_counter = 1
		elif self.jump_counter == 1 and 'double_jump' in pickup_data and pickup_data['double_jump'] == True:
			self.vel.y = - JUMP_HEIGHT
			self.create_jump_particles('double_jump')
			self.game.double_jump_fx.play()
			self.jump_counter = 0
		elif self.on_wall and not self.gun_showing:
			self.wall_jump()

	def wall_jump(self):
		if self.on_wall:
			self.vel.y = - JUMP_HEIGHT
			self.create_jump_particles('jump')
			self.jump_counter = 1
			self.on_wall = False
		
	def wall_slide(self):
		if 'wall_jump' in pickup_data:
			if not self.gun_showing and pickup_data['wall_jump'] == True:
				if not self.on_ground and self.vel.y > 1 and self.on_right or not self.on_ground and self.vel.y > 1 and self.on_left:
					self.vel.y = 1

	def holding(self):
		self.vel.x = 0
		self.hold_timer += 1
		if self.hold_timer >= HOLD_TIME - 20:
			self.hold_timer = 0
			self.hold = False

	def liquid_collisions(self):
		for sprite in self.game.level.liquid_sprites:
			if pygame.sprite.spritecollide(self, self.game.level.liquid_sprites, False, pygame.sprite.collide_rect_ratio(0.6)):
				self.liquid_collided = True
				if 'can_swim' not in pickup_data:
					if not self.invincible:
						self.game.current_health -= 50
						self.invincible = True
						self.invincibility_timer = 0
					if self.game.current_health <= 0:
						self.game.current_health = 0
						Particles(self, [self.game.level.visible_sprites, self.game.level.active_sprites], 'guard')
						self.alive = False
						self.kill()
						if self.gun_showing:
							self.game.level.gun_sprite.kill()	
			else:
				self.liquid_collided = False

	def enemy_collide(self):
		for sprite in self.game.level.collidable_enemy_sprites:
			if pygame.sprite.spritecollide(self, self.game.level.collidable_enemy_sprites, False, pygame.sprite.collide_rect_ratio(0.8)):	
				if not self.invincible:
					self.vel.y = - JUMP_HEIGHT
					self.game.current_health -= 25
					self.invincible = True
					self.invincibility_timer = 0
				if self.game.current_health <= 0:
					self.game.current_health = 0
					Particles(self, [self.game.level.visible_sprites, self.game.level.active_sprites], 'guard')
					self.alive = False
					self.kill()
					if self.gun_showing:
						self.game.level.gun_sprite.kill()	
		

	def update(self):
		self.enemy_collide()
		self.liquid_collisions()
		self.animate('loop')
		self.wall_slide()
		self.input()
		self.get_state()
		self.cooldowns()
		if self.hold:
			self.holding()
		if self.run_in:
			self.enter_level()
		else:
			if self.liquid_collided:
				self.speed = 2
			self.rect.x += self.vel.x * self.speed
		self.x_collisions()
		if self.going_down:
			self.rect.y += 3
		elif self.going_up:
			self.rect.y -= 3
		else:
			self.gravity()
		self.y_collisions()


	
		
