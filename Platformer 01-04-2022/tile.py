import pygame, random
from settings import *
from math import sin
from support import import_folder
from particles import Particles


class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, groups, surf = pygame.Surface((TILESIZE, TILESIZE))):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)

class VanishingBlocks(Tile):
	def __init__(self, game, pos, groups, surf):
		super().__init__(pos, groups)
		self.facing = 1
		self.game = game
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)

	def vanish_blocks(self):
		for sprite in self.game.level.vanishing_block_sprites:
			if sprite.rect.colliderect(self.game.level.player.rect):
				Particles(sprite, [self.game.level.visible_sprites, self.game.level.active_sprites], 'crumble')
				sprite.kill()
				
	def update(self):
		self.vanish_blocks()

class Platform(Tile):
	def __init__(self, game, pos, groups, surf):
		super().__init__(pos, groups)
		self.facing = 1
		self.game = game
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.drop_through = False


	def input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_DOWN]:
			self.drop_through = True

	def platform_collision(self):
		if self.drop_through == False:
			if self.game.level.player.rect.colliderect(self.rect) and self.game.level.player.rect.bottom < self.rect.top + 26 and self.game.level.player.vel.y > 0:
				self.game.level.player.rect.bottom = self.rect.top
				self.game.level.player.vel.y = 0 
				self.game.level.player.on_ground = True
				self.game.level.player.on_wall = False

		else:
			collided = self.game.level.player.rect.colliderect(self.rect)
			if not collided:
				self.drop_through = False
				

	def update(self):
		self.input()
		self.platform_collision()

class AnimatedTile(Tile):
	def __init__(self, pos, groups, path):
		super().__init__(pos, groups)

		#self.sprite_type = sprite_type
		self.frames = import_folder(path)
		self.frame_index = 0
		self.frame_rate = 0.15
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)

	def animate(self, animation_type):
		if animation_type == 'loop':
			self.frame_index += self.frame_rate
			if self.frame_index >= len(self.frames):
				self.frame_index = 0
		if animation_type == 'kill':
			self.frame_index += self.frame_rate
			if self.frame_index >= len(self.frames) -1:
				self.kill()
		self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.animate('loop')

class SavePoint(AnimatedTile):
	def __init__(self, pos, groups, path):
		super().__init__(pos, groups, path)

		self.frames = import_folder(path)
		self.surf = pygame.display.get_surface()
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)

	def update(self):
		self.animate('loop')

class Elevator(AnimatedTile):
	def __init__(self, game, pos, groups, path):
		super().__init__(pos, groups, path)

		self.game = game
		self.path = path
		self.frames = import_folder(path)
		self.frame_index = 0
		self.frame_rate = 0.05
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-124,0)
		self.vel = pygame.math.Vector2()


	def collision(self):
		on_elevator = self.game.level.player.rect.colliderect(self.hitbox)
		if on_elevator and self.game.level.player.rect.bottom < self.rect.bottom + 12 \
		and self.game.level.player.rect.bottom > self.rect.bottom - 12 \
		 and self.game.level.player.vel.y > 0:
			self.game.level.player.rect.bottom = self.rect.bottom - 12
			self.game.level.player.vel.y = 0
			self.game.level.player.on_elevator = True
			self.game.level.player.on_ground = True
		elif not on_elevator:
			self.game.level.player.on_elevator = False
			
		if not self.game.level.player.run_in:
			if self.path == 'img/elevators/up':
				if self.game.level.player.on_elevator and self.game.actions['up'] and self.game.level.player.vel.x == 0:
					self.game.level.player.going_up = True
					self.vel.y = -3
			
			if self.path == 'img/elevators/down':
				if self.game.level.player.on_elevator and self.game.actions['down'] and self.game.level.player.vel.x == 0:
					self.game.level.player.going_down = True
					self.vel.y = 3

	def update(self):
		self.collision()
		self.animate('loop')
		self.rect.y += self.vel.y

