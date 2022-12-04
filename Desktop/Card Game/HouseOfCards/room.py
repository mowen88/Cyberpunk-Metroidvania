import pygame, os, csv
from state import State
from player import Player, NPC
from tile import Tile, Coin, Platform, TrickPlatform, MovingPlatform, AnimatedTile, Interact, CollisionTile, Spike, CutsceneCollider, \
Lever, LeverRocker, Attack, Yoyo, Exit
from ui import UI
from map import Map
from camera import Camera
from dialogue import Dialogue
from cutscene import Cutscene
from enemies import WalkingEnemy, LungingEnemy, FlyingEnemy

class Room(State):
	def __init__(self, game):
		State.__init__(self, game)

		# #get size (length and width) of room in pixels
		# with open(f'room_map/room_blocks.csv', newline='') as csvfile:
		#     reader = csv.reader(csvfile, delimiter=',')
		#     for row in reader:
		#         rows = (sum (1 for row in reader) + 1)
		#         cols = len(row)
		# self.room_length = cols * self.game.TILESIZE 
		# self.room_height = rows * self.game.TILESIZE
		
		self.visible_sprites = Camera(self.game, self)
		self.active_sprites = pygame.sprite.Group()
		self.obstacle_sprites = pygame.sprite.Group()
		self.display_surf = pygame.display.get_surface()
		self.npc = None
		self.target = None

		self.exit_cooldown = 0
		self.entry_cooldown = 600
		self.exiting_area = False
		self.entering_area = True

		self.fade_surf = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		self.fade_surf.fill(self.game.BLACK)

		self.cutscene_running = False
		self.dialog_running = False
		self.npc_collided = False
		self.fade_timer = 0
		self.trigger_interact_box = True
		self.lever_on = False

		self.platform_sprites = pygame.sprite.Group()
		self.moving_platform_sprites = pygame.sprite.Group()
		self.collision_tile_sprites = pygame.sprite.Group()
		self.npc_sprites = pygame.sprite.Group()
		self.cutscene_sprites = pygame.sprite.Group()
		self.spike_sprites = pygame.sprite.Group()
		self.enemy_sprites = pygame.sprite.Group()
		self.exit_sprites = pygame.sprite.Group()
		self.interact_box_sprites = pygame.sprite.Group()

		self.coin_sprites = pygame.sprite.Group()

		self.attack_sprite = pygame.sprite.GroupSingle()
		self.yoyo_sprite = pygame.sprite.GroupSingle()
		self.lever_sprites = pygame.sprite.Group()
		
		self.create_map()

		self.ui = UI(self.game)

		#stop certain sprite being created when room loads
		self.create_attack()
		self.attack_sprite.kill()
		self.create_yoyo()
		self.yoyo_sprite.kill()

	def create_map(self):
		layouts = {
		'blocks':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_blocks.csv'),
		'collisions':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_collisions.csv'),
		'NPCs':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_NPCs.csv'),
		'cutscenes':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_cutscenes.csv'),
		'hazards':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_hazards.csv'),
		'enemies':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_enemies.csv'),
		'exits':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_exits.csv'),
		'entries':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_entries.csv'),
		'platforms':self.game.import_csv(f'rooms/{self.game.current_room}/{self.game.current_room}_platforms.csv')
		}

		images = {
		'blocks':self.game.import_folder(f'img/tiles/blocks')
		}
		for style, layout in layouts.items():
			for row_index, row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * self.game.TILESIZE
						y = row_index * self.game.TILESIZE

						if style == 'blocks':
							surf = images['blocks'][int(col)]
							Tile(self.game, (x,y), [self.visible_sprites, self.obstacle_sprites], surf)

						if style == 'collisions':
							surf = images['blocks'][int(col)]
							sprite = CollisionTile(self.game, (x,y), [], surf)
							self.collision_tile_sprites.add(sprite)

						if style == 'entries':
							if col == str(self.game.spawn_point):
								self.player = Player(self.game, self, 'player', (x, y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites)
								self.target = self.player
								if self.target.hitbox.centerx > self.visible_sprites.room_size[0] * 0.5:
									self.target.facing = -1

						if style == 'exits':
							exit_number = int(col)
							sprite = Exit(self.game, (x,y-self.game.TILESIZE), [self.visible_sprites, self.active_sprites], 'img/tiles/exit/00.png', exit_number)
							self.exit_sprites.add(sprite)
						
						if style == 'NPCs':
							npc_number = int(col)
							npc_number = NPC(self.game, self, npc_number, (x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites)
							self.npc_sprites.add(npc_number)
							
						if style == 'cutscenes':
							cutscene_number = f'cutscene_{int(col)}'
							cutscene_number = CutsceneCollider(self.game, (x,y), [], int(col))
							self.cutscene_sprites.add(cutscene_number)


						if style == 'hazards':
							surf = images['blocks'][int(col)]
							self.spike = Spike(self.game, (x,y), [self.visible_sprites], surf)
							self.spike_sprites.add(self.spike)

						if style == 'platforms':
							if col == '0':
								sprite = Platform(self.game, self, (x, y), [self.visible_sprites, self.active_sprites], 'img/platform0.png')
								self.platform_sprites.add(sprite)
	
							if col == '1':
								sprite = TrickPlatform(self.game, self, (x, y), [self.visible_sprites, self.active_sprites], 'img/trick_platform')
								self.platform_sprites.add(sprite)

							if col == '2':
								sprite = Lever(self.game, self, (x, y+15), [self.visible_sprites, self.active_sprites], 'img/lever.png')
								LeverRocker(self.game, (x - 11,y), [self.visible_sprites], 'img/lever_rocker.png')
								self.lever_sprites.add(sprite)

							if col == '3':
								sprite = MovingPlatform(self.game, self, (x, y), [self.visible_sprites, self.active_sprites], 'img/platform0.png', 'left_right')
								self.moving_platform_sprites.add(sprite)
							if col == '4':
								sprite = MovingPlatform(self.game, self, (x, y), [self.visible_sprites, self.active_sprites], 'img/platform0.png', 'left_right')
								self.moving_platform_sprites.add(sprite)
							if col == '5':
								sprite = MovingPlatform(self.game, self, (x, y), [self.visible_sprites, self.active_sprites], 'img/platform0.png', 'down_up')
								self.moving_platform_sprites.add(sprite)

							
	

						if style == 'enemies':
							if col == '0':
								self.enemy_red = FlyingEnemy(self.game, self, 'enemy', (x, y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites)
								self.enemy_sprites.add(self.enemy_red)

							if col == '1':
								self.walking_enemy = WalkingEnemy(self.game, self, 'club_guard', (x, y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites)
								self.enemy_sprites.add(self.walking_enemy)
							if col == '2':
								self.lunging_enemy = LungingEnemy(self.game, self, 'club_guard', (x, y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites)
								self.enemy_sprites.add(self.lunging_enemy)

						
	def exit_area(self):
		for sprite in self.exit_sprites:
			if sprite.hitbox.colliderect(self.player.hitbox):
				self.exiting_area = True
				self.game.current_room = self.game.room_dict[self.game.current_room][sprite.number]
				self.game.spawn_point = sprite.number

	def collide_npc_dialog(self):
		for sprite in self.npc_sprites:
			if sprite.hitbox.colliderect(self.player.hitbox):
				self.npc_collided = True
				dialog = self.game.dialog_dict[sprite.char]
				if self.game.actions['space'] and not self.dialog_running:
					self.dialog_running = True	
					new_state = Dialogue(self.game, self, sprite.char, dialog)
					new_state.enter_state()
			else:
			 	self.npc_collided = False

	def collide_npc_render_box(self):
		for sprite in self.npc_sprites:
			collided = pygame.sprite.spritecollide(self.target, self.npc_sprites, False)
			if collided and not self.dialog_running and not self.cutscene_running:
				if sprite.hitbox.colliderect(self.player.hitbox): 
				
					if self.trigger_interact_box:
						self.create_interact_box((sprite.hitbox.centerx, sprite.hitbox.centery - sprite.hitbox.height * 1.5))
						self.trigger_interact_box = False
					self.fade_timer += 255/20
					if self.fade_timer >= 255:
						self.fade_timer = 255

			else:
				self.fade_timer -= 255/50
				if self.fade_timer <= 0:
					self.fade_timer = 0
					self.trigger_interact_box = True
					for box in self.interact_box_sprites:
						box.kill()

		for i in self.interact_box_sprites:
			i.image.set_alpha(self.fade_timer)

	def reduce_health(self, amount):
		if not self.target.invincible:
			self.game.current_health -= amount
			if self.game.current_health <= 0:
				self.target.alive = False
				self.target.die()

	def enemy_hit_logic(self):
		for enemy in self.enemy_sprites:
			if enemy.hitbox.colliderect(self.attack_sprite) and enemy.alive and self.target.attacking\
			or enemy.hitbox.colliderect(self.yoyo_sprite) and enemy.alive and self.target.yoyoing:
				if not enemy.invincible and enemy.alive:
					enemy.invincible = True
					enemy.health -= 1
					if enemy.health <= 0:
						for i in range(enemy.coins_given):
							coin = Coin(self.game, self, enemy.rect.center, [self.visible_sprites, self.active_sprites], 'img/items/coin/')
							self.coin_sprites.add(coin)
						enemy.alive = False
						enemy.die()

	def respawn(self):
		if self.player.alpha <= 0 and not self.player.alive:
			#self.game.current_health = self.game.max_health
			#self.game.current_room = 0
			new_state = Room(self.game)
			new_state.enter_state()


	def cutscene(self):
		for sprite in self.cutscene_sprites:
			if sprite.rect.colliderect(self.player) and sprite.number not in self.game.cutscenes_completed:
				sprite.kill()
				self.cutscene_running = True
				new_state = Cutscene(self.game, self, sprite.number)
				new_state.enter_state()


	def create_interact_box(self, pos):
		self.interact_box = Interact(self.game, self, (pos), [self.visible_sprites, self.active_sprites])
		self.interact_box_sprites.add(self.interact_box)

	def create_attack(self):
		self.attack_sprite = Attack(self.game, self, self.player, (self.player.hitbox.center), [self.visible_sprites, self.active_sprites], 'img/card.png')

	def create_yoyo(self):
		self.yoyo_sprite = Yoyo(self.game, self, self.player, (self.player.hitbox.center), [self.visible_sprites, self.active_sprites], 'img/card.png')

	def create_yoyo_line(self):
		if self.player.yoyoing:
			pygame.draw.line(self.display_surf, ((self.game.BLACK)), (self.player.hitbox.centerx - self.visible_sprites.offset[0], self.player.hitbox.centery - self.visible_sprites.offset[1]), \
			(self.yoyo_sprite.rect.centerx - self.visible_sprites.offset[0], self.yoyo_sprite.rect.centery - self.visible_sprites.offset[1]), 2)

	def run_new_area(self):
		if self.exit_cooldown >= 255:
			new_state = Room(self.game)
			new_state.enter_state()
			
	def run_fade(self):
		if self.exiting_area:
			self.player.speed = 0
			self.exit_cooldown += 255/self.game.room_transition_speed
			self.fade_surf.set_alpha(self.exit_cooldown)
			self.display_surf.blit(self.fade_surf, (0,0))

		elif self.entering_area:
			self.entry_cooldown -= 255/self.game.room_transition_speed
			if self.entry_cooldown <= 0:
				self.entry_cooldown = 0
				self.entering_area = False

			self.fade_surf.set_alpha(self.entry_cooldown)
			self.display_surf.blit(self.fade_surf, (0,0))
		
	def update(self, actions):
		self.active_sprites.update()
		if not self.cutscene_running and not self.dialog_running and self.entry_cooldown < 100:
			self.target.input()
		self.collide_npc_dialog()
		self.respawn()
		self.cutscene()
		self.exit_area()
		self.run_new_area()
		self.enemy_hit_logic()


	def render(self, display):
		self.visible_sprites.offset_draw(self.target.rect.center)
		#self.create_yoyo_line()
		self.collide_npc_render_box()
		self.ui.render()
		self.run_fade()	
		# top debug messages
		self.game.draw_text(self.display_surf, str(self.player.on_platform), ((255,255,255)), 100, (self.game.screen.get_width()*0.33,140))
		self.game.draw_text(display, str(self.player.vel), ((255,255,255)), 100, (self.game.screen.get_width()*0.66,140))
		self.game.draw_text(display, str(self.player.cyote_timer), ((255,255,255)), 100, (self.game.screen.get_width()*0.5,140))