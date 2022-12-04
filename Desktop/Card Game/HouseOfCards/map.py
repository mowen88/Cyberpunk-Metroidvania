import pygame
from state import State

class RoomSprite(pygame.sprite.Sprite):
	def __init__(self, pos, surf):
		self.image = pygame.image.load(surf).convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)

class Map(State):
	def __init__(self, game, room):
		State.__init__(self, game)
		self.game = game
		self.room = room
		self.display_surf = pygame.display.get_surface()
		pos = (self.game.WIDTH // 12, self.game.HEIGHT // 12) # split the screen into 12x12 grid to place room sprites easily
		self.rooms = {
		'jail': RoomSprite((pos[0] * 8, pos[1] * 4), 'rooms/jail/map_piece.png'),
		'courtroom': RoomSprite((pos[0] * 4, pos[1] * 4), 'rooms/courtroom/map_piece.png'),
		'hallway': RoomSprite((pos[0] * 1, pos[1] * 4), 'rooms/hallway/map_piece.png'),
		'pantry': RoomSprite((pos[0] * 2, pos[1] * 2), 'rooms/pantry/map_piece.png'),
		}
		

		marker_offset_x = (self.rooms[self.game.current_room].rect.width * (self.room.player.hitbox.centerx/self.room.visible_sprites.room_size[0])) * self.game.SCALE
		marker_offset_y = (self.rooms[self.game.current_room].rect.height * (self.room.player.hitbox.centery/self.room.visible_sprites.room_size[1])) * self.game.SCALE


		marker_pos_x = self.rooms[self.game.current_room].rect.x + marker_offset_x
		marker_pos_y = self.rooms[self.game.current_room].rect.y + marker_offset_y
		self.marker_pos = (marker_pos_x, marker_pos_y)

		print(marker_offset_x)

		# player marker
		self.marker_surf = pygame.image.load('img/ui/marker.png').convert_alpha()
		self.marker_rect = self.marker_surf.get_rect(center = self.marker_pos)
		# self.icon_rect = self.marker_surf.get_rect(center = (self.game.WIDTH //2 - 120, self.game.HEIGHT - 192))
	
	def show_rooms(self):
		for sprite in self.rooms.values():
			sprite.image = pygame.transform.scale(sprite.image, (sprite.rect.width * self.game.SCALE, sprite.rect.height * self.game.SCALE))
			self.display_surf.blit(sprite.image, sprite.rect)


	def update(self, actions):
		if self.game.actions['m']:
			self.exit_state()
		self.game.reset_keys()

	def render(self, display):
		self.display_surf.fill(self.game.BLACK)
		# self.prev_state.prev_state.render(display)
		#self.prev_state.render(display)

		self.show_rooms()
		self.display_surf.blit(self.marker_surf, self.marker_rect)
		

	




		





	