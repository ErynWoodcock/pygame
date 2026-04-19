import pygame
import math
import random

pygame.init()
# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
GAME_NAME = "Slasher//io"
pygame.display.set_caption(GAME_NAME)
# Colours
SWORD_COLOUR = (100, 100, 100)
BACKGROUND_COLOUR = (100, 50, 0)
MONSTER_COLOUR = (255, 0, 0)
PLAYER_COLOUR = (0, 255, 0)
# Player setup
PLAYER_RADIUS = 20
PLAYER_SPEED = 1.5
# Sword setup
SWORD_LENGTH = 50
SWORD_WIDTH = 8
SWORD_SWING_SPEED = 0.1
# Monster setup
MONSTER_RADIUS = 18
MONSTER_SPEED = 1.2 

clock = pygame.time.Clock()

'''
All The player code is contained within this Player class section.
Within is a folder for drawing the shape, Movement, and the sword.
'''
class Player:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.angle = 0 
		self.health = 100
		self.last_damage_time = 0 
		self.vx = 0
		self.vy = 0

	def move(self, keys):
		if keys[pygame.K_w]:
			self.y -= PLAYER_SPEED
		if keys[pygame.K_s]:
			self.y += PLAYER_SPEED
		if keys[pygame.K_a]:
			self.x -= PLAYER_SPEED
		if keys[pygame.K_d]:
			self.x += PLAYER_SPEED
		self.x = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, self.x))
		self.y = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, self.y))

	def update_sword(self):
		self.angle += SWORD_SWING_SPEED
		if self.angle > 2 * math.pi:
			self.angle -= 2 * math.pi

	def update(self):
		# Apply knockback velocity and slow it over time
		self.x += self.vx
		self.y += self.vy
		# Friction
		self.vx *= 0.85
		self.vy *= 0.85
		# Keep player within bounds
		self.x = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, self.x))
		self.y = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, self.y))

	def draw(self, surface):
		pygame.draw.circle(surface, PLAYER_COLOUR, (int(self.x), int(self.y)), PLAYER_RADIUS)
		sword_x = self.x + math.cos(self.angle) * (PLAYER_RADIUS + SWORD_LENGTH)
		sword_y = self.y + math.sin(self.angle) * (PLAYER_RADIUS + SWORD_LENGTH)
		pygame.draw.line(surface, SWORD_COLOUR, (self.x, self.y), (sword_x, sword_y), SWORD_WIDTH)

	def get_sword_segment(self):
		start = (self.x, self.y)
		end = (self.x + math.cos(self.angle) * (PLAYER_RADIUS + SWORD_LENGTH),
			   self.y + math.sin(self.angle) * (PLAYER_RADIUS + SWORD_LENGTH))
		return start, end

