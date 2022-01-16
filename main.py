import random
from turtle import Screen, speed
from urllib.parse import DefragResult
import pygame
import time
import os
import math

pygame.font.init()

#Constants
WIDTH = 1280
HEIGHT = 720
GAME_FPS = 144


PLAYER_ROT_SPEED = 3
PLAYER_MAX_SPEED = 50
PLAYER_DRAG_COEFF = 0.3 / GAME_FPS
PLAYER_FORCE = 4.2 / GAME_FPS + PLAYER_DRAG_COEFF
ATTACK_COOLDOWN = .125

BULLET_SPEED = 12

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")


bullets = []
asteroids = []
global attackCooldown
#Load images
#Background
BLK_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-1.png")), (WIDTH, HEIGHT))
#Player ship 0 = engine off, 1 = engine on (visual change)
PLAYER_SHIP_0 = pygame.image.load(os.path.join("assets", "player_0.png"))
PLAYER_SHIP_1 = pygame.image.load(os.path.join("assets", "player_1.png"))
PLAYER_BULLET = pygame.image.load(os.path.join("assets", "bullet_1.png"))

#Asteroids
ASTEROID_LG_1 = pygame.image.load(os.path.join("assets", "asteroid_lg_1.png")) 
ASTEROID_LG_2 = pygame.image.load(os.path.join("assets", "asteroid_lg_2.png"))
ASTEROID_MD_1 = pygame.image.load(os.path.join("assets", "asteroid_md_1.png"))
ASTEROID_MD_2 = pygame.image.load(os.path.join("assets", "asteroid_md_2.png"))
ASTEROID_SM_1 = pygame.image.load(os.path.join("assets", "asteroid_sm_1.png"))
ASTEROID_SM_2 = pygame.image.load(os.path.join("assets", "asteroid_sm_2.png"))
ASTEROID_SM_3 = pygame.image.load(os.path.join("assets", "asteroid_sm_3.png"))




def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)

##PLAYER CLASS
class Player:
    def __init__(self, x, y, rot=90, health=100):
        self.x = x
        self.y = y
        self.rot = rot
        self.speed = pygame.Vector2()
        self.defImg = PLAYER_SHIP_0
        self.mask = pygame.mask.from_surface(PLAYER_SHIP_0)
        self.max_health = health
            
    def draw(self, window):
        self.curImg = self.defImg
        #change between img 0 and 1 self.
        #WINDOW.blit(self.curImg, (self.x, self.y))
        
        blitRotateCenter(WINDOW, self.curImg, (self.x, self.y), self.rot)
        
##ASTEROID CLASS
class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        #LARGE 
        if(size == "large"):
            self.img = ASTEROID_LG_1
            self.xVel = random.randint(-1, 1)
            self.yVel = random.randint(-1, 1)
            
        #MEDIUM
        elif(size== "medium"):
            self.img = ASTEROID_MD_1
            self.xVel = random.randint(-2, 2)
            self.yVel = random.randint(-2, 2)
        #SMALL
        elif(size== "small"):
            self.img = ASTEROID_SM_1
            self.xVel = random.randint(-4, 4)
            self.yVel = random.randint(-4, 4)
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        
    def destroy(self):
        if(self.size == "large"):
            #add points ****            
            #spawn sub asteroids
            asteroids.append(Asteroid(self.x + random.randint(0,15), self.y + random.randint(0, 15), "medium"))
            asteroids.append(Asteroid(self.x - random.randint(0,15), self.y - random.randint(0, 15), "medium"))
        elif(self.size == "medium"):
            #add points ****            
            #spawn sub asteroids
            asteroids.append(Asteroid(self.x + random.randint(0,10), self.y + random.randint(0, 10), "small"))
            asteroids.append(Asteroid(self.x - random.randint(0,10), self.y - random.randint(0, 10), "small"))                        
        #remove from game
        asteroids.remove(self)

        
##BULLET CLASS
class Bullet:
    def __init__(self, x, y, rot):
        self.x = x
        self.y = y
        self.rot = rot
        self.img = PLAYER_BULLET
        self.active = True
        
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        

