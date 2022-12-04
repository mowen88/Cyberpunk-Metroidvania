import pygame, random
from entities import Entity

class WalkingEnemy(Entity):
	def __init__(self, game, room, char, pos, groups, obstacle_sprites):
		super().__init__(game, room, char, pos, groups, obstacle_sprites)
		self.game = game
		self.room = room
		self.image = pygame.image.load(f'img/{char}/idle/0.png')
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-15, -10)
		

		self. vel = pygame.math.Vector2()
		self.speed = 1
		self.acceleration = self.speed / 12
		self.friction = self.speed / 6
		self.facing = 1
		self.health = 2
		self.coins_given = random.randint(4,6)

		self.knock_back_jump_height = 8

	def move(self, direction):
		if self.alive and not self.room.cutscene_running:
			if direction == 1 and self.vel.x >= 0:
				self.vel.x += self.acceleration
				self.facing = 1 
				if self.vel.x >= self.speed:
					self.vel.x = self.speed
			elif direction == -1 and self.vel.x <= 0:
				self.vel.x -= self.acceleration
				self.facing = -1
				if self.vel.x <= -self.speed:
					self.vel.x = -self.speed
			elif self.facing == 1:
				self.vel.x -= self.friction
				if self.vel.x <= 0:
					self.vel.x = 0
			else:
				self.vel.x += self.friction
				if self.vel.x >= 0:
					self.vel.x = 0

			self.hitbox.x += self.vel.x 
			self.x_collisions()
			self.apply_gravity()
			self.hitbox.y += self.vel.y
			self.y_collisions() 
			self.rect.center = self.hitbox.center

		elif not self.alive:
			self.hitbox.x += self.vel.x 
			self.apply_gravity()
			self.hitbox.y += self.vel.y 
			self.rect.center = self.hitbox.center

	def switch_direction(self):
		if self.on_right:
			self.facing = -1
		elif self.on_left:
			self.facing = 1
	
	def switch_direction_collision_tile(self):
		for sprite in self.room.collision_tile_sprites:
			if sprite.hitbox.colliderect(self.hitbox):
				if self.vel.x > 0:
					self.hitbox.right = sprite.hitbox.left
					self.on_right = True

				elif self.vel.x < 0:
					self.hitbox.left = sprite.hitbox.right
					self.on_left = True

	def update(self):
		self.animate(self.frame_rate)
		self.timers()
		self.set_state()
		self.hit_spikes()
		self.cooldowns()
		self.death_fade_away()
		self.switch_direction_collision_tile()
		self.switch_direction()
		self.move(self.facing)

class LungingEnemy(WalkingEnemy):
	def __init__(self, game, room, char, pos, groups, obstacle_sprites):
		super().__init__(game, room, char, pos, groups, obstacle_sprites)
		self.game = game
		self.room = room
		self.image = pygame.image.load(f'img/{char}/idle/0.png')
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-15, 30)
		self.vision_box = pygame.Rect(0,0,300, 80)

		self.alerted = False
		self.windup_timer = 0
		self.speed = 1
		self.attack_speed = self.speed * 8

		self.invincible_cooldown = 80
		self.knock_back_cooldown = 30

		self.coins_given = random.randint(4,6)

	def lock_direction(self):
		return self.facing

	def seen_player(self):
		if self.room.player.hitbox.colliderect(self.vision_box):
			self.alerted = True

	def action(self, direction, speed):
		if self.alive:

			if self.alerted and not self.attacking:
				self.vel.x = 0
				self.crouching = True
				self.windup_timer += 1
				if self.windup_timer >= 60:
					self.windup_timer = 0
					self.attacking = True

			elif self.attacking:
				self.facing = self.lock_direction()
				self.vel.x = self.attack_speed * self.facing
				self.attack_speed -= 0.1 
				if self.attack_speed <= 0:
					self.crouching = False
					self.attacking = False
					self.alerted = False
					self.attack_speed = 8

			else:
				if direction == 1 and self.vel.x >= 0:
					self.vel.x += self.acceleration
					self.facing = 1 
					if self.vel.x >= speed:
						self.vel.x = speed
				elif direction == -1 and self.vel.x <= 0:
					self.vel.x -= self.acceleration
					self.facing = -1
					if self.vel.x <= -speed:
						self.vel.x = -speed
				elif self.facing == 1:
					self.vel.x -= self.friction
					if self.vel.x <= 0:
						self.vel.x = 0
				else:
					self.vel.x += self.friction
					if self.vel.x >= 0:
						self.vel.x = 0
		

			self.hitbox.x += self.vel.x 
			self.x_collisions()
			self.apply_gravity()
			self.hitbox.y += self.vel.y
			self.y_collisions() 
			self.rect.center = self.hitbox.center

		elif not self.alive:
			self.hitbox.x += self.vel.x 
			self.apply_gravity()
			self.hitbox.y += self.vel.y 
			self.rect.center = self.hitbox.center


	def update(self):
		self.vision_box.center = (self.hitbox.centerx + 150 * self.facing, self.hitbox.centery)
		self.seen_player()
		self.animate(self.frame_rate)
		self.timers()
		self.set_state()
		self.hit_spikes()
		self.cooldowns()
		self.death_fade_away()
		self.switch_direction_collision_tile()
		if not (self.attacking or self.alerted):
			self.switch_direction()
			self.action(self.facing, self.speed)
		else:
			self.action(self.facing, self.attack_speed)

