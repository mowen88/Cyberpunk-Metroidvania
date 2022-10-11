import pygame
from settings import *
import math


class Pause:
	def __init__(self, game, msg, small_msg, surf):

		#setup
		self.game = game
		self.display_surf = surf

		self.font = pygame.font.Font(FONT, 40)
		self.small_font = pygame.font.Font(UI_FONT, 20)

		self.text_surf = self.font.render(str(msg), True, 'WHITE')
		self.small_text_surf = self.small_font.render(str(small_msg), True, 'WHITE')
		self.text_rect = self.text_surf.get_rect(center = (WIDTH //2, HEIGHT // 2 - 24))
		self.small_text_rect = self.small_text_surf.get_rect(center = (WIDTH //2, HEIGHT // 2 + 24))

		#self.entry_pos = entry_pos
		#self.current_level = exits[entry_pos]

	def input(self):
		keys = pygame.key.get_pressed()
		pass

		#if keys[pygame.K_SPACE]:
			#self.current_level +=1

	def run(self):
		
		self.display_surf.blit(self.text_surf, self.text_rect)
		self.display_surf.blit(self.small_text_surf, self.small_text_rect)
		self.input()

class PickupPause(Pause):
	def __init__(self, game, msg, small_msg, surf):
		Pause.__init__(self, game, msg, small_msg, surf)
		self.fade_in_counter = 0
		self.counter = 0
		self.fading_in = True
		self.fading_out = False
		
		self.text_rect = self.text_surf.get_rect(center = (WIDTH //2, HEIGHT - 48))

	def run(self):
		
		self.counter += 4

		pygame.draw.rect(self.display_surf, BLACK, (0, HEIGHT - self.fade_in_counter, WIDTH, HEIGHT))
		pygame.draw.rect(self.display_surf, BLACK, (0, 0, WIDTH, 0 + self.fade_in_counter))

		if self.counter >= 3 * HOLD_TIME:
			self.fading_out = True
			self.fading_in = False
		else:
			self.fading_out = False

		if self.fading_in == True:
			if self.fade_in_counter < 96:
				self.fade_in_counter += 4
		if self.fading_out == True:
			self.fade_in_counter -= 4

		if self.fade_in_counter >= 96:
			self.display_surf.blit(self.text_surf, self.text_rect)

	
class DialogueBox():
	def __init__(self, game, header, line1, line2, line3, surf):

		self.game = game
		self.display_surf = surf

		self.font = pygame.font.Font(FONT, 30)
		self.small_font = pygame.font.Font(UI_FONT, 20)

		self.header_text_surf = self.font.render(str(header), True, 'WHITE')
		self.header_text_rect = self.header_text_surf.get_rect(midleft = (WIDTH //2 - 240, HEIGHT // 2 + 144))

		self.line_1_text_surf = self.small_font.render(str(line1), True, 'WHITE')
		self.line_1_text_rect = self.line_1_text_surf.get_rect(midleft = (WIDTH //2 - 240, HEIGHT // 2 + 180))

		self.line_2_text_surf = self.small_font.render(str(line2), True, 'WHITE')
		self.line_2_text_rect = self.line_2_text_surf.get_rect(midleft = (WIDTH //2 - 240, HEIGHT // 2 + 204))

		self.line_3_text_surf = self.small_font.render(str(line3), True, 'WHITE')
		self.line_3_text_rect = self.line_3_text_surf.get_rect(midleft = (WIDTH //2 - 240, HEIGHT // 2 + 228))

	def run(self):
		pygame.draw.rect(self.display_surf, BLACK, (WIDTH //2 - 276, HEIGHT //2 + 104, 540,162))
		pygame.draw.rect(self.display_surf, NEON_BLUE, (WIDTH //2 - 270, HEIGHT //2 + 110, 528,150))
		pygame.draw.rect(self.display_surf, BLACK, (WIDTH //2 - 267, HEIGHT //2 + 113, 522, 144))
		self.display_surf.blit(self.header_text_surf, self.header_text_rect)
		self.display_surf.blit(self.line_1_text_surf, self.line_1_text_rect)
		self.display_surf.blit(self.line_2_text_surf, self.line_2_text_rect)
		self.display_surf.blit(self.line_3_text_surf, self.line_3_text_rect)


class LevelIntro:
	def __init__(self, new_level, msg, surf):

		#setup
		self.display_surf = surf
		self.new_level = new_level

		self.font = pygame.font.Font(FONT, 40)
		self.text_surf = self.font.render(str(msg), True, 'WHITE')
		self.text_rect = self.text_surf.get_rect(center = (WIDTH //2, HEIGHT // 2))

		#self.entry_pos = entry_pos
		#self.current_level = exits[entry_pos]

	def input(self):
		keys = pygame.key.get_pressed()
		pass

		#if keys[pygame.K_SPACE]:
			#self.current_level +=1

	def run(self):
		self.display_surf.blit(self.text_surf, self.text_rect)
		self.input()


class Transition:
	def __init__(self, game, surf):

		self.fade_in_counter = 0
		self.game = game
		self.display_surf = surf
		
	def run(self):
		self.fade_in_counter += 15
		pygame.draw.rect(self.display_surf, BLACK, (0, 0, WIDTH - self.fade_in_counter, HEIGHT))
		pygame.draw.rect(self.display_surf, BLACK, (0 + self.fade_in_counter, 0, WIDTH, HEIGHT))
		pygame.draw.rect(self.display_surf, BLACK, (0, 0, WIDTH, HEIGHT - (self.fade_in_counter * 0.5625)))
		pygame.draw.rect(self.display_surf, BLACK, (0, (0 + self.fade_in_counter * 0.5625), WIDTH, HEIGHT))

		if self.fade_in_counter >= (HEIGHT or WIDTH):
			self.game.level.timer = 60

class Map:
	def __init__(self, game, surf):
		self.game = game
		self.showing_rooms = False
		self.display_surf = surf
		msg = 'whatever'
		self.current_room = list(levels_visited.keys())[self.game.level.current_level]
		self.marker_surf = pygame.Surface((16, 16))
		self.marker_surf.fill((0,0,255))
		self.marker_rect = self.marker_surf.get_rect(center = (100, 100))

		self.font = pygame.font.Font(FONT, 40)
		self.small_font = pygame.font.Font(UI_FONT, 20)

		self.text_surf = self.font.render(str(msg), True, 'WHITE')
		self.small_text_surf = self.small_font.render(str(msg), True, 'WHITE')
		self.text_rect = self.text_surf.get_rect(center = (WIDTH //2, HEIGHT // 2 - 24))
		self.small_text_rect = self.small_text_surf.get_rect(center = (WIDTH //2, HEIGHT // 2 + 24))

		self.backdrop_surf = pygame.Surface((WIDTH - 128, HEIGHT -128))
		self.backdrop_rect = self.backdrop_surf.get_rect(center = (WIDTH // 2, HEIGHT //2))
		
		self.rooms = {
				'0': (120,100,64,40),
				'1': (190,100,64,40),
				'2': (260,100,60,100),
				'3': (200,160,40,30),
				'4': (330,140,40,30)
				}

	def show_rooms(self):
		for num in list(self.rooms.keys()):
			if num in list(levels_visited.keys()):
				pygame.draw.rect(self.display_surf, WHITE, self.rooms[num], 3)

	def run(self):
		self.display_surf.blit(self.backdrop_surf, self.backdrop_rect)
		self.show_rooms()
		self.display_surf.blit(self.marker_surf, self.marker_rect)
		print(self.current_room)

		#print(self.counter)

# class PauseMenu:
# 	def __init__(self, surf):

# 		#setup
# 		self.index = 'Resume'
# 		self.display_surf = surf
# 		self.can_move = True
# 		self.cursor_rect = pygame.Rect(0,0, 30, 30)
# 		self.offset = - 120

# 		self.font = 'font/failed attempt.ttf'

# 		self.resume_x = self.display_surf.get_width() // 2
# 		self.resume_y = self.display_surf.get_height() // 2 + 30
# 		self.quit_x = self.display_surf.get_width() // 2
# 		self.quit_y = self.display_surf.get_height() // 2 + 60
# 		self.cursor_rect.midtop = (self.resume_x + self.offset, self.resume_y)

# 	def draw_text(self, text, size, pos):
# 		font = pygame.font.Font(self.font, size)
# 		text_surf = font.render(text, True, WHITE)
# 		text_rect = text_surf.get_rect(center = pos)
# 		self.display_surf.blit(text_surf, text_rect)

# 	def draw_cursor(self):
# 		self.draw_text('*', 15, (self.cursor_rect.x, self.cursor_rect.y))

# 	def blit_screen(self, surf):
# 		self.display_surf.blit(surf, (0, 0))
# 		pygame.display.update()

# 	def input(self):
# 		keys = pygame.key.get_pressed()

# 		if self.can_move:
# 			if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
# 				if self.index == 'Resume':
# 					self.index = 'Quit'
# 					self.cursor_rect.midtop = (self.quit_x + self.offset, self.quit_y)
# 					self.selection_time = pygame.time.get_ticks()
# 					self.can_move = False
# 				elif self.index == 'Quit':
# 					self.index = 'Resume'
# 					self.cursor_rect.midtop = (self.resume_x + self.offset, self.resume_y)
# 					self.selection_time = pygame.time.get_ticks()
# 					self.can_move = False

# 		if keys[pygame.K_RETURN]:
# 			if self.index == 'Resume':
# 				self.kill()
# 			elif self.index == 'Quit':
# 				pass

# 	def selection_cooldown(self):
# 		if not self.can_move:
# 			current_time = pygame.time.get_ticks()
# 			if current_time - self.selection_time >= 300:
# 				self.can_move = True

# 	def run(self):
# 		self.selection_cooldown()
# 		self.input()
# 		self.display_surf.fill(BLACK)
# 		self.draw_text('Paused', 50, (self.display_surf.get_width() // 2, self.display_surf.get_height() // 2 - 30))
# 		self.draw_text('Resume', 30, (self.resume_x, self.resume_y))
# 		self.draw_text('Quit', 30, (self.quit_x, self.quit_y))
# 		self.draw_cursor()
# 		self.blit_screen(self.display_surf)








		