'''
All the Monster code is contained in this class folder.
Within is folders for spawn event, movement, drawing the monster character, attack, and take damage.
'''
class Monster:
	def __init__(self):
		edge = random.choice(['top', 'bottom', 'left', 'right'])
		if edge == 'top':
			self.x = random.randint(MONSTER_RADIUS, WIDTH - MONSTER_RADIUS)
			self.y = MONSTER_RADIUS
		elif edge == 'bottom':
			self.x = random.randint(MONSTER_RADIUS, WIDTH - MONSTER_RADIUS)
			self.y = HEIGHT - MONSTER_RADIUS
		elif edge == 'left':
			self.x = MONSTER_RADIUS
			self.y = random.randint(MONSTER_RADIUS, HEIGHT - MONSTER_RADIUS)
		else:
			self.x = WIDTH - MONSTER_RADIUS
			self.y = random.randint(MONSTER_RADIUS, HEIGHT - MONSTER_RADIUS)
		self.alive = True
		self.health = 3  # Monsters take 3 hits to kill
		self.last_hit_time = 0
		self.vx = 0
		self.vy = 0

	def move_towards(self, target_x, target_y):
		if not self.alive:
			return
		dx = target_x - self.x
		dy = target_y - self.y
		dist = math.hypot(dx, dy)
		if dist > 0:
			self.x += MONSTER_SPEED * dx / dist
			self.y += MONSTER_SPEED * dy / dist

	def draw(self, surface):
		if self.alive:
			pygame.draw.circle(surface, MONSTER_COLOUR, (int(self.x), int(self.y)), MONSTER_RADIUS)

	def update(self):
		# Knockback velocity and movement
		self.x += self.vx
		self.y += self.vy
		self.vx *= 0.85
		self.vy *= 0.85
		# Keep monsters in bounds
		self.x = max(MONSTER_RADIUS, min(WIDTH - MONSTER_RADIUS, self.x))
		self.y = max(MONSTER_RADIUS, min(HEIGHT - MONSTER_RADIUS, self.y))

	def check_hit(self, sword_segment):
		if not self.alive:
			return
		(start_x, start_y), (end_x, end_y) = sword_segment
		# Distance from point to line segment
		px, py = self.x, self.y
		seg_dx = end_x - start_x
		seg_dy = end_y - start_y
		seg_len_sq = seg_dx * seg_dx + seg_dy * seg_dy
		if seg_len_sq == 0:
			closest_x, closest_y = start_x, start_y
		else:
			# Project point onto segment, clamp t between 0 and 1
			t = ((px - start_x) * seg_dx + (py - start_y) * seg_dy) / seg_len_sq
			t = max(0, min(1, t))
			closest_x = start_x + seg_dx * t
			closest_y = start_y + seg_dy * t
		# If within reach of the sword (accounting for sword thickness), count as hit
		dist_to_sword = math.hypot(px - closest_x, py - closest_y)
		if dist_to_sword < MONSTER_RADIUS + SWORD_WIDTH / 2:
			current_time = pygame.time.get_ticks()
			if current_time - self.last_hit_time > 500:  # Prevent multiple hits in quick succession
				self.last_hit_time = current_time
				self.health -= 1
				# Knockback: push monster away from player with velocity
				dx = self.x - player.x
				dy = self.y - player.y
				dist = math.hypot(dx, dy)
				if dist > 0:
					knockback_speed = 12
					self.vx = (dx / dist) * knockback_speed
					self.vy = (dy / dist) * knockback_speed
				if self.health <= 0:
					self.alive = False
					global score
					score += 1

	def attack_player(self, player):
		if not self.alive:
			return
		dist = math.hypot(self.x - player.x, self.y - player.y)
		if dist < MONSTER_RADIUS + PLAYER_RADIUS:
			current_time = pygame.time.get_ticks()
			if current_time - player.last_damage_time > 1000:  # 1 second cooldown
				player.last_damage_time = current_time
				player.health -= 10
				# Knockback for player
				dx = player.x - self.x
				dy = player.y - self.y
				dist = math.hypot(dx, dy)
				if dist > 0:
					knockback_speed = 10
					player.vx = (dx / dist) * knockback_speed
					player.vy = (dy / dist) * knockback_speed