def main():
    run = True
    FPS = GAME_FPS
    player = Player(WIDTH/2, HEIGHT/2, 0, 100)
    global attackCooldown
    attackCooldown = 0
    
    ##testing temp
    asteroid1 = Asteroid(100,100, "large")
    asteroid2 = Asteroid(300,100, "medium")
    asteroid3 = Asteroid(500,500, "small")
    asteroids.append(asteroid1)
    asteroids.append(asteroid2)
    asteroids.append(asteroid3)
    
    
    
    
    clock = pygame.time.Clock()
    
    def update():
        global attackCooldown
        attackCooldown -= 1/GAME_FPS
        #Update player position
        player.x += player.speed.x
        player.y += player.speed.y
        
        #left bound
        if(player.x + 10 < 0):
            player.x = WIDTH
        #right bound
        if(player.x - 10 > WIDTH):
            player.x = -10
        #top bound
        if(player.y + 10 < 0):
            player.y = HEIGHT
        #bottom bound
        if(player.y - 10 > HEIGHT):
            player.y = -10
        
        #bullets and bullet collision
        for bullet in bullets:
            bullet.x += BULLET_SPEED*math.cos(bullet.rot * math.pi/180)
            bullet.y += -1*BULLET_SPEED*math.sin(bullet.rot * math.pi/180)
            for asteroid in asteroids:
                if(asteroid.x <= bullet.x and bullet.x <= asteroid.x + asteroid.img.get_width()):
                    if(asteroid.y <= bullet.y and bullet.y <= asteroid.y + asteroid.img.get_height()):
                        #bullet collided with asteroid.
                        bullets.remove(bullet)
                        asteroid.destroy()
                        break
                        #break is necessary because bullets are the outer for loop, so might still be other asteroids to check for this bullet's iteration, but bullet now doesnt exist.
        
        #asteroids and player-asteroid collision
        for asteroid in asteroids:
            asteroid.x += asteroid.xVel
            asteroid.y += asteroid.yVel
            #left bound
            if(asteroid.x + 10 < 0):
                asteroid.x = WIDTH
            #right bound
            if(asteroid.x - 10 > WIDTH):
                asteroid.x = -10
            #top bound
            if(asteroid.y + 10 < 0):
                asteroid.y = HEIGHT
            #bottom bound
            if(asteroid.y - 10 > HEIGHT):
                asteroid.y = -10   
       
       ##SPAWNING ASTEROIDS
        if(len(asteroids) == 0):
            for i in range(4):
                x = random.randint(0, WIDTH - 30)
                y = random.randint(0, HEIGHT - 30)
                
                if(abs(x - player.x) > 25 and abs(y - player.y) > 25):
                    asteroids.append(Asteroid(x,y, "large"))
               
        
        #DECELERATE PLAYER
        if(abs(player.speed.x) > 1):
           player.speed.x += -1 * player.speed.x * abs(player.speed.x) * PLAYER_DRAG_COEFF
        elif((abs(player.speed.x) + -1 * player.speed.x * PLAYER_DRAG_COEFF) > 0.01):
            player.speed.x += -1 * player.speed.x * PLAYER_DRAG_COEFF*3
        else:
            player.speed.x = 0
        
        if(abs(player.speed.y) > 1):
            player.speed.y += -1 * player.speed.y * abs(player.speed.y) * PLAYER_DRAG_COEFF
        elif((abs(player.speed.y) + -1 * player.speed.y * PLAYER_DRAG_COEFF) > 0.01):
            player.speed.y += -1 * player.speed.y * PLAYER_DRAG_COEFF*3
        else:
            player.speed.y = 0
            
    
    def draw():
        #draw background first
        WINDOW.blit(BLK_BACKGROUND, (0,0))
        
        #draw bullets
        for bullet in bullets:
            bullet.draw(WINDOW)
            
        #draw asteroids
        for asteroid in asteroids:
            asteroid.draw(WINDOW)            
         
        player.draw(WINDOW)
        
        pygame.display.update()        
    
    while run:
        clock.tick(FPS)
        update()
        draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        ##Handle Input
        keys = pygame.key.get_pressed()
        #Shooting
        if keys[pygame.K_SPACE]:
            if(attackCooldown <= 0):
                bullets.append(Bullet(player.x + player.curImg.get_width()/2 -1, player.y, player.rot))
                attackCooldown = ATTACK_COOLDOWN            
        if keys[pygame.K_a]:
            #rotate left
            player.rot += PLAYER_ROT_SPEED
        if keys[pygame.K_d]:
            #rotate right
            player.rot -= PLAYER_ROT_SPEED    
        if keys[pygame.K_w]:
            #accelerate            
            if(player.speed.x + PLAYER_FORCE * math.cos(player.rot * math.pi/180) < PLAYER_MAX_SPEED):
                player.speed.x += PLAYER_FORCE * math.cos(player.rot * math.pi/180)
            else:
                player.speed.x = PLAYER_MAX_SPEED
                
            if(player.speed.y + PLAYER_FORCE * -1*math.sin(player.rot * math.pi/180) < PLAYER_MAX_SPEED):
                player.speed.y += PLAYER_FORCE * -1*math.sin(player.rot * math.pi/180)
            else:
                player.speed.y = PLAYER_MAX_SPEED      
        
                
main()


