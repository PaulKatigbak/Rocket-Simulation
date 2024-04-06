import pygame
import numpy as np

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# The rotation of the flame is not perfect, but its decent (we really did try everything)

# rocket object for screen
class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_height, rocket_image, rb, flame_image, scale_factor=0.0):
        pygame.sprite.Sprite.__init__(self)
        self.rb = rb
        self.pos = [x, y]

        self.original_rocket = pygame.image.load(rocket_image)
        self.flame_image = pygame.image.load(flame_image)

        self.rect = self.original_rocket.get_rect()
        self.screen_height = screen_height

        # to change rocket size
        scaled_width = int(self.rect.width * scale_factor)
        scaled_height = int(self.rect.height * scale_factor)
        self.updated_image = pygame.transform.scale(self.original_rocket, (scaled_width, scaled_height))

        # Flame
        self.flame_rect = self.flame_image.get_rect()
        self.flame_offset = [0, scaled_height * 0.5]  # Initial flame offset from rocket center

        self.updated_flame = pygame.transform.scale(self.flame_image, (40, 50))

        self.image_rot = self.updated_image
        self.image_rot2 = self.updated_flame

    # Function to update the position of the flames based on rocket's tilt
    def update_flame_position(self):
        # Get the angle of rotation of the rocket
        angle, axis = self.rb.get_angle_2d()

        # Determine the direction of the flame based on the rocket's orientation
        if axis[2] >= 0:    # Rocket is facing upwards
            rotated_offset = self.rotate_point(self.flame_offset, -angle)
        else:               # Rocket is facing downwards
            rotated_offset = self.rotate_point(self.flame_offset, angle)

        # Calculate the position of the flames relative to the rocket's center
        self.flame_pos = [self.pos[0] + rotated_offset[0] - 20, self.pos[1] + rotated_offset[1] + 133]


    # Function to rotate a point around the origin
    def rotate_point(self, point, angle):
        x = point[0] * np.cos(np.radians(angle)) - point[1] * np.sin(np.radians(angle))
        y = point[0] * np.sin(np.radians(angle)) + point[1] * np.cos(np.radians(angle))
        return [x, y]

    # to rotate images
    def rotate(self, angle):
        self.image_rot = pygame.transform.rotate(self.updated_image, angle)
        self.image_rot2 = pygame.transform.rotate(self.updated_flame, angle)
        self.update_flame_position()

    def draw(self, surface):
        rect = self.image_rot.get_rect()
        rect.center = self.pos
        rect.centery = self.screen_height - rect.centery
        surface.blit(self.image_rot, rect)

        # if there is thrust, then draw rotated flame
        if self.rb.thrust:
            surface.blit(self.image_rot2, self.flame_pos)