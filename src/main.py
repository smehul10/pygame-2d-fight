import pygame
import sys
from classes import Fighter, Sprite
from utils import rectangular_collision, update_timer, determine_winner
import os

pygame.init()

# --- Setup ---
WIDTH, HEIGHT = 1024, 576
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Fighting Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)

gravity = 0.7
start_time = pygame.time.get_ticks()
game_over_flag = [False]

# --- Background ---
print(os.path.abspath('../assets/img/background.png'))
background = Sprite((0, 0), '../assets/img/background.png')

shop = Sprite((600, 128), '../assets/img/shop.png', scale=2.75, frames_max=6)

# --- Fighters ---
def create_fighters():
    p = Fighter(
        position=(0, 0),
        velocity=(0, 0),
        image_path='../assets/img/samuraiMack/Idle.png',
        frames_max=8,
        scale=2.5,
        offset=(215, 157),
        sprites={
            'idle': {'imageSrc': '../assets/img/samuraiMack/Idle.png', 'framesMax': 8},
            'run': {'imageSrc': '../assets/img/samuraiMack/Run.png', 'framesMax': 8},
            'jump': {'imageSrc': '../assets/img/samuraiMack/Jump.png', 'framesMax': 2},
            'fall': {'imageSrc': '../assets/img/samuraiMack/Fall.png', 'framesMax': 2},
            'attack1': {'imageSrc': '../assets/img/samuraiMack/Attack1.png', 'framesMax': 6},
            'takeHit': {'imageSrc': '../assets/img/samuraiMack/Take Hit - white silhouette.png', 'framesMax': 4},
            'death': {'imageSrc': '../assets/img/samuraiMack/Death.png', 'framesMax': 6}
        },
        attack_box={'offset': (100, 50), 'width': 160, 'height': 50}
    )
    e = Fighter(
        position=(400, 100),
        velocity=(0, 0),
        color='blue',
        image_path='../assets/img/kenji/Idle.png',
        frames_max=4,
        scale=2.5,
        offset=(215, 167),
        sprites={
            'idle': {'imageSrc': '../assets/img/kenji/Idle.png', 'framesMax': 4},
            'run': {'imageSrc': '../assets/img/kenji/Run.png', 'framesMax': 8},
            'jump': {'imageSrc': '../assets/img/kenji/Jump.png', 'framesMax': 2},
            'fall': {'imageSrc': '../assets/img/kenji/Fall.png', 'framesMax': 2},
            'attack1': {'imageSrc': '../assets/img/kenji/Attack1.png', 'framesMax': 4},
            'takeHit': {'imageSrc': '../assets/img/kenji/Take hit.png', 'framesMax': 3},
            'death': {'imageSrc': '../assets/img/kenji/Death.png', 'framesMax': 7}
        },
        attack_box={'offset': (-170, 50), 'width': 170, 'height': 50}
    )
    return p, e

player, enemy = create_fighters()

# --- Input State ---
keys = {'a': False, 'd': False, 'w': False, 'left': False, 'right': False, 'up': False}
player_last_key = ''
enemy_last_key = ''

# --- Game Loop ---
running = True
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    background.update(screen)
    shop.update(screen)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 38))
    screen.blit(overlay, (0, 0))

    player.update(screen, gravity, HEIGHT)
    enemy.update(screen, gravity, HEIGHT)

    player.velocity.x = 0
    enemy.velocity.x = 0

    if not player.dead:
        if keys['a'] and player_last_key == 'a':
            player.velocity.x = -5
            player.switch_sprite('run')
        elif keys['d'] and player_last_key == 'd':
            player.velocity.x = 5
            player.switch_sprite('run')
        else:
            player.switch_sprite('idle')

        if player.velocity.y < 0:
            player.switch_sprite('jump')
        elif player.velocity.y > 0:
            player.switch_sprite('fall')

    if not enemy.dead:
        if keys['left'] and enemy_last_key == 'left':
            enemy.velocity.x = -5
            enemy.switch_sprite('run')
        elif keys['right'] and enemy_last_key == 'right':
            enemy.velocity.x = 5
            enemy.switch_sprite('run')
        else:
            enemy.switch_sprite('idle')

        if enemy.velocity.y < 0:
            enemy.switch_sprite('jump')
        elif enemy.velocity.y > 0:
            enemy.switch_sprite('fall')

    if rectangular_collision(player, enemy) and player.is_attacking and player.frames_current == 4:
        enemy.take_hit()
        player.is_attacking = False

    if player.is_attacking and player.frames_current == 4:
        player.is_attacking = False

    if rectangular_collision(enemy, player) and enemy.is_attacking and enemy.frames_current == 2:
        player.take_hit()
        enemy.is_attacking = False

    if enemy.is_attacking and enemy.frames_current == 2:
        enemy.is_attacking = False

    if enemy.health <= 0 and not enemy.dead:
        enemy.switch_sprite('death')
    elif player.health <= 0 and not player.dead:
        player.switch_sprite('death')

    if (enemy.health <= 0 or player.health <= 0) and not game_over_flag[0]:
        determine_winner(player, enemy, font, screen)
        game_over_flag[0] = True

    if game_over_flag[0]:
        restart_text = font.render("Press R to Restart", True, (255, 255, 0))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)

    update_timer(screen, font, start_time, player, enemy, game_over_flag)

    # Health Bars
    pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 255, 0), (20, 20, 200 * (player.health / 100), 20))
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 220, 20, 200, 20))
    pygame.draw.rect(screen, (0, 255, 0), (WIDTH - 220, 20, 200 * (enemy.health / 100), 20))

    pygame.display.flip()

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if not player.dead:
                if event.key == pygame.K_a:
                    keys['a'] = True
                    player_last_key = 'a'
                elif event.key == pygame.K_d:
                    keys['d'] = True
                    player_last_key = 'd'
                elif event.key == pygame.K_w:
                    player.velocity.y = -30
                elif event.key == pygame.K_SPACE:
                    player.attack()
            if not enemy.dead:
                if event.key == pygame.K_LEFT:
                    keys['left'] = True
                    enemy_last_key = 'left'
                elif event.key == pygame.K_RIGHT:
                    keys['right'] = True
                    enemy_last_key = 'right'
                elif event.key == pygame.K_UP:
                    enemy.velocity.y = -30
                elif event.key == pygame.K_DOWN:
                    enemy.attack()

            if event.key == pygame.K_r and game_over_flag[0]:
                player, enemy = create_fighters()
                start_time = pygame.time.get_ticks()
                game_over_flag[0] = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                keys['a'] = False
            elif event.key == pygame.K_d:
                keys['d'] = False
            elif event.key == pygame.K_LEFT:
                keys['left'] = False
            elif event.key == pygame.K_RIGHT:
                keys['right'] = False

pygame.quit()
sys.exit()
