import pygame, json
from sys import exit

def load_image(filename):
    return pygame.image.load(f"images/{filename}").convert_alpha()

def load_font(filename, size):
    return pygame.font.Font(f"font/{filename}", size)

class Score(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = load_font("kongtext.ttf", 20)
        self.value = 0
        self.color = 'Black'
        self.typing = False
        self.digit_appending = False

    def increment(self):
        self.value += 1

    def decrement(self):
        if self.value > 0:
            self.value -= 1

    def reset(self):
        if self.typing:
            self.value = 0

    def change_color(self):
        if self.typing:
            self.color = '#0033CC'
        else:
            self.color = 'Black'

    def activate_typing(self):
        self.digit_appending = False
        if not self.typing:
            self.typing = True
        
        self.change_color()

    def deactivate_typing(self):
        if self.typing:
            self.typing = False
            self.digit_appending = False
            self.color = 'Black'

    def handle_typing(self, event):
        if event.key == pygame.K_BACKSPACE:
            if len(str(self.value)) > 1:
                self.value = int(str(self.value)[:-1])
            else:
                self.value = 0
        elif event.key == pygame.K_RETURN:
            self.deactivate_typing()
        elif event.unicode.isdigit():
            if not self.digit_appending:
                self.value = int(event.unicode)
                self.digit_appending = True
            else:
                self.value = int(str(self.value) + event.unicode)

    def draw(self, screen, x_pos, y_pos):
        score_value_surf = self.font.render(str(self.value), False, self.color)
        score_value_rect = score_value_surf.get_rect(midleft=(x_pos, y_pos))
        screen.blit(score_value_surf, score_value_rect)

        return score_value_rect

class Counter(Score):
    def __init__(self, name, x_pos, y_pos):
        super().__init__()
        self.name = name
        self.y_pos = y_pos
        self.x_pos = x_pos

        self.button_up = load_image("arrow_up.png").convert_alpha()
        self.button_down = load_image("arrow_down.png").convert_alpha()

    def draw(self, screen):
        score_surf = self.font.render(f"{self.name}: ", False, 'black')
        score_rect = score_surf.get_rect(midleft=(self.x_pos, self.y_pos))
        screen.blit(score_surf, score_rect)
        
        self.score_value_rect = super().draw(screen, score_rect.right, self.y_pos)
        
        self.button_up_rect = self.button_up.get_rect(midbottom=(self.score_value_rect.right + 30, self.y_pos - 7))
        self.button_down_rect = self.button_down.get_rect(midtop=(self.score_value_rect.right + 30, self.y_pos + 7))
        screen.blit(self.button_up, self.button_up_rect)
        screen.blit(self.button_down, self.button_down_rect)

class GameManager:
    def __init__(self):
        self.screen_width = 600
        self.screen_height = 400
        self.screen_center_x = self.screen_width // 2
        self.screen_center_y = self.screen_height // 2

        self.init_pygame()
        self.load_data()

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption('Streak Counter')
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        x_pos = self.screen_center_x - 155
        y_pos = self.screen_center_y - 85

        self.streak = Counter('Streak',x_pos, y_pos)
        self.relapse = Counter('Relapse',x_pos, y_pos + 55)
        self.total_days = Counter('Total Days',x_pos, y_pos + 110)
        self.best_streak = Counter('Best Streak',x_pos, y_pos + 165)
        counters = [self.streak, self.relapse, self.best_streak, self.total_days]
        self.counters = pygame.sprite.Group()
        for counter in counters:
            self.counters.add(counter)

    def load_data(self):
        try:
            with open('Streak_Counter.txt') as score_file:
                data = json.load(score_file)
                for counter in self.counters:
                    if counter.name in data:
                        counter.value = data[counter.name]
        except:
            pass

    def save_data(self):
        data = {}
        for counter in self.counters:
            data[counter.name] = counter.value

        with open('StreakCounter.txt', 'w') as score_file:
            json.dump(data, score_file)

    def deactivate(self, counters):
        for counter in counters:
            counter.deactivate_typing()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_data()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for counter in self.counters:
                    if counter.button_up_rect.collidepoint(event.pos):
                        counter.increment()
                        self.deactivate(self.counters)
                    elif counter.button_down_rect.collidepoint(event.pos):
                        counter.decrement()
                        self.deactivate(self.counters)
                    elif counter.score_value_rect.collidepoint(event.pos):
                        self.deactivate(self.counters)
                        counter.activate_typing()
                    else:
                        counter.deactivate_typing()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    for counter in self.counters:
                        if counter.typing:
                            counter.increment()
                elif event.key == pygame.K_DOWN:
                    for counter in self.counters:
                        if counter.typing:
                            counter.decrement()
                elif event.key == pygame.K_r:
                    for counter in self.counters:
                        counter.reset()
                    self.deactivate(self.counters)
                else:
                    for counter in self.counters:
                        if counter.typing:
                            counter.handle_typing(event)               

    def update_screen(self):
        self.screen.fill('White')

        self.streak.draw(self.screen)
        self.relapse.draw(self.screen)
        self.total_days.draw(self.screen)
        self.best_streak.draw(self.screen)

        pygame.display.update()

    def run(self):
        while True:
            self.handle_events()
            self.update_screen()
            self.clock.tick(60)

if __name__ == "__main__":
    game = GameManager()
    game.run()