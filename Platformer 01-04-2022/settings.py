# title
TITLE = 'METROIDVANIA'

# framerate
FPS = 60

SCALE = 3
TILESIZE = 16 * SCALE
WIDTH = 320 * SCALE
HEIGHT = 180 * SCALE

# player variables
HOLD_TIME = 96
JUMP_HEIGHT = 16
TERMINAL_VELOCITY = 24

# colours
BLACK = (0,0,0)
GREY = (21, 22, 23)
WHITE = (245,245,245)
GREEN = (100,180,100)
NEON_BLUE = (102,255,227)
PURPLE = (50,41,71)

# fonts
FONT = 'font/failed attempt.ttf'
UI_FONT = 'font/Gepestev-nRJgO.ttf'

CAMERA_BORDERS = {
	'left': 400,
	'right': WIDTH - 400,
	'top': 200,
	'bottom': HEIGHT - 200
}

collected_dict = {}

weapon_data = {
	'sword':{'cooldown': 800, 'damage': 15, 'img':'img/weapons/sword.png'},
	'lance':{'cooldown': 150, 'damage': 30, 'img':'img/weapons/sword.png'}
}

neobit_data = {}
health_data = {}

extra_healths_collected = {}
saved_extra_healths_collected = {}

gun_data = {}

enemy_gun_data = {
	0:{'bullet_speed': 10, 'cooldown': 300, 'damage': 20, 'img':'img/bullets/bullet_0.png', 'gun_img':'img/pickups/blaster/00.png', 'sfx':'audio/sfx/blaster.wav'},
	1:{'bullet_speed': 20, 'cooldown': 100, 'damage': 15, 'img':'img/bullets/bullet_2.png', 'gun_img':'img/pickups/hyper_blaster/00.png', 'sfx':'audio/sfx/blaster.wav'},
	2:{'bullet_speed': 40, 'cooldown': 500, 'damage': 50, 'img':'img/bullets/bullet_1.png', 'gun_img':'img/pickups/railgun/00.png', 'sfx':'audio/sfx/railgun.wav'}

}
saved_gun_data = {}

pickup_data = {'double_jump': False, 'wall_jump': False, 'dash': False, 'hovering': False, 'neobits': 0, 'tracker': False}
saved_pickup_data = {}

load_data = {
	'save_point': 0,'entry pos': 0, 'block_position': (200, 400), 'current_gun': 0, 'gun_showing': False
}

#for each level, key = the exit, the value = the level you enter at
levels = {
	0: {1:1, 2:3, 3:0, 4:0, 5:3, 6:2, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'Purple level'},
	1: {1:0, 2:0, 3:16, 4:0, 5:0, 6:0, 7:2, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'Orange level'},
	2: {1:0, 2:0, 3:8, 4:0, 5:0, 6:0, 7:1, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'Blue level'},
	3: {1:0, 2:0, 3:4, 4:0, 5:0, 6:12, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'Green level'},
	4: {1:8, 2:12, 3:3, 4:9, 5:7, 6:5, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	5: {1:11, 2:6, 3:0, 4:0, 5:0, 6:4, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	6: {1:0, 2:5, 3:0, 4:0, 5:0, 6:7, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	7: {1:0, 2:0, 3:0, 4:0, 5:4, 6:6, 7:0, 8:12, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	8: {1:4, 2:0, 3:2, 4:0, 5:0, 6:9, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	9: {1:0, 2:15, 3:0, 4:4, 5:0, 6:8, 7:10, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	10: {1:0, 2:0, 3:0, 4:0, 5:0, 6:11, 7:9, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	11: {1:5, 2:0, 3:0, 4:0, 5:0, 6:10, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	12: {1:13, 2:4, 3:0, 4:0, 5:0, 6:3, 7:13, 8:7, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	13: {1:14, 2:0, 3:0, 4:0, 5:0, 6:0, 7:12, 8:7, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	14: {1:13, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:7, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	15: {1:0, 2:9, 3:0, 4:0, 5:0, 6:16, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'},
	16: {1:0, 2:0, 3:1, 4:0, 5:0, 6:15, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0, 'level_name':'save level'}
}

levels_visited = {'got_map': False}
saved_levels_visited = {}

exits = {
	0:0, 1:1, 2:1
}

enemy_data = {
	'guard': {'health': 100, 'exp': 100, 'damage': 20, 'attack_type': 'slash', 'attack_sound':'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_distance': 80, 'alert_distance': 360}
}

bosses = {'boss_1': True, 'boss_2': True, 'boss_3': True}

dialogues = {
'NPC0': ['Information', \
		  'Welcome. Neobits are the currency around here. The', \
		  'more you acquire the more you can do. If you die, all',
		  'your neobits go to the state.'],
'NPC1': ['Local', \
		  "Woah, nice sword duuuude. Old school! Press x to", \
		  'swing it buddy. That should protect you around', \
	      'here. for now...'],
'NPC2': ['Scientist', \
	  "Consent to give us your biometrics information", \
	  "and if you die, you will automatically regenerate ", \
      "here."],
'NPC3': ['Engineer', \
		  "Hey stranger. Here, take this prototype jetpack I made.", \
		  "It will be useful getting around here. Hold shift while", \
	      "in the air to use."],
'NPC4': ['Doc', \
		  "I'm sure I left an adrenaline shot around somewhere?", \
		  "Anyway, take this tracker. It will allow you to see", \
	      "where you have been by pressing space bar."],
'NPC5': ['Druglord', \
		  "Brave you are, coming here uninvited. Yes, that is an", \
		  "elusive railgun. Bring me 200 neobits and it's yours.", \
	      "I promise....."],
'NPC6': ['Henchman', \
		  "What you looking at punk? Best be outta here soon", \
		  "before I introduce you to my two friends here....", \
	      ""],
'NPC7': ['Information', \
		  "All employees - please remember to bring your jump", \
		  "boots to ascend the high walls in the engineering", \
	      "sector."],
'NPC8': ['Access denied!!!', \
	  "________________ Password required _________________", \
	  "", \
      ""],
'NPC9': ['Worker', \
	  "I lost my arm and eyes in here. It's cool though,", \
	  "they fitted me with this mechanical arm and welding", \
      "glasses so now I can work all day! I think..."],
'NPC10': ['Information', \
		  "Guns are for guards only! Press z to draw your gun.", \
		  "When gun is drawn, press x to fire. Press tab to", \
	      'toggle between guns.'],
'NPC11': ['Envirosuit dispenser', \
		  "The environsuit gives you immunity to electric", \
		  "shocks and toxic waters. Wade through the sewers", \
	      "at will, If that's your kinda thing?!"],
'NPC12': ['Speed', \
		  "Hey, they call me Speed. Especially when I use that", \
		  "warp core baby! Take it bro, you can go faster than", \
	      "you ever thought possible, but it's short lived."],
'NPC13': ['Cyber Monk', \
		  "Welcome to the shrine of other worlds. We are", \
		  "currently exhibiting the magnaglove. Made of such", \
	      "high friction material it can get you up walls..."],
'NPC14': ['Cyber Monk', \
		  "Did you steal the magnaglove? We will make you pay.", \
		  "Your time will come!", \
	      ""],

}


