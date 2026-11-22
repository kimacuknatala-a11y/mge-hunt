import os
import json
import random
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.audio import SoundLoader

# ========== ПЛАТФОРМА ==========
IS_MOBILE = platform in ['android', 'ios']
IS_PC = not IS_MOBILE

# ========== ПУТИ ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_resource_path(filename):
    return os.path.join(BASE_DIR, filename)

# ========== НАСТРОЙКИ ==========
CHARACTERS = {
    "heavy": {"name": "MGE Heavy", "rarity": "Обычный", "price": 0, 
              "image": "Photo/heavy.png", "sound_folder": "music/heavy"},
    "sniper": {"name": "MGE Sniper", "rarity": "Редкий", "price": 500, 
               "image": "Photo/sniper.jpg", "sound_folder": "music/sniper"},
    "scout": {"name": "MGE Scout", "rarity": "Мифический", "price": 5000, 
              "image": "Photo/mgescout.jpg", "sound_folder": "music/scoutmge"},
    "engineer": {"name": "MGE Engineer", "rarity": "Ультра Легендарный", "price": 100000000, 
                 "image": "Photo/ingenier.jpg", "sound_folder": "music/ingenier"}
}
CHARACTER_ORDER = ["heavy", "sniper", "scout", "engineer"]

BG_IMAGE = get_resource_path("Photo/back.png")
SCOUT_IMAGE = get_resource_path("Photo/scoutfemboy.png")
MUSIC_FILE = get_resource_path("music/main_sound.ogg")
SCREAM_FILE = get_resource_path("music/scoutfemboy.ogg")

# ========== СОХРАНЕНИЯ ==========
SAVE_FILE = os.path.join(BASE_DIR, "save.json")

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"total_scouts": 0, "unlocked": ["heavy"], "current_character": "heavy"}

def save_game(data):
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass


# ========== ЗВУКИ ==========
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music = None
        self.scream = None
        
        for char_id, char_data in CHARACTERS.items():
            folder = get_resource_path(char_data["sound_folder"])
            if os.path.exists(folder):
                self.sounds[char_id] = {"attack": [], "start": []}
                for file in os.listdir(folder):
                    if file.endswith('.ogg'):
                        path = os.path.join(folder, file)
                        sound = SoundLoader.load(path)
                        if sound:
                            if 'attack' in file.lower():
                                self.sounds[char_id]["attack"].append(sound)
                            elif 'start' in file.lower():
                                self.sounds[char_id]["start"].append(sound)
        
        if os.path.exists(MUSIC_FILE):
            self.music = SoundLoader.load(MUSIC_FILE)
            if self.music:
                self.music.loop = True
                self.music.volume = 0.3
        
        if os.path.exists(SCREAM_FILE):
            self.scream = SoundLoader.load(SCREAM_FILE)
    
    def play_start(self, char_id):
        if char_id in self.sounds and self.sounds[char_id]["start"]:
            sound = random.choice(self.sounds[char_id]["start"])
            sound.play()
    
    def play_attack(self, char_id):
        if char_id in self.sounds and self.sounds[char_id]["attack"]:
            sound = random.choice(self.sounds[char_id]["attack"])
            sound.play()
    
    def play_scream(self):
        if self.scream:
            self.scream.play()
    
    def start_music(self):
        if self.music:
            self.music.play()


# ========== ФОНОВЫЙ ВИДЖЕТ ==========
class BackgroundImage(Image):
    """Картинка-фон, растягивающаяся на весь экран"""
    def __init__(self, source, **kwargs):
        super().__init__(source=source, **kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.size_hint = (1, 1)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}