class Exit(AnimatedTile):
	def __init__(self, pos, groups, path, number):
		super().__init__(pos, groups, path)

		self.number = number
		self.surf = pygame.display.get_surface()
	
	def animate(self):
		self.frame_index += 0.2
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		right_img = self.frames[int(self.frame_index)]
		if self.rect.centerx < self.surf.get_width() // 2:
			self.image = right_img
		else:
			left_img = pygame.transform.flip(right_img, True, False)
			self.image = left_img


	def update(self):
		self.animate()

class Entity(pygame.sprite.Sprite):
	def __init__(self,groups):
		super().__init__(groups)

	def animate(self, animation_type):
		animation = self.animations[self.state]

		self.frame_index += self.frame_rate
		if animation_type == 'kill':
			if self.frame_index >= len(animation)-1:
				self.kill()

		if animation_type == 'loop':
			if self.frame_index >= len(animation):
				self.frame_index = 0

		right_img = animation[int(self.frame_index)]
		if self.facing == 1:
			self.image = right_img
		else:
			left_img = pygame.transform.flip(right_img, True, False)
			self.image = left_img

class Character(Entity):
	def __init__(self, groups):
		super().__init__(groups)

		self.current_x = 0
		self.alive = True
		self.state = 'idle'
		self.facing = 1
		self.frame_index = 0
		self.frame_rate = 0.2

		self.vel = pygame.math.Vector2()

	def animate(self, animation_type):
		animation = self.animations[self.state]

		self.frame_index += self.frame_rate
		if animation_type == 'kill':
			if self.frame_index >= len(animation)-1:
				self.kill()

		if animation_type == 'loop':
			if self.frame_index >= len(animation):
				self.frame_index = 0

		right_img = animation[int(self.frame_index)]
		if self.facing == 1:
			self.image = right_img
		else:
			left_img = pygame.transform.flip(right_img, True, False)
			self.image = left_img

		if self.on_ground and self.on_right:
			self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
		elif self.on_ground and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
		elif self.on_ground:
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		elif self.on_ceiling and self.on_right:
			self.rect = self.image.get_rect(topright = self.rect.topright)
		elif self.on_ceiling and self.on_left:
			self.rect = self.image.get_rect(topleft = self.rect.topleft)
		elif self.on_ceiling:
			self.rect = self.image.get_rect(midtop = self.rect.midtop)

		if self.invincible:
			alpha = self.wave_func()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)
	
	def wave_func(self):
		value = sin(pygame.time.get_ticks())
		if value >= 0: return 255
		else: return 0

	def gravity(self):
		self.vel.y += 0.8
		self.rect.y += self.vel.y
		if self.vel.y > TERMINAL_VELOCITY:
			self.vel.y = TERMINAL_VELOCITY

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


	def get_state(self):
		if self.alive:
			if self.attacking:
				self.state = 'attack'
			elif self.vel.y < 0:
				self.state = 'jump'
			elif self.vel.y > 1:
				self.state = 'fall'
			else:
				if self.vel.x != 0:
					self.state = 'run' 
				else:
					self.state = 'idle'
		else:
			self.state = 'death'

class Melee(Entity):
	def __init__(self, game, groups, surf):
		super().__init__(groups)
	
		self.random_animations = random.choice(['swipe', 'swipe2'])
		self.import_assets(self.random_animations)

		self.game = game
		self.sword_collided = False
		self.vel = pygame.math.Vector2()
		self.vel.x = self.game.level.player.vel.x
		self.facing = self.game.level.player.facing
		self.state = 'sword'
		self.frame_index = 0
		self.frame_rate = 0.3
		
		self.image = self.animations['sword'][self.frame_index]
		self.rect = self.image.get_rect(center = self.game.level.player.rect.center)

	def import_assets(self, name):
		char_path = f'img/{name}/'
		self.animations = {'sword': []}

		for animation in self.animations.keys():
			full_path = char_path + animation
			self.animations[animation] = import_folder(full_path)

	def enemy_hit(self):
		for enemy in self.game.level.enemy_sprites:
			if enemy.rect.colliderect(self.rect):
				if not enemy.invincible:
					self.game.level.bullet_hit_enemy = True
					enemy.health -= 25
					enemy.invincible = True
					enemy.invincibility_timer = 0
				if enemy.health <= 0:
					Particles(enemy, [self.game.level.visible_sprites, self.game.level.active_sprites], enemy.sprite_type)
					enemy.alive = False
					enemy.kill()
				print(enemy.health)

	
	def update(self):
		self.enemy_hit()
		if self.facing == 1:
			self.rect = self.image.get_rect(midleft = self.game.level.player.rect.midleft)
		else:
			self.image = pygame.transform.flip(self.image, True, False)
			self.rect = self.image.get_rect(midright = self.game.level.player.rect.midright)

		self.animate('kill')

