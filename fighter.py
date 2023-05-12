import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 #0:idle #1:run #2:jump, #3: attack1 #4: attack2 #5: hit #6: death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        #extract images from sheet
        animation_lst = []
        for y, animation in enumerate(animation_steps):
            temp_img_lst = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, 
                                                   self.size, self.size)
                temp_img_lst.append(pygame.transform.scale(
                    temp_img, (self.size * self.image_scale, 
                               self.size * self.image_scale)))
            animation_lst.append(temp_img_lst)
        return animation_lst

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        gravity = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        #get key inputs
        key = pygame.key.get_pressed()

        #can only do other actions if not attacking
        if self.attacking is False and self.alive is True and round_over is False:
            #check player 1 controls
            if self.player == 1:
                #movement
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                #jumping
                if key[pygame.K_w] and self.jump is False:
                    self.vel_y = -30
                    self.jump = True
                
                #attacks
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    #which attack type
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    
                    if key[pygame.K_t]:
                        self.attack_type = 2

            #check player 2 controls
            if self.player == 2:
                #movement
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                #jumping
                if key[pygame.K_UP] and self.jump is False:
                    self.vel_y = -30
                    self.jump = True
                
                #attacks
                if key[pygame.K_1] or key[pygame.K_2]:
                    self.attack(target)
                    #which attack type
                    if key[pygame.K_1]:
                        self.attack_type = 1
                    
                    if key[pygame.K_2]:
                        self.attack_type = 2

        #add gravity
        self.vel_y += gravity
        dy += self.vel_y

        #boundaries
        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left

        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        #make players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        #apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        #update player pos
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        #check which action player is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6) #death
        elif self.hit is True:
            self.update_action(5) #hit
        elif self.attacking is True:
            if self.attack_type == 1:
                self.update_action(3) #attack 1
            elif self.attack_type == 2:
                self.update_action(4) #attack 2
        elif self.jump is True:
            self.update_action(2) #jump
        elif self.running is True:
            self.update_action(1) #run
        else:
            self.update_action(0) #idle

        animation_cooldown = 50
        #update image
        self.image = self.animation_list[self.action][self.frame_index]
        #checking if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        #check if animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            #check if player is dead then end animation
            if self.alive is False:
                self.frame_index = len(self.animation_list[self.action]) -1
            else:
                self.frame_index = 0
                #check if attack was made
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                #check if damage was taken
                if self.action == 5:
                    self.hit = False
                    #if player was in the middle of attack, then stop attack
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - 
                                        (2*self.rect.width * self.flip), 
                                        self.rect.y, 2 * self.rect.width, 
                                        self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 20
                target.hit = True

    def update_action(self, new_action):
        #check if new action is diff from prev
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), 
                                  self.rect.y -(self.offset[1] * self.image_scale)))