# ========== МЕНЮ ==========
class MenuScreen(FloatLayout):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.save_data = load_save()
        
        # Фон
        if os.path.exists(BG_IMAGE):
            self.add_widget(BackgroundImage(BG_IMAGE))
        
        # Затемнение
        with self.canvas:
            Color(0, 0, 0, 0.7)
            self.dark_rect = Rectangle(pos=(0, 0), size=self.size)
        self.bind(size=self._update_dark, pos=self._update_dark)
        
        # Заголовок
        title = Label(
            text="TF2: MGE HUNT",
            size_hint=(1, 0.15),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            font_size='48sp', bold=True,
            color=(1, 0.84, 0, 1),
            halign='center', valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        self.add_widget(title)
        
        # Статистика
        stats = Label(
            text=f"Всего поймано: {self.save_data['total_scouts']}\nПерсонаж: {CHARACTERS[self.save_data['current_character']]['name']}",
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.75},
            font_size='20sp',
            color=(1, 1, 1, 1),
            halign='center', valign='middle'
        )
        stats.bind(size=stats.setter('text_size'))
        self.add_widget(stats)
        
        # Кнопки (FloatLayout правильно обрабатывает pos_hint!)
        btn_start = Button(
            text="НАЧАТЬ ОХОТУ",
            size_hint=(0.5, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
            background_color=(0.3, 0.7, 0.3, 1),
            font_size='24sp'
        )
        btn_start.bind(on_press=lambda x: app_ref.start_game())
        self.add_widget(btn_start)
        
        btn_shop = Button(
            text="МАГАЗИН",
            size_hint=(0.5, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.42},
            background_color=(0.2, 0.6, 0.9, 1),
            font_size='24sp'
        )
        btn_shop.bind(on_press=lambda x: app_ref.show_shop())
        self.add_widget(btn_shop)
        
        hint_text = "WASD / Стрелки" if IS_PC else "Кнопки на экране"
        hint = Label(
            text=hint_text,
            size_hint=(1, 0.05),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1),
            halign='center', valign='middle'
        )
        hint.bind(size=hint.setter('text_size'))
        self.add_widget(hint)
    
    def _update_dark(self, *args):
        if hasattr(self, 'dark_rect'):
            self.dark_rect.pos = self.pos
            self.dark_rect.size = self.size


