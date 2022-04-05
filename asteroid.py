from turtle import position
from pyglet import window, font
from if3_game.engine import Sprite, Game, Layer, Text
from math import cos, sin, radians
from random import randint, choice


RESOLUTION = (800, 600)
LIFE_MAX = 5

class AsteroidGame(Game):
    
    def __init__(self):
        super().__init__()

        font.add_file("fonts/bug_report.ttf")

        # creation des layers

        self.bg_layer = Layer()
        self.add(self.bg_layer)

        self.game_layer = Layer()
        self.add(self.game_layer)

        self.ui_layer = UILayer()
        self.add(self.ui_layer)

        #créer les éléments de jeu

        position = (RESOLUTION[0] / 2, RESOLUTION[1] / 2)
        self.spaceship = Spaceship(position)

        self.game_layer.add(self.spaceship)
        self.ui_layer.spaceship = self.spaceship

        for n in range(3):
            x = randint(0, RESOLUTION[0])
            while x >= 200 and x <= RESOLUTION[0] - 200:
                x = randint(0, RESOLUTION[0])

            y = randint(0, RESOLUTION[1])
            while y >= 200 and y <= RESOLUTION[1] - 200:
                y = randint(0, RESOLUTION[1])
    
            position = (x, y)

            sx =  randint(-100, 100)
            sy = randint(-100, 100)
            speed = (sx, sy)

            asteroid = Asteroid(position, speed)
            self.game_layer.add(asteroid)
            self.ui_layer.asteroids.append(asteroid)

        # créer les éléments de background

        bg = Sprite("images/bg.png")
        self.bg_layer.add(bg)


class UILayer(Layer):

    def __init__(self):
        super().__init__()
        self.spaceship = None
        self.asteroids = []

        self.lifes = []

        for n in range(LIFE_MAX):
            x = 780 - n * 24
            y = 580

            image = "images/life.gif"
            position = (x, y)
            anchor = (8, 8)

            sprite = Sprite(image, position, anchor=anchor)
            self.add(sprite)

            self.lifes.append(sprite)
        
        position = (RESOLUTION[0] / 2, RESOLUTION[1] / 2)
        color = (66, 189, 65)
        anchor = "center"

        self.game_over_message = Text(
            "", position,72, font_name="Bug Report", color=color, anchor=anchor)
        self.add(self.game_over_message)

        self.win_message = Text(
            "", position,72, font_name="Bug Report", color=color, anchor=anchor)
        self.add(self.win_message)


    def update(self, dt):
        super().update(dt)

        #affichage de la vie du vaisseau

        for index in range(len(self.lifes)):
            if index < self.spaceship.life:
                self.lifes[index].opacity = 255
            else:
                self.lifes[index].opacity = 0

        if self.spaceship.life <= 0:
            self.game_over_message.text = "Game Over"
        else:
            self.game_over_message.text = ""

        player_won = True
        for asteroid in self.asteroids:
            if asteroid.is_destroyed == False:
                player_won = False
                break

        if player_won:
            print("test")
            self.win_message.text = "Victory"


class SpaceItem(Sprite):
    def __init__(
        self, image, position, anchor, speed=(0, 0), rotation_speed=0):
        
        super().__init__(
            image, position, anchor=anchor, collision_shape= "circle")
        self.speed = speed
        self.rotation_speed = rotation_speed

    def update(self, dt):
        super().update(dt)
        # Position actuelle
        pos_x = self.position[0]
        pos_y = self.position[1]

        # Calcul du déplacement
        move = (self.speed[0] * dt, self.speed[1] * dt)
        
        # Application du déplacement
        pos_x += move[0]
        pos_y += move[1]

        # Correction de la position si on sort de l'écran
        if pos_x > RESOLUTION[0] + 32:
            pos_x = -32
        elif pos_x < -32:
            pos_x = RESOLUTION[0] + 32

        if pos_y > RESOLUTION[1] + 32:
            pos_y = -32
        elif pos_y < -32:
            pos_y = RESOLUTION[1] + 32

        # On bouge effectivement l'objet
        self.position = (pos_x, pos_y)

        # On applique la rotation ici
        self.rotation += self.rotation_speed * dt


