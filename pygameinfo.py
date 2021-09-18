import pygame
from random import randint as random

info_storage = {}
info_age = {}
remove_info = []
fps = 60


def info_put(screen):
    screen: pygame.display
    for count, text in enumerate(info_storage):
        transparent = info_storage[text]
        if info_age[text] <= fps:
            number = info_age[text] * 255/fps
            transparent.set_alpha(int(number))
        screen.blit(transparent, (10, screen.get_size()[1]-30-(count*20)))
        info_age[text] -= 1
        if info_age[text] <= 0:
            remove_info.append(text)

    for kill in remove_info:
        if info_age.__contains__(kill):
            if info_storage.__contains__(kill):
                info_age.pop(kill)
                info_storage.pop(kill)
                remove_info.remove(kill)
    while screen.get_size()[1]-30-(len(info_storage)*20) < 0:
        key = list(info_age.keys())[0]
        if info_age.__contains__(key):
            info_age.pop(key)
            info_storage.pop(key)


def add_info_text(text, font, _fps, noise=None):
    text: str
    _fps: int
    if noise is None:
        random_num = str(random(1, 2189332323232))
    else:
        random_num = noise
    global fps
    fps = _fps
    font: pygame.font
    info_storage[str(text) + random_num] = font.render(text, True, (0, 0, 0))
    info_age[str(text) + random_num] = fps*2
