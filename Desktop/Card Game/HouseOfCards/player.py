import pygame
from entities import Entity
from map import Map

		
class Player(Entity):
	def __init__(self, game, room, char, pos, groups, obstacle_sprites):
		super().__init__(game, room, char, pos, groups, obstacle_sprites)

		self.game = game
		self.room = room
		self.char = char
		self.display_surf = pygame.display.get_surface()
		self.import_imgs()

		self.image = pygame.image.load('img/player/idle/0.png')
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-15, -10)

		# movement
		self.speed = 6
		self.run_speed = 6
		self.crawl_speed = self.run_speed / 2
		self.acceleration = self.speed / 12
		self.friction = self.speed/ 6
		self.gravity = 0.75
		self.jump_height = 16
		self.max_fall_speed = 16
		self.facing = 1
		self.cyote_timer = 0

	
	def import_imgs(self):
		char_path = f'img/{self.char}/'
		self.animations = {'attack':[],'crawling':[], 'crouching':[], 'run':[], 'idle':[], 'jump':[],'fall':[], 'max_fall':[], 'death':[], 'dashing':[], 'wall_hanging':[]}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = self.game.import_folder(full_path)


	def stop_at_edge_of_room(self):
		if self.rect.right >= self.room.visible_sprites.room_size[0]:
			self.vel.x = 0
			self.on_right = True
		elif self.rect.left <= 0:
			self.vel.x = 0
			self.on_left = True
		if self.rect.bottom >= self.room.visible_sprites.room_size[1]:
			self.vel.y = 0
			self.on_ground = True
		elif self.rect.top <= 0:
			self.vel.y = 0
			self.on_ceiling = True


	def enemy_collision_knockback(self):
		for enemy in self.room.enemy_sprites:
			if enemy.hitbox.colliderect(self.hitbox):
				if enemy.alive and not enemy.invincible and not self.invincible and not self.dashing:
					self.knock_back_cooldown = enemy.knock_back_cooldown
					self.knock_back_jump_height = enemy.knock_back_cooldown * 0.5
					self.knock_back()
					self.room.reduce_health(1)
					self.invincible = True

	def hit_spikes(self):
		for spike in self.room.spike_sprites:
			if spike.hitbox.colliderect(self.hitbox):
				if not self.invincible:
					self.room.reduce_health(1)
					self.invincible = True
					self.die()


			
	def update(self):
		if self.crouching:
			self.speed = self.crawl_speed
		else:
			self.speed = self.run_speed
		self.moving_left_and_right()
		self.death_fade_away()
		self.apply_acceleration()
		self.wall_slide()
		self.cooldowns()
		self.timers()
		self.set_state()
		self.hit_spikes()
		self.enemy_collision_knockback()
		self.move(self.speed)
		self.animate(self.frame_rate)
		self.stop_at_edge_of_room()
		




class NPC(Entity):
	def __init__(self, game, room, char, pos, groups, obstacle_sprites):
		super().__init__(game, room, char, pos, groups, obstacle_sprites)
		self.game = game
		self.char = char
		self.room = room
		self.obstacle_sprites = obstacle_sprites
		self.image = pygame.image.load(f'img/NPCs/{self.char}/idle/0.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0, 0)


	def import_imgs(self):
		char_path = f'img/NPCs/{self.char}/'
		self.animations = {'attack':[],'crawling':[], 'crouching':[], 'run':[], 'idle':[], 'jump':[],'fall':[], 'max_fall':[], 'death':[], 'dashing':[], 'wall_hanging':[]}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = self.game.import_folder(full_path)


	def update(self):
		self.death_fade_away()
		self.apply_acceleration()
		self.animate(self.frame_rate)
		self.wall_slide()
		self.cooldowns()
		self.timers()
		self.set_state()
		self.move(self.speed)


		
		



	
		