class Spaceship(SpaceItem):

    def __init__(self, position):
        image = "images/spaceship.png"
        anchor = (32, 32)
        super().__init__(
            image, position, anchor)
        self.velocity = 0

        self.invulnerability = False
        self.chrono = 0
        
        self.is_overpowerded = False
        self.power_chrono = 0

        self.life = 3

    def update(self, dt):

        if self.invulnerability == True:
            self.opacity = 125
            self.chrono += dt
            if self.chrono >= 3:
                self.invulnerability = False
                self.chrono = 0
        else:
            self.opacity = 255

        if self.is_overpowerded == True:
            self.power_chrono += dt
            if self.power_chrono >= 10:
                self.is_overpowerded = False
                self.change_image("images/spaceship.png")
                self.power_chrono = 0

        dsx = cos(radians(self.rotation)) * self.velocity
        dsy = sin(radians(self.rotation)) * self.velocity * -1

        sx = self.speed[0] + dsx
        sy = self.speed[1] + dsy
        self.speed = (sx, sy)

        super().update(dt)

    def over_power_on(self):
        self.change_image("images/spaceship_power.png")
        self.is_overpowerded = True
        self.power_chrono = 0

    def on_key_press(self, key, modifiers):
        if key == window.key.LEFT:
            self.rotation_speed = -50

        elif key == window.key.RIGHT:
            self.rotation_speed = 50
        elif key == window.key.UP:
            self.velocity = 5
        elif key == window.key.SPACE:
            self.spawn_bullet()

    def on_key_release(self, key, modifiers):
        if key == window.key.LEFT and self.rotation_speed < 0:
            self.rotation_speed = 0 
        elif key == window.key.RIGHT and self.rotation_speed > 0:
            self.rotation_speed = 0
        elif key == window.key.UP:
            self.velocity = 0

    def spawn_bullet(self):

        bullet_velocity = 100
        sx = cos(radians(self.rotation)) * bullet_velocity
        sy = sin(radians(self.rotation)) * bullet_velocity * -1

        bullet_speed = (
            self.speed[0] + sx, self.speed[1] + sy)

        x = cos(radians(self.rotation)) * 40
        y = sin(radians(self.rotation)) * 40 * -1

        bullet_positon = (self.position[0] + x, self.position[1] + y)

        bullet = Bullet(bullet_positon, bullet_speed)
        self.layer.add(bullet)

    def on_collision(self, other):
        if isinstance(other, Asteroid):
            if self.is_overpowerded:
                other.destroy()
            else:
                self.destroy()

    def destroy(self):
        if self.invulnerability == False:
            self.invulnerability = True
            self.life -= 1
            if self.life <= 0:
                super().destroy()


class Asteroid(SpaceItem):

    def __init__(self, position, speed, level=3):

        self.level = level
        if level == 3:
            image = "images/asteroid128.png"
            anchor = (64, 64)
        elif level == 2:
            image = "images/asteroid64.png"
            anchor = (32, 32)
        else:
            image = "images/asteroid32.png"
            anchor = (16, 16)

        rotation_speed = 50
        super().__init__(
            image, position, anchor, speed, rotation_speed)

    def destroy(self):
        if self.level > 1:
            for n in range(2):
                sx = randint(-300, 300)
                sy = randint(-300, 300)
                speed = (sx, sy)

                level = self.level-1

                asteroid = Asteroid(
                    self.position, speed, level=level)

                self.layer.add(asteroid)
                self.layer.game.ui_layer.asteroids.append(asteroid)

        if randint(1, 5) == 1:
            possibilities = [
                OneUp(self.position), 
                OverPower(self.position)]
            power_up = choice(possibilities)
            self.layer.add(power_up)

        super().destroy()


class Bullet(SpaceItem):

    def __init__(self, position, speed):
        image = "images/bullet.png"
        anchor = (8, 8)
        rotation_speed = 200
        super().__init__(
            image, position, anchor, speed, rotation_speed)

        self.life_time = 0

    def update(self, dt):
        super().update(dt)

        self.life_time += dt
        
        if self.life_time >= 3:
            self.destroy()

    def on_collision(self, other):
        if isinstance(other, Asteroid):
            self.destroy()
            other.destroy()


class PowerUp(SpaceItem):

    def __init__(self,image, position, anchor, life_time):
        super().__init__(image, position, anchor)
        self.life_time = life_time

    def update(self, dt):
        super().update(dt)

        self.life_time -= dt
        if self.life_time <= 0:
            self.destroy()

    def on_collision(self, other):
        if isinstance(other, Spaceship):
            self.apply_effect(other)
            self.destroy()

    def apply_effect(self, spaceship):
        pass

class OneUp(PowerUp):

    def __init__(self, position):
        image = "images/get_a_life.gif"
        anchor = (16, 16)
        life_time = 10
        super().__init__(image, position, anchor, life_time)

    def apply_effect(self, spaceship):
        if spaceship.life < LIFE_MAX:
            spaceship.life += 1


class OverPower(PowerUp):
     
    def __init__(self, position):
        image = "images/get_power.gif"
        anchor = (16, 16)
        life_time = 10
        super().__init__(image, position, anchor, life_time)

    def apply_effect(self, spaceship):
        spaceship.over_power_on()