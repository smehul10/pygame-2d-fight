import pygame

# Collision detection using Fighter attributes
def rectangular_collision(attacker, target):
    ax, ay = attacker.attack_box_position
    aw, ah = attacker.attack_box_size
    tx, ty = target.position
    tw, th = target.sprite_width, target.sprite_height

    return (
        ax + aw >= tx and
        ax <= tx + tw and
        ay + ah >= ty and
        ay <= ty + th
    )

# Display winner text on the screen
def determine_winner(player, enemy, font, screen):
    if player.health == enemy.health:
        text = "Tie"
    elif player.health > enemy.health:
        text = "Player 1 Wins"
    else:
        text = "Player 2 Wins"

    render_text(screen, text, font)

# Render centered text
def render_text(screen, text, font):
    surface = font.render(text, True, (255, 255, 255))
    rect = surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(surface, rect)

# Draws the countdown timer and triggers winner logic
def update_timer(screen, font, start_time, player, enemy):
    elapsed = pygame.time.get_ticks() - start_time
    remaining = max(0, (60000 - elapsed) // 1000)

    if remaining == 0:
        determine_winner(player, enemy, font, screen)

    timer_surface = font.render(str(remaining), True, (255, 255, 255))
    screen.blit(timer_surface, (20, 20))