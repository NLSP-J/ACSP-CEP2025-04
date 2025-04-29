import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blob Dodge")

# Colors
WHITE = (255, 255, 255)
BLOB_COLOR = (63, 238, 179)
BULLET_COLOR = (239, 255, 0)
POWERUP_COLOR_SPEED = (255, 100, 255)
POWERUP_COLOR_INVINCIBLE = (255, 215, 0)
BLACK = (0, 0, 0)

# Clock and font
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 40)

# Blob
BLOB_RADIUS = 20
blob_x = WIDTH // 2
blob_y = HEIGHT // 2
blob_base_speed = 5
blob_speed = blob_base_speed

# Bullet
BULLET_WIDTH = 5
BULLET_HEIGHT = 5
bullets = []
bullet_speed = 5
SPAWN_BULLET_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_BULLET_EVENT, 500)

# Power-Up
POWERUP_RADIUS = 10
powerup = None
powerup_spawn_time = 0
POWERUP_DURATION = 5000  # Speed power-up duration
INVINCIBILITY_DURATION = 10000  # Invincibility lasts 10s
powerup_active_until = 0
invincible_until = 0
powerup_type = None

# Score
start_time = pygame.time.get_ticks()

def draw_blob(x, y):
    if current_time < invincible_until and current_time % 500 < 250:  # Flashing effect during invincibility
        return
    pygame.draw.circle(SCREEN, BLOB_COLOR, (x, y), BLOB_RADIUS)

def draw_bullet(bullet):
    pygame.draw.rect(SCREEN, BULLET_COLOR, bullet)

def draw_powerup(powerup_rect):
    if powerup_type == "speed":
        color = POWERUP_COLOR_SPEED
    else:
        color = POWERUP_COLOR_INVINCIBLE
    pygame.draw.circle(SCREEN, color, powerup_rect.center, POWERUP_RADIUS)

def show_score(score):
    text = FONT.render(f"Score: {score}", True, WHITE)
    SCREEN.blit(text, (10, 10))

def game_over(score):
    SCREEN.fill(BLACK)
    text = FONT.render(f"Game Over! Final Score: {score}", True, WHITE)
    SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

def spawn_bullet():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, WIDTH)
        y = -BULLET_HEIGHT
        dx = random.uniform(-1, 1)
        dy = 1
    elif side == 'bottom':
        x = random.randint(0, WIDTH)
        y = HEIGHT
        dx = random.uniform(-1, 1)
        dy = -1
    elif side == 'left':
        x = -BULLET_WIDTH
        y = random.randint(0, HEIGHT)
        dx = 1
        dy = random.uniform(-1, 1)
    else:  # right
        x = WIDTH
        y = random.randint(0, HEIGHT)
        dx = -1
        dy = random.uniform(-1, 1)
    
    length = (dx ** 2 + dy ** 2) ** 0.5
    dx /= length
    dy /= length
    return [pygame.Rect(x, y, BULLET_WIDTH, BULLET_HEIGHT), dx * bullet_speed, dy * bullet_speed]

def spawn_powerup():
    global powerup_type
    powerup_type = random.choice(["speed", "invincibility"])
    x = random.randint(POWERUP_RADIUS, WIDTH - POWERUP_RADIUS)
    y = random.randint(POWERUP_RADIUS, HEIGHT - POWERUP_RADIUS)
    return pygame.Rect(x - POWERUP_RADIUS, y - POWERUP_RADIUS, POWERUP_RADIUS * 2, POWERUP_RADIUS * 2)

def circle_rect_collision(circle_x, circle_y, radius, rect):
    closest_x = max(rect.left, min(circle_x, rect.right))
    closest_y = max(rect.top, min(circle_y, rect.bottom))
    distance = math.hypot(circle_x - closest_x, circle_y - closest_y)
    return distance < radius

# Game loop
def main():
    global blob_x, blob_y, powerup, bullets, powerup_spawn_time, invincible_until, powerup_active_until, blob_speed, score, current_time
    running = True
    while running:
        clock.tick(60)
        SCREEN.fill(BLACK)

        current_time = pygame.time.get_ticks()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SPAWN_BULLET_EVENT:
                bullets.append(spawn_bullet())

        # Move blob
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            blob_x -= blob_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            blob_x += blob_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            blob_y -= blob_speed
        if keys[pygame.K_DOWN]:
            blob_y += blob_speed

        # Keep blob on screen
        blob_x = max(BLOB_RADIUS, min(WIDTH - BLOB_RADIUS, blob_x))
        blob_y = max(BLOB_RADIUS, min(HEIGHT - BLOB_RADIUS, blob_y))

        # Update and draw bullets
        for bullet in bullets[:]:
            bullet[0].x += bullet[1]
            bullet[0].y += bullet[2]
            draw_bullet(bullet[0])
            if current_time > invincible_until and circle_rect_collision(blob_x, blob_y, BLOB_RADIUS, bullet[0]):
                score = (current_time - start_time) // 1000
                game_over(score)
            if bullet[0].x < -50 or bullet[0].x > WIDTH + 50 or bullet[0].y < -50 or bullet[0].y > HEIGHT + 50:
                bullets.remove(bullet)

        # Power-up spawn logic
        if powerup is None and current_time - powerup_spawn_time > random.randint(10000, 20000):
            powerup = spawn_powerup()
            powerup_spawn_time = current_time

        # Draw and handle power-up
        if powerup:
            draw_powerup(powerup)
            blob_rect = pygame.Rect(blob_x - BLOB_RADIUS, blob_y - BLOB_RADIUS, BLOB_RADIUS * 2, BLOB_RADIUS * 2)
            if powerup.colliderect(blob_rect):
                if powerup_type == "speed":
                    blob_speed = 20
                    powerup_active_until = current_time + POWERUP_DURATION
                elif powerup_type == "invincibility":
                    invincible_until = current_time + INVINCIBILITY_DURATION
                powerup = None

        # Reset blob speed if power-up expired
        if powerup_active_until and current_time > powerup_active_until:
            blob_speed = blob_base_speed
            powerup_active_until = 0

        # Draw blob
        draw_blob(blob_x, blob_y)

        # Show score
        score = (current_time - start_time) // 1000
        show_score(score)

        pygame.display.update()

    pygame.quit()

main()