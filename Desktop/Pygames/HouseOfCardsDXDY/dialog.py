import pygame, time
from state import State
from player import NPC
from random import randint

class Dialog(State):
	def __init__(self, game, npc, dialog):
		State.__init__(self, game)

		self.npc = npc
		self.dialog = dialog
		self.char_img = pygame.image.load(self.npc).convert_alpha()
		self.char_img = pygame.transform.scale(self.char_img, (self.char_img.get_width() *10, self.char_img.get_height() * 10))
		self.box_img = pygame.image.load('img/ui/dialog_bg.png').convert_alpha()
		self.box_img = pygame.transform.scale(self.box_img, (self.game.WIDTH *0.9, self.game.HEIGHT * 0.35))
		self.fadebox_img = pygame.Surface((self.game.WIDTH *0.6, self.game.HEIGHT * 0.25))
		self.fadebox_img.fill(self.game.BLUE)
		self.display_surf = pygame.display.get_surface()
		self.transitioning = True
		self.fade_speed = 8

		self.timer = self.game.HEIGHT
		self.fade_timer = 255
		self.opening = True
		self.closing = False
		self.step = 0

	def blit_text(self, pos, display):
		
	    words = [word.split(' ') for word in self.dialog[self.step].splitlines()]  # 2D array where each row is a list of words.
	    space = self.game.font.size(' ')[0]  # The width of a space.
	    max_width = self.box_img.get_rect().right
	    max_height = self.box_img.get_rect().bottom
	    x, y = pos
	    random_y = randint(int(y - 2), int(y + 2))
	    colour = self.game.WHITE
	    for line in words:
	        for word in line:
	            word_surface = self.game.font.render(word, True, colour)
	            word_width, word_height = word_surface.get_size()
	            if x + word_width >= max_width:
	                x = pos[0]  # Reset the x.
	                y += word_height  # Start on new row.
	            if word == 'Angry' or word == 'now!':
	           		display.blit(word_surface, (x, random_y))
	            display.blit(word_surface, (x, y))
	            x += word_width + space
	        x = pos[0]  # Reset the x.
	        y += word_height  # Start on new row.


	def fade(self, display):
		self.fade_timer -= self.fade_speed
		if self.fade_timer <= 255:
			self.fadebox_img.set_alpha(self.fade_timer)
			display.blit(self.fadebox_img, (self.game.WIDTH * 0.3, self.game.HEIGHT * 0.72))
		if self.fade_timer <= 0:
			self.transitioning = False
			self.fade_timer = 0
		else:
			self.trasitioning = True

	def box(self, display):
		if self.opening == True:
			self.timer -= 8
			if self.timer <= self.game.HEIGHT * 0.65:
				self.timer = self.game.HEIGHT * 0.65
				self.opening = False

	def update(self, actions):
		if actions['space'] and not self.transitioning:
			if self.transitioning == False:
				self.fade_timer = 255
				self.transitioning = True
			if self.step < len(self.dialog) -1:
				self.step += 1
			else:
				self.step = len(self.dialog) -1
				self.closing = True
		else:
			self.transitioning = False
		if self.timer >= self.game.HEIGHT and self.closing:
			self.exit_state()
		self.game.reset_keys()

	def render(self, display):
		self.prev_state.render(display)
		if self.closing:
			self.timer += 5
		else:
			self.box(display)
		display.blit(self.box_img, (self.game.WIDTH * 0.05, self.timer))
		
		if not (self.opening or self.closing):
			display.blit(self.char_img, (self.game.WIDTH * 0.05,  self.timer))
			self.blit_text((self.game.WIDTH * 0.3, self.game.HEIGHT * 0.72), display)
			self.fade(display)



		self.game.draw_text(display, str(self.transitioning), ((200,200,200)), 100, (self.game.WIDTH * 0.5, self.game.HEIGHT * 0.1))