class Crate(Entity):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)

		self.game = game
		self.vel = pygame.math.Vector2()
		self.image = pygame.image.load(f'img/tiles/{surf}.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE *1.5, self.image.get_height() * SCALE *1.5))
		self.rect = self.image.get_rect(topleft = pos)

	def x_collisions(self):
		for sprite in self.game.level.moveable_block_sprites.sprites():
			if sprite.rect.colliderect(self.game.level.player.rect):
				if self.game.level.player.vel.x > 0  and self.game.level.player.rect.right < sprite.rect.centerx:
					sprite.rect.left = self.game.level.player.rect.right
				
				if self.game.level.player.vel.x < 0 and self.game.level.player.rect.left > sprite.rect.centerx:
					sprite.rect.right = self.game.level.player.rect.left
			
		# pushing block collisions
		for sprite in self.game.level.obstacle_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.game.level.player.vel.x > 0:
					self.game.level.player.vel.x = 0
					self.rect.right = sprite.rect.left
					self.game.level.player.rect.right = self.rect.left

				elif self.game.level.player.vel.x < 0:
					self.game.level.player.vel.x = 0
					self.rect.left = sprite.rect.right
					self.game.level.player.rect.left = self.rect.right

	def y_collisions(self):
		for sprite in self.game.level.moveable_block_sprites.sprites():
			if sprite.rect.colliderect(self.game.level.player.rect):
				if self.game.level.player.vel.y > 0:
					self.game.level.player.rect.bottom = sprite.rect.top
					self.game.level.player.vel.y = 0
					self.game.level.player.on_ground = True
				if self.game.level.player.vel.y < 0:
					self.game.level.player.rect.top = sprite.rect.bottom
					self.game.level.player.vel.y = 0

		for sprite in self.game.level.obstacle_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if self.vel.y > 0:
					self.rect.bottom = sprite.rect.top
					self.vel.y = 0
				elif self.vel.y < 0:
					self.rect.top = sprite.rect.bottom
					self.vel.y = 0

	def gravity(self):
		self.vel.y += 0.8
		self.rect.y += self.vel.y
		if self.vel.y > TERMINAL_VELOCITY:
			self.vel.y = TERMINAL_VELOCITY

	def update(self):
		self.x_collisions()
		self.gravity()
		self.y_collisions()
		self.rect.x += self.vel.x

class Gun(Entity):
	def __init__(self, player, groups, surf):
		super().__init__(groups)

		self.player = player
		self.image = pygame.image.load(list(gun_data.values())[self.player.gun]['gun_img']).convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE, self.image.get_height() * SCALE))
		self.right_image = self.image
		self.left_image = pygame.transform.flip(self.image, True, False)
		self.rect = self.image.get_rect(center = self.player.rect.center)
		self.facing = player.facing

		
	def update(self):
		if not self.player.gun_showing:
			self.kill()
		if self.player.facing == 1:
			self.image = self.right_image
			self.rect = self.image.get_rect(midleft = (self.player.rect.centerx - 4, self.player.rect.centery - 4))
		else:
			self.image = self.left_image
			self.rect = self.image.get_rect(midright = (self.player.rect.centerx + 4, self.player.rect.centery - 4))
	
