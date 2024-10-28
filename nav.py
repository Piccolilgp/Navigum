import pygame
import cv2
import numpy as np
import random
import os
import sys
from PIL import Image


# Define o caminho para a pasta de imagens com base no diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))
image_player = os.path.join(script_dir, 'images', 'Navigum.gif')
image_enemy1 = os.path.join(script_dir, 'images', 'Enemy1.gif')
image_explosion = os.path.join(script_dir, 'images', 'explosion2.gif')
image_bg = os.path.join(script_dir, 'images', 'Bg4.jpg')
image_laserplayer = os.path.join(script_dir, 'images', 'laserplayer.png')
image_laserenemy = os.path.join(script_dir, 'images', 'laserenemy2.png')
loginscreen_intro = os.path.join(script_dir, 'images', 'LogoScreen.mp4')
image_life_item = os.path.join(script_dir, 'images', 'heart.png')
load_laser_sound = os.path.join(script_dir, 'sfx', 'laser.mp3')
load_explosion_sound = os.path.join(script_dir, 'sfx', 'explosion.mp3')
load_main_theme = os.path.join(script_dir, 'sfx', 'saturn_bloody_tears.mp3')

pygame.init()
pygame.mixer.init()


def load_gif(filename):
    img = Image.open(filename)
    frames = []
    
    try:
        while True:
            frame = img.copy().convert("RGBA")
            frames.append(pygame.image.fromstring(frame.tobytes(), frame.size, 'RGBA'))
            img.seek(len(frames))
    except EOFError:
        pass
    
    return frames


x = 1200
y = 720
score = 0
lives = 3
font = pygame.font.SysFont('Segoe', 36)
enemy_active = True
game_over = False
game_started = False
screen = pygame.display.set_mode((x, y))
pygame.display.set_caption('Navigum 🚀 v.1.0 BETA')
player1 = load_gif(image_player)
frame_index1 = 0
clock = pygame.time.Clock()
enemy1 = load_gif(image_enemy1)
frame_index2 = 0
explosion_frames = load_gif(image_explosion)
explosion_index = 0
explosion_active = False
explosion_timer = 0
explosion_duration = 70  
bg1 = pygame.image.load(image_bg).convert_alpha()
bg1 = pygame.transform.scale(bg1, (x, y))

shoot_sound = pygame.mixer.Sound(load_laser_sound)
explosion_sound = pygame.mixer.Sound(load_explosion_sound)
music_main_theme = pygame.mixer.Sound(load_main_theme)

rodando = 0
pausado = 1
jogo = rodando

def sons_ligados():
    pygame.mixer.music.unpause()
    pygame.mixer.music.set_volume(0.3)
    shoot_sound.set_volume(0.2)
    explosion_sound.set_volume(0.4)
def sons_desligados():
    pygame.mixer.music.pause()  # Pausa a música
    shoot_sound.set_volume(0.0)
    explosion_sound.set_volume(0.0)
def musica_ligada():
    pygame.mixer.music.load(load_main_theme)
    pygame.mixer.music.play(-1)
def musica_desligada():
    pygame.mixer.music.stop()

musica_ativa = True
sons_ativos = True
sons_ligados()
pygame.mixer.music.load(load_main_theme)
pygame.mixer.music.play(-1)

player_x = 50
player_y = (y - player1[0].get_height()) // 2

upper_limit = 65
lower_limit = y - 100 - player1[0].get_height()


def reset_game():
    global score, lives, game_over, player_x, player_y, player_projectiles, enemy_projectiles, enemies
    score = 0
    lives = 3
    game_over = False
    player_x = 50
    player_y = (y - player1[0].get_height()) // 2
    player_projectiles.clear()
    enemy_projectiles.clear()
    enemies = [create_enemy() for _ in range(3)]
    


