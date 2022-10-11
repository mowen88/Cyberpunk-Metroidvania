import pygame, random
from settings import *
from support import *
from tile import Entity, Character
from particles import Particles
from tile import Bullet

class Guard(Character):
	def __init__(self, game, pos, groups, obstacle_sprites, sprite_type, health):
		super().__init__(groups)

		self.import_assets(sprite_type)
		self.sprite_type = sprite_type
		self.game = game
		self.game = game
		self.health = health
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(bottomleft = (pos[0], pos[1] + TILESIZE))
		self.hitbox = self.rect.inflate(-20, -20)
		self.attacking = False
		self.on_ground = False
		self.on_ceiling = False
		self.on_right = False
		self.on_left = False
		self.moving_right = True
		self.move_timer = 0
		self.idle_timer = 0
		self.idling = False
		self.invincible = False
		self.invincibility_timer = 0

		self.vel = pygame.math.Vector2()
		self.obstacle_sprites = obstacle_sprites
			
	def import_assets(self, name):
		char_path = f'img/{name}/'
		self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': [], 'facing': []}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = import_folder(full_path)

	def move(self):
		self.move_timer += 1
		if self.idling:
			self.idle_timer += 1
			self.move_timer = 0
			self.vel = pygame.math.Vector2()
		else:
			self.vel.x = 1
			self.vel.y = 0

			if self.moving_right:
				self.rect.x += self.vel.x
				self.facing = 1
			else:
				self.moving_right = False
				self.rect.x -= self.vel.x
				self.facing = -1

	def collide(self):
		for sprite in self.game.level.collision_block_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.moving_right:
					self.moving_right = False
				elif not self.moving_right:
					self.moving_right = True

	def update(self):
		self.animate('loop')
		self.get_state()
		self.move()
		self.collide()
	

class ArmedGuard(Character):
	def __init__(self, game, pos, groups, obstacle_sprites, sprite_type, gun_index, health):
		super().__init__(groups)

		self.import_assets(sprite_type)
		self.game = game
		self.sprite_type = sprite_type
		self.gun_index = gun_index
		self.health = health
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(bottomleft = (pos[0], pos[1] + TILESIZE))
		self.hitbox = self.rect.inflate(-20, -20)
		self.attacking = False
		self.on_ground = False
		self.on_ceiling = False
		self.on_right = False
		self.on_left = False
		self.moving_right = True
		self.move_timer = 0
		self.idle_timer = 0
		self.idling = False
		self.invincible = False
		self.invincibility_timer = 0
		self.vision_box = pygame.Rect(0, 0, 400, 80)
		
		self.vel = pygame.math.Vector2()
		self.obstacle_sprites = obstacle_sprites

		# shoot stuff
		self.can_shoot = True
		self.shoot_time = pygame.time.get_ticks()
		self.shoot_cooldown = (list(enemy_gun_data.values())[self.gun_index]['cooldown'])

	def import_assets(self, name):
		char_path = f'img/{name}/'
		self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': [], 'facing': [], 'death': []}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = import_folder(full_path)

	def move(self):
		if self.alive:
			self.move_timer += 1
			if self.idling:
				self.idle_timer += 1
				self.move_timer = 0
				self.vel = pygame.math.Vector2()
			else:
				self.vel.x = 1
				self.vel.y = 0 

				if self.moving_right:
					self.rect.x += self.vel.x
					self.facing = 1
				else:
					self.moving_right = False
					self.rect.x -= self.vel.x
					self.facing = -1

	def ai(self):
		if random.randint(1,300) == 1:
			self.idling = True
		if self.idle_timer >= 120:
			self.idling = False
			self.idle_timer = 0

	def collide(self):
		for sprite in self.game.level.collision_block_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.moving_right:
					self.moving_right = False
				elif not self.moving_right:
					self.moving_right = True
	
	def ai(self):
		if random.randint(1,300) == 1:
			self.idling = True
		if self.idle_timer >= 120:
			self.idling = False
			self.idle_timer = 0

	def vision(self):
		self.vision_box.center = (self.rect.centerx + 180 * self.facing, self.rect.centery)
	
	def alert(self):
		if (self.vision_box.colliderect(self.game.level.player) and self.game.level.player.alive) or self.game.level.bullet_hit_enemy:
			self.idling = True
			if self.game.level.player.rect > self.rect:
				self.facing = 1
			else:
				self.facing = -1

			if self.can_shoot:
				self.shoot_time = pygame.time.get_ticks()
				self.enemy_bullet = Bullet(self.game, self, self.gun_index, enemy_gun_data, [self.game.level.visible_sprites, self.game.level.active_sprites], self.obstacle_sprites)
				pygame.mixer.Sound(self.enemy_bullet.sfx).play()
				self.game.level.bullet_sprites.add(self.enemy_bullet)
				self.can_shoot = False
		if not self.vision_box.colliderect(self.game.level.player):
			self.game.level.bullet_hit_enemy = False
	
		
	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if self.can_shoot == False:
			if current_time - self.shoot_time >= self.shoot_cooldown:
				self.can_shoot = True

	def update(self):	
		self.animate('loop')
		self.get_state()
		self.vision()
		if self.game.level.player.alive:
			self.alert()
		self.move()
		self.ai()
		self.collide()
		self.cooldowns()
		
class NPC(Character):
	def __init__(self, pos, groups, obstacle_sprites, sprite_type):
		super().__init__(groups)

		self.sprite_type = sprite_type
		self.frame_rate = 0.1
		self.import_assets(self.sprite_type)
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(bottomleft = (pos[0], pos[1] + TILESIZE))
		self.attacking = False
		self.on_ground = False
		self.on_ceiling = False
		self.on_right = False
		self.on_left = False
		self.invincible = False

		self.obstacle_sprites = obstacle_sprites

	def import_assets(self, name):
		char_path = f'img/NPCs/{name}/'
		self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': [], 'facing': []}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = import_folder(full_path)

	def update(self):
		self.animate('loop')
		self.get_state()