class FlyingEnemy(Entity):
	def __init__(self, game, room, char, pos, groups, obstacle_sprites):
		super().__init__(game, room, char, pos, groups, obstacle_sprites)

		self.game = game
		self.room = room
		self.image = pygame.image.load(f'img/{char}/idle/0.png')
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-15, -10)

		# self.tween = pytweening.easeInOutSine
		# self.step = 0
		# self.sweep_range = 10
		# self.distance_to_target = None

		self.health = 2
		self.speed = 6
		self.acceleration = self.speed / 24
		self.facing = 1
		self.invincible_cooldown = 60
		self.knock_back_cooldown = 15

		self.coins_given = random.randint(4,6)

		self.import_imgs()

	def set_state(self):
		distance = self.get_distance_direction_and_angle(self.room.player)[0]
		# if distance > 600:
		# 	self.change_state('idle', 0.1)
		if self.alive:
			if distance > 400:
				self.change_state('idle', 0.1, 'loop')
			elif self.vel != 0:
				self.change_state('run', 0.2, 'loop')

		else:
			self.change_state('death', 0.3, 'loop')

	def move(self):
		if not self.state == 'idle' and self.alive:

			if self.hitbox.centerx >= self.room.player.hitbox.centerx:
				self.vel.x -= self.acceleration
				self.facing = -1
				
			elif self.hitbox.centerx < self.room.player.hitbox.centerx:
				self.vel.x += self.acceleration
				self.facing = 1
			
			else:
				self.alive = False

			if self.hitbox.centery >= self.room.player.hitbox.centery:
				self.vel.y -= self.acceleration
			if self.hitbox.centery < self.room.player.hitbox.centery:
				self.vel.y += self.acceleration

			if self.vel.x > self.speed:
				self.vel.x = self.speed
			elif self.vel.x < -self.speed:
				self.vel.x = -self.speed

			if self.vel.x > self.speed:
				self.vel.x = self.speed
			elif self.vel.x < -self.speed:
				self.vel.x = -self.speed

			if self.vel.y > self.speed:
				self.vel.y = self.speed
			elif self.vel.y < -self.speed:
				self.vel.y = -self.speed

			self.hitbox.x += self.vel.x 
			self.x_collisions()
			self.hitbox.y += self.vel.y
			self.y_collisions() 
			self.rect.center = self.hitbox.center

		elif not self.alive:
			self.hitbox.x += self.vel.x 
			self.apply_gravity()
			self.hitbox.y += self.vel.y 
			self.rect.center = self.hitbox.center


	def update(self):
		self.animate(self.frame_rate)
		self.timers()
		self.cooldowns()
		self.death_fade_away()
		self.set_state()
		self.move()

		
		
			