# ========== ИГРОВОЙ ЭКРАН ==========
class GameScreen(FloatLayout):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.save_data = load_save()
        self.sound_manager = app_ref.sound_manager
        
        self.player_size = 100
        self.player_speed = 8
        self.session_scouts = 0
        self.game_time = 60
        self.running = False
        self.targets = []
        self.target_widgets = []
        
        self.move_x = 0
        self.move_y = 0
        
        self.player_x = Window.width / 2
        self.player_y = Window.height / 2
        
        # Фон
        if os.path.exists(BG_IMAGE):
            self.add_widget(BackgroundImage(BG_IMAGE))
        
        # Игрок
        char_id = self.save_data["current_character"]
        char_image_path = get_resource_path(CHARACTERS[char_id]["image"])
        
        if os.path.exists(char_image_path):
            self.player_img = Image(
                source=char_image_path,
                size_hint=(None, None),
                size=(100, 100),
                pos=(self.player_x - 50, self.player_y - 50)
            )
            self.add_widget(self.player_img)
            self.player_rect = None
        else:
            with self.canvas:
                Color(0.35, 0.52, 0.64, 1)
                self.player_rect = Rectangle(
                    pos=(self.player_x - 50, self.player_y - 50),
                    size=(100, 100)
                )
            self.player_img = None
        
        # UI: счётчик
        self.score_label = Label(
            text="Поймано: 0",
            size_hint=(None, None),
            size=(250, 50),
            pos=(10, Window.height - 60),
            font_size='24sp', bold=True,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.score_label)
        
        # UI: таймер
        self.time_label = Label(
            text="Время: 60",
            size_hint=(None, None),
            size=(250, 50),
            pos=(Window.width - 260, Window.height - 60),
            font_size='24sp', bold=True,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.time_label)
        
        # Мобильные кнопки
        if IS_MOBILE:
            self._add_mobile_controls()
        
        # Клавиатура ПК
        if IS_PC:
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
    
    def _keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        if key in ['w', 'up']: self.move_y = 1
        elif key in ['s', 'down']: self.move_y = -1
        elif key in ['a', 'left']: self.move_x = -1
        elif key in ['d', 'right']: self.move_x = 1
        elif key == 'escape': self.app_ref.stop_game()
        return True
    
    def _on_key_up(self, keyboard, keycode):
        key = keycode[1] if isinstance(keycode, tuple) else str(keycode)
        if key in ['w', 's', 'up', 'down']: self.move_y = 0
        if key in ['a', 'd', 'left', 'right']: self.move_x = 0
        return True
    
    def _add_mobile_controls(self):
        btn_size = (80, 80)
        margin = 30
        
        buttons = [
            ('▲', (0, 1), (Window.width/2 - 40, margin + 180)),
            ('▼', (0, -1), (Window.width/2 - 40, margin)),
            ('◀', (-1, 0), (margin, margin + 90)),
            ('▶', (1, 0), (Window.width - margin - 80, margin + 90))
        ]
        
        for symbol, (dx, dy), pos in buttons:
            btn = Button(text=symbol, font_size='32sp', size_hint=(None, None),
                        size=btn_size, pos=pos, background_color=(0.3, 0.3, 0.3, 0.7))
            btn.bind(on_press=lambda x, dx=dx, dy=dy: self._set_move(dx, dy),
                    on_release=lambda x: self._set_move(0, 0))
            self.add_widget(btn)
    
    def _set_move(self, dx, dy):
        self.move_x = dx
        self.move_y = dy
    
    def start_game(self):
        self.running = True
        self.game_time = 60
        self.session_scouts = 0
        self.player_x = Window.width / 2
        self.player_y = Window.height / 2
        self._spawn_targets(5)
        
        Clock.schedule_interval(self._update, 1/60)
        Clock.schedule_interval(self._update_timer, 1)
        
        self.sound_manager.start_music()
        self.sound_manager.play_start(self.save_data["current_character"])
    
    def _spawn_targets(self, count):
        for _ in range(count):
            tx = random.randint(100, int(Window.width) - 100)
            ty = random.randint(100, int(Window.height) - 200)
            target = {'x': tx, 'y': ty, 'speed_x': random.choice([-3, -2, 2, 3]),
                     'speed_y': random.choice([-3, -2, 2, 3])}
            self.targets.append(target)
            
            if os.path.exists(SCOUT_IMAGE):
                img = Image(source=SCOUT_IMAGE, size_hint=(None, None),
                           size=(70, 70), pos=(tx - 35, ty - 35))
                self.add_widget(img)
                self.target_widgets.append({'data': target, 'widget': img, 'type': 'image'})
            else:
                with self.canvas:
                    Color(0.72, 0.22, 0.23, 1)
                    rect = Ellipse(pos=(tx - 30, ty - 30), size=(60, 60))
                self.target_widgets.append({'data': target, 'widget': rect, 'type': 'canvas'})
    
    def _update(self, dt):
        if not self.running:
            return
        
        self.player_x += self.move_x * self.player_speed
        self.player_y += self.move_y * self.player_speed
        self.player_x = max(50, min(Window.width - 50, self.player_x))
        self.player_y = max(50, min(Window.height - 50, self.player_y))
        
        if self.player_img:
            self.player_img.pos = (self.player_x - 50, self.player_y - 50)
        elif self.player_rect:
            self.player_rect.pos = (self.player_x - 50, self.player_y - 50)
        
        for tw in self.target_widgets[:]:
            t = tw['data']
            dist = ((t['x'] - self.player_x)**2 + (t['y'] - self.player_y)**2)**0.5
            
            if dist < 100:
                dx = t['x'] - self.player_x
                dy = t['y'] - self.player_y
                length = max(1, (dx**2 + dy**2)**0.5)
                t['x'] += (dx / length) * 5
                t['y'] += (dy / length) * 5
            else:
                t['x'] += t['speed_x']
                t['y'] += t['speed_y']
            
            if t['x'] < 30 or t['x'] > Window.width - 30:
                t['speed_x'] *= -1
            if t['y'] < 30 or t['y'] > Window.height - 200:
                t['speed_y'] *= -1
            
            t['x'] = max(30, min(Window.width - 30, t['x']))
            t['y'] = max(30, min(Window.height - 200, t['y']))
            
            if tw['type'] == 'image':
                tw['widget'].pos = (t['x'] - 35, t['y'] - 35)
            else:
                tw['widget'].pos = (t['x'] - 30, t['y'] - 30)
            
            if abs(t['x'] - self.player_x) < 50 and abs(t['y'] - self.player_y) < 50:
                self.session_scouts += 1
                self.score_label.text = f"Поймано: {self.session_scouts}"
                
                self.sound_manager.play_attack(self.save_data["current_character"])
                self.sound_manager.play_scream()
                
                if tw['type'] == 'image':
                    self.remove_widget(tw['widget'])
                else:
                    self.canvas.remove(tw['widget'])
                self.target_widgets.remove(tw)
                self.targets.remove(t)
                self._spawn_targets(1)
    
    def _update_timer(self, dt):
        if not self.running:
            return
        self.game_time -= 1
        self.time_label.text = f"Время: {self.game_time}"
        if self.game_time <= 0:
            self.end_game()
    
    def end_game(self):
        self.running = False
        self.save_data["total_scouts"] += self.session_scouts
        save_game(self.save_data)
        self.app_ref.show_end_screen(self.session_scouts)