player = Player(WIDTH // 2, HEIGHT // 2)
monsters = []

game_state = 'menu'
paused = False
game_over = False
game_start_time = 0
last_spawn_time = 0
spawn_interval = 1500 
score = 0
pause_font = pygame.font.SysFont(None, 64)


SPAWN_EVENT = pygame.USEREVENT + 1

running = True
while running:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		# Menu
		if game_state == 'menu' and event.type == pygame.MOUSEBUTTONDOWN:
			# Check if click is within play button bounds
			mouse_x, mouse_y = pygame.mouse.get_pos()
			button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
			if button_rect.collidepoint(mouse_x, mouse_y):
				# Start the game
				game_state = 'play'
				paused = False
				game_start_time = pygame.time.get_ticks()
				last_spawn_time = game_start_time
				spawn_interval = 1500  # Start with 1.5 seconds between spawns
				# Reset the game
				monsters.clear()
				player.x = WIDTH // 2
				player.y = HEIGHT // 2
				player.angle = 0
				player.health = 100
				player.last_damage_time = 0
				score = 0
				game_over = False

		# Pause game
		if game_state == 'play' and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			paused = not paused

		# Handle pause menu button click
		if paused and event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			home_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
			if home_button_rect.collidepoint(mouse_x, mouse_y):
				# Return to home screen
				game_state = 'menu'
				paused = False

	if game_state == 'play' and not paused:
		keys = pygame.key.get_pressed()
		player.move(keys)
		player.update_sword()
		player.update()

		# Increase spawn rate over time (gradually spawn faster)
		elapsed_time = pygame.time.get_ticks() - game_start_time
		# Start at 1500ms and decrease to 400ms over time
		spawn_interval = max(400, 1500 - (elapsed_time // 200))
		
		# Manual spawn timer
		current_time = pygame.time.get_ticks()
		if current_time - last_spawn_time >= spawn_interval:
			last_spawn_time = current_time
			monsters.append(Monster())

		sword_segment = player.get_sword_segment()
		for monster in monsters:
			monster.move_towards(player.x, player.y)
			monster.update()
			monster.check_hit(sword_segment)
			monster.attack_player(player)

		# Remove dead monsters
		monsters = [m for m in monsters if m.alive]

		# Check for player death
		if player.health <= 0:
			game_state = 'menu'
			game_over = True

	# Draw
	screen.fill(BACKGROUND_COLOUR)
	if game_state == 'menu':
		# Simple title screen with button
		font = pygame.font.SysFont(None, 56)
		button_font = pygame.font.SysFont(None, 48)
		title_text = 'Game Over' if game_over else GAME_NAME
		title = font.render(title_text, True, (255, 255, 255))
		screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
		
		# Draw play button with hover effect
		button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
		mouse_x, mouse_y = pygame.mouse.get_pos()
		is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
		button_color = (0, 255, 0) if is_hovering else (0, 200, 0)  # Brighter green on hover
		pygame.draw.rect(screen, button_color, button_rect)  # Button fill
		pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)  # White border
		button_label = 'Retry' if game_over else 'Play'
		button_text = button_font.render(button_label, True, (0, 0, 0))  # Black text
		screen.blit(button_text, button_text.get_rect(center=button_rect.center))
	else:
		player.draw(screen)
		for monster in monsters:
			monster.draw(screen)

		# Player health display
		health_text = pause_font.render(f'Health: {max(0, player.health)}', True, (255, 255, 255))
		screen.blit(health_text, (10, 10))
		score_text = pause_font.render(f'Score: {score}', True, (255, 255, 255))
		screen.blit(score_text, (10, 50))

		if paused:
			pause_text = pause_font.render('Paused', True, (255, 255, 255))
			pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
			# Semi-transparent overlay
			overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
			overlay.fill((0, 0, 0, 120))
			screen.blit(overlay, (0, 0))
			screen.blit(pause_text, pause_rect)
			
			# Draw "Back to Home" button
			button_font = pygame.font.SysFont(None, 40)
			home_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
			mouse_x, mouse_y = pygame.mouse.get_pos()
			is_hovering = home_button_rect.collidepoint(mouse_x, mouse_y)
			button_color = (200, 0, 0) if is_hovering else (150, 0, 0)  # Red button, brighter on hover
			pygame.draw.rect(screen, button_color, home_button_rect)
			pygame.draw.rect(screen, (255, 255, 255), home_button_rect, 2)  # White border
			button_text = button_font.render('Back to Home', True, (255, 255, 255))
			screen.blit(button_text, button_text.get_rect(center=home_button_rect.center))

	pygame.display.flip()
	clock.tick(60)

pygame.quit()
