import pgzrun
import random
import math

# Configurações da tela
WIDTH = 800
HEIGHT = 600
TITLE = "A Missão Cristalina"

class Character:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y 
        self.width = width
        self.height = height 
        self.velocity_x = 0
        self.velocity_y = 0
        self.current_frame = 0
        self.animation_speed = 0.2
        self.is_moving = False
        
    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

class Hero(Character):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 70)
        self.jump_power = -15
        self.gravity = 0.8
        self.speed = 5
        self.on_ground = False
        self.move_left = False
        self.move_right = False
        
        # Sprites do herói
        self.idle_frames = ["hero_idle_1", "hero_idle_2", "hero_idle_3", "hero_idle_4"]
        self.walk_frames = ["hero_walk_1", "hero_walk_2", "hero_walk_3", "hero_walk_4", "hero_walk_5", "hero_walk_6"]
        self.current_animation = self.idle_frames
        
        self.actor = Actor(self.idle_frames[0])
        self.actor.pos = (x + 25, y + 5)
        
    def update(self, platforms):
        # Movimento horizontal
        self.velocity_x = 0
        if self.move_left:
            self.velocity_x = -self.speed
        if self.move_right:
            self.velocity_x = self.speed
        
        # Aplicar gravidade
        self.velocity_y += self.gravity
        
        # Movimento horizontal
        new_x = self.x + self.velocity_x
        if new_x < 0:
            new_x = 0
        elif new_x > WIDTH - self.width:
            new_x = WIDTH - self.width
        self.x = new_x
        
        # Movimento vertical 
        new_y = self.y + self.velocity_y 
        self.on_ground = False
        
        # Verificação de colisão SIMPLES que estava funcionando
        future_rect = Rect(self.x, new_y, self.width, self.height)
        
        for platform in platforms:
            if future_rect.colliderect(platform):
                # Se está caindo, para em cima da plataforma
                if self.velocity_y > 0:
                    new_y = platform.top - self.height 
                    self.velocity_y = 0
                    self.on_ground =True
                    break
        
        self.y = new_y
        
        # Se cair fora da tela, respawn
        if self.y > HEIGHT:
            self.x = 100
            self.y = 430
            self.velocity_y = 0
            self.on_ground = True
        
        # Animação
        self.is_moving = self.move_left or self.move_right
        if self.is_moving:
            self.current_animation = self.walk_frames
        else:
            self.current_animation = self.idle_frames
            
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.current_animation):
            self.current_frame = 0
            
        self.actor.pos = (self.x + 25, self.y + 5)
    
    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
    
    def draw(self):
        frame_index = int(self.current_frame) % len(self.current_animation)
        self.actor.image = self.current_animation[frame_index]
        self.actor.draw()

class Enemy(Character):
    def __init__(self, x, y, patrol_distance):
        super().__init__(x, y, 40, 40)
        self.patrol_distance = patrol_distance
        self.start_x = x
        self.speed = 2
        self.velocity_x = self.speed
        
        # Sprites do inimigo
        self.walk_frames = ["enemy_walk_1", "enemy_walk_2", "enemy_walk_3", "enemy_walk_4"]
        
        self.actor = Actor(self.walk_frames[0])
        self.actor.pos = (x + 20, y + 20)
        
    def update(self, platforms):
        # Movimento de patrulha
        new_x = self.x + self.velocity_x
        
        # Verificar limites
        if new_x > self.start_x + self.patrol_distance or new_x < self.start_x - self.patrol_distance:
            self.velocity_x = -self.velocity_x
        
        # Verificar colisão
        test_rect = Rect(new_x, self.y, self.width, self.height)
        can_move = True
        
        for platform in platforms:
            if test_rect.colliderect(platform):
                self.velocity_x = -self.velocity_x
                can_move = False
                break
        
        if can_move:
            self.x = new_x
            
        self.is_moving = True
        self.current_frame += self.animation_speed
        
        self.actor.pos = (self.x + 20, self.y + 20)
    
    def draw(self):
        frame_index = int(self.current_frame) % len(self.walk_frames)
        self.actor.image = self.walk_frames[frame_index]
        self.actor.draw()

