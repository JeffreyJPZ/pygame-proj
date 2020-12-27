import pygame, os, sys, random

pygame.init()

win_width, win_height = 1200, 600
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Hotshot")
clock = pygame.time.Clock()
game_font = pygame.font.SysFont('comicsans', 40)

# player car
red_car = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'redf1car.png')), (win_width // 6, win_height // 4)).convert_alpha() # Transparent image

# cars
blue_car = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'bluef1car.png')), (win_width // 6, win_height // 4)).convert_alpha()
green_car = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'greenf1car.png')), (win_width // 6, win_height // 4)).convert_alpha()
pink_car = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'pinkf1car.png')), (win_width // 6, win_height // 4)).convert_alpha()
purple_car = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'purplef1car.png')), (win_width // 6, win_height // 4)).convert_alpha()
yellow_car = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'yellowf1car.png')), (win_width // 6, win_height // 4)).convert_alpha()

# background
backg = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'highway_backg.png')), (win_width, win_height)).convert()
backg_x1 = 0
backg_x2 = backg.get_width()

# pickups and obstacles
wrench = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'wrench_pickup.png')), (win_width // 8, win_height // 4)).convert_alpha()
tire = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'tire_pickup.png')), (win_width // 8, win_height // 4)).convert_alpha()
spike = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'road_spike.png')), (win_width // 8, win_height // 4)).convert_alpha()



class Car:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.car_img = None
        self.health = health

    def draw(self, win):
        win.blit(self.car_img, (self.x, self.y))

    def car_width(self):
        return self.car_img.get_width() # gets car width

    def car_height(self):
        return self.car_img.get_height() # gets car height



class Player(Car):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health) 
        self.car_img = red_car
        self.mask = pygame.mask.from_surface(self.car_img) # For "pixel-perfect" collision 
        self.max_health = health

    def health_bar(self, win):
        pygame.draw.rect(win, (255,0,0), (self.x + self.car_img.get_width() + self.car_img.get_width() // 20, self.y, self.car_img.get_width() // 20, self.car_img.get_height())) # Coords, size of healthbar
        pygame.draw.rect(win, (0,255,0), (self.x + self.car_img.get_width() + self.car_img.get_width() // 20, self.y, self.car_img.get_width() // 20, self.car_img.get_height() * (self.health/self.max_health)))

    def draw(self, win): # pickups change health bar
        super().draw(win)
        self.health_bar(win)



class Enemy(Car):     #  Decreases health if collision, random spawn location, random color
    
    enemy_cars = {"blue": blue_car, "green": green_car, "pink": pink_car, "purple": purple_car, "yellow": yellow_car}
    
    def __init__(self, x, y, colour, health=100):
        super().__init__(x, y, health)
        self.car_img = self.enemy_cars[colour]
        self.mask = pygame.mask.from_surface(self.car_img) # collision detection of NPC car
    
    def enemy_move(self, game_speed): # Move cars left
        self.x -= game_speed



class Pickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pickup_img = None
        
    def draw_pickup(self, win):
        win.blit(self.pickup_img, (self.x, self.y))

    def pickup_move(self, game_speed):
        self.x -= game_speed

    def pickup_width(self):
        return self.pickup_img.get_width() # gets pickup width

    def pickup_height(self):
        return self.pickup_img.get_height() # gets pickup height



class Wrench(Pickup):   # Fully repairs car, spawns less frequently
    def __init__(self, x, y):
        super().__init__(x, y)
        self.pickup_img = wrench
        self.mask = pygame.mask.from_surface(self.pickup_img)
        
    

class Tire(Pickup):     # Adds small amount of health, spawns more frequently
    def __init__(self, x, y):
        super().__init__(x, y)
        self.pickup_img = tire
        self.mask = pygame.mask.from_surface(self.pickup_img)

    

class Spike(Pickup):    # Instant game over if collision occurs
    def __init__(self, x, y):
        super().__init__(x, y)
        self.pickup_img = spike
        self.mask = pygame.mask.from_surface(self.pickup_img)
        


def collision(obj_a, obj_b):    # Check if point of intersection exists
    offset_x = obj_b.x - obj_a.x # Dist. between x and y coords
    offset_y = obj_b.y - obj_a.y

    return obj_a.mask.overlap(obj_b.mask, (offset_x, offset_y)) != None # returns tuple and not "none"

    

def main():
    run = True
    FPS = 120
    score = 0
    level = 0

    # Many game parameters
    scroll_speed = 10 # Change scroll speed of background, higher value for FAST

    spawn_win_width = win_width * 5 # Greatest distance that objects can spawn

    score_timer = 0 # Used for incrementing score

    player = Player(0, win_height // 2)
    player_width = player.car_width()
    player_height = player.car_height()

    lane_spawns = [0, win_height // 4, win_height // 2, win_height // 2 + win_height // 4] # Objects spawn on one of four lanes
    
    enemy_cars = {"blue": blue_car, "green": green_car, "pink": pink_car, "purple": purple_car, "yellow": yellow_car}
    enemies = []
    enemy_num = 0
    enemy_health_decrease = player.max_health // 4 # Change value as needed
    
    game_speed = 3 # Sets speed of objects

    wrenches = []
    tires = []
    spikes = []
    
    wrench_num = 0
    tire_num = 0
    spike_num = 0
    wrench_health_increase = player.max_health # Increment and decrement pickup values
    tire_health_increase = player.max_health // 4
    spike_health_decrease = player.max_health
    
    game_over = False
    game_over_pause = 0


    
    def backg_scroll():
        global backg_x1, backg_x2
        
        if backg_x1 <= backg.get_width() * -1:  # Resets x coord of background 1
            backg_x1 = backg.get_width()

        if backg_x2 <= backg.get_width() * -1:  # Resets x coord of background 2 
            backg_x2 = backg.get_width()

        backg_x1 -= scroll_speed # Both backgrounds move left
        backg_x2 -= scroll_speed



    def redraw_win():
        
        display_score = game_font.render(f'Score: {score}', 1, (255,255,255))
        display_level = game_font.render(f'Level: {level}', 1, (255,255,255))
        
        win.blit(backg, (backg_x1, 0))
        win.blit(backg, (backg_x2, 0))
        win.blit(display_score, (win_width / 3 + win_width / 3 - display_score.get_width() / 2, win_height - display_score.get_height() - 20))
        win.blit(display_level, (win_width / 3 - display_level.get_width() / 2, win_height - display_level.get_height() - 20))
        
        for enemy in enemies: # Draws objects to screen with attributes "draw" and "draw_pickup"
            enemy.draw(win)

        for wrench in wrenches:
            wrench.draw_pickup(win)

        for tire in tires:
            tire.draw_pickup(win)

        for spike in spikes:
            spike.draw_pickup(win)

        player.draw(win)

        if game_over:
            game_over_font = pygame.font.SysFont('comicsans', 100, 1)
            
            display_game_over = game_over_font.render(f'YOU DIED', 1, (255,0,0))
            display_final_score = game_over_font.render(f'Your score was: {score}', 1, (255,0,0))
            
            win.blit(display_game_over, (win_width / 2 - display_game_over.get_width() / 2, win_height / 3))
            win.blit(display_final_score, (win_width / 2 - display_final_score.get_width() / 2, win_height / 3 + win_height / 3))
        
        pygame.display.update()



    while run:
        clock.tick(FPS)
        
        score_timer += 1

        backg_scroll()
        
        redraw_win()
        
        if player.health <= 0:
            game_over = True
            game_over_pause += 1

        if game_over:
            if game_over_pause > FPS * 5: # Wait x seconds before going to menu screen
                run = False
            else:
                continue
            
        if score_timer % FPS == 0: # Every x seconds score goes up by y
            score += 1

        if len(enemies) == 0 and len(wrenches) == 0 and len(tires) == 0 and len(spikes) == 0: # If all objects have been removed
            level += 1 
            enemy_num += 5 # Change enemy number as needed, 3-5 is fairly balanced

            if level % 5 == 0: # Every 5 levels the game speed increases
                game_speed += 3
                scroll_speed += 5
                spawn_win_width *= 2
            
            if random.randint(1, 100) <= 5:  # Chance of pickups spawning
                wrench_num += 1

            if random.randint(1, 100) <= 20:
                tire_num += 1

            if random.randint(1, 100) <= 10:
                spike_num += 1
            
            for i in range(enemy_num):  # Spawns all objects at once
                enemy = Enemy(random.randrange(win_width, spawn_win_width), random.choice(lane_spawns), random.choice(list(enemy_cars.keys()))) # Choose random colour
                enemies.append(enemy) # Add to list
                
            for i in range(wrench_num):
                wrench = Wrench(random.randrange(win_width, spawn_win_width), random.choice(lane_spawns))
                wrenches.append(wrench)
                
            for i in range(tire_num):
                tire = Tire(random.randrange(win_width, spawn_win_width), random.choice(lane_spawns))
                tires.append(tire)
                
            for i in range(spike_num):
                spike = Spike(random.randrange(win_width, spawn_win_width), random.choice(lane_spawns))
                spikes.append(spike)
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
              run = False
              pygame.quit()
              sys.exit()
              
            if event.type == pygame.KEYDOWN: # Single input
                keys = pygame.key.get_pressed() # Check for input
                if keys[pygame.K_w] or keys[pygame.K_UP]:    # move up one lane
                    if player.y > 0:
                        player.y -= win_height // 4
                if keys[pygame.K_s] or keys[pygame.K_DOWN]: # move down one lane
                    if player.y < win_height - player_height:
                        player.y += win_height // 4

        for enemy in enemies[:]:
            enemy.enemy_move(game_speed)

            if collision(enemy, player):
                player.health -= enemy_health_decrease # subtract x health
                enemies.remove(enemy) # Removes from list if collision occurs
                
            elif enemy.x + enemy.car_width() < 0: # Otherwise, deletes objects if off-screen
                enemies.remove(enemy)

        for wrench in wrenches[:]:
            wrench.pickup_move(game_speed)

            if collision(wrench, player):
                player.health = wrench_health_increase # Sets health equal to max
                wrenches.remove(wrench)
                    
            elif wrench.x + wrench.pickup_width() < 0:
                wrenches.remove(wrench)
                
        for tire in tires[:]:
            tire.pickup_move(game_speed)

            if collision(tire, player):
                
                if player.health + tire_health_increase >= player.max_health: # If new health greater or equal to max health, health remains at max
                    player.health = player.max_health
                else:
                    player.health += tire_health_increase # Else health is increased by x

                tires.remove(tire)

            elif tire.x + tire.pickup_width() < 0:
                tires.remove(tire)
                
        for spike in spikes[:]:
            spike.pickup_move(game_speed)

            if collision(spike, player):
                player.health -= spike_health_decrease # Instant game over
                
                if player.health < 0: # Health cannot be negative
                    player.health = 0
                spikes.remove(spike)

            elif spike.x + spike.pickup_width() < 0:
                spikes.remove(spike)
                


def instructions():
    instructions_font = pygame.font.SysFont('comicsans', 50)

    run = True

    while run:
        display_instructions = instructions_font.render(f'Cars/spikes BAD | Tires/wrenches GOOD | Press any button to go back', 1, (255,255,255))
        display_instructions2 = instructions_font.render(f'The only limit is your REFLEXES (and luck, maybe)', 1, (255,0,0))
        
        win.fill((0,0,0))
        win.blit(display_instructions, (win_width / 2 - display_instructions.get_width() / 2, win_height / 3))
        win.blit(display_instructions2, (win_width / 2 - display_instructions2.get_width() / 2, win_height / 3 + win_height / 3))

        pygame.display.update()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.KEYDOWN: # Go back to menu
                menu_screen()

            if event.type == pygame.MOUSEBUTTONDOWN:
                menu_screen()

    pygame.quit()
    sys.exit()

def menu_screen():
    title_font = pygame.font.SysFont('comicsans', 120, 1)
    menu_font = pygame.font.SysFont('comicsans', 60)
    
    run = True

    while run:
        display_title = title_font.render(f'H0T_SH0T', 1, (255,0,0))
        display_subtitle = menu_font.render(f'Press E for instructions or press any button to begin', 1, (255,255,255))

        win.fill((0,0,0))
        win.blit(display_title, (win_width / 2 - display_title.get_width() / 2, win_height / 3))
        win.blit(display_subtitle, (win_width / 2 - display_subtitle.get_width() / 2, win_height / 3 + win_height / 3))

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
              run = False
              
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                
                if keys[pygame.K_e]: # E pressed, goes to instruction screen
                    instructions()
                else:
                    main()

            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()
    sys.exit()


menu_screen()
