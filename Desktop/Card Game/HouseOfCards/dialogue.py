import pygame, time, os, sys
from state import State
from player import NPC
from random import randint


class Board(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 0
        self.fade_speed = 10 # lower is faster
        self.image = pygame.Surface((self.game.WIDTH * 0.7, self.game.HEIGHT * 0.25))
        self.image.fill(self.game.BLACK)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect()
      
    def add(self, letter, pos):
        s = self.game.font.render(letter, 1, self.game.WHITE)
        self.image.blit(s, pos)

class Cursor(pygame.sprite.Sprite):
    def __init__(self, board):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.text_height = 35
        self.text_width = 20
        self.rect = self.image.get_rect(topleft=(self.text_width, self.text_height))
        self.board = board
        self.step = 0
        self.text = ''
        self.cooldown = 0
        self.cooldowns = {'.': 12,
                        ' ': 6,
                        '\n': 20}

    def write(self, text):
        self.text = list(text)

    def update(self):
        if not self.cooldown and self.text:
        	self.cooldowns = {'.': 12,
                    ' ': 6,
                    '\n': 20}

        	letter = self.text.pop(0)
        	if letter not in self.cooldowns:
        		self.cooldowns.update({letter: 3})

        	if pygame.key.get_pressed()[pygame.K_SPACE]:
        		self.cooldowns = {}

        	if letter == '\n':
        		self.rect.move_ip((0, self.text_height + 5))
        		self.rect.x = self.text_width
        	else:
        		self.board.add(letter, (self.rect.topleft[0] + 30, self.rect.topleft[1]))
        		self.rect.move_ip((self.text_width, 0))

        	self.cooldown = self.cooldowns.get(letter, 1)

        if self.cooldown:
            self.cooldown -= 1
            
class Dialogue(State):
	def __init__(self, game, room, number, dialog):
		State.__init__(self, game)

		self.display = pygame.display.get_surface()
		self.room = room
		self.number = number
		self.dialog = dialog
		self.box_img = pygame.Surface((self.game.WIDTH *0.6, self.game.HEIGHT * 0.3))

		self.arrow_img = pygame.image.load('img/ui/spade.png').convert_alpha()
		self.arrow_img = pygame.transform.scale(self.arrow_img, (self.arrow_img.get_width() * self.game.SCALE, self.arrow_img.get_height() * self.game.SCALE))
		
		self.timer = self.game.HEIGHT
		self.opening = True
		self.closing = False
		self.step = 0
		self.state = 'asking'
		self.hover_yes = True
		self.room.dialog_running = True
		
		self.get_initial_state()
		
		self.board = Board(self.game)
		self.cursor = Cursor(self.board)

		self.yes_img = pygame.image.load('img/ui/yes.png').convert_alpha()
		self.yes_img = pygame.transform.scale(self.yes_img, (self.yes_img.get_width() * self.game.SCALE, self.yes_img.get_height() * self.game.SCALE))
		self.no_img = pygame.image.load('img/ui/no.png').convert_alpha()
		self.no_img = pygame.transform.scale(self.no_img, (self.no_img.get_width() * self.game.SCALE, self.no_img.get_height() * self.game.SCALE))
	

		self.text_box = pygame.sprite.Group()
		self.text_box.add(self.board)

		self.cursor.write(self.dialog[self.state][self.step])
		

	def get_initial_state(self):
		if not self.dialog['normal'] == 'done':
			if self.state not in self.dialog:
				self.state = 'normal'
			else:
				self.state = 'asking'
		else:
			self.state = 'done'

		print(self.dialog)
	

	def yes_no(self):
		pass

	def box(self, display):
		if self.opening == True:
			# self.timer -= 8
			# if self.timer <= self.game.HEIGHT * 0.7:
			# 	self.timer = self.game.HEIGHT * 0.7
			# 	self.opening = False
			self.board.alpha += 255/self.board.fade_speed
			if self.board.alpha >= 255:
				self.board.alpha = 255
				self.opening = False

	def draw_border(self, display, pos):
		if self.board.alpha == 255:
			border_surf = pygame.Surface((self.board.rect.width - 10, self.board.rect.height - 10))
			border_surf.fill((self.game.WHITE))
			border_rect = border_surf.get_rect(center = pos)
			pygame.draw.rect(display, self.game.WHITE, border_rect, 3)

	def update(self, actions):
		
		if not self.opening and not self.closing:
			
			self.cursor.update()
			if not self.cursor.text:

				if self.step >= len(self.dialog[self.state])-1 and self.state == 'asking':
					if actions['left']:
						self.hover_yes = True
					if actions['right']:
						self.hover_yes = False
					if actions['space']:
						self.board.image.fill(self.game.BLACK)
						self.step += 1
						if self.step >= len(self.dialog[self.state]):
							if self.hover_yes:
								self.state = 'yes'
							elif not self.hover_yes:
								self.state = 'no'
							self.step = -1

				if actions['space']:
					self.board.image.fill(self.game.BLACK)
					self.step += 1
					if self.step >= len(self.dialog[self.state]):
						self.step = 0
						self.closing = True

					self.cursor.write(self.dialog[self.state][self.step])
					self.cursor.rect.x, self.cursor.rect.y = self.cursor.text_width, self.cursor.text_height
						
		if self.closing:
			self.room.dialog_running = False
			if self.state == 'yes':
				self.game.dialog_dict[self.number]['normal'] = 'done'
 
				print(self.game.dialog_dict)
			self.exit_state()
		
		# below fixes a bug where the sprites do not update when dialog runs within cutscene (as the 
		#dialog tries to call prev_state method and this is not available as prev_state is cutscene)
		if self.room.cutscene_running: 
			if not self.room.dialog_running:
				self.prev_state.prev_state.active_sprites.update()
			
			elif self.room.dialog_running:
				self.prev_state.prev_state.active_sprites.update()

		else:
			self.prev_state.active_sprites.update()

		#yes or no buttons
				
		self.game.reset_keys()

	def draw_yes_no(self, display):
		pos = self.display.get_width() *0.5 - (self.yes_img.get_width() * 0.5), self.board.rect.height +25, 200, 50
		if self.state == 'asking' and self.step >= len(self.dialog[self.state])-1:
			if not self.hover_yes:
				display.blit(self.no_img, pos)
			else:
				display.blit(self.yes_img, pos)


	
		print(self.state)

	def render(self, display):
		self.prev_state.render(display)
		if self.closing:
			self.board.alpha -= 255/self.board.fade_speed
			self.board.image.set_alpha(self.board.alpha)
		else:
			self.box(display)
		#self.board.rect.topleft = (self.game.WIDTH * 0.2, self.timer)
		self.board.rect.midtop = (self.game.WIDTH * 0.5, self.game.HEIGHT * 0.15)
		self.text_box.draw(display)

		if not self.cursor.text:
			display.blit(self.arrow_img,((self.board.rect.bottomright[0] - self.arrow_img.get_width())-10, (self.board.rect.bottomright[1] - self.arrow_img.get_height()-10)))
			self.draw_yes_no(display)

		self.draw_border(display, self.board.rect.center)
		self.board.image.set_alpha(self.board.alpha)
		
		self.game.draw_text(display, str(self.hover_yes), (self.game.WHITE), 100, (self.game.WIDTH * 0.6, self.game.HEIGHT * 0.6))
		self.game.draw_text(display, str(self.state), (self.game.WHITE), 100, (self.game.WIDTH * 0.4, self.game.HEIGHT * 0.6))
		
		

# class Dialogue(State):
# 	def __init__(self, game, npc, dialog):
# 		State.__init__(self, game)

# 		self.npc = npc
# 		self.dialog = dialog
# 		self.char_img = pygame.image.load(self.npc).convert_alpha()
# 		self.char_img = pygame.transform.scale(self.char_img, (self.char_img.get_width() *10, self.char_img.get_height() * 10))
# 		self.box_img = pygame.image.load('img/ui/dialog_bg.png').convert_alpha()
# 		self.box_img = pygame.transform.scale(self.box_img, (self.game.WIDTH *0.9, self.game.HEIGHT * 0.35))
# 		self.fadebox_img = pygame.Surface((self.game.WIDTH *0.6, self.game.HEIGHT * 0.25))
# 		self.fadebox_img.fill(self.game.BLUE)
# 		self.display_surf = pygame.display.get_surface()
# 		self.transitioning = True
# 		self.fade_speed = 8
		

# 		self.timer = self.game.HEIGHT
# 		self.fade_timer = 255
# 		self.opening = True
# 		self.closing = False
# 		self.step = 0

# 		self.index = -1
# 		self.words = []
# 		self.msg = []
# 		self.line = None
# 		self.lines = []
# 		self.typing = True
# 		self.message = "Computer: Hello, nice to meet you. \n Me: Nice to meet you. \n Computer: You too, goodbye!"

# 	def blit_text(self, display):
# 		initial_x = self.game.WIDTH * 0.3
# 		initial_y = self.game.HEIGHT * 0.7
# 		max_width = 700
# 		line_length = len(self.dialog[0][0])
# 		second_line_length = len(self.dialog[1][0])
# 		third_line_length  = len(self.dialog[1][0])
	
# 		offset_x = 12
# 		offset_y = 30

# 		if self.typing: 
# 			for letter in self.dialog[0]:
# 				self.index += 1
# 				offset_x *= self.index
# 				char = letter[self.index]
# 				if self.index >= line_length -1:
# 					self.index = -1
# 					self.typing = False
# 			self.words.append(char)
# 			self.line = (''.join(self.words))

# 		print(self.lines)
		
# 		line_surf = self.game.font.render(self.line, True, self.game.WHITE, 80)
# 		display.blit(line_surf, (initial_x, initial_y))

# 		pygame.time.wait(20)
	

# 	def fade(self, display):
# 		self.fade_timer -= self.fade_speed
# 		if self.fade_timer <= 255:
# 			self.fadebox_img.set_alpha(self.fade_timer)
# 			display.blit(self.fadebox_img, (self.game.self.game.WIDTH * 0.3, self.game.self.game.HEIGHT * 0.72))
# 		if self.fade_timer <= 0:
# 			self.transitioning = False
# 			self.fade_timer = 0
# 		else:
# 			self.trasitioning = True

# 	def box(self, display):
# 		if self.opening == True:
# 			self.timer -= 8
# 			if self.timer <= self.game.HEIGHT * 0.65:
# 				self.timer = self.game.HEIGHT * 0.65
# 				self.opening = False

# 	def update(self, actions):
# 		if actions['space'] and not self.transitioning:
# 			if self.transitioning == False:
# 				self.fade_timer = 255
# 				self.transitioning = True
# 			if self.step < len(self.dialog) -1:
# 				self.step += 1
# 			else:
# 				self.step = len(self.dialog) -1
# 				self.closing = True
# 		else:
# 			self.transitioning = False
# 		if self.timer >= self.game.HEIGHT and self.closing:
# 			self.exit_state()
# 		self.game.reset_keys()

# 	def render(self, display):
# 		self.prev_state.render(display)
# 		if self.closing:
# 			self.timer += 5
# 		else:
# 			self.box(display)
# 		display.blit(self.box_img, (self.game.WIDTH * 0.05, self.timer))
# 		if not (self.opening or self.closing):
# 			display.blit(self.char_img, (self.game.WIDTH * 0.05,  self.timer))
# 			self.blit_text(display)
# 			#self.fade(display)

# 		self.game.draw_text(display, str(self.line), ((200,200,200)), 100, (self.game.WIDTH * 0.5, self.game.HEIGHT * 0.1))