class Bullet(Entity):
	def __init__(self, game, sprite_type, gun_index, gun_data_type, groups, obstacle_sprites):
		super().__init__(groups)

		self.game = game
		self.gun_data_type = gun_data_type
		self.image = pygame.image.load(list(self.gun_data_type.values())[gun_index]['img']).convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE, self.image.get_height() * SCALE))
		self.right_image = self.image
		self.left_image = pygame.transform.flip(self.image, True, False)
		self.rect = self.image.get_rect(center = sprite_type.rect.center)
		self.sfx = list(self.gun_data_type.values())[gun_index]['sfx']
		self.speed = list(self.gun_data_type.values())[gun_index]['bullet_speed']
		self.damage = list(self.gun_data_type.values())[gun_index]['damage']
		self.bullet_hit_enemy = False

		self.facing = sprite_type.facing

		if self.facing == 1:
			self.image = self.right_image
			self.rect = self.image.get_rect(midleft = (sprite_type.rect.centerx + 32, sprite_type.rect.centery - 8))
		else:
			self.image = self.left_image
			self.rect = self.image.get_rect(midright = (sprite_type.rect.centerx - 32, sprite_type.rect.centery - 8))

		self.obstacle_sprites = obstacle_sprites

	def bullet_speed(self):
		if self.facing == 1:
			self.rect.x += self.speed
		else:
			self.rect.x -= self.speed

	def collisions(self):
		for sprite in self.game.level.obstacle_sprites:
			if sprite.rect.colliderect(self.rect):
				Particles(self, [self.game.level.visible_sprites, self.game.level.active_sprites], 'flash')
				self.kill()

		for sprite in self.game.level.moveable_block_sprites: 
			if sprite.rect.colliderect(self.rect):
				Particles(self, [self.game.level.visible_sprites, self.game.level.active_sprites], 'flash')
				self.kill()

		for sprite in self.game.level.vanishing_block_sprites: 
			if sprite.rect.colliderect(self.rect):
				Particles(self, [self.game.level.visible_sprites, self.game.level.active_sprites], 'flash')
				self.kill()

	def enemy_hit(self):
		for enemy in self.game.level.enemy_sprites:
			if enemy.rect.colliderect(self.rect):
				self.game.level.bullet_hit_enemy = True
				Particles(self, [self.game.level.visible_sprites, self.game.level.active_sprites], 'flash')
				if enemy.health >= 0:
					enemy.health -= self.damage
				self.kill()
				if enemy.health <= 0:
					Particles(enemy, [self.game.level.visible_sprites, self.game.level.active_sprites], enemy.sprite_type)
					enemy.alive = False
					enemy.kill()

				print(enemy.alive)

	def player_hit(self):
		if self.game.level.player.alive:
			for sprite in self.game.level.bullet_sprites:
				if sprite.rect.colliderect(self.game.level.player):
					Particles(self.game.level.player, [self.game.level.visible_sprites, self.game.level.active_sprites], 'flash')
					if self.game.current_health >= 0:
						self.game.current_health -= self.damage
					sprite.kill()
					if self.game.current_health <= 0:
						self.game.current_health = 0
						Particles(self.game.level.player, [self.game.level.visible_sprites, self.game.level.active_sprites], 'player')
						self.game.level.player.alive = False
						self.game.level.player.kill()
						if self.game.level.player.gun_showing:
							self.game.level.gun_sprite.kill()			
				
	def update(self):
		self.player_hit()
		self.enemy_hit()
		self.collisions()
		self.bullet_speed()

class Pickup(AnimatedTile):
	def __init__(self, pos, groups, path, index, name):
		super().__init__(pos, groups, path)

		self.facing = 1
		self.index = index
		self.name = name

class LiquidTile(AnimatedTile):
	def __init__(self, pos, groups, path):
		super().__init__(pos, groups)

		






		


	
		
		

		





		


