import pygame, csv, json
from tile import Tile, VanishingBlocks, Platform, Elevator, AnimatedTile, Exit, Melee, Bullet, Crate, Gun, Pickup, SavePoint
from settings import *
from camera import LayerCameraGroup
from player import Player
from enemies import NPC, Guard, ArmedGuard
from support import import_csv, import_folder
from pause import Pause, PickupPause, DialogueBox, LevelIntro, Transition
from map import Map
from particles import Particles

class Level:
	def __init__(self, game, current_level, entry_pos, new_block_position, current_gun, gun_showing, surf, create_level, update_neobits, update_health):

		self.game_paused = False
		self.map_showing = False
		self.pickup_pause = False
		self.collided_save = False
		self.death_restart_timer = 0
		self.gun_list = []
		self.offset = 60

		# setup level
		self.game = game
		self.new_block_position = new_block_position
		self.current_gun = current_gun
		self.gun_showing = gun_showing
		self.entry_pos = entry_pos
		self.display_surf = surf
		self.current_level = current_level
		self.create_level = create_level
		self.update_neobits = update_neobits
		self.update_health = update_health
		self.current_level = current_level
		self.timer = 0
		self.player_grounded = False
		self.pickup_timer = 0
		self.pickup_name = None
		self.bullet_hit_enemy = False
		if self.current_level not in list(levels_visited.keys()):
			levels_visited.update({str(self.current_level): True})

		#get size (length and width) of level in pixels
		with open(f'levels/{self.current_level}/level_{self.current_level}_blocks.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		self.level_length = cols * TILESIZE 
		self.level_height = rows * TILESIZE

		# main sprite groups
		self.visible_sprites = LayerCameraGroup(self.game, self.current_level, self.level_length, self.level_height)
		self.active_sprites = pygame.sprite.Group()
		self.obstacle_sprites = pygame.sprite.Group()
		self.NPC_sprites = pygame.sprite.Group()
		self.enemy_sprites = pygame.sprite.Group()
		self.collidable_enemy_sprites = pygame.sprite.Group()
		self.second_layer_sprites = pygame.sprite.Group()

		#upgrades
		self.pickup_sprites = pygame.sprite.Group()
		self.cost_pickup_sprites = pygame.sprite.Group()
		self.collectible_sprites = pygame.sprite.Group()
		self.collision_block_sprites = pygame.sprite.Group()
	
		# moveable blocks
		self.moveable_block_sprites = pygame.sprite.Group()
		self.block_position = self.new_block_position

		# static blocks
		self.vanishing_block_sprites = pygame.sprite.Group()
		self.liquid_sprites = pygame.sprite.Group()

		#exit doors
		self.exit_sprites = pygame.sprite.Group()
		self.save_sprites = pygame.sprite.GroupSingle()

		# elevator
		self.elevator_sprite = pygame.sprite.Group()
		self.platform_sprites = pygame.sprite.Group()

		# weapon sprites
		self.melee_attack = pygame.sprite.GroupSingle()
		self.gun_sprite = pygame.sprite.GroupSingle()
		self.bullet_sprites = pygame.sprite.Group()

		# pause moments
		self.transition = Transition(self.game, self.display_surf)
		self.pause = Pause(self.game, 'Paused', 'Press ESC to go to main menu', self.display_surf)
		self.intro_text = LevelIntro(self.current_level,(levels[self.current_level]['level_name']), self.display_surf)
		self.map = Map(self.game, self.current_level, self.level_length, self.level_height, self.display_surf)

		self.create_map()
		
	def create_map(self):

		layouts = {
		'blocks':import_csv(f'levels/{self.current_level}/level_{self.current_level}_blocks.csv'),
		'collision_blocks':import_csv(f'levels/{self.current_level}/level_{self.current_level}_collision_blocks.csv'),
		'pickups':import_csv(f'levels/{self.current_level}/level_{self.current_level}_pickups.csv'),
		'collectibles':import_csv(f'levels/{self.current_level}/level_{self.current_level}_collectibles.csv'),
		'enemies':import_csv(f'levels/{self.current_level}/level_{self.current_level}_enemies.csv'),
		'NPCs':import_csv(f'levels/{self.current_level}/level_{self.current_level}_NPCs.csv'),
		'entrances':import_csv(f'levels/{self.current_level}/level_{self.current_level}_entrances.csv'),
		'exits':import_csv(f'levels/{self.current_level}/level_{self.current_level}_exits.csv'),
		'save':import_csv(f'levels/{self.current_level}/level_{self.current_level}_save.csv'),
		'vanishing_blocks':import_csv(f'levels/{self.current_level}/level_{self.current_level}_vanishing_blocks.csv'),
		'elevator':import_csv(f'levels/{self.current_level}/level_{self.current_level}_elevator.csv'),
		'liquid':import_csv(f'levels/{self.current_level}/level_{self.current_level}_liquid.csv'),
		'platform':import_csv(f'levels/{self.current_level}/level_{self.current_level}_platform.csv')
		}

		images = {
		'blocks':import_folder(f'img/tiles/blocks')
		}

		for style, layout in layouts.items():
			for row_index, row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE

						if style == 'blocks':
							surf = images['blocks'][int(col)]
							Tile((x,y), [self.visible_sprites, self.obstacle_sprites], surf)

						if style == 'collision_blocks':
							surf = images['blocks'][int(col)]
							sprite = Tile((x,y), [], surf)
							self.collision_block_sprites.add(sprite)

						if style == 'vanishing_blocks':
							surf = images['blocks'][int(col)]
							sprite = VanishingBlocks(self.game, (x,y), [self.visible_sprites, self.active_sprites], surf)
							self.vanishing_block_sprites.add(sprite)

						if style == 'platform':
							surf = images['blocks'][int(col)]
							sprite = Platform(self.game, (x,y), [self.visible_sprites, self.active_sprites], surf)
							self.platform_sprites.add(sprite)
							self.second_layer_sprites.add(sprite)

						if style == 'pickups':
							if col == '0' and '0' not in list(gun_data.keys()): 
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/blaster', {'0':{'bullet_speed': 10, 'cooldown': 300, 'damage': 20, 'img':'img/bullets/bullet_0.png', 'gun_img':'img/weapons/gun_sprites/blaster.png', 'sfx':'audio/sfx/blaster.wav'}}, 'Blaster')
								self.pickup_sprites.add(sprite)
							elif col == '1' and '1' not in list(gun_data.keys()): 
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/hyper_blaster', {'1':{'bullet_speed': 20, 'cooldown': 100, 'damage': 15, 'img':'img/bullets/bullet_2.png', 'gun_img':'img/weapons/gun_sprites/hyper_blaster.png', 'sfx':'audio/sfx/blaster.wav'}}, 'Hyper Blaster')
								self.pickup_sprites.add(sprite)
							elif col == '2' and '2' not in list(gun_data.keys()): 
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/railgun', {'2':{'bullet_speed': 40, 'cooldown': 500, 'damage': 50, 'img':'img/bullets/bullet_1.png', 'gun_img':'img/weapons/gun_sprites/railgun.png', 'sfx':'audio/sfx/railgun.wav'}}, 'Railgun')
								self.cost_pickup_sprites.add(sprite)
							elif col == '5' and 'double_jump' not in list(pickup_data.keys()):  
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/jump_boots', None, 'Jump Boots')
								self.pickup_sprites.add(sprite)
							elif col == '6' and 'hovering' not in list(pickup_data.keys()): 
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/jetpack', None, 'Jetpack')
								self.pickup_sprites.add(sprite)
							elif col == '7' and 'wall_jump' not in list(pickup_data.keys()):
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/magnaglove', None, 'Magnaglove')
								self.pickup_sprites.add(sprite)
							elif col == '8' and 'dash' not in list(pickup_data.keys()):
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/warp_core', None, 'Warp Core')
								self.pickup_sprites.add(sprite)
							elif col == '9' and 'can_swim' not in list(pickup_data.keys()): 
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/envirosuit', None, 'Envirosuit')
								self.pickup_sprites.add(sprite)
							elif col == '14' and 'tracker' not in list(pickup_data.keys()): 
								sprite = Pickup((x,y), [self.visible_sprites, self.active_sprites], 'img/pickups/tracker', None, 'Tracker')
								self.pickup_sprites.add(sprite)

						if style == 'liquid':
							if col == '0':
								sprite = AnimatedTile((x, y), [self.visible_sprites, self.active_sprites], 'img/tiles/acid_top')
								self.liquid_sprites.add(sprite)
							if col == '1':
								sprite = AnimatedTile((x, y), [self.visible_sprites, self.active_sprites], 'img/tiles/acid')
								self.liquid_sprites.add(sprite)
							if col == '2':
								sprite = AnimatedTile((x, y), [self.visible_sprites, self.active_sprites], 'img/tiles/prongs_floor')
								self.liquid_sprites.add(sprite)
							if col == '3':
								sprite = AnimatedTile((x, y), [self.visible_sprites, self.active_sprites], 'img/tiles/prongs_ceiling')
								self.liquid_sprites.add(sprite)

						
						if style == 'elevator':
							if col == '0': 
								self.elevator_sprite = Elevator(self.game, (x, y - 12), [self.visible_sprites, self.active_sprites], 'img/elevators/up')
							if col == '1': 
								self.elevator_sprite = Elevator(self.game, (x, y - 12), [self.visible_sprites, self.active_sprites], 'img/elevators/down')

						if style == 'collectibles':
							if col == '3': 
								sprite = Pickup((x + (TILESIZE // 3), y + (TILESIZE // 3)), [self.visible_sprites, self.active_sprites], 'img/pickups/neobits/green_neobit', 1, 'Neobit')
								self.collectible_sprites.add(sprite)
							elif col == '4': 
								sprite = Pickup((x + (TILESIZE // 3),y + (TILESIZE // 3)), [self.visible_sprites, self.active_sprites], 'img/pickups/neobits/orange_neobit', 3, 'Neobit')
								self.collectible_sprites.add(sprite)
							elif col == '10' and '0' not in list(extra_healths_collected.keys()): 
								sprite = Pickup((x, y), [self.visible_sprites, self.active_sprites], 'img/pickups/seringe', '0', 'Extra health')
								self.collectible_sprites.add(sprite)
							elif col == '11' and '1' not in list(extra_healths_collected.keys()): 
								sprite = Pickup((x, y), [self.visible_sprites, self.active_sprites], 'img/pickups/seringe', '1', 'Extra health')
								self.collectible_sprites.add(sprite)
							elif col == '12' and '2' not in list(extra_healths_collected.keys()): 
								sprite = Pickup((x, y), [self.visible_sprites, self.active_sprites], 'img/pickups/seringe', '2', 'Extra health')
								self.collectible_sprites.add(sprite)
							elif col == '13' and '3' not in list(extra_healths_collected.keys()): 
								sprite = Pickup((x, y), [self.visible_sprites, self.active_sprites], 'img/pickups/seringe', '3', 'Extra health')
								self.collectible_sprites.add(sprite)

						if style == 'NPCs':
							if col == '0': 
									sprite = NPC((x - (TILESIZE // 2),y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC0')
									self.NPC_sprites.add(sprite)
							if col == '1': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC1')
									self.NPC_sprites.add(sprite)
							if col == '2': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC2')
									self.NPC_sprites.add(sprite)
							if col == '10': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC2')
									self.NPC_sprites.add(sprite)
							if col == '11': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC3')
									self.NPC_sprites.add(sprite)
							if col == '12': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC4')
									self.NPC_sprites.add(sprite)
							if col == '13': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC5')
									self.NPC_sprites.add(sprite)
							if col == '14': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC6')
									self.NPC_sprites.add(sprite)
							if col == '15': 
									sprite = NPC((x - (TILESIZE // 2),y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC7')
									self.NPC_sprites.add(sprite)
							if col == '16': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC8')
									self.NPC_sprites.add(sprite)
									self.second_layer_sprites.add(sprite)
							if col == '17': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC9')
									self.NPC_sprites.add(sprite)
							if col == '18': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC10')
									self.NPC_sprites.add(sprite)
							if col == '19': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC11')
									self.NPC_sprites.add(sprite)
							if col == '20': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC12')
									self.NPC_sprites.add(sprite)
							if col == '21': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC13')
									self.NPC_sprites.add(sprite)
							if col == '22': 
									sprite = NPC((x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'NPC14')
									self.NPC_sprites.add(sprite)

						if style == 'enemies':
							if col == '0': 
								sprite = ArmedGuard(self.game, (x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'guard', 0, 50)
								self.enemy_sprites.add(sprite)
							if col == '1': 
								sprite = Guard(self.game, (x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'bug', 50)
								self.enemy_sprites.add(sprite)
								self.collidable_enemy_sprites.add(sprite)
							if col == '1': 
								sprite = Guard(self.game, (x,y), [self.visible_sprites, self.active_sprites], self.obstacle_sprites,'bug', 50)
								self.enemy_sprites.add(sprite)
								self.collidable_enemy_sprites.add(sprite)

						if style == 'entrances':
							if col == str(self.entry_pos):
								self.player = Player(self.game,\
									(x, y), \
									[self.visible_sprites, self.active_sprites],\
									 self.obstacle_sprites, \
									 self.create_melee, \
									 self.create_run_particles, \
									 self.create_jump_particles,\
									 self.create_dash_particles, \
									 self.create_hover_particles, \
									 self.shoot, \
									 self.current_gun, \
									 self.gun_showing)

						if style == 'save':
							sprite = SavePoint((x,y - (TILESIZE * 2)), [self.visible_sprites, self.active_sprites], 'img/tiles/save')
							self.save_sprites.add(sprite)
							self.second_layer_sprites.add(sprite)
								
						if style == 'exits':
							if col == '1': 
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 1)
								self.exit_sprites.add(sprite)
								self.second_layer_sprites.add(sprite)
							elif col == '2':
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 2)
								self.exit_sprites.add(sprite)
								self.second_layer_sprites.add(sprite)
							elif col == '3': 
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 3)
								self.exit_sprites.add(sprite)
								self.second_layer_sprites.add(sprite)
							elif col == '4': 
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 4)
								self.exit_sprites.add(sprite)
								self.second_layer_sprites.add(sprite)
							elif col == '5':
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 5)
								self.exit_sprites.add(sprite)
							elif col == '6':
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 6)
								self.exit_sprites.add(sprite)
								self.visible_sprites.remove(sprite) # 6, 7, and 8 are reserved for elevator exits so do not show the arrows on screen
							elif col == '7':
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 7)
								self.exit_sprites.add(sprite)
								self.visible_sprites.remove(sprite) # 6, 7, and 8 are reserved for elevator exits so do not show the arrows on screen
							elif col == '8':
								sprite = Exit((x,y), [self.visible_sprites, self.active_sprites], 'img/tiles/exit', 8)
								self.exit_sprites.add(sprite)
								self.visible_sprites.remove(sprite) # 6, 7, and 8 are reserved for elevator exits so do not show the arrows on screen

		# moveable blocks staying in same place when return to level
		if self.current_level == 17:
			self.moveable_block_sprite = Crate(self.game, (self.new_block_position), [self.visible_sprites, self.active_sprites], 'crate')
			self.moveable_block_sprites.add(self.moveable_block_sprite)

	# make sure the block stays in the place you left it when returning to new level
	def get_block_pos(self):
		for sprite in self.moveable_block_sprites.sprites():
			self.block_position = sprite.rect.topleft

	def create_melee(self):
		if not self.player.air_attacked:
			self.melee_attack = Melee(self.game, [self.visible_sprites, self.active_sprites], self.display_surf)
			self.game.melee_fx.play()
			self.player.air_attacked = True

	def shoot(self, gun):
		if self.player.gun_showing and self.player.alive:
				self.player_bullet = Bullet(self.game, self.player, gun, gun_data, [self.visible_sprites, self.active_sprites], self.obstacle_sprites)
				pygame.mixer.Sound(self.player_bullet.sfx).play()
				self.bullet_sprites.add(self.player_bullet)
	def gun_equipped(self):
		if gun_data and self.player.alive:
			self.gun_sprite = Gun(self.player, [self.visible_sprites, self.active_sprites], self.display_surf)

	def show_gun(self):
		if gun_data and self.player.alive:
			self.player.gun_showing = not self.player.gun_showing
			self.gun_sprite = Gun(self.player, [self.visible_sprites, self.active_sprites], self.display_surf)
			if self.player.gun_showing:
				self.game.load_fx.play()
			else:
				self.game.unload_fx.play()

	def show_new_gun(self):
		if self.player.gun_showing and gun_data:
			self.gun_sprite.kill()
			self.game.load_fx.play()
			self.gun_sprite = Gun(self.player, [self.visible_sprites, self.active_sprites], self.display_surf)

	def create_run_particles(self):
		if self.player.alive and self.player.vel.x != 0 and self.player.on_ground and not self.player.state == 'idle' and not self.player.liquid_collided\
		 and not self.player.state == 'idle_armed' and not (self.player.on_left or self.player.on_right) and not self.player.gun_showing:
			self.player.run_particle_timer += 1
		if self.player.run_particle_timer >= 20:
			Particles(self.player, [self.visible_sprites, self.active_sprites], 'run')
			self.player.run_particle_timer = 0

	def create_dash_particles(self):
		if self.player.dashing:
			self.player.dash_particle_timer += 1
		if self.player.dash_particle_timer >= 1:
			Particles(self.player, [self.visible_sprites, self.active_sprites], 'dash')
			self.player.dash_particle_timer = 0

	def create_hover_particles(self):
		if self.player.hovering:
			self.player.hover_particle_timer += 1
		if self.player.hover_particle_timer >= 20:
			Particles(self.player, [self.visible_sprites, self.active_sprites], 'hover')
			self.player.hover_particle_timer = 0

	def create_jump_particles(self, particle_type):
		if not self.player.liquid_collided:
			Particles(self.player, [self.visible_sprites, self.active_sprites], particle_type)	

	def get_player_grounded(self):
		if self.player.on_ground:
			self.player_grounded = True
		else:
			self.player_grounded = False

	def create_landing_particles(self):
		if not self.player_grounded and self.player.on_ground and not self.player.run_in and not self.player.liquid_collided:
			self.game.landing_fx.play()
			Particles(self.player, [self.visible_sprites, self.active_sprites], 'land')
								
	# this gets the data for the new level, then it is called in exit_level func below

	def exit_level(self):
		if not self.player.run_in:
			collided_exits = pygame.sprite.spritecollide(self.player, self.exit_sprites, False, pygame.sprite.collide_rect_ratio(0.6))
			if collided_exits:
				for exit in collided_exits:
					self.visible_sprites.empty()
					self.active_sprites.empty()
					self.obstacle_sprites.empty()
					self.new_block_position = self.block_position
					self.new_level = levels[self.current_level][exit.number]
					self.exit_list = list(levels[self.current_level].keys())
					self.entry_pos = self.exit_list[exit.number -1]
					self.current_gun = self.player.gun
					self.gun_showing = self.player.gun_showing
					self.create_level(self.new_level,self.entry_pos, self.new_block_position, self.current_gun, self.gun_showing)

	def elevator_message(self):
		if self.game.level.player.on_elevator and self.elevator_sprite.path == 'img/elevators/up':
			Pause(self.game, '', "Press up to ride the elevator", self.display_surf).run()
		elif self.game.level.player.on_elevator and self.elevator_sprite.path == 'img/elevators/down':
			Pause(self.game, '', "Press down to ride the elevator", self.display_surf).run()

	def save_point(self):
		self.collided_save = pygame.sprite.spritecollide(self.player, self.save_sprites, False)
		if not self.player.run_in and self.collided_save and self.game.actions['up'] and self.player.vel.x == 0:
			self.game.save_fx.play()
			self.store_save_data()
			self.pickup_pause = True
			self.player.hold = True
			self.load_point()
		elif self.collided_save and self.player.run_in:
			self.store_save_data()
		elif self.collided_save:
			Pause(self.game, 'Checkpoint', "Press up to save game", self.display_surf).run()

	def store_save_data(self):
		self.dump_data('gun_data.txt', 'gun_file', saved_gun_data, gun_data)
		saved_gun_data.update(gun_data)

		self.dump_data('pickup_data.txt', 'pickup_file', saved_pickup_data, pickup_data)
		saved_pickup_data.update(pickup_data)

		self.dump_data('map_data.txt', 'map_file', saved_levels_visited, levels_visited)
		saved_levels_visited.update(levels_visited)

		self.dump_data('extra_healths_data.txt', 'extra_healths_file', saved_extra_healths_collected, extra_healths_collected)
		saved_extra_healths_collected.update(extra_healths_collected)

		neobit_data.update({'neobits': self.game.neobits})
		self.dump_data('neobit_data.txt', 'neobit_file', neobit_data, neobit_data)

		health_data.update({'max_health': self.game.max_health})
		self.dump_data('health_data.txt', 'health_file', health_data, health_data)
		
		load_data.update({'save_point': self.current_level, 'block_position': self.new_block_position, \
		'current_gun': self.current_gun, 'gun_showing': self.gun_showing})
							
	def load_point(self):
		self.new_block_position = self.block_position
		self.current_gun = self.player.gun
		self.gun_showing = self.player.gun_showing
		gun_data.clear()
		gun_data.update(saved_gun_data)
		pickup_data.clear()
		pickup_data.update(saved_pickup_data)
		levels_visited.clear()
		levels_visited.update(saved_levels_visited)
		extra_healths_collected.clear()
		extra_healths_collected.update(saved_extra_healths_collected)
		load_data.update(load_data)
		self.create_level(load_data['save_point'], 0, load_data['block_position'], load_data['current_gun'], load_data['gun_showing'])
	
	def entry_cooldown(self):
		self.timer += 1
		if self.timer >= 60:
			self.player.run_in = False
		else:
			self.intro_text.run()
		if self.timer <= 100:
			self.transition.run()

	def collectible_collision(self):
		collided = pygame.sprite.spritecollide(self.player, self.collectible_sprites, True)
		if collided:
			for item in collided:
				if item.name == 'Neobit':
					self.game.neobit_fx.play()
					Particles(item, [self.visible_sprites, self.active_sprites], 'pickup')					
					self.update_neobits(item.index)
				elif item.name == 'Extra health':
					self.game.collect_fx.play()
					self.update_health(50, 50)
					extra_healths_collected.update({str(item.index): True})
					self.pickup_pause = True
					self.player.hold = True
					self.pickup_message(item.name)

	def pickup_collision(self):
		collided_pickups = pygame.sprite.spritecollide(self.player, self.pickup_sprites, True, pygame.sprite.collide_rect_ratio(0.6))
		if collided_pickups:
			self.game.collect_fx.play()
			try: 
				del(self.pickup_message) # gets rid of bug where a previous pickup message is still showing and you hit another pickup immediately after
			except:
				pass
			finally:
				for pickup in collided_pickups:
					if pickup.name == 'Blaster' or pickup.name == 'Hyper Blaster':
						gun_data.update(pickup.index)
					elif pickup.name == 'Magnaglove':
						pickup_data.update({'wall_jump': True})
					elif pickup.name == 'Warp Core':
						pickup_data.update({'dash': True})
					elif pickup.name == 'Jump Boots':
						pickup_data.update({'double_jump': True})
					elif pickup.name == 'Jetpack':	
						pickup_data.update({'hovering': True})
					elif pickup.name == 'Envirosuit':	
						pickup_data.update({'can_swim': True})
					elif pickup.name == 'Tracker':	
						pickup_data.update({'tracker': True})
					self.pickup_pause = True
					self.player.hold = True
					self.pickup_message(pickup.name)	
		if self.game.neobits >= 200:
			collided_cost_pickups = pygame.sprite.spritecollide(self.player, self.cost_pickup_sprites, True, pygame.sprite.collide_rect_ratio(0.6))
			if collided_cost_pickups:
				try:
					del(self.pickup_message)
				except:
					pass
				finally:
					for costed in collided_cost_pickups:
						if costed.name == 'Railgun':
							gun_data.update(costed.index)
						self.pickup_pause = True
						self.player.hold = True
						self.pickup_message(costed.name)
						self.game.update_neobits(-200)	
						
	def pickup_message(self, name):
		self.pickup_message = PickupPause(self.game, name, '', self.display_surf)
		self.pickup_message.run()

	def pickup_cooldown(self):
		if self.pickup_pause:
			self.pickup_message.run()
			self.pickup_timer += 1
			if self.pickup_timer >= HOLD_TIME:
				self.pickup_pause = False
				self.pickup_timer = 0
				del(self.pickup_message)

	def NPC_collision(self):
		collided_NPC = pygame.sprite.spritecollide(self.player, self.NPC_sprites, False)
		if collided_NPC:
			for npc in collided_NPC:
				DialogueBox(self.game, dialogues[npc.sprite_type][0], dialogues[npc.sprite_type][1], dialogues[npc.sprite_type][2], dialogues[npc.sprite_type][3], self.display_surf).run()

	def dump_data(self, text_file, save_as_file, saved_dict, current_dict):
		with open((f'{text_file}'), 'w') as save_as_file:
			json.dump(saved_dict, save_as_file)
			current_dict.update(saved_dict)

	def player_death(self):
		if not self.player.alive:
			Pause(self.game, 'You died', "Restart? y / n", self.display_surf).run()

	def sprite_group_invincibility(self, group):
		for sprite in group:
			if sprite.invincible:
				sprite.can_shoot = False
				sprite.invincibility_timer += 1
				if sprite.invincibility_timer >= 60:
					sprite.invincible = False
					sprite.can_shoot = True

	def sprite_invincibility(self, sprite):
		if sprite.invincible:
			sprite.invincibility_timer += 1
			if sprite.invincibility_timer >= 120:
				sprite.invincible = False

	def paused(self):
		if not self.map_showing:
			self.game_paused = not self.game_paused

	def show_map(self):
		self.map_showing = not self.map_showing	

	def run(self):
		self.get_block_pos()
		if self.timer == 60 and self.map_showing:
			self.map.run()
		else:
			self.sprite_group_invincibility(self.enemy_sprites)
			self.sprite_invincibility(self.player)
			self.get_player_grounded()
			self.create_run_particles()
			self.create_dash_particles()
			self.create_hover_particles()
			self.active_sprites.update()
			self.visible_sprites.offset_draw(self.player)
			self.create_landing_particles()
			self.player_death()
			self.elevator_message()
			self.collectible_collision()
			self.NPC_collision()
			self.pickup_collision()
			self.pickup_cooldown()
			self.entry_cooldown()
			self.exit_level()
			self.save_point()
			



		
	


		

		



		




	

	



		