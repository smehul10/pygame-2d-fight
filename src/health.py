# src/health.py
import pygame

class HealthComponent:
    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.invincible = False

    def take_damage(self, amount):
        if self.invincible:
            return
        self.current_hp = max(0, self.current_hp - amount)

    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)


class HealthBar:
    def __init__(self, component, x, y, width, height):
        self.comp = component
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0), self.rect)
        # Foreground (green) scaled to current HP
        pct = self.comp.current_hp / self.comp.max_hp
        fg = self.rect.copy()
        fg.width = int(self.rect.width * pct)
        pygame.draw.rect(surface, (0, 255, 0), fg)

