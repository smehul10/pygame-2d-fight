import pygame
from abc import ABC, abstractmethod

# Abstract base class
class AbstractSprite(ABC):
    def __init__(self, position):
        self.position = pygame.Vector2(position)

    @abstractmethod
    def draw(self, surface):
        pass

    @abstractmethod
    def update(self, surface):
        pass


class Sprite(AbstractSprite):
    def __init__(self, position, image_path, scale=1, frames_max=1, offset=(0, 0)):
        super().__init__(position)
        self.scale = scale
        self.frames_max = frames_max
        self.frames_current = 0
        self.frames_elapsed = 0
        self.frames_hold = 5
        self.offset = pygame.Vector2(offset)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.sprite_width = self.image.get_width() // self.frames_max
        self.sprite_height = self.image.get_height()
        self.rect = pygame.Rect(self.position.x, self.position.y, self.sprite_width, self.sprite_height)

    def draw(self, surface):
        frame_rect = pygame.Rect(self.frames_current * self.sprite_width, 0, self.sprite_width, self.sprite_height)
        scaled_image = pygame.transform.scale(
            self.image.subsurface(frame_rect),
            (int(self.sprite_width * self.scale), int(self.sprite_height * self.scale))
        )
        surface.blit(scaled_image, (self.position.x - self.offset.x, self.position.y - self.offset.y))

    def animate_frames(self):
        self.frames_elapsed += 1
        if self.frames_elapsed % self.frames_hold == 0:
            if self.frames_current < self.frames_max - 1:
                self.frames_current += 1
            else:
                self.frames_current = 0

    def update(self, surface):
        self.draw(surface)
        self.animate_frames()


class Fighter(Sprite):
    def __init__(self, position, velocity, color='red', image_path=None, scale=1, frames_max=1, offset=(0, 0),
                 sprites=None, attack_box=None):
        super().__init__(position, image_path, scale, frames_max, offset)
        self.velocity = pygame.Vector2(velocity)
        self.color = color
        self.attack_box_offset = pygame.Vector2(attack_box.get('offset', (0, 0)))
        self.attack_box_size = (attack_box.get('width', 0), attack_box.get('height', 0))
        self.attack_box_position = self.position + self.attack_box_offset
        self.is_attacking = False
        self.health = 100
        self.dead = False
        self.sprites = sprites or {}
        self.load_sprites()

        # --- Double Jump Support ---
        self.max_jumps = 2
        self.jumps_left = self.max_jumps

    def load_sprites(self):
        for key, sprite in self.sprites.items():
            sprite['image'] = pygame.image.load(sprite['imageSrc']).convert_alpha()

    def update(self, surface, gravity, screen_height):
        if not self.dead:
            self.animate_frames()

        self.attack_box_position = self.position + self.attack_box_offset
        self.position += self.velocity

        if self.position.y + self.sprite_height >= screen_height - 40:
            self.velocity.y = 0
            self.position.y = screen_height - 40 - self.sprite_height
            self.jumps_left = self.max_jumps  # Reset jump count on ground
        else:
            self.velocity.y += gravity

        self.draw(surface)

    def attack(self):
        if not self.dead:
            self.switch_sprite('attack1')
            self.is_attacking = True

    def take_hit(self):
        self.health -= 20
        if self.health <= 0:
            self.switch_sprite('death')
        else:
            self.switch_sprite('takeHit')

    def switch_sprite(self, sprite_name):
        if self.image == self.sprites.get('death', {}).get('image'):
            if self.frames_current < self.sprites['death']['framesMax'] - 1:
                return
            else:
                self.dead = True
                return

        if self.image == self.sprites.get('attack1', {}).get('image'):
            if self.frames_current < self.sprites['attack1']['framesMax'] - 1:
                return

        if self.image == self.sprites.get('takeHit', {}).get('image'):
            if self.frames_current < self.sprites['takeHit']['framesMax'] - 1:
                return

        if self.dead:
            return

        sprite = self.sprites.get(sprite_name)
        if not sprite or self.image == sprite['image']:
            return

        self.image = sprite['image']
        self.frames_max = sprite['framesMax']
        self.frames_current = 0