# ========== МАГАЗИН ==========
class ShopScreen(FloatLayout):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.save_data = load_save()
        
        with self.canvas:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        title = Label(
            text="МАГАЗИН",
            size_hint=(1, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            font_size='36sp', bold=True,
            color=(1, 0.84, 0, 1),
            halign='center', valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        self.add_widget(title)
        
        balance = Label(
            text=f"Баланс: {self.save_data['total_scouts']} скаутов",
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'top': 0.82},
            font_size='20sp',
            color=(1, 1, 1, 1),
            halign='center', valign='middle'
        )
        balance.bind(size=balance.setter('text_size'))
        self.add_widget(balance)
        
        # Карточки персонажей (используем pos_hint для центрирования)
        y_positions = [0.70, 0.58, 0.46, 0.34]
        for i, char_id in enumerate(CHARACTER_ORDER):
            char = CHARACTERS[char_id]
            unlocked = char_id in self.save_data["unlocked"]
            current = char_id == self.save_data["current_character"]
            
            card_text = f"{char['name']} | {char['rarity']} | Цена: {char['price']}"
            card = Label(
                text=card_text,
                size_hint=(0.7, 0.1),
                pos_hint={'center_x': 0.5, 'top': y_positions[i]},
                font_size='16sp',
                color=(1, 1, 1, 1),
                halign='left', valign='middle'
            )
            card.bind(size=card.setter('text_size'))
            self.add_widget(card)
            
            # Картинка персонажа
            img_path = get_resource_path(char["image"])
            if os.path.exists(img_path):
                img = Image(
                    source=img_path,
                    size_hint=(None, None),
                    size=(60, 60),
                    pos_hint={'x': 0.05, 'top': y_positions[i] + 0.02}
                )
                self.add_widget(img)
            
            # Кнопки
            if unlocked:
                if current:
                    status = Label(
                        text="✓ ВЫБРАН",
                        size_hint=(None, None),
                        size=(150, 40),
                        pos_hint={'right': 0.95, 'top': y_positions[i] + 0.03},
                        font_size='16sp',
                        color=(1, 0.84, 0, 1)
                    )
                    self.add_widget(status)
                else:
                    btn = Button(
                        text="ВЫБРАТЬ",
                        size_hint=(None, None),
                        size=(150, 50),
                        pos_hint={'right': 0.95, 'top': y_positions[i] + 0.02},
                        background_color=(0.2, 0.6, 0.9, 1)
                    )
                    btn.bind(on_press=lambda x, cid=char_id: self._select(cid))
                    self.add_widget(btn)
            else:
                if self.save_data["total_scouts"] >= char["price"]:
                    btn = Button(
                        text="КУПИТЬ",
                        size_hint=(None, None),
                        size=(150, 50),
                        pos_hint={'right': 0.95, 'top': y_positions[i] + 0.02},
                        background_color=(0.3, 0.7, 0.3, 1)
                    )
                    btn.bind(on_press=lambda x, cid=char_id: self._buy(cid))
                    self.add_widget(btn)
                else:
                    status = Label(
                        text="НЕ ХВАТАЕТ",
                        size_hint=(None, None),
                        size=(150, 40),
                        pos_hint={'right': 0.95, 'top': y_positions[i] + 0.03},
                        font_size='14sp',
                        color=(0.5, 0.5, 0.5, 1)
                    )
                    self.add_widget(status)
        
        btn_back = Button(
            text="НАЗАД",
            size_hint=(0.4, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            background_color=(0.8, 0.2, 0.2, 1),
            font_size='20sp'
        )
        btn_back.bind(on_press=lambda x: app_ref.show_menu())
        self.add_widget(btn_back)
    
    def _update_bg(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def _select(self, char_id):
        self.save_data["current_character"] = char_id
        save_game(self.save_data)
        self.app_ref.show_shop()
    
    def _buy(self, char_id):
        char = CHARACTERS[char_id]
        if self.save_data["total_scouts"] >= char["price"]:
            self.save_data["total_scouts"] -= char["price"]
            if char_id not in self.save_data["unlocked"]:
                self.save_data["unlocked"].append(char_id)
            self.save_data["current_character"] = char_id
            save_game(self.save_data)
            self.app_ref.show_shop()


# ========== КОНЕЦ ИГРЫ ==========
class EndScreen(FloatLayout):
    def __init__(self, app_ref, score, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        
        with self.canvas:
            Color(0.1, 0.1, 0.15, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        title = Label(
            text="ОХОТА ОКОНЧЕНА!",
            size_hint=(1, 0.15),
            pos_hint={'center_x': 0.5, 'top': 0.85},
            font_size='40sp', bold=True,
            color=(1, 0.84, 0, 1),
            halign='center', valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        self.add_widget(title)
        
        score_lbl = Label(
            text=f"Поймано: {score}",
            size_hint=(1, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.65},
            font_size='28sp',
            color=(1, 1, 1, 1),
            halign='center', valign='middle'
        )
        score_lbl.bind(size=score_lbl.setter('text_size'))
        self.add_widget(score_lbl)
        
        btn = Button(
            text="В МЕНЮ",
            size_hint=(0.4, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.3, 0.7, 0.3, 1),
            font_size='24sp'
        )
        btn.bind(on_press=lambda x: app_ref.show_menu())
        self.add_widget(btn)
    
    def _update_bg(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size


# ========== ПРИЛОЖЕНИЕ ==========
class MGEHuntApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_widget = None
        self.game_widget = None
        self.sound_manager = SoundManager()
    
    def build(self):
        # ВАЖНО: корневой виджет — FloatLayout, а не Widget!
        self.root_widget = FloatLayout()
        Window.clearcolor = (0.1, 0.1, 0.15, 1)
        self.show_menu()
        return self.root_widget
    
    def show_menu(self):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(MenuScreen(self))
    
    def start_game(self):
        self.root_widget.clear_widgets()
        self.game_widget = GameScreen(self)
        self.root_widget.add_widget(self.game_widget)
        self.game_widget.start_game()
    
    def show_end_screen(self, score):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(EndScreen(self, score))
    
    def show_shop(self):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(ShopScreen(self))
    
    def stop_game(self):
        if self.game_widget:
            self.game_widget.running = False
        self.show_menu()


if __name__ == '__main__':
    MGEHuntApp().run()