class Crystal:
    def __init__(self, x, y, width=25, height=25):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.collected = False
        
        # Sprite única do cristal
        self.actor = Actor("crystal")
        self.actor.pos = (x + width//2, y + height//2)
    
    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)
    
    def draw(self):
        if not self.collected:
            self.actor.draw()

class Game:
    def __init__(self):
        self.state = "menu"
        self.music_on = True
        self.sounds_on = True
        self.level = 1
        self.score = 0
        self.crystals_collected = 0
        self.hero = None
        self.enemies = []
        self.platforms = []
        self.crystals = []
        self.total_crystals_per_level = 3
        
        # Iniciar música de fundo com volume aumentado
        if self.music_on:
            music.play("background_music")
            music.set_volume(0.6)
        
        self.initialize_game()
        
    def reset_game_stats(self):
        self.level = 1
        self.score = 0
        self.crystals_collected = 0
        
    def initialize_game(self):
        self.platforms = [
            Rect(150, 400, 150, 20),   # Plataforma do meio esquerda
            Rect(400, 400, 150, 20),   # Plataforma do meio direita
            Rect(400, 200, 150, 20),   # Plataforma do superior 
            Rect(610, 300, 100, 20),   # Plataforma do superior direita
            Rect(250, 300, 100, 20),   # Plataforma superior esquerda
            Rect(0, 500, WIDTH, 20)    # Chão
        ]
        
        # Personagem na posição correta
        self.hero = Hero(100, 300)     # Sobre plataforma inferior
        
        # INIMIGOS 
        self.enemies = [
            Enemy(200, 430, 80),       # Sobre plataforma do meio esquerda
            Enemy(450, 430, 80)        # Sobre plataforma do meio direita
        ]
        
        # CRISTAIS 
        self.crystals = [
            Crystal(640, 275),         # Sobre plataforma superior direita
            Crystal(450, 475),         # Sobre plataforma inferior
            Crystal(280, 275)          # Sobre plataforma superior
        ]
    
    def start_new_game(self):
        self.reset_game_stats()
        self.initialize_game()
        self.state = "playing"
        
        # Reiniciar música com volume aumentado
        if self.music_on:
            music.play("background_music")
            music.set_volume(0.6)
    
    def next_level(self):
        self.level += 1
        self.score += 500
        self.crystals_collected = 0
        self.initialize_game()
    
    def update(self):
        if self.state == "playing":
            self.hero.update(self.platforms)
            
            for enemy in self.enemies:
                enemy.update(self.platforms)
                
            hero_rect = self.hero.get_rect()
            game_over = False
            
            for enemy in self.enemies:
                if hero_rect.colliderect(enemy.get_rect()):
                    game_over = True
                    break
            
            if game_over:
                self.state = "game_over"
                # Tocar som de colisão com inimigo
                if self.sounds_on:
                    sounds.hit.play()
                if self.music_on:
                    music.stop()
                return
                
            crystals_to_remove = []
            for crystal in self.crystals:
                if not crystal.collected and hero_rect.colliderect(crystal.get_rect()):
                    crystal.collected = True
                    crystals_to_remove.append(crystal)
                    self.crystals_collected += 1
                    self.score += 100
                    
                    # Tocar som de coleta
                    if self.sounds_on:
                        sounds.crystal_collect.play()
            
            for crystal in crystals_to_remove:
                self.crystals.remove(crystal)
            
            if len(self.crystals) == 0:
                if self.level < 3:
                    self.next_level()
                    # Tocar som de vitória do nível
                    if self.sounds_on:
                        sounds.victory.play()
                else:
                    self.state = "victory"
                    # Tocar som de vitória final
                    if self.sounds_on:
                        sounds.victory.play()
                    if self.music_on:
                        music.stop()

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 255)):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.color = color
        
    def draw(self):
        screen.draw.filled_rect(self.rect, self.color)
        screen.draw.text(self.text, 
                        center=self.rect.center,
                        color=(255, 255, 255),
                        fontsize=24)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Inicialização do jogo
game = Game()
start_button = Button(300, 200, 200, 50, "Iniciar Jogo", color=(0, 0, 0))
music_button = Button(300, 270, 200, 50, "Música: LIGADA", color=(0, 0, 0))
sounds_button = Button(300, 340, 200, 50, "Sons: LIGADOS", color=(0, 0, 0))
quit_button = Button(300, 410, 200, 50, "Sair", color=(0, 0, 0))

