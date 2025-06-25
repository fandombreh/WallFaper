import asyncio
import platform
import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
NUM_PARTICLES = 50
ANIMATED_SECTION_HEIGHT = HEIGHT // 3
MENU_WIDTH = 200

# Particle class
class Particle:
    def __init__(self, x, y, effect_type):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.size = random.randint(3, 7)
        if effect_type == "bounce":
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-2, 2)
            self.alpha = 255
        elif effect_type == "fade":
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
            self.alpha = random.randint(50, 255)
            self.alpha_decay = random.uniform(1, 3)
        elif effect_type == "orbit":
            self.angle = random.uniform(0, 2 * math.pi)
            self.radius = random.uniform(50, 150)
            self.speed = random.uniform(0.02, 0.05)
            self.alpha = 255

    def update(self, mouse_pos=None):
        if self.effect_type == "bounce":
            self.x += self.vx
            self.y += self.vy
            if self.x < 0 or self.x > WIDTH - MENU_WIDTH:
                self.vx *= -1
            if self.y < 0 or self.y > HEIGHT - ANIMATED_SECTION_HEIGHT:
                self.vy *= -1
        elif self.effect_type == "fade":
            self.x += self.vx
            self.y += self.vy
            self.alpha -= self.alpha_decay
            if self.alpha <= 0:
                self.x, self.y = random.randint(0, WIDTH - MENU_WIDTH), random.randint(0, HEIGHT - ANIMATED_SECTION_HEIGHT)
                self.alpha = 255
                self.vx = random.uniform(-1, 1)
                self.vy = random.uniform(-1, 1)
        elif self.effect_type == "orbit" and mouse_pos:
            self.angle += self.speed
            self.x = mouse_pos[0] + math.cos(self.angle) * self.radius
            self.y = mouse_pos[1] + math.sin(self.angle) * self.radius
            if self.x < 0 or self.x > WIDTH - MENU_WIDTH or self.y < 0 or self.y > HEIGHT - ANIMATED_SECTION_HEIGHT:
                self.angle += math.pi  # Reverse orbit direction

    def draw(self, screen):
        surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, self.color + (int(self.alpha),), (self.size, self.size), self.size)
        screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))

# Global variables
particles = []
screen = None
background_type = "gradient"
effect_type = "bounce"
menu_open = False
clock = None
font = None

def setup():
    global screen, particles, clock, font
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dynamic Wallpaper")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)
    reset_particles()

def reset_particles():
    global particles
    particles = [Particle(random.randint(0, WIDTH - MENU_WIDTH), random.randint(0, HEIGHT - ANIMATED_SECTION_HEIGHT), effect_type)
                 for _ in range(NUM_PARTICLES)]

def draw_background():
    if background_type == "gradient":
        for y in range(HEIGHT):
            r = int(20 * (1 - y / HEIGHT))
            g = int(40 * (1 - y / HEIGHT))
            b = int(100 * (1 - y / HEIGHT))
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    elif background_type == "solid_red":
        screen.fill((100, 0, 0))
    elif background_type == "solid_green":
        screen.fill((0, 100, 0))
    elif background_type == "solid_blue":
        screen.fill((0, 0, 100))
    elif background_type == "checkerboard":
        size = 50
        for y in range(0, HEIGHT, size):
            for x in range(0, WIDTH, size):
                color = (50, 50, 50) if (x // size + y // size) % 2 == 0 else (100, 100, 100)
                pygame.draw.rect(screen, color, (x, y, size, size))

def draw_animated_section(time):
    # Pulsing grid in bottom third
    grid_size = 20
    for x in range(0, WIDTH, grid_size):
        for y in range(HEIGHT - ANIMATED_SECTION_HEIGHT, HEIGHT, grid_size):
            offset = math.sin(time / 1000 + x / 100 + y / 100) * 5
            color = (int(50 + offset * 5), int(100 + offset * 5), int(150 + offset * 5))
            pygame.draw.rect(screen, color, (x, y, grid_size - 2, grid_size - 2))

def draw_menu():
    pygame.draw.rect(screen, (30, 30, 30), (WIDTH - MENU_WIDTH, 0, MENU_WIDTH, HEIGHT))
    # Background options
    bg_options = ["Gradient", "Solid Red", "Solid Green", "Solid Blue", "Checkerboard"]
    for i, option in enumerate(bg_options):
        rect = pygame.Rect(WIDTH - MENU_WIDTH + 10, 50 + i * 40, MENU_WIDTH - 20, 30)
        pygame.draw.rect(screen, (100, 100, 100), rect)
        text = font.render(option, True, (255, 255, 255))
        screen.blit(text, (rect.x + 10, rect.y + 5))
    # Effect options
    effect_options = ["Bounce", "Fade", "Orbit"]
    for i, option in enumerate(effect_options):
        rect = pygame.Rect(WIDTH - MENU_WIDTH + 10, 300 + i * 40, MENU_WIDTH - 20, 30)
        pygame.draw.rect(screen, (100, 100, 100), rect)
        text = font.render(option, True, (255, 255, 255))
        screen.blit(text, (rect.x + 10, rect.y + 5))
    # Menu toggle button
    toggle_rect = pygame.Rect(WIDTH - MENU_WIDTH, 10, MENU_WIDTH - 20, 30)
    pygame.draw.rect(screen, (150, 150, 150), toggle_rect)
    text = font.render("Toggle Menu", True, (255, 255, 255))
    screen.blit(text, (toggle_rect.x + 10, toggle_rect.y + 5))

def handle_menu_click(pos):
    global background_type, effect_type, menu_open
    if not menu_open:
        toggle_rect = pygame.Rect(WIDTH - MENU_WIDTH, 10, MENU_WIDTH - 20, 30)
        if toggle_rect.collidepoint(pos):
            menu_open = True
        return
    # Check toggle button
    toggle_rect = pygame.Rect(WIDTH - MENU_WIDTH, 10, MENU_WIDTH - 20, 30)
    if toggle_rect.collidepoint(pos):
        menu_open = False
        return
    # Background options
    bg_options = ["gradient", "solid_red", "solid_green", "solid_blue", "checkerboard"]
    for i, option in enumerate(bg_options):
        rect = pygame.Rect(WIDTH - MENU_WIDTH + 10, 50 + i * 40, MENU_WIDTH - 20, 30)
        if rect.collidepoint(pos):
            background_type = option
    # Effect options
    effect_options = ["bounce", "fade", "orbit"]
    for i, option in enumerate(effect_options):
        rect = pygame.Rect(WIDTH - MENU_WIDTH + 10, 300 + i * 40, MENU_WIDTH - 20, 30)
        if rect.collidepoint(pos):
            effect_type = option
            reset_particles()

def update_loop():
    global screen, particles
    mouse_pos = pygame.mouse.get_pos()
    time = pygame.time.get_ticks()
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_menu_click(event.pos)
    # Draw
    draw_background()
    draw_animated_section(time)
    for particle in particles:
        particle.update(mouse_pos if effect_type == "orbit" else None)
        particle.draw(screen)
    if menu_open or mouse_pos[0] > WIDTH - MENU_WIDTH:
        draw_menu()
    pygame.display.flip()
    clock.tick(FPS)
    return True

async def main():
    setup()
    while True:
        if not update_loop():
            break
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