def display_video_login(video_path):
    cap = cv2.VideoCapture(video_path)

    
    frame_delay = 20  

    while True:
        
        if not cap.isOpened():
            cap = cv2.VideoCapture(video_path)
        
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  
            continue

        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)  
        frame = np.flipud(frame)  

        
        frame_surface = pygame.surfarray.make_surface(frame)

        
        screen.blit(frame_surface, (0, 0))
        pygame.display.flip()

        
        pygame.time.delay(frame_delay)

        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  
                    cap.release()
                    return
                elif event.key == pygame.K_KP_ENTER:
                    cap.release()
                    return
                elif event.key == pygame.K_ESCAPE: 
                    cap.release()
                    pygame.quit()
                    sys.exit()


display_video_login(loginscreen_intro)  


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = enemy1[0].get_width()
        self.height = enemy1[0].get_height()
        self.speed_x = random.choice([-2, 2])
        self.speed_y = random.choice([-2, 2])
        self.vivo = True
        self.shoot_interval = random.randint(50, 150)
        self.shoot_timer = 0

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x < x // 2 or self.x + self.width > x - 50:
            self.speed_x = -self.speed_x 
        if self.y < 20 or self.y + self.height > y - 100:
            self.speed_y = -self.speed_y

    def draw(self, screen):
        if self.vivo:
            
            screen.blit(enemy1[frame_index2], (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def shoot(self):
        enemy_projectile_speed = -5
        if self.shoot_timer >= self.shoot_interval and self.vivo:
            enemy_projectile_y = self.y + self.height // 2
            enemy_projectiles.append(Projectile(self.x, enemy_projectile_y, enemy_projectile_image, enemy_projectile_speed))
            self.shoot_timer = 1
            self.shoot_interval = random.randint(1000 , 2000)
        else:
            self.shoot_timer += 1


def create_enemy():

    enemy_x = x - 50 - enemy1[0].get_width()
    enemy_y = random.randint(upper_limit, lower_limit)
    return Enemy(enemy_x, enemy_y)


enemies = [create_enemy() for _ in range(3)]
bg_x1 = 0
bg_x2 = bg1.get_width()
player_projectiles = []
enemy_projectiles = []
life_items = []  
space_pressed = False
player_projectile_image = pygame.image.load(image_laserplayer).convert_alpha()
enemy_projectile_image = pygame.image.load(image_laserenemy).convert_alpha()
player_projectile_image = pygame.transform.scale(player_projectile_image, (80, 20))
enemy_projectile_image = pygame.transform.scale(enemy_projectile_image, (60, 30))
heart_item = pygame.image.load(image_life_item).convert_alpha()

class Projectile:
    def __init__(self, x, y, image, speed):
        self.x = x
        self.y = y
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()
        self.speed = speed

    def move(self):
        self.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class LifeItem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_life_item).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vivo = True
    
    def move(self):
        self.x -= +3

    def draw(self, screen):
        if self.vivo:  
            screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


while True:

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                if sons_ativos:
                    sons_desligados()
                else:
                    sons_ligados()
                sons_ativos = not sons_ativos
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if musica_ativa:
                    musica_desligada()
                else:
                    musica_ligada()
                musica_ativa = not musica_ativa
        if keys[pygame.K_ESCAPE]:
            display_video_login(loginscreen_intro)   
        if keys[pygame.K_p]:
            if jogo != pausado:
                jogo = pausado
            else:
                jogo = rodando
                sons_ligados()
            continue

    if game_over:
        game_over_text = font.render("Game Over! Press ENTER to Restart or Esc to quit.", True, (255, 255, 255))
        screen.blit(game_over_text, (x // 2 - game_over_text.get_width() // 2, y // 2))
        pygame.display.flip()
        
        
        if keys[pygame.K_RETURN]:
            reset_game()
        elif keys[pygame.K_KP_ENTER]:
            reset_game()
        elif keys[pygame.K_ESCAPE]:
            display_video_login(loginscreen_intro)
        continue
    if jogo == pausado:
        sons_desligados()
        pause_font = pygame.font.SysFont('Arial', 60)
        pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(pause_text, (x // 2 - pause_text.get_width() // 2, y // 2))
        pygame.display.flip()
        continue

    if keys[pygame.K_UP]:
        player_y -= 5
    if keys[pygame.K_DOWN]:
        player_y += 5

    if player_y < upper_limit:
        player_y = upper_limit
    if player_y > lower_limit:
        player_y = lower_limit

    if keys[pygame.K_SPACE]:
        if not space_pressed:
            projectile_y = player_y + player1[frame_index1].get_height() // 2 - 2
            player_projectiles.append(Projectile(player_x + player1[frame_index1].get_width(), projectile_y, player_projectile_image, 10))
            space_pressed = True
            shoot_sound.play()
            
    else:
        space_pressed = False

    for projectile in player_projectiles[:]:
        projectile.move()
        if projectile.x > x:
            player_projectiles.remove(projectile)

    for projectile in enemy_projectiles[:]:
        projectile.move()
        if projectile.x < 0:
            enemy_projectiles.remove(projectile)

    for enemy in enemies:
        if enemy.vivo:
            enemy.move()
            enemy.shoot()
            for projectile in player_projectiles[:]:
                if projectile.get_rect().colliderect(enemy.get_rect()):
                    player_projectiles.remove(projectile)
                    score += 1
                    explosion_active = True
                    explosion_sound.play()
                    explosion_x = enemy.x
                    explosion_y = enemy.y
                    enemy.vivo = False
                    explosion_timer = 0
                    
                    if random.random() < 0.05:  # 5% de chance
                        life_item = LifeItem(enemy.x, enemy.y)
                        life_items.append(life_item)

    player_rect = pygame.Rect(player_x, player_y, player1[0].get_width(), player1[0].get_height())
    
    for projectile in enemy_projectiles[:]:
        if projectile.get_rect().colliderect(player_rect):
            enemy_projectiles.remove(projectile)
            lives -= 1
            if lives <= 0:
                game_over = True
    
    for life_item in life_items[:]:
        life_item.move()
        if life_item.x < 0:  
            life_items.remove(life_item)
        if life_item.vivo and player_rect.colliderect(life_item.get_rect()):
            life_items.remove(life_item)
            lives += 1  

    enemies = [enemy for enemy in enemies if enemy.vivo]
    while len(enemies) < 3:
        enemies.append(create_enemy())                   

    bg_x1 -= 2
    bg_x2 -= 2

    if bg_x1 <= -bg1.get_width():
        bg_x1 = bg1.get_width()
    if bg_x2 <= -bg1.get_width():
        bg_x2 = bg1.get_width()

    screen.blit(bg1, (bg_x1, 0))
    screen.blit(bg1, (bg_x2, 0))
    screen.blit(player1[frame_index1], (player_x, player_y))

    for enemy in enemies:
        enemy.draw(screen)

    for projectile in player_projectiles:
        projectile.draw(screen)

    for projectile in enemy_projectiles:
        projectile.draw(screen)

    for life_item in life_items:
         life_item.draw(screen)

    if explosion_active:
        screen.blit(explosion_frames[explosion_index], (explosion_x, explosion_y))
        explosion_index = (explosion_index + 1) % len(explosion_frames)
        explosion_timer += 1
        if explosion_timer >= explosion_duration:
            explosion_active = False
    
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    lives_text = font.render(f'Lives: {lives}', True, (255, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    info_font = pygame.font.SysFont('Arial', 15)
    info_text = info_font.render("Press 'S' to turn off sound, 'ESC' for quit, 'P' for pause", True, (255, 255, 255))
    screen.blit(info_text, (400, 650))



    pygame.display.flip()

    frame_index1 = (frame_index1 + 1) % len(player1)
    frame_index2 = (frame_index2 + 1) % len(enemy1)  
    clock.tick(150)

pygame.quit()
