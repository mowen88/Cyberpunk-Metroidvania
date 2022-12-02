import pygame
from state import State
from dialogue import Dialogue

class Cutscene(State):
	def __init__(self, game, room, cutscene_number):
		State.__init__(self, game)

		self.room = room
		self.cutscene_number = cutscene_number
		self.timer = 0
		self.camera_moving = False

		self.opening = True
		self.closing = False

		self.bar_timer = 0
		self.bottom_bar_timer = self.game.HEIGHT + 4

		self.bottom_bar_height = self.game.HEIGHT * 0.9
		self.top_bar_height = self.game.HEIGHT * 0.1

		self.bottom_bar_img = pygame.Surface((self.game.WIDTH, self.top_bar_height))
		self.bottom_bar_img.fill(self.game.RED)

		self.direction = pygame.math.Vector2()


		# self.room.visible_sprites.offset[0] += 5
		
	def move_camera(self, speed_x, speed_y):
		self.room.visible_sprites.offset[0] += speed_x
		self.room.visible_sprites.offset[1] += speed_y

	def action_sequence(self, cutscene):

		if cutscene == 0:
			if self.timer > 0 and self.timer < 80:
				for sprite in self.room.npc_sprites:
					self.room.target = sprite

				self.room.target.vel.x = 1
				# if self.room.walking_enemy.alive:
				# 	self.room.target = self.room.walking_enemy

			elif self.timer > 40 and self.timer < 150:
				self.room.target.vel.x = 0

				if self.timer == 80:
					new_state = Dialogue(self.game, self.room, self.game.dialog_dict[0]['path'], self.game.dialog_dict[0])
					new_state.enter_state()
			
			elif self.timer > 150 and self.timer < 240:
				self.room.target = self.room.player
				if self.timer == 180:
					self.room.player.crouch('down')
				if self.timer == 200:
					self.room.player.crouch('up')

			elif self.timer >= 240:
				self.closing = True
				self.room.cutscene_running = False
				self.game.cutscenes_completed.append(self.cutscene_number)
				if self.bar_timer <= 0 and self.closing:
					self.exit_state()
				
			else:
				self.room.player.moving_left, self.room.player.moving_right = False, False

		if cutscene == 1:
			if self.timer > 20 and self.timer < 50:
				self.room.player.moving_left = True
				if self.timer == 30:
					self.room.player.jump(self.room.player.jump_height)
				#self.move_camera(3, 3)
				
			elif self.timer == 75:
				new_state = Dialogue(self.game, self.room, self.game.dialog_dict[1]['path'], self.game.dialog_dict[1])
				new_state.enter_state()

			elif self.timer > 120 and self.timer < 170:
				if self.timer == 130:
					self.room.player.jump(self.room.player.jump_height)
				self.room.player.moving_left = True

			elif self.timer > 200 and self.timer < 250: 
				self.camera_moving = True

			elif self.timer > 250 and self.timer < 300:
				self.move_camera(-3,-3)

			elif self.timer >= 300:
				self.closing = True
				self.room.cutscene_running = False
				self.game.cutscenes_completed.append(self.cutscene_number)
				if self.bar_timer <= 0 and self.closing:
					self.exit_state()
				
			else:
				self.room.player.moving_left, self.room.player.moving_right = False, False

	def boxes(self, display):
		if self.opening == True:
			self.bar_timer += 4
			self.bottom_bar_timer -= 4
			if self.bar_timer >= self.top_bar_height:
				self.bar_timer = self.top_bar_height
				self.opening = False
			if self.bottom_bar_timer <= self.bottom_bar_height:
				self.bottom_bar_timer = self.bottom_bar_height
				self.opening = False

	def update(self, actions):
		self.timer += 1
		self.action_sequence(self.cutscene_number)
		self.prev_state.active_sprites.update()
		
	def render(self, display):
		self.prev_state.render(display)
		if self.closing:
			self.bar_timer -= 4
			self.bottom_bar_timer += 4
		self.boxes(display)
		pygame.draw.rect(display, self.game.BLUE, (0, 0, self.game.WIDTH, self.bar_timer))
		display.blit(self.bottom_bar_img, (0, self.bottom_bar_timer))
		#self.game.draw_text(self.game.screen, str(self.room.visible_sprites.offset[0]), ((255,255,255)), 100, (self.game.screen.get_width()//4, 24))
		self.game.draw_text(self.game.screen, str(self.bottom_bar_timer), self.game.BLACK, 100, (self.game.screen.get_width()//6, 24))



