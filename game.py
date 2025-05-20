import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("El jueguito de Halloween")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

clock = pygame.time.Clock()

def resize_image(image_path, width, height):
    image = pygame.image.load(image_path).convert_alpha()
    return pygame.transform.scale(image, (width, height))

background_img = resize_image("fondo.jpg", WIDTH, HEIGHT)
player_img = resize_image("yoLiteral.png", 60, 80)
candy_img = resize_image("dulce.png", 40, 40)
pistol_img = resize_image("pistola.png", 50, 35)
ghost_img = resize_image("esqueleto.png", 60, 80)
zombie_img = resize_image("zombie.png", 60, 80)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 60)
        self.speed = 5
        self.space_pressed = False

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Candy(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(3, 6)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        base_speed = random.randint(2, 5)
        self.speed = base_speed + difficulty_level

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 11))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Gun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pistol_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = 4

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

player = Player()
candies = pygame.sprite.Group(Candy(candy_img) for _ in range(10))
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
guns = pygame.sprite.Group()

all_sprites = pygame.sprite.Group(player, candies)

score = 0
lives = 3
has_gun = False
gun_timer = 0
difficulty_level = 1
victory = False
font = pygame.font.Font(None, 36)

intro_texts = [
    "Era el día de Halloween, y el pequeño Edwin estaba recogiendo dulces como todos los años, pero se encontro con una puerta misteriosa, sin pensarlo entró por dulces, y pasó lo que ninguno se esperaba, dentro de esta casa había una maldición la cual hizo que comenzaran a aparecer muertos vivientes...",
    "Edwin se propone acabar con los monstruos, pero para ello necesita recoger 100 dulces mientras los esquiva y los destruye.",
    " ADVERTENCIA:  Recoge dulces, esquiva monstruos y destruye a los que puedas, pero ten cuidado, si te tocan perderás una vida, y si te tocan 3 veces perderás el juego. Ten en cuenta que puedes agarrar pistolas para matar a los monstruos",
]
intro_index = 0
showing_intro = True

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if showing_intro:
                if event.key == pygame.K_RETURN:
                    intro_index += 1
                    if intro_index >= len(intro_texts):
                        showing_intro = False

    if showing_intro:
        screen.fill(BLACK)
        margin_x = 80
        max_width = WIDTH - 2 * margin_x
        text = intro_texts[intro_index]
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            rendered = font.render(line, True, WHITE)
            text_x = WIDTH // 2 - rendered.get_width() // 2
            text_y = HEIGHT // 3 + i * 50
            screen.blit(rendered, (text_x, text_y))

        pygame.display.flip()
        continue

    screen.blit(background_img, (0, 0))
    keys = pygame.key.get_pressed()
    player.update(keys)

    if has_gun and keys[pygame.K_SPACE]:
        if not player.space_pressed:
            bullet = Bullet(player.rect.centerx, player.rect.top)
            bullets.add(bullet)
            all_sprites.add(bullet)
            player.space_pressed = True
    else:
        player.space_pressed = False

    candies.update()
    enemies.update()
    bullets.update()
    guns.update()

    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, enemies, True)
        if hits:
            bullet.kill()

    for candy in pygame.sprite.spritecollide(player, candies, True):
        score += 1

        if score % 20 == 0:
            difficulty_level += 1

        if score >= 100:
            victory = True
            showing_intro = True
            intro_texts = ["Ganaste, conseguiste los 100 dulces y paraste la maldición"]
            intro_index = 0

        new_candy = Candy(candy_img)
        candies.add(new_candy)
        all_sprites.add(new_candy)

    for gun in pygame.sprite.spritecollide(player, guns, True):
        has_gun = True
        gun_timer = pygame.time.get_ticks()
        player.space_pressed = False

    while len(enemies) < difficulty_level * 6:
        image = random.choice([ghost_img, zombie_img])
        enemy = Enemy(image)
        enemies.add(enemy)
        all_sprites.add(enemy)

    if not has_gun and random.random() < 0.005 * difficulty_level:
        new_gun = Gun()
        guns.add(new_gun)
        all_sprites.add(new_gun)

    if len(candies) < 10:
        for _ in range(10 - len(candies)):
            new_candy = Candy(candy_img)
            candies.add(new_candy)
            all_sprites.add(new_candy)

    if pygame.sprite.spritecollide(player, enemies, True):
        lives -= 1
        if lives <= 0:
            showing_intro = True
            intro_texts = ["Perdiste, los monstruos te mataron"]
            intro_index = 0

    if has_gun:
        elapsed_time = (pygame.time.get_ticks() - gun_timer) // 1000
        if elapsed_time >= 10:
            has_gun = False

    all_sprites.draw(screen)
    score_text = font.render(f"Puntos: {score}", True, ORANGE)
    screen.blit(score_text, (10, 10))

    lives_text = font.render(f"Vidas: {lives}", True, RED)
    screen.blit(lives_text, (WIDTH - 120, 10))

    difficulty_text = font.render(f"Dificultad: {difficulty_level}", True, WHITE)
    screen.blit(difficulty_text, (10, 50))

    if has_gun:
        remaining = 10 - (pygame.time.get_ticks() - gun_timer) // 1000
        timer_text = font.render(f"Arma: {remaining}s", True, WHITE)
        screen.blit(timer_text, (WIDTH // 2 - 50, 10))

    pygame.display.flip()

pygame.quit()
