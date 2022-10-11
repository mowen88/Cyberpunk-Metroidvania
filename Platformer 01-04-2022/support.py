from os import walk
import pygame
from csv import reader
from settings import TILESIZE, SCALE

def import_csv(path):
	terrain_map = []
	with open(path) as map:
		level = reader(map, delimiter=',')
		for row in level:
			terrain_map.append(list(row))

	return terrain_map

def import_cut_imgs(path):
	surf = pygame.image.load(path).convert_alpha()
	tile_no_x = int(surf.get_size()[0] // TILESIZE)
	tile_no_y = int(surf.get_size()[1] // TILESIZE)

	cut_tiles = []
	for row in range(tile_no_y):
		for col in range(tile_no_x):
			x = col * TILESIZE
			y = row * TILESIZE
			new_surf = pygame.Surface((TILESIZE, TILESIZE))
			new_surf.blit(surf, (0, 0), pygame.Rect(x, y, TILESIZE, TILESIZE))
			cut_tiles.append(new_surf)

	return cut_tiles
	
def import_folder(path):
	surf_list = []

	for _, __, img_files in walk(path):
		for img in img_files:
			full_path = path + '/' + img
			img_surf = pygame.image.load(full_path).convert_alpha()
			img_surf = pygame.transform.scale(img_surf,(img_surf.get_width() * SCALE, img_surf.get_height() * SCALE))
			surf_list.append(img_surf)

	return surf_list


