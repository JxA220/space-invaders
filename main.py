import pygame
import os 
import random

# INICIANDO FUENTES
pygame.font.init()

# INICIANDO SONIDOS
pygame.mixer.init()

# COLORES
WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,255)
RED = (0,0,255)

# FUENTES
LIVES_FONT = pygame.font.SysFont('poppins', 50)
LEVEL_FONT = pygame.font.SysFont('poppins', 50)
GAME_OVER_FONT = pygame.font.SysFont('poppins', 60)

# VENTANA
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
WINDOW_NAME = pygame.display.set_caption('Space Invaders')

# VARIABLES DE JUGADOR
PLAYER_WIDTH = 80
PLAYER_HEIGHT = 80
PLAYER_LIVES = 3

# VARIABLES DE LASER
LASER_X = 0
LASER_Y = 0 

# IMAGENES
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets','space.png')), (WIDTH, HEIGHT))
CURSOR = pygame.image.load(os.path.join('assets','cursor.png'))

# SONIDO DE DISPARO DEL JUGADOR
SHOOT_SOUND = pygame.mixer.Sound(os.path.join('assets', 'shoot.mp3'))

# LASERS
YELLOW_LASER = pygame.image.load(os.path.join('assets','pixel_laser_yellow.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets','pixel_laser_blue.png'))
RED_LASER = pygame.image.load(os.path.join('assets','pixel_laser_red.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets','pixel_laser_green.png'))

# JUGADOR
PLAYER = pygame.transform.scale(pygame.image.load(os.path.join('assets','pixel_ship_yellow.png')), (PLAYER_WIDTH, PLAYER_HEIGHT))

# ENEMIGOS
GREEN_SHIP = pygame.image.load(os.path.join('assets','pixel_ship_green_small.png'))
BLUE_SHIP = pygame.image.load(os.path.join('assets','pixel_ship_blue_small.png'))
RED_SHIP = pygame.image.load(os.path.join('assets','pixel_ship_red_small.png'))

# VARIABLE DE NIVEL
LEVEL = 0

# VARIABLES DE VELOCIDAD
VEL = 0.8
ENEMY_VEL = 0.2
LASER_VEL = 0.4

# VISIBILIDAD DEL MOUSE
pygame.mouse.set_visible(0)

# LIMITE DE FPS
FPS = 60

# RELOJ
clock = pygame.time.Clock()

# CLASE DE LASER
class Laser():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.mask = pygame.mask.from_surface(self.color)

    def draw(self, window):
        WINDOW.blit(self.color, (self.x, self.y))
    
    def movement(self,vel):
        self.y += vel
    
    def out_screen(self, size):
        return not(self.y <= size and self.y >= 0)

    def collision(self, object):
        return crash(self, object)


# CLASE DE NAVE
class Ship():
    COOLDOWN = 30

    def __init__(self, x, y, lives):
        self.x = x
        self.y = y
        self.lives = lives
        self.img = None
        self.laser_image = None
        self.lasers = []
        self.cool_down = 0

    def get_width(self):
        return self.img.get_width()
    
    def get_height(self):
        return self.img.get_height()

    def draw(self, WINDOW):
        WINDOW.blit(self.img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(WINDOW)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.movement(vel)
            if laser.out_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.lives -= 1
                self.lasers.remove(laser)
            
    def cooldown(self):
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1

    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down = 1


# CLASE DE JUGADOR
class Player(Ship):
    def __init__(self, x, y, img, lives = 3):
        super().__init__(x, y, lives = lives)
        self.img = PLAYER
        self.laser_image = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.img)

    def laser_movement(self, vel, objects):
         self.cooldown()
         for laser in self.lasers:
            laser.movement(vel)
            if laser.out_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for object in objects:
                    if laser.collision(object):
                        objects.remove(object)
                        self.lasers.remove(laser)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
        
    

player = Player(380, 500, PLAYER)


# CLASE DE ENEMIGO
class Enemy(Ship):
    
    # SELECCION DE NAVE ENEMIGA
    COLOR_SELECTION = {'red': (RED_SHIP, RED_LASER), 'blue': (BLUE_SHIP, BLUE_LASER), 'green': (GREEN_SHIP, GREEN_LASER)}

    def __init__(self, x, y, color, lives = 1):
        super().__init__(x, y, lives= lives)
        self.img, self.laser_image = self.COLOR_SELECTION[color]
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, vel):
        self.y += vel


def player_movement():
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_d] and player.x + player.get_width() < WIDTH:
        player.x += VEL
    if keys_pressed[pygame.K_a] and player.x > 0:
        player.x -= VEL
    if keys_pressed[pygame.K_w] and player.y > 0:
        player.y -= VEL
    if keys_pressed[pygame.K_s] and player.y + player.get_height() < HEIGHT:
        player.y += VEL
    if keys_pressed[pygame.K_SPACE]:
        player.shoot()


# FUNCION DE CHOQUE DE LASER
def crash(object1, object2):
    axis_x = object2.x - object1.x 
    axis_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (int(axis_x),  int(axis_y))) != None


# FUNCION DE MAIN LOOP
def main():

    run = True
    clock.tick(FPS)

    ENEMIES_LIST = []
    WAVE = 3
   

    # FUNCION DE PINTAR EN LA PANTALLA
    def draw_window():
        WINDOW.blit(BG,(0,0))

        # TEXTOS DE VIDA Y NIVEL
        lives_text = LIVES_FONT.render(f'Vidas: {player.lives}', 1, WHITE)
        level_text = LEVEL_FONT.render(f'Nivel: {LEVEL}', 1, WHITE)
        WINDOW.blit(lives_text, (20,20))
        WINDOW.blit(level_text, (WIDTH - level_text.get_width() - 20, 20))

        # CURSOR
        MOUSE_POS = pygame.mouse.get_pos()
        mouse_x = MOUSE_POS[0]
        mouse_y = MOUSE_POS[1]
        WINDOW.blit(CURSOR, (mouse_x, mouse_y))

        # ENEMIGOS
        for enemy in ENEMIES_LIST:
            enemy.draw(WINDOW)

        # JUGADOR
        player.draw(WINDOW)

        if player.lives == 0:
            GAME_OVER_TEXT = GAME_OVER_FONT.render(f'HAS PERDIDO', 1, WHITE)
            WINDOW.blit(GAME_OVER_TEXT, (WIDTH/3.5, HEIGHT/2.5))

        pygame.display.update()
 

    while run:
        
        if player.lives == 0:
            player.lives = 0
            pygame.time.delay(3000)
            pygame.QUIT()

        if len(ENEMIES_LIST) == 0:
            global LEVEL
            LEVEL += 1
            WAVE += 3
            for i in range(WAVE):
                enemy = Enemy(random.randrange(50, 700), random.randrange(-500, -100), random.choice(['red','blue','green']))
                ENEMIES_LIST.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.QUIT
        
        if random.randrange(0, 2*220) == 1:
            enemy.shoot()

        for enemy in ENEMIES_LIST:
            enemy.move(ENEMY_VEL)
            enemy.move_lasers(LASER_VEL, player)
            if enemy.y + enemy.get_height() > HEIGHT:
                player.lives -= 1
                ENEMIES_LIST.remove(enemy)        
            
        player.laser_movement(-LASER_VEL, ENEMIES_LIST)
        player_movement()
        draw_window()
        
main()
pygame.QUIT

if __name__=='__main__':
    main()
