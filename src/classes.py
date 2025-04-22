import pygame
from abc import ABC, abstractmethod
from health import HealthComponent, HealthBar


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
        self.base_scale = scale
        self.frames_max = frames_max
        self.frames_current = 0
        self.frames_elapsed = 0
        self.frames_hold = 5
        self.offset = pygame.Vector2(offset)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.sprite_width = self.image.get_width() // self.frames_max
        self.sprite_height = self.image.get_height()
        self.rect = pygame.Rect(self.position.x, self.position.y, self.sprite_width, self.sprite_height)

    # def draw(self, surface):
    #     frame_rect = pygame.Rect(self.frames_current * self.sprite_width, 0, self.sprite_width, self.sprite_height)
    #     scaled_image = pygame.transform.scale(
    #         self.image.subsurface(frame_rect),
    #         (int(self.sprite_width * self.scale), int(self.sprite_height * self.scale))
    #     )
    #     surface.blit(scaled_image, (self.position.x - self.offset.x, self.position.y - self.offset.y))
    def draw(self, surface):
        # pick the right subframe
        frame_rect = pygame.Rect(
            self.frames_current * self.sprite_width,
            0,
            self.sprite_width,
            self.sprite_height
        )

        # scale the image
        scaled_w = int(self.sprite_width * self.scale)
        scaled_h = int(self.sprite_height * self.scale)
        scaled_image = pygame.transform.scale(
            self.image.subsurface(frame_rect),
            (scaled_w, scaled_h)
        )

        # Scale the offset by the current sprite scale
                # Invert the factor so offset shrinks when sprite grows
        scale_factor = self.base_scale / self.scale
        scaled_offset = self.offset * scale_factor

        # draw with the scaled offset
        surface.blit(
            scaled_image,
            (self.position.x - scaled_offset.x,
            self.position.y - scaled_offset.y)
        )

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
                 sprites=None, attack_box=None, character_profiles=None):
        super().__init__(position, image_path, scale, frames_max, offset)
        self.velocity = pygame.Vector2(velocity)
        self.color = color
        self.attack_box_offset = pygame.Vector2(attack_box.get('offset', (0, 0)))
        self.attack_box_size = (attack_box.get('width', 0), attack_box.get('height', 0))
        self.attack_box_position = self.position + self.attack_box_offset
        self.is_attacking = False
        #self.health = 100
        # Health logic separated into component and bar
        self.health_comp = HealthComponent(100)
        # Position the bar at top-left; tweak as desired
        self.health_bar  = HealthBar(self.health_comp, x=20, y=20, width=200, height=20)
        self.damage = 20
        self.dead = False
        self.sprites = sprites or {}
        self.load_sprites()

        # --- Double Jump Support ---
        self.max_jumps = 2
        self.jumps_left = self.max_jumps


        # --- New for transformation ---
        self.character_profiles = character_profiles or {}
        self.transform_active = False
        self.transform_count = 0        

    def load_sprites(self):
        for key, sprite in self.sprites.items():
            sprite['image'] = pygame.image.load(sprite['imageSrc']).convert_alpha()

    # def update(self, surface, gravity, screen_height):
    #     if not self.dead:
    #         self.animate_frames()

    #     self.screen_height = screen_height

    #     self.attack_box_position = self.position + self.attack_box_offset
    #     self.position += self.velocity

    #     # --- Adjust ground collision depending on scale ---
    #     if self.scale == 2.5:
    #         # Normal size (no scaling)
    #         if self.position.y + self.sprite_height >= screen_height - 40:
    #             self.velocity.y = 0
    #             self.position.y = screen_height - 40 - self.sprite_height
    #             self.jumps_left = self.max_jumps
    #         else:
    #             self.velocity.y += gravity
    #     else:
    #         # Scaled up size (power mode)
    #         scaled_height = self.sprite_height * self.scale
    #         if self.position.y + scaled_height >= screen_height - 40:
    #             self.velocity.y = 0
    #             self.position.y = screen_height - 40 - scaled_height
    #             self.jumps_left = self.max_jumps
    #         else:
    #             self.velocity.y += gravity

    #     self.draw(surface)

 
    def update(self, surface, gravity, screen_height, screen_width):
        if not self.dead:
            self.animate_frames()

        self.screen_height = screen_height

        self.attack_box_position = self.position + self.attack_box_offset
        self.position += self.velocity

        # 🧱 X-axis barrier to keep fighters on screen
        self.position.x = max(0, min(self.position.x, 950))


        # --- New Ground Collision Handling ---
        if self.transform_active:
            scaled_height = self.sprite_height * self.scale
            if self.position.y + scaled_height >= screen_height - 40:
                self.velocity.y = 0
                self.position.y = screen_height - 40 - scaled_height
                self.jumps_left = self.max_jumps
            else:
                self.velocity.y += gravity
        else:
            if self.position.y + self.sprite_height >= screen_height - 40:
                self.velocity.y = 0
                self.position.y = screen_height - 40 - self.sprite_height
                self.jumps_left = self.max_jumps
            else:
                self.velocity.y += gravity

        # Revert transformation after timer expires
        if self.transform_active and pygame.time.get_ticks() >= self.transform_end_time:
            self.revert_to_base()

        self.draw(surface)

    
    # def draw(self, surface):
    #     # Choose current frame
    #     frame_rect = pygame.Rect(
    #         self.frames_current * self.sprite_width,
    #         0,
    #         self.sprite_width,
    #         self.sprite_height
    #     )
    #     # Scale the frame
    #     scaled_w = int(self.sprite_width * self.scale)
    #     scaled_h = int(self.sprite_height * self.scale)
    #     scaled_img = pygame.transform.scale(
    #         self.image.subsurface(frame_rect),
    #         (scaled_w, scaled_h)
    #     )
    #     # Compute X with offset scaled normally
    #     x = self.position.x - (self.offset.x * (self.scale / self.base_scale))
    #     # Compute Y: pin to ground when transformed or use normal offset
    #     if self.transform_active:
    #         y = self.screen_height - 40 - scaled_h
    #     else:
    #         y = self.position.y - (self.offset.y * (self.scale / self.base_scale))
    #     # Blit the sprite
    #     surface.blit(scaled_img, (x, y))
    def draw(self, surface):
        # 1) Pick the correct frame
        frame_rect = pygame.Rect(
            self.frames_current * self.sprite_width,
            0,
            self.sprite_width,
            self.sprite_height
        )
        # 2) Scale it
        scaled_w = int(self.sprite_width * self.scale)
        scaled_h = int(self.sprite_height * self.scale)
        scaled_img = pygame.transform.scale(
            self.image.subsurface(frame_rect),
            (scaled_w, scaled_h)
        )

        # 3) Compute X the same way you have been
        x = self.position.x - (self.offset.x * (self.scale / self.base_scale))

        # 4) Compute Y:
        if self.transform_active:
            # Pin the bottom of the sprite to screen_height - 40
            y = self.screen_height - 40 - scaled_h
            y = 120
        else:
            # Normal mode: use your standard offset logic
            y = self.position.y - (self.offset.y * (self.scale / self.base_scale))

        # 5) Draw it
        surface.blit(scaled_img, (x, y))

    def attack(self):
        if not self.dead:
            self.switch_sprite('attack1')
            self.is_attacking = True

    def take_hit(self, damage_amount):
        # self.health -= 20
        # if self.health <= 0:
        # Apply reduced damage when transformed, else full damage
        # dmg = 10 if self.transform_active else 20
        # self.health_comp.take_damage(dmg)
        # if self.health_comp.current_hp <= 0:
        #     self.switch_sprite('death')
        # else:
        #     self.switch_sprite('takeHit')
        self.health_comp.take_damage(damage_amount)
        if self.health_comp.current_hp <= 0:
            self.switch_sprite('death')
        else:
            self.switch_sprite('takeHit')

    # def transform(self, profile_name):
    #     if hasattr(self, 'transform_count') and self.transform_count >= 2:
    #         return
    #     if getattr(self, 'transform_active', False):
    #         return

    #     profile = self.character_profiles.get(profile_name)
    #     if not profile:
    #         return

    #     self.damage = profile['damage']
    #     self.sprites = profile['sprites']
    #     self.load_sprites()
    #     self.transform_active = True
    #     self.transform_end_time = pygame.time.get_ticks() + 5000  # 5 seconds
    #     if not hasattr(self, 'transform_count'):
    #         self.transform_count = 0
    #     self.transform_count += 1
    #     if profile_name == 'power':
    #         self.scale = 3.0  # make power character bigger
    #     else:
    #         self.scale = 2.5  # normal size
    # def transform(self):
    #     if self.transform_count >= 2:
    #         return
    #     if self.transform_active:
    #         return

    #     self.scale = 3.0   # Make character bigger
    #     self.damage = 40   # Increase attack damage
    #     self.transform_active = True
    #     self.transform_end_time = pygame.time.get_ticks() + 5000  # 5 seconds
    #     self.transform_count += 1

    #     # --- New: Reset Y position immediately ---
    #     if hasattr(self, 'screen_height'):
    #         self.position.y = self.screen_height - 40 - self.sprite_height * self.scale
    def transform(self):
        if self.transform_count >= 2:
            return
        if self.transform_active:
            return

        self.scale = 3.0
        self.damage = 40
        self.transform_active = True
        self.transform_end_time = pygame.time.get_ticks() + 5000
        self.transform_count += 1
        self.health_comp.invincible = True
        self.damage = 10

        # if hasattr(self, 'screen_height'):
        #     #self.position.y -= self.sprite_height * 0.25
        #     # Snap transformed sprite to the ground
        #     #self.position.y = self.screen_height - 40 - self.sprite_height * self.scale
        #     # Hardcode transformed sprite Y so it sits at ground level
        #     #self.position.y = self.screen_height - 150  # adjust 100 until aligned
        #     # Align transformed sprite on the ground, accounting for draw offset
        #     target_y = self.screen_height - 40 - self.sprite_height * self.scale
        #     # Calculate how draw() will shift by offset
        #     scale_factor = self.base_scale / self.scale
        #     offset_correction = self.offset.y * scale_factor
        #     # Position so that after draw's offset, the feet sit at target_y
        #     self.position.y = target_y + offset_correction


    # def revert_to_base(self):
    #     profile = self.character_profiles['base']
    #     self.damage = profile['damage']
    #     self.sprites = profile['sprites']
    #     self.load_sprites()
        #     self.transform_active = False
    def revert_to_base(self):
        self.scale = 2.5    # Return to normal size
        self.damage = 20    # Return to normal damage
        self.transform_active = False

        # --- New: Reset Y position immediately ---

        if hasattr(self, 'screen_height'):
            #self.position.y += self.sprite_height * 0.5
             # Snap reverted sprite back to the ground
            self.position.y = self.screen_height - 40 - self.sprite_height * self.scale

        self.health_comp.invincible = False
        self.damage = 20

    # def switch_sprite(self, sprite_name):
    #     if self.image == self.sprites.get('death', {}).get('image'):
    #         if self.frames_current < self.sprites['death']['framesMax'] - 1:
    #             return
    #         else:
    #             self.dead = True
    #             return

    #     if self.image == self.sprites.get('attack1', {}).get('image'):
    #         if self.frames_current < self.sprites['attack1']['framesMax'] - 1:
    #             return

    #     if self.image == self.sprites.get('takeHit', {}).get('image'):
    #         if self.frames_current < self.sprites['takeHit']['framesMax'] - 1:
    #             return

    #     if self.dead:
    #         return

    #     sprite = self.sprites.get(sprite_name)
    #     if not sprite or self.image == sprite['image']:
    #         return


    #     self.image = sprite['image']
    #     self.frames_max = sprite['framesMax']
    #     self.frames_current = 0
    def switch_sprite(self, sprite_name):
        # If already playing death animation and it’s not finished, do nothing
        if self.image == self.sprites.get('death', {}).get('image'):
            if self.frames_current < self.sprites['death']['framesMax'] - 1:
                return
            else:
                self.dead = True
                return

        # If playing attack animation and it's not finished, don't interrupt it
        if self.image == self.sprites.get('attack1', {}).get('image'):
            if self.frames_current < self.sprites['attack1']['framesMax'] - 1:
                return

        # Same for takeHit animation
        if self.image == self.sprites.get('takeHit', {}).get('image'):
            if self.frames_current < self.sprites['takeHit']['framesMax'] - 1:
                return

        if self.dead:
            return

        sprite = self.sprites.get(sprite_name)
        if not sprite or self.image == sprite['image']:
            return

        # --- Switch to new sprite ---
        self.image = sprite['image']
        self.frames_max = sprite['framesMax']
        self.frames_current = 0  # IMPORTANT: reset current frame!

        # --- ALSO update sprite width! ---
        self.sprite_width = self.image.get_width() // self.frames_max
        self.sprite_height = self.image.get_height()
    

