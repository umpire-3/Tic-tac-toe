import pygame


Nought = 0
Cross = 1


class Unit(pygame.sprite.Sprite):

    def __init__(self, unit_type=Cross, pos=(0, 0), size=(100, 100)):
        super().__init__()

        image = 'cross' if unit_type == Cross\
            else 'nought'

        image = 'img/' + image + '.png'
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.x, self.y = pos

    def update(self, map):
        self._set_rect(map[self.x, self.y])

    def _set_rect(self, rect):
        if rect.w != self.rect.w or rect.h != self.rect.h:
            self.image = pygame.transform.scale(self.image, (rect.w, rect.h))
        self.rect = rect