def draw():
    screen.clear()
    
    # Background
    screen.blit("background", (0, 0))
    
    if game.state == "menu":
        screen.draw.text("A Missão Cristalina", 
                        center=(WIDTH/2, 100), 
                        fontsize=48, 
                        color=(255, 0, 0))
        
        start_button.draw()
        music_button.draw()
        sounds_button.draw()
        quit_button.draw()
        
    elif game.state == "playing":
        # Desenhar plataformas (simples)
        for platform in game.platforms:
            screen.draw.filled_rect(platform, (59, 136, 14))
            screen.draw.rect(platform, (47, 109, 11))
        
        # Desenhar cristais
        for crystal in game.crystals:
            crystal.draw()
        
        # Desenhar inimigos
        for enemy in game.enemies:
            enemy.draw()
        
        # Desenhar herói
        game.hero.draw()
        
        # HUD
        screen.draw.filled_rect(Rect(5, 5, 150, 90), (200, 200, 200, 150))
        screen.draw.text(f"Pontuação: {game.score}", (10, 10), color=(47, 109, 11))
        screen.draw.text(f"Nível: {game.level}/3", (10, 40), color=(47, 109, 11))
        screen.draw.text(f"Cristais: {game.crystals_collected}/{game.total_crystals_per_level}", 
                        (10, 70), color=(47, 109, 11))
        screen.draw.text("Setas laterais mover, ESPAÇO pular", (WIDTH-330, HEIGHT-30), color=(0, 0, 0))
    
    elif game.state == "game_over":
        screen.draw.filled_rect(Rect(100, 150, WIDTH-200, 250), (0, 0, 0, 200))
        screen.draw.text("FIM DE JOGO", center=(WIDTH/2, 200), fontsize=48, color=(255, 0, 0))
        screen.draw.text(f"Pontuação Final: {game.score}", center=(WIDTH/2, 280), fontsize=32, color=(255, 255, 255))
        screen.draw.text("Clique para voltar ao menu", center=(WIDTH/2, 350), fontsize=24, color=(200, 200, 200))
    
    elif game.state == "victory":
        screen.draw.filled_rect(Rect(50, 120, WIDTH-100, 300), (0, 0, 0, 200))
        screen.draw.text("VITÓRIA!", center=(WIDTH/2, 150), fontsize=64, color=(255, 215, 0))
        screen.draw.text("Você coletou todos os cristais!", center=(WIDTH/2, 230), fontsize=32, color=(255, 255, 255))
        screen.draw.text(f"Pontuação Final: {game.score}", center=(WIDTH/2, 280), fontsize=32, color=(255, 255, 255))
        screen.draw.text(f"Níveis Completos: 3/3", center=(WIDTH/2, 320), fontsize=32, color=(255, 255, 255))
        screen.draw.text("Clique para jogar novamente", center=(WIDTH/2, 380), fontsize=24, color=(200, 200, 255))

def update():
    game.update()

def on_key_down(key):
    if game.state == "playing":
        if key == keys.LEFT:
            game.hero.move_left = True
        elif key == keys.RIGHT:
            game.hero.move_right = True
        elif key == keys.SPACE:
            game.hero.jump()

def on_key_up(key):
    if game.state == "playing":
        if key == keys.LEFT:
            game.hero.move_left = False
        elif key == keys.RIGHT:
            game.hero.move_right = False

def on_mouse_down(pos):
    if game.state == "menu":
        if start_button.is_clicked(pos):
            game.start_new_game()
        elif music_button.is_clicked(pos):
            game.music_on = not game.music_on
            music_button.text = f"Música: {'LIGADA' if game.music_on else 'DESLIGADA'}"
            if game.music_on:
                music.play("background_music")
                music.set_volume(0.6)
            else:
                music.stop()
        elif sounds_button.is_clicked(pos):
            game.sounds_on = not game.sounds_on
            sounds_button.text = f"Sons: {'LIGADOS' if game.sounds_on else 'DESLIGADOS'}"
        elif quit_button.is_clicked(pos):
            exit()
    
    elif game.state == "game_over":
        game.state = "menu"
    
    elif game.state == "victory":
        game.state = "menu"

pgzrun.go()
