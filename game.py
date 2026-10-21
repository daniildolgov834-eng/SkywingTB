import pygame
import random
import sys
import math
import json
import os
from datetime import datetime
import time
from enum import Enum
from typing import List, Tuple, Optional, Dict
import numpy as np
import hashlib

try:
    import cv2
    OPENCV_AVAILABLE = True
    print("OpenCV loaded successfully")
except ImportError:
    OPENCV_AVAILABLE = False
    print("OpenCV not found")

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

pygame.joystick.init()
joysticks = []
for i in range(pygame.joystick.get_count()):
    try:
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        print(f"Found gamepad: {joystick.get_name()}")
    except Exception as e:
        print(f"Error initializing gamepad {i}: {e}")

BASE_WIDTH = 360
BASE_HEIGHT = 640
FPS = 60

RETRO_WHITE = (240, 235, 220)
RETRO_BLACK = (20, 18, 15)
RETRO_BG = (45, 40, 35)
RETRO_BG_LIGHT = (60, 55, 48)
RETRO_GOLD = (210, 180, 120)
RETRO_SILVER = (190, 185, 175)
RETRO_RED = (200, 80, 60)
RETRO_GREEN = (120, 180, 100)
RETRO_BLUE = (100, 150, 200)
RETRO_PURPLE = (160, 100, 180)
RETRO_ORANGE = (200, 140, 60)
RETRO_YELLOW = (220, 200, 100)
RETRO_GRAY = (130, 125, 120)
RETRO_DARK = (35, 30, 25)

LAKERS_YELLOW = (253, 185, 39)
LAKERS_GOLD = (250, 200, 60)

WHITE = RETRO_WHITE
BLACK = RETRO_BLACK
GOLD = RETRO_GOLD
SILVER = RETRO_SILVER
RED = RETRO_RED
GREEN = RETRO_GREEN
BLUE = RETRO_BLUE
PURPLE = RETRO_PURPLE
ORANGE = RETRO_ORANGE
YELLOW = RETRO_YELLOW
GRAY = RETRO_GRAY
DARK_GRAY = RETRO_DARK

MAGENTA = (200, 50, 200)
TURQUOISE = (64, 224, 208)
VIOLET = (180, 50, 200)
PINK = (220, 150, 180)
LIME = (180, 210, 80)
TEAL = (0, 150, 136)
INDIGO = (75, 0, 130)
LAVENDER = (210, 200, 230)
CRIMSON = (200, 40, 60)
DARK_PURPLE = (100, 50, 150)
LIGHT_GRAY = (200, 195, 185)
DARK_RED = (150, 40, 30)
DARK_BLUE = (0, 0, 139)
DARK_GREEN = (0, 100, 0)
BROWN = (120, 80, 50)
LIGHT_BROWN = (160, 120, 80)
DARK_BROWN = (80, 50, 30)
CYAN = (100, 200, 220)
BRONZE = (180, 140, 70)
DIAMOND = (200, 230, 255)
BEIGE_GREEN = (164, 196, 128)
GREEN_YELLOW = (173, 255, 47)
BRONZE_GREEN = (205, 165, 80)
SILVER_GREEN = (192, 192, 180)
GOLD_GREEN = (255, 215, 120)
EXP_BAR_COLOR = (120, 200, 180)
LEVEL_UP_COLOR = RETRO_GOLD
GROUND_COLOR = (180, 170, 140)
BACKGROUND_COLOR = RETRO_BG
BACKGROUND_COLOR_TOP = (80, 75, 65)
BACKGROUND_COLOR_BOTTOM = (40, 35, 30)
BASKETBALL_ORANGE = (200, 140, 60)
TENNIS_CLAY = (180, 130, 90)
TENNIS_GRASS = (120, 180, 100)
TENNIS_HARD = (160, 155, 145)
RETRO_BORDER = (200, 180, 150)
SILVER_GLOW = (220, 215, 205)
SILVER_SHINE = (240, 235, 225)

GAME_TITLE = "Skywing"
GAME_VERSION = "3.4.2"
GAME_SUBTITLE = "TENNIS and BASKETBALL"

IS_ANDROID = hasattr(sys, 'getandroidapilevel') or 'ANDROID_STORAGE' in os.environ or os.environ.get('ANDROID_ARGUMENT') is not None

if IS_ANDROID:
    try:
        from android import mActivity
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    except Exception as e:
        print(f"Android permissions error: {e}")


class ControlType(Enum):
    KEYBOARD = "keyboard"
    GAMEPAD = "gamepad"
    TOUCH = "touch"


class AntiCheat:
    def __init__(self):
        self.salt = "SKYWING_ANTICHEAT_SALT_2024"
        self.verified = True

    def verify_save_data(self, data):
        if not data:
            return False
        try:
            data_hash = data.get('_hash', '')
            if data_hash:
                verify_data = {k: v for k, v in data.items() if k != '_hash'}
                check_str = json.dumps(verify_data, sort_keys=True) + self.salt
                check_hash = hashlib.md5(check_str.encode()).hexdigest()
                if check_hash != data_hash:
                    return False
            return True
        except Exception as e:
            print(f"Anti-cheat verification error: {e}")
            return False

    def generate_hash(self, data):
        try:
            data_str = json.dumps(data, sort_keys=True) + self.salt
            return hashlib.md5(data_str.encode()).hexdigest()
        except:
            return ""

    def check_coins(self, coins, previous_coins, max_change=1000):
        if coins > previous_coins:
            change = coins - previous_coins
            if change > max_change:
                return False, f"Too many coins at once: +{change}"
        return True, "OK"

    def check_stats(self, stats):
        if stats.get('score', 0) > 10000:
            return False, "Score too high"
        if stats.get('max_combo', 0) > 1000:
            return False, "Combo too high"
        if stats.get('coins', 0) > 10000000:
            return False, "Too many coins"
        return True, "OK"


anti_cheat = AntiCheat()


def get_android_storage_path():
    if not IS_ANDROID:
        return None
    possible_paths = [
        "/storage/emulated/0/Skywing",
        "/sdcard/Skywing",
        os.path.expanduser("~/Skywing"),
    ]
    for p in possible_paths:
        try:
            if not os.path.exists(p):
                os.makedirs(p)
            test_file = os.path.join(p, ".test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return p
        except Exception:
            continue
    return None


ANDROID_STORAGE_PATH = get_android_storage_path() if IS_ANDROID else None


def get_skin_search_paths(mode, is_opponent=False, is_cup=False):
    paths = []
    if is_cup:
        local_dir = f"skins/cups/{mode}"
    elif is_opponent:
        local_dir = f"skins/{mode}_opponent"
    else:
        local_dir = f"skins/{mode}"
    paths.append(local_dir)
    if IS_ANDROID:
        if ANDROID_STORAGE_PATH:
            if is_cup:
                paths.append(os.path.join(ANDROID_STORAGE_PATH, f"skins/cups/{mode}"))
            elif is_opponent:
                paths.append(os.path.join(ANDROID_STORAGE_PATH, f"skins/{mode}_opponent"))
            else:
                paths.append(os.path.join(ANDROID_STORAGE_PATH, f"skins/{mode}"))
        paths.append(f"/sdcard/Skywing/skins/{mode}")
        paths.append(f"/storage/emulated/0/Skywing/skins/{mode}")
    return paths


def find_skin_directory(mode, is_opponent=False, is_cup=False):
    for path in get_skin_search_paths(mode, is_opponent, is_cup):
        if os.path.exists(path) and os.path.isdir(path):
            return path
    for path in get_skin_search_paths(mode, is_opponent, is_cup):
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except Exception:
            continue
    return get_skin_search_paths(mode, is_opponent, is_cup)[0]


def generate_random_nicks(count=100):
    prefixes = ["xX", "Xx", "Kill", "Death", "Shadow", "Night", "Dark", "Light", "Fire", "Ice", "Storm", "Thunder",
                "Crimson", "Phantom", "Ghost", "Viper", "Wolf", "Hawk", "Falcon", "Eagle", "Tiger", "Dragon",
                "Sniper", "Hunter", "Warden", "Reaper", "Venom", "Fury", "Rage", "Wraith", "Spectre", "Nova",
                "Zero", "Omega", "Alpha", "Beta", "Sigma", "Delta", "Neon", "Void", "Frost", "Blaze", "Vortex",
                "Mystic", "Crystal", "Blade", "Steel", "Iron", "Silver", "Golden", "Diamond", "Platinum"]

    suffixes = ["_", "-", " ", " ", " ", "Pro", "Elite", "Legend", "God", "King",
                "Queen", "Lord", "Master", "Slayer", "Killer", "Demon", "Angel", "Devil", "Saint", "Sinner", "Hero"]

    middles = ["", "Reap", "Slay", "Destroy", "Annihilate", "Obliterate", "Decimate", "Devastate", "Crush", "Smash",
               "Rip", "Tear", "Break", "Shatter", "Fracture", "Sunder", "Sever", "Cleave", "Carve", "Mangle"]

    numbers = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18",
               "19", "20"]

    nicks = []
    for _ in range(count):
        prefix = random.choice(prefixes)
        middle = random.choice(middles) if random.random() < 0.3 else ""
        suffix = random.choice(suffixes) if random.random() < 0.2 else ""
        number = random.choice(numbers) if random.random() < 0.3 else ""

        if random.random() < 0.4:
            nick = random.choice(prefixes[:20]) + random.choice(suffixes[:5]) + random.choice(numbers[:5])
        elif random.random() < 0.7:
            nick = random.choice(prefixes) + random.choice(middles[:10]) + random.choice(suffixes) + random.choice(
                numbers[:10])
        else:
            nick = random.choice(prefixes) + random.choice(suffixes[:3]) + random.choice(
                middles) + random.choice(suffixes) + random.choice(numbers)

        nick = nick.replace("_xX", "").replace("Xx_", "").replace(" ", "")
        if len(nick) > 20:
            nick = nick[:20]
        if nick and nick not in nicks:
            nicks.append(nick)

    unique_nicks = ["NoobSlayer", "ProGamer", "KingKiller", "ShadowStrike", "NightHawk",
                    "CrimsonFury", "PhantomReaper", "StormBreaker", "IceCold", "FireStorm",
                    "DarkAngel", "LightningBolt", "ThunderGod", "WolfPack", "DragonSlayer"]
    for nick in unique_nicks:
        if nick not in nicks:
            nicks.append(nick)

    return nicks[:count]


def create_game_directories():
    dirs = [
        "skins/tennis",
        "skins/tennis_opponent",
        "skins/basketball",
        "skins/basketball_opponent",
        "skins/cups/tennis",
        "skins/cups/basketball",
        "backgrounds/main_menu",
        "backgrounds/basketball",
        "backgrounds/tennis",
        "backgrounds/world_ranking",
        "backgrounds/shop",
        "music/menu",
        "music/tennis",
        "music/basketball",
        "sounds/common",
        "sounds/tennis/player",
        "sounds/tennis/opponent",
        "sounds/basketball",
        "sounds/game",
        "tv_videos",
        "tv_tapes",
        "icons",
        "icons/desktop",
    ]

    if IS_ANDROID and ANDROID_STORAGE_PATH:
        android_dirs = [
            "skins/tennis", "skins/tennis_opponent", "skins/basketball", "skins/basketball_opponent",
            "skins/cups/tennis", "skins/cups/basketball", "backgrounds", "music", "sounds", "tv_videos", "tv_tapes"
        ]
        for d in android_dirs:
            try:
                os.makedirs(os.path.join(ANDROID_STORAGE_PATH, d), exist_ok=True)
            except Exception as e:
                print(f"Could not create Android directory {d}: {e}")

    for dir_path in dirs:
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created folder: {dir_path}")
        except Exception as e:
            print(f"Could not create {dir_path}: {e}")


def load_icon_from_folder(folder_path, icon_name="game_icon"):
    if not os.path.exists(folder_path):
        return None

    extensions = ["png", "ico", "jpg", "jpeg", "bmp", "gif"]
    for ext in extensions:
        file_path = os.path.join(folder_path, f"{icon_name}.{ext}")
        if os.path.exists(file_path):
            try:
                return pygame.image.load(file_path)
            except Exception as e:
                print(f"Failed to load icon {file_path}: {e}")
                continue
    return None


def set_game_icon():
    icon_surface = load_icon_from_folder("icons")

    if icon_surface is not None:
        try:
            pygame.display.set_icon(icon_surface)
            print("Game icon loaded from icons folder")
            return True
        except Exception as e:
            print(f"Failed to set icon: {e}")

    print("Icon not found in icons folder, creating pixel icon")
    pixel_icon = create_pixel_icon()
    pygame.display.set_icon(pixel_icon)
    return False


def create_pixel_icon():
    icon_size = 64
    icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    colors = {
        'bg': (0, 0, 0, 0),
        'body': (253, 185, 39),
        'body_dark': (200, 150, 30),
        'eye': (240, 235, 220),
        'pupil': (20, 18, 15),
        'beak': (200, 160, 80),
        'wing': (120, 180, 100),
        'outline': (44, 62, 80)
    }
    pygame.draw.circle(icon_surface, colors['body'], (32, 32), 24)
    pygame.draw.circle(icon_surface, colors['body_dark'], (32, 34), 20)
    pygame.draw.circle(icon_surface, colors['eye'], (40, 24), 6)
    pygame.draw.circle(icon_surface, colors['pupil'], (42, 24), 3)
    pygame.draw.circle(icon_surface, colors['eye'], (44, 22), 2)
    beak_points = [(48, 28), (60, 30), (48, 34)]
    pygame.draw.polygon(icon_surface, colors['beak'], beak_points)
    wing_points = [(20, 38), (8, 32), (16, 44), (28, 46)]
    pygame.draw.polygon(icon_surface, colors['wing'], wing_points)
    crest_points = [(28, 8), (36, 0), (44, 8)]
    pygame.draw.polygon(icon_surface, colors['body_dark'], crest_points)
    return icon_surface


def create_desktop_shortcut():
    if IS_ANDROID:
        return
    try:
        if sys.platform == "win32":
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")

            if os.path.exists(desktop_path):
                icon_path = os.path.join(os.getcwd(), "icons/desktop/game_icon.ico")
                if not os.path.exists(icon_path):
                    png_path = os.path.join(os.getcwd(), "icons/desktop/game_icon.png")
                    if os.path.exists(png_path):
                        icon_path = png_path
                    else:
                        icon_path = ""

                shortcut_path = os.path.join(desktop_path, "SKYWING.lnk")

                if not os.path.exists(shortcut_path):
                    script = f'''
                    $WScriptShell = New-Object -ComObject WScript.Shell
                    $Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}")
                    $Shortcut.TargetPath = "{sys.executable}"
                    $Shortcut.Arguments = "{os.path.abspath(__file__)}"
                    $Shortcut.WorkingDirectory = "{os.getcwd()}"
                    '''
                    if icon_path and os.path.exists(icon_path):
                        script += f'$Shortcut.IconLocation = "{icon_path}"\n'
                    script += '$Shortcut.Save()\n'

                    with open("create_shortcut.ps1", "w", encoding="utf-8") as f:
                        f.write(script)

                    try:
                        import subprocess
                        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "create_shortcut.ps1"],
                                       capture_output=True, timeout=10)
                        os.remove("create_shortcut.ps1")
                        print(f"Created desktop shortcut: {shortcut_path}")
                    except Exception as e:
                        print(f"Failed to create shortcut: {e}")

        elif sys.platform == "linux":
            desktop_path = os.path.expanduser("~/Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~/Рабочий стол")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~/desktop")

            if os.path.exists(desktop_path):
                icon_file = None
                icon_path = "icons/desktop/game_icon.png"
                if os.path.exists(icon_path):
                    icon_file = icon_path
                else:
                    for ext in ["ico", "jpg", "jpeg", "bmp", "gif"]:
                        test_path = f"icons/desktop/game_icon.{ext}"
                        if os.path.exists(test_path):
                            icon_file = test_path
                            break

                if not icon_file:
                    for ext in ["png", "ico", "jpg", "jpeg"]:
                        test_path = f"icons/game_icon.{ext}"
                        if os.path.exists(test_path):
                            icon_file = test_path
                            break

                if icon_file:
                    icon_path_abs = os.path.abspath(icon_file)
                else:
                    icon_path_abs = ""

                shortcut_path = os.path.join(desktop_path, "SKYWING.desktop")

                if not os.path.exists(shortcut_path):
                    shortcut_content = f'''[Desktop Entry]
Name=SKYWING
Comment=Tennis and Basketball
Exec=python3 "{os.path.abspath(__file__)}"
'''
                    if icon_path_abs:
                        shortcut_content += f'Icon={icon_path_abs}\n'
                    shortcut_content += '''Terminal=false
Type=Application
Categories=Game;
'''
                    with open(shortcut_path, "w", encoding="utf-8") as f:
                        f.write(shortcut_content)
                    os.chmod(shortcut_path, 0o755)
                    print(f"Created desktop shortcut: {shortcut_path}")

    except Exception as e:
        print(f"Failed to create shortcut: {e}")


create_game_directories()
set_game_icon()
create_desktop_shortcut()

pygame.display.set_caption(f"{GAME_TITLE} v{GAME_VERSION}")


class TVTape:
    def __init__(self, tape_id, name, video_path, price, rarity="common", description=""):
        self.id = tape_id
        self.name = name
        self.video_path = video_path
        self.price = min(price, 100000)
        self.rarity = rarity
        self.description = description
        self.owned = False
        self.equipped = False

    @property
    def rarity_color(self):
        colors = {"common": RETRO_GRAY, "rare": RETRO_BLUE, "epic": RETRO_PURPLE,
                  "legendary": RETRO_GOLD, "mythic": MAGENTA}
        return colors.get(self.rarity, RETRO_GRAY)

    @property
    def rarity_name(self):
        names = {"common": "Common", "rare": "Rare", "epic": "Epic",
                 "legendary": "Legendary", "mythic": "Mythic"}
        return names.get(self.rarity, "Common")

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'video_path': self.video_path,
            'price': self.price, 'rarity': self.rarity, 'description': self.description,
            'owned': self.owned, 'equipped': self.equipped
        }

    @classmethod
    def from_dict(cls, data):
        tape = cls(data['id'], data['name'], data['video_path'], data['price'],
                   data['rarity'], data['description'])
        tape.owned = data.get('owned', False)
        tape.equipped = data.get('equipped', False)
        return tape


class TVVideoPlayer:
    def __init__(self):
        self.video_files = []
        self.current_video_index = 0
        self.video_capture = None
        self.video_surface = None
        self.playing = False
        self.video_dir = "tv_videos"
        self.tape_dir = "tv_tapes"
        self.tv_bg_color = (40, 35, 30)
        self.tv_screen_color = (10, 15, 20)
        self.scan_lines = []
        self.static_noise = 0
        self.last_frame_time = 0
        self.fps = 30
        self.video_loaded = False
        self.pixel_size = 2
        self.test_frame_index = 0
        self.test_frames = []
        self.current_tape = None
        self.tapes = []

        self.pixelation_divider = 15
        self.video_quality = "retro"

        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)
        if not os.path.exists(self.tape_dir):
            os.makedirs(self.tape_dir)

        self.create_scan_lines()
        self.tapes = self.create_default_tapes()
        self.load_videos()

    def create_scan_lines(self):
        for i in range(0, 100, 4):
            self.scan_lines.append(i)

    def create_default_tapes(self):
        tapes = []
        tape_data = [
            (0, "Classic", "classic.mp4", 50000, "common", "Classic tape"),
            (1, "Adventure", "adventure.mp4", 75000, "rare", "Adventure tape"),
            (2, "Space", "space.mp4", 100000, "epic", "Space tape"),
            (3, "Fantasy", "fantasy.mp4", 150000, "legendary", "Fantasy tape"),
            (4, "Legends", "legends.mp4", 250000, "mythic", "Legendary tape"),
        ]

        for tape_id, name, video_file, price, rarity, desc in tape_data:
            tape_path = os.path.join(self.tape_dir, video_file)
            tape = TVTape(tape_id, name, tape_path, price, rarity, desc)
            if tape_id == 0:
                tape.owned = True
                tape.equipped = True
                self.current_tape = tape
            tapes.append(tape)

        return tapes

    def get_tape_by_id(self, tape_id):
        for tape in self.tapes:
            if tape.id == tape_id:
                return tape
        return None

    def get_equipped_tape(self):
        for tape in self.tapes:
            if tape.equipped and tape.owned:
                return tape
        for tape in self.tapes:
            if tape.owned:
                return tape
        return self.tapes[0] if self.tapes else None

    def get_owned_tapes(self):
        return [t for t in self.tapes if t.owned]

    def buy_tape(self, tape_id, coins):
        tape = self.get_tape_by_id(tape_id)
        if tape and not tape.owned and coins >= tape.price:
            tape.owned = True
            return True
        return False

    def equip_tape(self, tape_id):
        tape = self.get_tape_by_id(tape_id)
        if not tape or not tape.owned:
            return False
        for t in self.tapes:
            t.equipped = False
        tape.equipped = True
        self.current_tape = tape
        if os.path.exists(tape.video_path):
            self.load_video(tape.video_path)
        return True

    def load_videos(self):
        if os.path.exists(self.video_dir):
            for file in os.listdir(self.video_dir):
                if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.ogv')):
                    self.video_files.append(os.path.join(self.video_dir, file))

        equipped_tape = self.get_equipped_tape()
        if equipped_tape and os.path.exists(equipped_tape.video_path):
            self.load_video(equipped_tape.video_path)
        elif self.video_files:
            self.load_video(self.video_files[0])
        else:
            self.create_test_animation()

    def load_video(self, filepath):
        if not OPENCV_AVAILABLE:
            self.create_test_animation()
            return False

        try:
            if self.video_capture is not None:
                self.video_capture.release()

            self.video_capture = cv2.VideoCapture(filepath)

            if not self.video_capture.isOpened():
                self.create_test_animation()
                return False

            self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0:
                self.fps = 30

            self.playing = True
            self.video_loaded = True
            self.last_frame_time = pygame.time.get_ticks()
            self.update_frame()
            return True

        except Exception as e:
            self.create_test_animation()
            return False

    def update_frame(self):
        if self.video_capture is None or not self.video_capture.isOpened():
            return

        try:
            ret, frame = self.video_capture.read()

            if not ret:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.video_capture.read()
                if not ret:
                    return

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame_rgb.shape[:2]

            if self.video_quality == "pixelated":
                pixel_w = max(1, w // 40)
                pixel_h = max(1, h // 30)
                small = cv2.resize(frame_rgb, (pixel_w, pixel_h), interpolation=cv2.INTER_NEAREST)
                pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                pixelated = np.transpose(pixelated, (1, 0, 2))
                self.video_surface = pygame.surfarray.make_surface(pixelated)

            elif self.video_quality == "retro":
                pixel_w = max(1, w // self.pixelation_divider)
                pixel_h = max(1, h // int(self.pixelation_divider * 0.7))
                small = cv2.resize(frame_rgb, (pixel_w, pixel_h), interpolation=cv2.INTER_NEAREST)
                pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
                pixelated = np.transpose(pixelated, (1, 0, 2))
                self.video_surface = pygame.surfarray.make_surface(pixelated)

            else:
                target_w = 130
                target_h = 90
                smooth = cv2.resize(frame_rgb, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
                smooth = np.transpose(smooth, (1, 0, 2))
                self.video_surface = pygame.surfarray.make_surface(smooth)

        except Exception as e:
            pass

    def create_test_animation(self):
        self.video_surface = None
        self.playing = False
        self.video_loaded = False
        self.test_frames = []

        for frame in range(60):
            surf = pygame.Surface((110, 80))
            surf.fill((20, 25, 30))

            for i in range(15):
                x = (i * 8 + frame * 2) % 110
                y = (i * 6 + frame * 3) % 80
                color = (50 + i * 14, 30 + i * 10, 100 + i * 7)
                pygame.draw.rect(surf, color, (x, y, 4, 4))

            font = pygame.font.Font(None, 16)
            text = font.render("NO SIGNAL", True, (80, 80, 80))
            text_rect = text.get_rect(center=(55, 40))
            surf.blit(text, text_rect)

            self.test_frames.append(surf)

        self.test_frame_index = 0
        if self.test_frames:
            self.video_surface = self.test_frames[0]

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.video_loaded and self.video_capture is not None and self.video_capture.isOpened():
            frame_delay = int(1000 / self.fps) if self.fps > 0 else 33
            if current_time - self.last_frame_time > frame_delay:
                self.update_frame()
                self.last_frame_time = current_time
        elif self.test_frames:
            if current_time - self.last_frame_time > 150:
                self.test_frame_index = (self.test_frame_index + 1) % len(self.test_frames)
                self.video_surface = self.test_frames[self.test_frame_index]
                self.last_frame_time = current_time

        self.static_noise = random.random() * 0.03

    def draw(self, screen, x, y, width, height):
        tv_width = width + 24
        tv_height = height + 50
        tv_x = x - 12
        tv_y = y - 10

        shadow_rect = pygame.Rect(tv_x + 4, tv_y + 4, tv_width, tv_height)
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, 0, 12)

        pygame.draw.rect(screen, self.tv_bg_color, (tv_x, tv_y, tv_width, tv_height), 0, 12)
        pygame.draw.rect(screen, (60, 55, 50), (tv_x, tv_y, tv_width, tv_height), 3, 12)

        inner_rect = pygame.Rect(tv_x + 10, tv_y + 8, width + 4, height + 4)
        pygame.draw.rect(screen, (25, 22, 20), inner_rect, 0, 4)

        screen_rect = pygame.Rect(tv_x + 12, tv_y + 10, width, height)

        if self.video_surface is not None:
            if self.video_quality == "retro":
                scaled = pygame.transform.scale(self.video_surface, (width, height))
            else:
                scaled = pygame.transform.smoothscale(self.video_surface, (width, height))
            screen.blit(scaled, screen_rect)
        else:
            pygame.draw.rect(screen, self.tv_screen_color, screen_rect)
            font = pygame.font.Font(None, 18)
            text = font.render("NO SIGNAL", True, (60, 60, 60))
            text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
            screen.blit(text, text_rect)

        if self.static_noise > 0.01:
            noise_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            for _ in range(int(15 * self.static_noise)):
                nx = random.randint(0, width - 1)
                ny = random.randint(0, height - 1)
                alpha = int(40 * self.static_noise)
                noise_surf.set_at((nx, ny), (255, 255, 255, alpha))
            screen.blit(noise_surf, screen_rect)

        scan_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for line_y in self.scan_lines:
            if line_y < height:
                alpha = 8 + int(4 * math.sin(pygame.time.get_ticks() * 0.001 + line_y * 0.1))
                pygame.draw.line(scan_surf, (0, 0, 0, alpha), (0, line_y), (width, line_y))
        screen.blit(scan_surf, screen_rect)

        glare_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(2):
            gradient_y = height // 3 + i * 25
            alpha = 12 - i * 6
            pygame.draw.ellipse(glare_surf, (255, 255, 255, alpha),
                                (width // 4, gradient_y - 8, width // 2, 16))
        screen.blit(glare_surf, screen_rect)

        pygame.draw.rect(screen, (50, 45, 40), screen_rect, 2, 3)

        power_light = pygame.Rect(tv_x + tv_width - 18, tv_y + 6, 5, 5)
        glow = int(150 + 100 * math.sin(pygame.time.get_ticks() * 0.002))
        pygame.draw.circle(screen, (glow, glow // 2, 0), power_light.center, 4)
        pygame.draw.circle(screen, (200, 100, 0), power_light.center, 3)
        pygame.draw.circle(screen, (255, 150, 50), power_light.center, 2)

        button_y = tv_y + tv_height - 14
        for i in range(3):
            btn_x = tv_x + 18 + i * 16
            pygame.draw.circle(screen, (70, 65, 60), (btn_x, button_y), 4)
            pygame.draw.circle(screen, (45, 40, 35), (btn_x, button_y), 3)

        font = pygame.font.Font(None, 11)
        tv_label = font.render("TV", True, (70, 65, 60))
        screen.blit(tv_label, (tv_x + 12, tv_y + tv_height - 20))

        antenna_x = tv_x + tv_width // 2
        antenna_y = tv_y - 2
        pygame.draw.line(screen, (60, 55, 50), (antenna_x, antenna_y), (antenna_x - 8, antenna_y - 8), 2)
        pygame.draw.line(screen, (60, 55, 50), (antenna_x, antenna_y), (antenna_x + 8, antenna_y - 8), 2)
        pygame.draw.circle(screen, (60, 55, 50), (antenna_x - 8, antenna_y - 8), 2)
        pygame.draw.circle(screen, (60, 55, 50), (antenna_x + 8, antenna_y - 8), 2)

        return pygame.Rect(tv_x, tv_y, tv_width, tv_height)


class TVTapeShop:
    def __init__(self, tv_player):
        self.tv_player = tv_player
        self.page = 0
        self.selected_tape = None

    def draw(self, screen, coins):
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 40, 240))
        screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 16)

        title = font_large.render("Tape Shop", True, RETRO_SILVER)
        title_shadow = font_large.render("Tape Shop", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 21))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 20))

        coins_text = font_medium.render(f"Coins: {coins}", True, RETRO_GOLD)
        coins_shadow = font_medium.render(f"Coins: {coins}", True, BLACK)
        screen.blit(coins_shadow, (BASE_WIDTH // 2 - coins_text.get_width() // 2 + 1, 56))
        screen.blit(coins_text, (BASE_WIDTH // 2 - coins_text.get_width() // 2, 55))

        tapes = self.tv_player.tapes
        start_y = 90

        for i, tape in enumerate(tapes):
            rect = pygame.Rect(20, start_y + i * 70, BASE_WIDTH - 40, 60)

            if tape.owned and tape.equipped:
                pygame.draw.rect(screen, (46, 204, 113, 200), rect, 0, 10)
            elif tape.owned:
                pygame.draw.rect(screen, (155, 89, 182, 200), rect, 0, 10)
            else:
                pygame.draw.rect(screen, (60, 60, 80), rect, 0, 10)

            pygame.draw.rect(screen, RETRO_SILVER, rect, 2, 10)

            rarity_rect = pygame.Rect(rect.x + 5, rect.y + 5, 10, 10)
            pygame.draw.circle(screen, tape.rarity_color, rarity_rect.center, 5)

            name_text = font_small.render(tape.name, True, RETRO_GOLD)
            name_shadow = font_small.render(tape.name, True, BLACK)
            screen.blit(name_shadow, (rect.x + 21, rect.y + 5))
            screen.blit(name_text, (rect.x + 20, rect.y + 4))

            rarity_text = font_tiny.render(tape.rarity_name, True, tape.rarity_color)
            rarity_shadow = font_tiny.render(tape.rarity_name, True, BLACK)
            screen.blit(rarity_shadow, (rect.x + 21, rect.y + 24))
            screen.blit(rarity_text, (rect.x + 20, rect.y + 23))

            if tape.owned:
                if tape.equipped:
                    status = "Equipped"
                    status_color = RETRO_GREEN
                else:
                    status = "Equip"
                    status_color = RETRO_YELLOW
            else:
                status = f"{tape.price} coins"
                status_color = RETRO_GOLD

            status_text = font_tiny.render(status, True, status_color)
            status_shadow = font_tiny.render(status, True, BLACK)
            screen.blit(status_shadow,
                        (rect.right - status_text.get_width() - 5, rect.centery - status_text.get_height() // 2 + 1))
            screen.blit(status_text,
                        (rect.right - status_text.get_width() - 6, rect.centery - status_text.get_height() // 2))

        back_rect = pygame.Rect(BASE_WIDTH // 2 - 100, BASE_HEIGHT - 50, 200, 40)
        pygame.draw.rect(screen, RETRO_PURPLE, back_rect, 0, 10)
        pygame.draw.rect(screen, RETRO_SILVER, back_rect, 2, 10)
        back_text = font_medium.render("Back", True, RETRO_GOLD)
        back_shadow = font_medium.render("Back", True, BLACK)
        screen.blit(back_shadow, (
            back_rect.centerx - back_text.get_width() // 2 + 1, back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text,
                    (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

        return back_rect

    def handle_click(self, x, y, coins):
        tapes = self.tv_player.tapes
        start_y = 90
        for i, tape in enumerate(tapes):
            rect = pygame.Rect(20, start_y + i * 70, BASE_WIDTH - 40, 60)
            if rect.collidepoint(x, y):
                if tape.owned:
                    if not tape.equipped:
                        self.tv_player.equip_tape(tape.id)
                        return ("equip", tape.id)
                    else:
                        return ("already_equipped", tape.id)
                else:
                    if self.tv_player.buy_tape(tape.id, coins):
                        return ("buy", tape.id)
                    else:
                        return ("not_enough_coins", tape.id)

        back_rect = pygame.Rect(BASE_WIDTH // 2 - 100, BASE_HEIGHT - 50, 200, 40)
        if back_rect.collidepoint(x, y):
            return ("back", None)

        return None


class TVVideoManager:
    def __init__(self):
        self.player = None
        self.tv_rect = None
        self.tv_x = 15
        self.tv_y = BASE_HEIGHT - 140
        self.tv_width = 130
        self.tv_height = 90
        self.last_update_time = 0

    def set_player(self, player):
        self.player = player

    def update(self):
        if self.player:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time > 30:
                self.player.update()
                self.last_update_time = current_time

    def draw(self, screen):
        if self.player:
            self.tv_rect = self.player.draw(screen, self.tv_x, self.tv_y, self.tv_width, self.tv_height)
        return self.tv_rect

    def handle_click(self, x, y):
        if self.tv_rect and self.tv_rect.collidepoint(x, y):
            if self.player and self.player.video_files and self.player.video_loaded:
                return "tv_click"
        return None


class ImageSkin:
    def __init__(self, skin_id, name, image_path, price, description="", rarity="common", is_opponent=False,
                 mode="main", is_cup=False):
        self.id = skin_id
        self.name = name
        self.image_path = image_path
        self.image = None
        self.image_right = None
        self.image_left = None
        self.folder_path = None
        self.has_animation = False

        if rarity == "common":
            self.price = max(1000, price) if price < 1000 else price
        else:
            self.price = price
        self.description = description
        self.rarity = rarity
        self.owned = False
        self.equipped = False
        self.is_opponent = is_opponent
        self.mode = mode
        self.is_cup = is_cup
        self.load_image()

    def load_image(self):
        try:
            path = self.image_path
            if path and os.path.isdir(path):
                self.folder_path = path
                self.has_animation = True
                files = [f for f in sorted(os.listdir(path))
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

                if not files:
                    self.image = None
                    self.has_animation = False
                    return

                main_img = None
                right_img = None
                left_img = None

                for f in files:
                    fl = f.lower()
                    if main_img is None and ("main" in fl or "idle" in fl or "base" in fl):
                        main_img = f
                    if right_img is None and ("right" in fl or "hit_r" in fl or "shot_r" in fl):
                        right_img = f
                    if left_img is None and ("left" in fl or "hit_l" in fl or "shot_l" in fl):
                        left_img = f

                remaining = [f for f in files if f != main_img]
                if main_img is None and files:
                    main_img = files[0]
                    remaining = files[1:]
                if right_img is None and remaining:
                    right_img = remaining[0]
                if left_img is None and len(remaining) > 1:
                    left_img = remaining[1]

                if main_img:
                    try:
                        self.image = pygame.image.load(os.path.join(path, main_img)).convert_alpha()
                    except Exception as e:
                        self.image = None

                if right_img:
                    try:
                        self.image_right = pygame.image.load(os.path.join(path, right_img)).convert_alpha()
                    except Exception as e:
                        pass

                if left_img:
                    try:
                        self.image_left = pygame.image.load(os.path.join(path, left_img)).convert_alpha()
                    except Exception as e:
                        pass

                if self.image_right is None:
                    self.image_right = self.image
                if self.image_left is None:
                    self.image_left = self.image

            elif path and os.path.exists(path):
                self.image = pygame.image.load(path).convert_alpha()
                self.has_animation = False
            else:
                self.image = None

            self._resize_for_mode()
        except Exception as e:
            self.image = None

    def _resize_for_mode(self):
        target_size = None
        if self.is_cup:
            target_size = (40, 40)
        elif self.mode in ["tennis", "tennis_opponent"]:
            target_size = (60, 60)
        elif self.mode in ["basketball", "basketball_opponent"]:
            target_size = (70, 70) if self.is_opponent else (60, 60)

        if target_size is None:
            return
        if self.image is not None:
            self.image = pygame.transform.scale(self.image, target_size)
        if self.image_right is not None:
            self.image_right = pygame.transform.scale(self.image_right, target_size)
        if self.image_left is not None:
            self.image_left = pygame.transform.scale(self.image_left, target_size)

    def get_image_for_shot(self, shot_side):
        if not self.has_animation:
            return None
        if shot_side == "right" and self.image_right is not None:
            return self.image_right
        if shot_side == "left" and self.image_left is not None:
            return self.image_left
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_path': self.image_path,
            'price': self.price,
            'description': self.description,
            'rarity': self.rarity,
            'owned': self.owned,
            'equipped': self.equipped,
            'is_opponent': self.is_opponent,
            'mode': self.mode,
            'is_cup': self.is_cup
        }

    @classmethod
    def from_dict(cls, data):
        skin = cls(
            data['id'],
            data['name'],
            data.get('image_path', ''),
            data['price'],
            data.get('description', ''),
            data.get('rarity', 'common'),
            data.get('is_opponent', False),
            data.get('mode', 'main'),
            data.get('is_cup', False)
        )
        skin.owned = data.get('owned', False)
        skin.equipped = data.get('equipped', False)
        return skin

    @property
    def rarity_color(self):
        colors = {"common": GRAY, "rare": BLUE, "epic": PURPLE, "legendary": GOLD}
        return colors.get(self.rarity, GRAY)

    @property
    def main_color(self):
        return self.rarity_color


class SkinManager:
    def __init__(self, mode="main", is_opponent=False, is_cup=False):
        self.skins = []
        self.current_skin = None
        self.mode = mode
        self.is_opponent = is_opponent
        self.is_cup = is_cup

        self.skins_dir = find_skin_directory(mode, is_opponent, is_cup)
        print(f"Skin directory for {mode} (opponent={is_opponent}, cup={is_cup}): {self.skins_dir}")

        self.create_skins()

    def create_skins(self):
        self.load_skins_from_folder()
        if not self.skins:
            self.create_default_skin()

    def load_skins_from_folder(self):
        skin_id = 0
        if not os.path.exists(self.skins_dir):
            return

        try:
            entries = sorted(os.listdir(self.skins_dir))
        except Exception as e:
            print(f"Could not list skin directory {self.skins_dir}: {e}")
            return

        for entry in entries:
            full_path = os.path.join(self.skins_dir, entry)

            if os.path.isdir(full_path):
                rarity, price = self._determine_rarity_and_price(entry)
                display_name = self._clean_skin_name(entry)
                skin = ImageSkin(skin_id, display_name, full_path, price,
                                 f"Skin: {display_name}",
                                 rarity, self.is_opponent, self.mode, self.is_cup)
                self._assign_default_ownership(skin, skin_id)
                self.skins.append(skin)
                skin_id += 1

            elif entry.lower().endswith(('.png', '.jpg', '.jpeg')):
                rarity, price = self._determine_rarity_and_price(entry)
                display_name = self._clean_skin_name(os.path.splitext(entry)[0])
                skin = ImageSkin(skin_id, display_name, full_path, price,
                                 f"Skin: {display_name}",
                                 rarity, self.is_opponent, self.mode, self.is_cup)
                self._assign_default_ownership(skin, skin_id)
                self.skins.append(skin)
                skin_id += 1

    def _determine_rarity_and_price(self, filename):
        if self.is_cup:
            return "legendary", 10000
        rarity = "common"
        fl = filename.lower()
        if "legendary" in fl or "легенд" in fl:
            rarity = "legendary"
        elif "epic" in fl or "эпич" in fl:
            rarity = "epic"
        elif "rare" in fl or "редк" in fl:
            rarity = "rare"

        if rarity == "legendary":
            price = 100000
        elif rarity == "epic":
            price = 50000
        elif rarity == "rare":
            price = 10000
        else:
            price = 1000
        return rarity, price

    def _clean_skin_name(self, name):
        result = name
        for keyword in ["legendary", "epic", "rare", "common",
                        "легенд", "эпич", "редк", "обыч"]:
            low = result.lower()
            idx = low.find(keyword)
            if idx != -1:
                result = result[:idx] + result[idx + len(keyword):]
        result = result.strip("_- ")
        if not result:
            result = name
        return result.replace('_', ' ').replace('-', ' ').title()

    def _assign_default_ownership(self, skin, skin_id):
        if self.is_cup:
            skin.owned = True
            skin.equipped = False
        elif self.is_opponent:
            skin.owned = True
            skin.equipped = True
        else:
            if skin_id == 0:
                skin.owned = True
                skin.equipped = True

    def create_default_skin(self):
        default_skin = ImageSkin(0, f"Default {self.mode}", "", 1000, f"Default {self.mode} skin.", "common",
                                 self.is_opponent, self.mode, self.is_cup)
        if not self.is_opponent and not self.is_cup:
            default_skin.owned = True
            default_skin.equipped = True
        else:
            default_skin.owned = True
        default_skin.image = self.create_default_skin_image()
        default_skin.mode = self.mode
        self.skins = [default_skin]

    def create_default_skin_image(self):
        surf = pygame.Surface((60, 60), pygame.SRCALPHA)

        if self.is_cup:
            pygame.draw.rect(surf, GOLD, (10, 20, 40, 25), 0, 5)
            pygame.draw.rect(surf, GOLD, (20, 10, 20, 15), 0, 5)
            pygame.draw.rect(surf, GOLD, (25, 45, 10, 5), 0, 2)
            pygame.draw.ellipse(surf, GOLD, (15, 5, 30, 10))
            font = pygame.font.Font(None, 14)
            text = font.render("CUP", True, WHITE)
            surf.blit(text, (10, 40))
            return surf

        colors = {
            "tennis": (200, 80, 80),
            "basketball": (200, 140, 60),
            "tennis_opponent": (200, 50, 50),
            "basketball_opponent": (160, 100, 50),
        }
        color = colors.get(self.mode, (100, 180, 220))

        pygame.draw.circle(surf, color, (30, 30), 25)

        pygame.draw.circle(surf, WHITE, (35, 22), 6)
        pygame.draw.circle(surf, BLACK, (36, 22), 3)
        beak_points = [(40, 28), (48, 28), (40, 32)]
        pygame.draw.polygon(surf, (200, 160, 80), beak_points)
        wing_points = [(20, 35), (12, 28), (22, 42)]
        pygame.draw.polygon(surf, (60, 160, 215), wing_points)
        font = pygame.font.Font(None, 12)
        mode_text = font.render(self.mode[:3].upper(), True, WHITE)
        surf.blit(mode_text, (10, 10))
        if self.is_opponent:
            pygame.draw.circle(surf, (200, 0, 0, 100), (30, 30), 28, 2)
            ai_font = pygame.font.Font(None, 14)
            ai_text = ai_font.render("AI", True, (200, 0, 0))
            surf.blit(ai_text, (15, 40))
        return surf

    def get_skin_by_id(self, skin_id):
        for skin in self.skins:
            if skin.id == skin_id:
                return skin
        return None

    def get_equipped_skin(self):
        if self.is_cup:
            for skin in self.skins:
                if skin.owned:
                    return skin
            return None
        elif self.is_opponent:
            valid_skins = [s for s in self.skins if s.owned and s.image is not None]
            if valid_skins:
                return random.choice(valid_skins)
            if self.skins:
                return self.skins[0]
            return None

        for skin in self.skins:
            if skin.equipped:
                return skin
        return self.skins[0] if self.skins else None

    def get_random_opponent_skin(self, player_skin_id=None):
        if not self.is_opponent or not self.skins:
            return None

        valid_skins = []
        for s in self.skins:
            if s.owned and s.image is not None:
                valid_skins.append(s)
            elif s.owned:
                s.load_image()
                if s.image is not None:
                    valid_skins.append(s)

        if not valid_skins:
            self.create_default_skin()
            if self.skins and self.skins[0].image is not None:
                return self.skins[0]
            return None

        if len(valid_skins) == 1:
            return valid_skins[0]

        if player_skin_id is not None:
            available_skins = [s for s in valid_skins if s.id != player_skin_id]
            if available_skins:
                return random.choice(available_skins)

        return random.choice(valid_skins)

    def get_equipped_skin_id(self):
        if self.is_opponent:
            valid_skins = [s for s in self.skins if s.owned and s.image is not None]
            if valid_skins:
                return random.choice(valid_skins).id
            return 0
        for skin in self.skins:
            if skin.equipped:
                return skin.id
        return 0

    def equip_skin(self, skin_id):
        if self.is_opponent or self.is_cup:
            return False
        skin = self.get_skin_by_id(skin_id)
        if not skin or not skin.owned:
            return False
        for s in self.skins:
            s.equipped = False
        skin.equipped = True
        return True

    def buy_skin(self, skin_id, coins):
        if self.is_opponent or self.is_cup:
            return False
        skin = self.get_skin_by_id(skin_id)
        if skin and not skin.owned:
            if coins >= skin.price:
                skin.owned = True
                return True
            else:
                return False
        return False

    def get_owned_skins(self):
        if self.is_opponent or self.is_cup:
            return []
        return [skin for skin in self.skins if skin.owned]

    def get_all_skins(self):
        return self.skins[:]

    def to_dict(self):
        return {'skins': [skin.to_dict() for skin in self.skins]}

    def from_dict(self, data):
        if 'skins' in data:
            loaded_skins = []
            for skin_data in data['skins']:
                skin = ImageSkin(
                    skin_data.get('id', len(loaded_skins)),
                    skin_data.get('name', f"Skin {len(loaded_skins)}"),
                    skin_data.get('image_path', ''),
                    skin_data.get('price', 100),
                    skin_data.get('description', ''),
                    skin_data.get('rarity', 'common'),
                    self.is_opponent,
                    self.mode,
                    self.is_cup
                )
                skin.owned = skin_data.get('owned', False)
                skin.equipped = skin_data.get('equipped', False)
                skin.load_image()
                loaded_skins.append(skin)

            if loaded_skins:
                self.skins = loaded_skins
                if self.is_opponent:
                    for skin in self.skins:
                        skin.owned = True
            else:
                self.create_skins()
        else:
            self.create_skins()


class BackgroundManager:
    def __init__(self, mode="main_menu"):
        self.mode = mode
        self.bg_dir = f"backgrounds/{mode}"
        self.backgrounds = []
        self.current_background = None

        if not os.path.exists(self.bg_dir):
            os.makedirs(self.bg_dir)

        self.load_backgrounds()

    def load_backgrounds(self):
        if os.path.exists(self.bg_dir):
            for file in os.listdir(self.bg_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        image = pygame.image.load(os.path.join(self.bg_dir, file)).convert()
                        image = pygame.transform.scale(image, (BASE_WIDTH, BASE_HEIGHT))
                        self.backgrounds.append(image)
                    except Exception as e:
                        pass

        if not self.backgrounds:
            self.create_default_background()

    def create_default_background(self):
        surf = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        if self.mode == "main_menu":
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(45 * (1 - t) + 60 * t)
                g = int(40 * (1 - t) + 55 * t)
                b = int(35 * (1 - t) + 48 * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (BASE_WIDTH, y))
        elif self.mode == "basketball":
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(160 * (1 - t) + 120 * t)
                g = int(130 * (1 - t) + 100 * t)
                b = int(90 * (1 - t) + 70 * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (BASE_WIDTH, y))
        elif self.mode == "tennis":
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(120 * (1 - t) + 80 * t)
                g = int(180 * (1 - t) + 120 * t)
                b = int(80 * (1 - t) + 60 * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (BASE_WIDTH, y))
        elif self.mode == "shop":
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(60 * (1 - t) + 80 * t)
                g = int(55 * (1 - t) + 70 * t)
                b = int(48 * (1 - t) + 60 * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (BASE_WIDTH, y))
        elif self.mode == "world_ranking":
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(30 * (1 - t) + 20 * t)
                g = int(35 * (1 - t) + 25 * t)
                b = int(40 * (1 - t) + 30 * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (BASE_WIDTH, y))
        else:
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(40 * (1 - t) + 30 * t)
                g = int(35 * (1 - t) + 25 * t)
                b = int(30 * (1 - t) + 25 * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (BASE_WIDTH, y))
        self.backgrounds.append(surf)

    def get_random_background(self):
        if self.backgrounds:
            return random.choice(self.backgrounds)
        return None

    def get_background(self, index=0):
        if self.backgrounds and index < len(self.backgrounds):
            return self.backgrounds[index]
        return None


class MusicManager:
    def __init__(self):
        self.current_music = None
        self.current_mode = "menu"
        self.is_playing = False
        self.music_volume = 0.3

        self.music_dirs = {
            "menu": "music/menu",
            "tennis": "music/tennis",
            "basketball": "music/basketball"
        }

        for dir_path in self.music_dirs.values():
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created folder: {dir_path}")

        self.load_music_for_mode("menu")

    def get_music_files(self, mode):
        folder = self.music_dirs.get(mode)
        if not folder or not os.path.exists(folder):
            return []

        files = []
        for file in os.listdir(folder):
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                files.append(os.path.join(folder, file))
        return files

    def load_music_for_mode(self, mode):
        if self.current_mode == mode and self.is_playing:
            return True

        files = self.get_music_files(mode)
        if not files:
            print(f"No music in folder {self.music_dirs.get(mode)}")
            return False

        music_file = random.choice(files)

        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(self.music_volume)

            self.current_music = music_file
            self.current_mode = mode
            self.is_playing = True

            print(f"Playing music: {mode} - {os.path.basename(music_file)}")
            return True

        except Exception as e:
            print(f"Music load error: {e}")
            return False

    def play_menu_music(self):
        return self.load_music_for_mode("menu")

    def play_tennis_music(self):
        return self.load_music_for_mode("tennis")

    def play_basketball_music(self):
        return self.load_music_for_mode("basketball")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_music = None
        print("Music stopped")

    def pause_music(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            print("Music paused")

    def unpause_music(self):
        if self.is_playing:
            pygame.mixer.music.unpause()
            print("Music resumed")

    def set_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def is_playing_music(self):
        return self.is_playing


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = True
        self.music_enabled = True
        self.music_volume = 0.2
        self.sound_volume = 0.7
        self.channels = {}
        self.channels['sfx'] = pygame.mixer.Channel(0)
        self.channels['music'] = pygame.mixer.Channel(1)
        self.channels['ambient'] = pygame.mixer.Channel(2)

        self.music_manager = MusicManager()

        self.create_sound_directories()
        self.load_all_sounds()

    def create_sound_directories(self):
        dirs = [
            "sounds/common",
            "sounds/tennis/player",
            "sounds/tennis/opponent",
            "sounds/basketball",
            "sounds/game"
        ]
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created folder: {dir_path}")

    def load_all_sounds(self):
        self.load_sounds_from_folder("sounds/common")
        self.load_sounds_from_folder("sounds/tennis/player", "tennis_player_")
        self.load_sounds_from_folder("sounds/tennis/opponent", "tennis_opponent_")
        self.load_specific_tennis_sounds()
        self.load_sounds_from_folder("sounds/basketball", "basketball_")
        self.load_sounds_from_folder("sounds/game", "game_")

        if len(self.sounds) < 10:
            self.generate_all_sounds_programmatically()

    def load_sounds_from_folder(self, folder, prefix=""):
        if not os.path.exists(folder):
            return

        for file in os.listdir(folder):
            if file.lower().endswith(('.wav', '.mp3', '.ogg')):
                name = prefix + os.path.splitext(file)[0]
                path = os.path.join(folder, file)
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    print(f"Loaded sound: {name}")
                except Exception as e:
                    print(f"Error loading {file}: {e}")

    def load_specific_tennis_sounds(self):
        tennis_sounds = {
            'tennis_point_win': 'sounds/tennis/point_win.wav',
            'tennis_point_lose': 'sounds/tennis/point_lose.wav',
            'tennis_game_win': 'sounds/tennis/game_win.wav',
            'tennis_wall': 'sounds/tennis/wall.wav'
        }

        for name, path in tennis_sounds.items():
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    print(f"Loaded sound: {name}")
                except:
                    pass

    def generate_all_sounds_programmatically(self):
        sample_rate = 22050
        self._generate_common_sounds(sample_rate)
        self._generate_tennis_sounds(sample_rate)
        self._generate_basketball_sounds(sample_rate)

    def _generate_common_sounds(self, sample_rate):
        if 'button' not in self.sounds:
            duration = 0.05
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.3 * np.sin(2 * np.pi * 800 * t) * np.exp(-30 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['button'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'game_over' not in self.sounds:
            duration = 0.8
            t = np.linspace(0, duration, int(sample_rate * duration))
            freq = 440 * np.exp(-4 * t)
            wave = 0.4 * np.sin(2 * np.pi * freq * t) * np.exp(-3 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['game_over'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'powerup' not in self.sounds:
            duration = 0.4
            t = np.linspace(0, duration, int(sample_rate * duration))
            freq = 440 * (1 + 1.5 * t / duration)
            wave = 0.3 * np.sin(2 * np.pi * freq * t) * np.exp(-2 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['powerup'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'level_up' not in self.sounds:
            self.sounds['level_up'] = self.sounds['powerup']

    def _generate_tennis_sounds(self, sample_rate):
        if 'tennis_player_hit' not in self.sounds:
            duration = 0.15
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.5 * np.sin(2 * np.pi * 1000 * t) * np.exp(-20 * t)
            wave += 0.3 * np.sin(2 * np.pi * 700 * t) * np.exp(-15 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['tennis_player_hit'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'tennis_opponent_hit' not in self.sounds:
            duration = 0.15
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.4 * np.sin(2 * np.pi * 800 * t) * np.exp(-18 * t)
            wave += 0.3 * np.sin(2 * np.pi * 600 * t) * np.exp(-12 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['tennis_opponent_hit'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'tennis_point_win' not in self.sounds:
            duration = 0.3
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = (0.4 * np.sin(2 * np.pi * 523.25 * t) +
                    0.25 * np.sin(2 * np.pi * 659.25 * t) +
                    0.2 * np.sin(2 * np.pi * 783.99 * t))
            wave *= np.exp(-5 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['tennis_point_win'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'tennis_point_lose' not in self.sounds:
            duration = 0.2
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.3 * np.sin(2 * np.pi * 200 * t) * np.exp(-10 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['tennis_point_lose'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'tennis_wall' not in self.sounds:
            duration = 0.08
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.3 * np.sin(2 * np.pi * 400 * t) * np.exp(-15 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['tennis_wall'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

    def _generate_basketball_sounds(self, sample_rate):
        if 'basketball_score' not in self.sounds:
            duration = 0.4
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.5 * np.sin(2 * np.pi * 600 * t) * np.exp(-8 * t)
            wave += 0.3 * np.sin(2 * np.pi * 900 * t) * np.exp(-10 * t)
            wave += 0.2 * np.sin(2 * np.pi * 1200 * t) * np.exp(-12 * t)
            wave += 0.15 * np.random.normal(0, 0.5, len(t)) * np.exp(-15 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['basketball_score'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'basketball_miss' not in self.sounds:
            duration = 0.3
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.4 * np.sin(2 * np.pi * 200 * t) * np.exp(-8 * t)
            wave += 0.3 * np.sin(2 * np.pi * 150 * t) * np.exp(-10 * t)
            wave += 0.1 * np.random.normal(0, 0.3, len(t)) * np.exp(-5 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['basketball_miss'] = pygame.sndarray.make_sound(np.repeat(wave.reshape(-1, 1), 2, axis=1))

        if 'basketball_dribble' not in self.sounds:
            duration = 0.1
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = 0.3 * np.sin(2 * np.pi * 300 * t) * np.exp(-20 * t)
            wave = (wave * 32767).astype(np.int16)
            self.sounds['basketball_dribble'] = pygame.sndarray.make_sound(
                np.repeat(wave.reshape(-1, 1), 2, axis=1))

    def play_sound(self, sound_name, channel='sfx', volume=None):
        if not self.sound_enabled:
            return
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(self.sound_volume)
            if channel in self.channels:
                self.channels[channel].play(sound)
            else:
                sound.play()

    def play_sound_loop(self, sound_name, channel='sfx', volume=None):
        if not self.sound_enabled:
            return
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(self.sound_volume)
            if channel in self.channels:
                self.channels[channel].play(sound, loops=-1)
            else:
                sound.play(loops=-1)

    def stop_sound(self, channel='sfx'):
        if channel in self.channels:
            self.channels[channel].stop()

    def play_tennis_player_hit(self):
        self.play_sound('tennis_player_hit')

    def play_tennis_opponent_hit(self):
        self.play_sound('tennis_opponent_hit')

    def play_tennis_point_win(self):
        self.play_sound('tennis_point_win')

    def play_tennis_point_lose(self):
        self.play_sound('tennis_point_lose')

    def play_tennis_game_win(self):
        self.play_sound('tennis_game_win')

    def play_tennis_wall(self):
        self.play_sound('tennis_wall')

    def play_basketball_score(self):
        self.play_sound('basketball_score')

    def play_basketball_miss(self):
        self.play_sound('basketball_miss')

    def play_basketball_dribble(self):
        self.play_sound('basketball_dribble')

    def play_button(self):
        self.play_sound('button')

    def play_game_over(self):
        self.play_sound('game_over')

    def play_powerup(self):
        self.play_sound('powerup')

    def play_level_up(self):
        self.play_sound('level_up')

    def play_menu_music(self):
        if self.music_enabled:
            return self.music_manager.play_menu_music()
        return False

    def play_tennis_music(self):
        if self.music_enabled:
            return self.music_manager.play_tennis_music()
        return False

    def play_basketball_music(self):
        if self.music_enabled:
            return self.music_manager.play_basketball_music()
        return False

    def stop_music(self):
        self.music_manager.stop_music()

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            if self.music_manager.current_mode == "menu":
                self.play_menu_music()
            elif self.music_manager.current_mode == "tennis":
                self.play_tennis_music()
            elif self.music_manager.current_mode == "basketball":
                self.play_basketball_music()
        else:
            self.stop_music()
        return self.music_enabled

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        self.music_manager.set_volume(volume)

    def set_sound_volume(self, volume):
        self.sound_volume = max(0.0, min(1.0, volume))

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled


class GameSkinManager:
    def __init__(self):
        self.tennis_skins = SkinManager("tennis")
        self.basketball_skins = SkinManager("basketball")
        self.tennis_opponent_skins = SkinManager("tennis", is_opponent=True)
        self.basketball_opponent_skins = SkinManager("basketball", is_opponent=True)
        self.cup_skins_tennis = SkinManager("tennis", is_cup=True)
        self.cup_skins_basketball = SkinManager("basketball", is_cup=True)

        self.bg_main_menu = BackgroundManager("main_menu")
        self.bg_basketball = BackgroundManager("basketball")
        self.bg_tennis = BackgroundManager("tennis")
        self.bg_world_ranking = BackgroundManager("world_ranking")
        self.bg_shop = BackgroundManager("shop")

        self.music_manager = MusicManager()

    def get_skins_for_mode(self, mode, is_opponent=False, is_cup=False):
        if is_cup:
            if mode == "tennis":
                return self.cup_skins_tennis
            elif mode == "basketball":
                return self.cup_skins_basketball
        elif is_opponent:
            if mode == "tennis":
                return self.tennis_opponent_skins
            elif mode == "basketball":
                return self.basketball_opponent_skins
        else:
            if mode == "tennis":
                return self.tennis_skins
            elif mode == "basketball":
                return self.basketball_skins
        return self.tennis_skins

    def get_equipped_skin(self, mode="tennis", is_opponent=False, is_cup=False, player_skin_id=None):
        manager = self.get_skins_for_mode(mode, is_opponent, is_cup)
        if is_cup:
            return manager.get_equipped_skin()
        elif is_opponent:
            return manager.get_random_opponent_skin(player_skin_id)
        return manager.get_equipped_skin()

    def get_bg_for_mode(self, mode="main_menu"):
        bg_map = {
            "main_menu": self.bg_main_menu,
            "basketball": self.bg_basketball,
            "tennis": self.bg_tennis,
            "world_ranking": self.bg_world_ranking,
            "shop": self.bg_shop,
        }
        return bg_map.get(mode, self.bg_main_menu)

    def get_all_tennis_skins(self):
        return self.tennis_skins.get_all_skins()

    def to_dict(self):
        return {
            'tennis': self.tennis_skins.to_dict(),
            'basketball': self.basketball_skins.to_dict(),
            'tennis_opponent': self.tennis_opponent_skins.to_dict(),
            'basketball_opponent': self.basketball_opponent_skins.to_dict(),
            'cups_tennis': self.cup_skins_tennis.to_dict(),
            'cups_basketball': self.cup_skins_basketball.to_dict(),
        }

    def from_dict(self, data):
        if 'tennis' in data:
            self.tennis_skins.from_dict(data['tennis'])
        if 'basketball' in data:
            self.basketball_skins.from_dict(data['basketball'])
        if 'tennis_opponent' in data:
            self.tennis_opponent_skins.from_dict(data['tennis_opponent'])
        if 'basketball_opponent' in data:
            self.basketball_opponent_skins.from_dict(data['basketball_opponent'])
        if 'cups_tennis' in data:
            self.cup_skins_tennis.from_dict(data['cups_tennis'])
        if 'cups_basketball' in data:
            self.cup_skins_basketball.from_dict(data['cups_basketball'])


class PixelCursor:
    def __init__(self):
        self.x = BASE_WIDTH // 2
        self.y = BASE_HEIGHT // 2
        self.visible = False
        self.size = 16
        self.speed = 8
        self.last_move_time = 0
        self.click_cooldown = 0
        self.create_cursor_surface()

    def create_cursor_surface(self):
        self.cursor_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        colors = [(240, 235, 220, 200), (210, 180, 120, 200), (100, 150, 200, 200)]
        for i in range(4):
            color_idx = min(i, len(colors) - 1)
            pygame.draw.line(self.cursor_surf, colors[color_idx],
                             (i, i), (self.size - i - 1, self.size - i - 1), 1)
        pygame.draw.line(self.cursor_surf, (240, 235, 220, 255),
                         (0, 0), (self.size, self.size), 2)
        pygame.draw.line(self.cursor_surf, (240, 235, 220, 255),
                         (self.size - 1, 0), (0, self.size - 1), 1)
        pygame.draw.circle(self.cursor_surf, (210, 180, 120, 150),
                           (self.size // 2, self.size // 2), self.size // 3)

    def update_from_gamepad(self):
        game = getattr(Game, '_instance', None)
        if game is None:
            self.visible = False
            return

        show = False
        if game.state == 'main_menu':
            show = True
        elif game.state in ['tennis_ranked', 'basketball_campaign', 'world_ranking',
                            'achievements', 'shop', 'controls',
                            'duel_court', 'duel_start']:
            show = True
        elif game.state == 'game_over':
            show = True
        if game.settings_menu.active:
            show = True
        if game.state == 'story':
            show = False
        if game.state == 'play':
            show = False
        if game.state == 'duel_skins':
            show = False
        if game.state == 'duel_setup':
            show = False

        if control_manager.control_type == ControlType.GAMEPAD and show:
            self.visible = True
            move_x = 0
            move_y = 0
            gamepad = control_manager.get_active_gamepad()
            if gamepad:
                try:
                    axis_x = gamepad.get_axis(0)
                    axis_y = gamepad.get_axis(1)
                    if abs(axis_x) > 0.2:
                        move_x = axis_x
                    if abs(axis_y) > 0.2:
                        move_y = axis_y
                    hat = gamepad.get_hat(0)
                    if hat[0] != 0:
                        move_x = hat[0]
                    if hat[1] != 0:
                        move_y = hat[1]
                except:
                    pass
            if move_x != 0 or move_y != 0:
                self.x += move_x * self.speed
                self.y += move_y * self.speed
                self.x = max(0, min(BASE_WIDTH, self.x))
                self.y = max(0, min(BASE_HEIGHT, self.y))
                self.last_move_time = pygame.time.get_ticks()
        else:
            self.visible = False

    def is_clicking(self):
        if control_manager.control_type != ControlType.GAMEPAD:
            return False
        game = getattr(Game, '_instance', None)
        if game is None:
            return False
        show = False
        if game.state == 'main_menu':
            show = True
        elif game.state in ['tennis_ranked', 'basketball_campaign', 'world_ranking',
                            'achievements', 'shop', 'controls',
                            'duel_court', 'duel_start']:
            show = True
        elif game.state == 'game_over':
            show = True
        if game.settings_menu.active:
            show = True
        if game.state == 'story' or game.state == 'play':
            show = False
        if game.state == 'duel_skins':
            show = False
        if game.state == 'duel_setup':
            show = False
        if not show:
            return False
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
            return False
        gamepad = control_manager.get_active_gamepad()
        if gamepad:
            for button in [0, 7, 9, 2, 3]:
                try:
                    if button < gamepad.get_numbuttons() and gamepad.get_button(button):
                        self.click_cooldown = 10
                        return True
                except:
                    pass
        return False

    def draw(self, screen):
        if self.visible:
            screen.blit(self.cursor_surf, (self.x - self.size // 2, self.y - self.size // 2))


class ControlManager:
    def __init__(self):
        if IS_ANDROID:
            self.control_type = ControlType.TOUCH
        else:
            self.control_type = ControlType.KEYBOARD
        self.selected_gamepad_index = 0
        self._last_button_states = {}
        self._menu_nav_cooldown = 0
        self._gamepad_cursor_mode = True

    def set_control_type(self, control_type):
        self.control_type = control_type

    def get_control_type(self):
        return self.control_type

    def is_gamepad_available(self):
        return len(joysticks) > 0

    def get_active_gamepad(self):
        if self.is_gamepad_available() and self.selected_gamepad_index < len(joysticks):
            return joysticks[self.selected_gamepad_index]
        return None

    def get_gamepad_by_index(self, index):
        if index < len(joysticks):
            return joysticks[index]
        return None

    def set_gamepad_index(self, index):
        if index < len(joysticks):
            self.selected_gamepad_index = index

    def get_gamepad_count(self):
        return len(joysticks)

    def _safe_get_button(self, gamepad, button):
        try:
            if gamepad and button < gamepad.get_numbuttons():
                return gamepad.get_button(button)
        except:
            pass
        return False

    def _safe_get_hat(self, gamepad, hat_index):
        try:
            if gamepad:
                return gamepad.get_hat(hat_index)
        except:
            pass
        return (0, 0)

    def _safe_get_axis(self, gamepad, axis):
        try:
            if gamepad and axis < gamepad.get_numaxes():
                return gamepad.get_axis(axis)
        except:
            pass
        return 0.0

    def is_menu_up_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_UP] or keys[pygame.K_w]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                hat = self._safe_get_hat(gamepad, 0)
                if hat[1] > 0:
                    return True
                axis_y = self._safe_get_axis(gamepad, 1)
                if axis_y < -0.5:
                    return True
            return False
        return False

    def is_menu_down_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_DOWN] or keys[pygame.K_s]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                hat = self._safe_get_hat(gamepad, 0)
                if hat[1] < 0:
                    return True
                axis_y = self._safe_get_axis(gamepad, 1)
                if axis_y > 0.5:
                    return True
            return False
        return False

    def is_menu_left_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_LEFT] or keys[pygame.K_a]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                hat = self._safe_get_hat(gamepad, 0)
                if hat[0] < 0:
                    return True
                axis_x = self._safe_get_axis(gamepad, 0)
                if axis_x < -0.5:
                    return True
            return False
        return False

    def is_menu_right_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_RIGHT] or keys[pygame.K_d]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                hat = self._safe_get_hat(gamepad, 0)
                if hat[0] > 0:
                    return True
                axis_x = self._safe_get_axis(gamepad, 0)
                if axis_x > 0.5:
                    return True
            return False
        return False

    def is_menu_select_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_RETURN] or keys[pygame.K_SPACE]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                for btn in [0, 7, 2, 3, 9]:
                    if self._safe_get_button(gamepad, btn):
                        return True
            return False
        return False

    def is_menu_back_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_ESCAPE]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                for btn in [1, 6]:
                    if self._safe_get_button(gamepad, btn):
                        return True
            return False
        return False

    def update_menu_cooldown(self):
        if self._menu_nav_cooldown > 0:
            self._menu_nav_cooldown -= 1

    def can_menu_navigate(self):
        if self._menu_nav_cooldown <= 0:
            self._menu_nav_cooldown = 8
            return True
        return False

    def is_topspin_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_q]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                return self._safe_get_button(gamepad, 4)
            return False
        return False

    def is_dropshot_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_e]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                return self._safe_get_button(gamepad, 5)
            return False
        return False

    def is_slice_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_f]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                return self._safe_get_button(gamepad, 2)
            return False
        return False

    def is_straight_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_w]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                return self._safe_get_button(gamepad, 3)
            return False
        return False

    def is_curve_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_r]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                rt_value = self._safe_get_axis(gamepad, 5)
                if rt_value > 0.5:
                    return True
                if self._safe_get_button(gamepad, 7):
                    return True
            return False
        return False

    def is_rt_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            return False
        gamepad = self.get_active_gamepad()
        if gamepad:
            rt_value = self._safe_get_axis(gamepad, 5)
            if rt_value > 0.5:
                return True
            for btn in [7, 10]:
                if self._safe_get_button(gamepad, btn):
                    return True
        return False

    def is_lt_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            return False
        gamepad = self.get_active_gamepad()
        if gamepad:
            lt_value = self._safe_get_axis(gamepad, 4)
            if lt_value > 0.5:
                return True
            for btn in [6, 8]:
                if self._safe_get_button(gamepad, btn):
                    return True
        return False

    def get_move_x(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            return (-1 if left else 0) + (1 if right else 0)
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                axis_x = self._safe_get_axis(gamepad, 0)
                if abs(axis_x) > 0.2:
                    return axis_x
                hat = self._safe_get_hat(gamepad, 0)
                if hat[0] != 0:
                    return hat[0]
            return 0
        return 0

    def get_move_axis(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            dx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
            dy = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)
            return dx, dy
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                axis_x = self._safe_get_axis(gamepad, 0)
                axis_y = self._safe_get_axis(gamepad, 1)
                if abs(axis_x) > 0.2 or abs(axis_y) > 0.2:
                    return axis_x, axis_y
                hat = self._safe_get_hat(gamepad, 0)
                if hat[0] != 0 or hat[1] != 0:
                    return hat[0], hat[1]
            return 0, 0
        return 0, 0

    def get_aim_position(self):
        if self.control_type == ControlType.KEYBOARD:
            return 0, 0
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                try:
                    aim_x = self._safe_get_axis(gamepad, 2)
                    aim_y = self._safe_get_axis(gamepad, 3)
                    if abs(aim_x) > 0.2 or abs(aim_y) > 0.2:
                        return aim_x, aim_y
                except:
                    pass
            return 0, 0
        return 0, 0

    def get_aim_move(self):
        return self.get_move_x()

    def is_charging_shot(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_SPACE]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                for button in [1, 6, 8, 9, 10, 11, 12, 13, 14, 15]:
                    if self._safe_get_button(gamepad, button):
                        return True
            return False
        return False

    def is_shoot_pressed(self):
        if self.control_type == ControlType.KEYBOARD:
            keys = pygame.key.get_pressed()
            return keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
        elif self.control_type == ControlType.GAMEPAD:
            gamepad = self.get_active_gamepad()
            if gamepad:
                num_buttons = gamepad.get_numbuttons()
                for button in range(min(num_buttons, 16)):
                    if self._safe_get_button(gamepad, button):
                        return True
            return False
        return False

    def to_dict(self):
        return {
            'control_type': self.control_type.value,
            'selected_gamepad_index': self.selected_gamepad_index
        }

    def from_dict(self, data):
        if 'control_type' in data:
            try:
                if data['control_type'] == 'touch':
                    self.control_type = ControlType.TOUCH
                elif data['control_type'] == 'gamepad':
                    self.control_type = ControlType.GAMEPAD
                else:
                    self.control_type = ControlType.KEYBOARD
            except:
                self.control_type = ControlType.TOUCH if IS_ANDROID else ControlType.KEYBOARD
        if 'selected_gamepad_index' in data:
            self.selected_gamepad_index = data['selected_gamepad_index']


control_manager = ControlManager()
pixel_cursor = PixelCursor()


class TouchControls:
    def __init__(self):
        self.visible = IS_ANDROID
        self.joystick_center = (80, BASE_HEIGHT - 100)
        self.joystick_radius = 50
        self.joystick_knob_radius = 20
        self.joystick_active = False
        self.joystick_touch_id = None
        self.joystick_pos = [0, 0]
        self.joystick_vector = (0, 0)
        self.action_buttons = []
        self.button_states = {}
        self._update_buttons()

    def _update_buttons(self):
        self.action_buttons = [
            {'id': 'shoot', 'rect': pygame.Rect(BASE_WIDTH - 100, BASE_HEIGHT - 180, 70, 70),
             'label': 'SHOOT', 'color': (200, 140, 60), 'text_color': WHITE},
            {'id': 'left', 'rect': pygame.Rect(BASE_WIDTH - 200, BASE_HEIGHT - 100, 55, 55),
             'label': 'LEFT', 'color': (200, 80, 60), 'text_color': WHITE},
            {'id': 'right', 'rect': pygame.Rect(BASE_WIDTH - 100, BASE_HEIGHT - 100, 55, 55),
             'label': 'RIGHT', 'color': (100, 150, 200), 'text_color': WHITE},
            {'id': 'slice', 'rect': pygame.Rect(BASE_WIDTH - 200, BASE_HEIGHT - 180, 55, 55),
             'label': 'SLICE', 'color': (150, 100, 180), 'text_color': WHITE},
            {'id': 'straight', 'rect': pygame.Rect(BASE_WIDTH - 300, BASE_HEIGHT - 180, 55, 55),
             'label': 'STRAIGHT', 'color': (220, 200, 100), 'text_color': BLACK},
            {'id': 'curve', 'rect': pygame.Rect(BASE_WIDTH - 300, BASE_HEIGHT - 100, 55, 55),
             'label': 'CURVE', 'color': (230, 120, 60), 'text_color': WHITE},
            {'id': 'back', 'rect': pygame.Rect(BASE_WIDTH - 40, 10, 30, 30),
             'label': 'X', 'color': RETRO_RED, 'text_color': WHITE},
        ]

    def update_positions(self):
        self._update_buttons()

    def handle_touch_down(self, pos, touch_id=0):
        x, y = pos
        dx = x - self.joystick_center[0]
        dy = y - self.joystick_center[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < self.joystick_radius + 20:
            self.joystick_active = True
            self.joystick_touch_id = touch_id
            self._update_joystick(pos)
            return 'joystick'

        for button in self.action_buttons:
            if button['rect'].collidepoint(x, y):
                self.button_states[button['id']] = True
                return button['id']
        return None

    def handle_touch_move(self, pos, touch_id=0):
        if self.joystick_active and touch_id == self.joystick_touch_id:
            self._update_joystick(pos)

    def handle_touch_up(self, pos, touch_id=0):
        if self.joystick_active and touch_id == self.joystick_touch_id:
            self.joystick_active = False
            self.joystick_touch_id = None
            self.joystick_pos = [0, 0]
            self.joystick_vector = (0, 0)

        for button in self.action_buttons:
            if button['rect'].collidepoint(pos[0], pos[1]):
                self.button_states[button['id']] = False

    def _update_joystick(self, pos):
        dx = pos[0] - self.joystick_center[0]
        dy = pos[1] - self.joystick_center[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > self.joystick_radius:
            dx = dx / dist * self.joystick_radius
            dy = dy / dist * self.joystick_radius
        self.joystick_pos = [dx, dy]
        max_dist = self.joystick_radius
        nx = dx / max_dist if max_dist > 0 else 0
        ny = dy / max_dist if max_dist > 0 else 0
        self.joystick_vector = (nx, ny)

    def is_button_pressed(self, button_id):
        return self.button_states.get(button_id, False)

    def get_joystick_vector(self):
        return self.joystick_vector

    def get_move_x(self):
        return self.joystick_vector[0]

    def is_charging_shot(self):
        return self.button_states.get('shoot', False)

    def is_topspin_pressed(self):
        return self.button_states.get('left', False)

    def is_dropshot_pressed(self):
        return self.button_states.get('right', False)

    def is_slice_pressed(self):
        return self.button_states.get('slice', False)

    def is_straight_pressed(self):
        return self.button_states.get('straight', False)

    def is_curve_pressed(self):
        return self.button_states.get('curve', False)

    def draw(self, screen):
        if not self.visible:
            return

        if self.joystick_active:
            pygame.draw.circle(screen, (50, 50, 70, 150),
                               (self.joystick_center[0], self.joystick_center[1]),
                               self.joystick_radius, 2)
            knob_pos = (self.joystick_center[0] + self.joystick_pos[0],
                        self.joystick_center[1] + self.joystick_pos[1])
            pygame.draw.circle(screen, (150, 150, 180, 200), knob_pos, self.joystick_knob_radius)
            pygame.draw.circle(screen, (200, 200, 220, 200), knob_pos, self.joystick_knob_radius, 2)

        for button in self.action_buttons:
            is_pressed = self.button_states.get(button['id'], False)
            color = button['color']
            if is_pressed:
                light_color = tuple(min(255, c + 40) for c in color)
                pygame.draw.rect(screen, light_color, button['rect'], 0, 15)
            else:
                dark_color = tuple(max(0, c - 30) for c in color)
                pygame.draw.rect(screen, dark_color, button['rect'], 0, 15)

            pygame.draw.rect(screen, (220, 220, 220, 200), button['rect'], 2, 15)

            font = pygame.font.Font(None, 18 if len(button['label']) > 4 else 22)
            text = font.render(button['label'], True, button['text_color'])
            text_shadow = font.render(button['label'], True, BLACK)
            text_rect = text.get_rect(center=button['rect'].center)
            shadow_rect = text_rect.copy()
            shadow_rect.x += 1
            shadow_rect.y += 1
            screen.blit(text_shadow, shadow_rect)
            screen.blit(text, text_rect)

        screen.blit(screen, (0, 0))
        pygame.draw.circle(screen, (120, 120, 140, 100),
                           (self.joystick_center[0], self.joystick_center[1]),
                           self.joystick_radius, 1)
        pygame.draw.circle(screen, (150, 150, 170, 100),
                           (self.joystick_center[0], self.joystick_center[1]),
                           self.joystick_knob_radius, 1)


touch_controls = TouchControls()


class Achievement:
    def __init__(self, ach_id, name, description, category, rarity=0, reward_coins=0, reward_exp=0):
        self.id = ach_id
        self.name = name
        self.description = description
        self.category = category
        self.rarity = rarity
        self.reward_coins = reward_coins
        self.reward_exp = reward_exp
        self.unlocked = False
        self.unlocked_date = None
        self.progress = 0
        self.target = 1
        self.icon_type = self._get_icon_type()

    def _get_icon_type(self):
        icons = {
            "tennis": ["tennis", "racket", "ball", "trophy", "star", "crown", "fire", "lightning"],
            "basketball": ["basketball", "hoop", "ball", "trophy", "star", "crown", "fire", "lightning"]
        }
        idx = min(self.rarity, 7)
        return icons.get(self.category, icons["tennis"])[idx]

    @property
    def rarity_name(self):
        names = ["Common", "Rare", "Epic", "Legendary", "Mythic"]
        return names[min(self.rarity, 4)]

    @property
    def rarity_color(self):
        colors = [RETRO_GRAY, RETRO_BLUE, RETRO_PURPLE, RETRO_GOLD, MAGENTA]
        return colors[min(self.rarity, 4)]

    def to_dict(self):
        return {
            'id': self.id,
            'unlocked': self.unlocked,
            'unlocked_date': self.unlocked_date,
            'progress': self.progress
        }

    @classmethod
    def from_dict(cls, data, template):
        ach = cls(template.id, template.name, template.description, template.category,
                  template.rarity, template.reward_coins, template.reward_exp)
        ach.unlocked = data.get('unlocked', False)
        ach.unlocked_date = data.get('unlocked_date', None)
        ach.progress = data.get('progress', 0)
        ach.target = template.target
        return ach


class AchievementManager:
    def __init__(self, sound_manager=None):
        self.achievements = []
        self.sound_manager = sound_manager
        self.create_achievements()

    def create_achievements(self):
        tennis = [
            Achievement("tennis_first_win", "First Victory", "Win your first tennis match", "tennis", 0, 50, 20),
            Achievement("tennis_5_wins", "Rising Star", "Win 5 tennis matches", "tennis", 0, 100, 40),
            Achievement("tennis_10_wins", "Tennis Pro", "Win 10 tennis matches", "tennis", 1, 200, 80),
            Achievement("tennis_25_wins", "Court Master", "Win 25 tennis matches", "tennis", 1, 400, 150),
            Achievement("tennis_50_wins", "Tennis Legend", "Win 50 tennis matches", "tennis", 2, 800, 300),
            Achievement("tennis_perfect_set", "Perfect Set", "Win a match without losing a game", "tennis", 1, 300, 100),
            Achievement("tennis_ace_master", "Ace Master", "Win 10 points in a row", "tennis", 1, 250, 90),
            Achievement("tennis_rally_10", "Rally Master", "Reach 10 hit rally", "tennis", 0, 100, 40),
            Achievement("tennis_rally_20", "Rally God", "Reach 20 hit rally", "tennis", 1, 200, 80),
            Achievement("tennis_rally_30", "Unstoppable", "Reach 30 hit rally", "tennis", 2, 400, 150),
            Achievement("tennis_tournament_1", "First Tournament", "Win your first tournament", "tennis", 1, 500, 200),
            Achievement("tennis_tournament_3", "Tournament Hunter", "Win 3 tournaments", "tennis", 2, 800, 300),
            Achievement("tennis_tournament_5", "Tournament Champion", "Win 5 tournaments", "tennis", 2, 1000, 400),
            Achievement("tennis_tournament_all", "Grand Slam", "Win all tournaments", "tennis", 3, 2000, 800),
            Achievement("tennis_world_champion", "World Champion", "Reach 2000 ELO in tennis", "tennis", 4, 5000, 2000),
            Achievement("tennis_elo_1200", "Advanced Player", "Reach 1200 ELO", "tennis", 0, 150, 60),
            Achievement("tennis_elo_1500", "Expert Player", "Reach 1500 ELO", "tennis", 1, 400, 150),
            Achievement("tennis_elo_1800", "Master Player", "Reach 1800 ELO", "tennis", 2, 800, 300),
            Achievement("tennis_legends_win", "Legend Slayer", "Defeat a Legends Tournament opponent", "tennis", 3, 1500, 600),
            Achievement("tennis_legends_5", "Legends Hunter", "Defeat 5 Legends opponents", "tennis", 3, 2500, 1000),
            Achievement("tennis_no_losses", "Flawless", "Win a tournament without losing a match", "tennis", 2, 600, 250),
            Achievement("tennis_streak_5", "Hot Streak", "Win 5 matches in a row", "tennis", 1, 300, 120),
            Achievement("tennis_streak_10", "On Fire", "Win 10 matches in a row", "tennis", 2, 600, 250),
            Achievement("tennis_deuce_win", "Deuce Master", "Win a game from deuce", "tennis", 0, 100, 40),
            Achievement("tennis_5_deuce", "Clutch Player", "Win 5 games from deuce", "tennis", 1, 250, 100),
        ]

        basketball = [
            Achievement("basketball_first_win", "First Basket", "Win your first basketball match", "basketball", 0, 50, 20),
            Achievement("basketball_5_wins", "Rising Star", "Win 5 basketball matches", "basketball", 0, 100, 40),
            Achievement("basketball_10_wins", "Basketball Pro", "Win 10 basketball matches", "basketball", 1, 200, 80),
            Achievement("basketball_25_wins", "Court Master", "Win 25 basketball matches", "basketball", 1, 400, 150),
            Achievement("basketball_50_wins", "Basketball Legend", "Win 50 basketball matches", "basketball", 2, 800, 300),
            Achievement("basketball_perfect_game", "Perfect Game", "Win without missing a shot", "basketball", 2, 500, 200),
            Achievement("basketball_streak_5", "Hot Hand", "Score 5 shots in a row", "basketball", 0, 150, 60),
            Achievement("basketball_streak_10", "On Fire", "Score 10 shots in a row", "basketball", 1, 300, 120),
            Achievement("basketball_streak_15", "Unstoppable", "Score 15 shots in a row", "basketball", 2, 600, 250),
            Achievement("basketball_3pt_master", "Three-Point Master", "Score 5 three-pointers in a game", "basketball", 1, 200, 80),
            Achievement("basketball_3pt_god", "Three-Point God", "Score 10 three-pointers in a game", "basketball", 2, 400, 150),
            Achievement("basketball_perfect_shot_5", "Sharpshooter", "Make 5 perfect shots", "basketball", 1, 250, 100),
            Achievement("basketball_perfect_shot_10", "Sniper", "Make 10 perfect shots", "basketball", 2, 500, 200),
            Achievement("basketball_campaign_1", "First Step", "Complete first campaign level", "basketball", 0, 100, 40),
            Achievement("basketball_campaign_5", "Rising Star", "Complete 5 campaign levels", "basketball", 1, 300, 120),
            Achievement("basketball_campaign_10", "Campaign Master", "Complete 10 campaign levels", "basketball", 2, 600, 250),
            Achievement("basketball_campaign_all", "Basketball Champion", "Complete all campaign levels", "basketball", 3, 2000, 800),
            Achievement("basketball_ranked_first", "Ranked Debut", "Win your first ranked match", "basketball", 1, 400, 150),
            Achievement("basketball_ranked_5", "Ranked Warrior", "Win 5 ranked matches", "basketball", 2, 800, 300),
            Achievement("basketball_ranked_10", "Ranked Champion", "Win 10 ranked matches", "basketball", 2, 1200, 500),
            Achievement("basketball_elo_1200", "Advanced Player", "Reach 1200 ELO", "basketball", 0, 150, 60),
            Achievement("basketball_elo_1500", "Expert Player", "Reach 1500 ELO", "basketball", 1, 400, 150),
            Achievement("basketball_elo_1800", "Master Player", "Reach 1800 ELO", "basketball", 2, 800, 300),
            Achievement("basketball_elo_2000", "World Champion", "Reach 2000 ELO in basketball", "basketball", 4, 5000, 2000),
            Achievement("basketball_streak_bonus", "Streak Bonus", "Earn streak bonus in ranked", "basketball", 1, 300, 120),
        ]

        self.achievements = tennis + basketball

    def get_achievement(self, ach_id):
        for ach in self.achievements:
            if ach.id == ach_id:
                return ach
        return None

    def unlock(self, ach_id):
        ach = self.get_achievement(ach_id)
        if ach and not ach.unlocked:
            ach.unlocked = True
            ach.unlocked_date = datetime.now().strftime("%d.%m.%Y")
            if self.sound_manager:
                self.sound_manager.play_level_up()
            return True
        return False

    def check_progress(self, ach_id, progress):
        ach = self.get_achievement(ach_id)
        if ach and not ach.unlocked:
            ach.progress = progress
            if progress >= ach.target:
                return self.unlock(ach_id)
        return False

    def get_unlocked_count(self, category=None):
        if category:
            return len([a for a in self.achievements if a.category == category and a.unlocked])
        return len([a for a in self.achievements if a.unlocked])

    def get_total_count(self, category=None):
        if category:
            return len([a for a in self.achievements if a.category == category])
        return len(self.achievements)

    def to_dict(self):
        return {'achievements': [a.to_dict() for a in self.achievements]}

    def from_dict(self, data):
        if 'achievements' in data:
            for ach_data in data['achievements']:
                template = self.get_achievement(ach_data['id'])
                if template:
                    template.unlocked = ach_data.get('unlocked', False)
                    template.unlocked_date = ach_data.get('unlocked_date', None)
                    template.progress = ach_data.get('progress', 0)


class AchievementScreen:
    def __init__(self, achievement_manager, sound_manager=None, background_manager=None):
        self.achievement_manager = achievement_manager
        self.sound_manager = sound_manager
        self.background_manager = background_manager
        self.page = 0
        self.category = "all"
        self.animation = 0
        self.back_rect = None
        self.scroll_offset = 0
        self.dragging = False

    def get_filtered_achievements(self):
        if self.category == "all":
            return self.achievement_manager.achievements
        return [a for a in self.achievement_manager.achievements if a.category == self.category]

    def draw(self, screen):
        self.animation += 0.02

        if self.background_manager:
            bg = self.background_manager.get_random_background()
            if bg:
                screen.blit(bg, (0, 0))
            else:
                screen.fill((20, 25, 35))
        else:
            screen.fill((20, 25, 35))

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        font_title = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        font_tiny = pygame.font.Font(None, 18)

        title = font_title.render("Achievements", True, RETRO_GOLD)
        title_shadow = font_title.render("Achievements", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 9))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 8))

        tabs = [("All", "all"), ("Tennis", "tennis"), ("Basketball", "basketball")]
        tab_width = 95
        tab_start_x = BASE_WIDTH // 2 - (tab_width * 3 + 10) // 2
        for i, (name, key) in enumerate(tabs):
            tab_rect = pygame.Rect(tab_start_x + i * (tab_width + 5), 42, tab_width, 26)
            if self.category == key:
                pygame.draw.rect(screen, RETRO_PURPLE, tab_rect, 0, 6)
                pygame.draw.rect(screen, RETRO_SILVER, tab_rect, 2, 6)
            else:
                pygame.draw.rect(screen, (50, 50, 70), tab_rect, 0, 6)
                pygame.draw.rect(screen, RETRO_GRAY, tab_rect, 2, 6)
            tab_text = font_small.render(name, True, RETRO_GOLD)
            tab_shadow = font_small.render(name, True, BLACK)
            screen.blit(tab_shadow, (tab_rect.centerx - tab_text.get_width() // 2 + 1,
                                     tab_rect.centery - tab_text.get_height() // 2 + 1))
            screen.blit(tab_text, (tab_rect.centerx - tab_text.get_width() // 2,
                                   tab_rect.centery - tab_text.get_height() // 2))

        unlocked_total = self.achievement_manager.get_unlocked_count()
        total = self.achievement_manager.get_total_count()
        progress_text = font_small.render(f"Unlocked: {unlocked_total}/{total}", True, RETRO_GOLD)
        progress_shadow = font_small.render(f"Unlocked: {unlocked_total}/{total}", True, BLACK)
        screen.blit(progress_shadow, (BASE_WIDTH // 2 - progress_text.get_width() // 2 + 1, 74))
        screen.blit(progress_text, (BASE_WIDTH // 2 - progress_text.get_width() // 2, 73))

        achievements = self.get_filtered_achievements()
        per_page = 6
        total_pages = max(1, (len(achievements) + per_page - 1) // per_page)
        if self.page >= total_pages:
            self.page = total_pages - 1
        start_idx = self.page * per_page
        end_idx = min(start_idx + per_page, len(achievements))

        start_y = 108
        for i in range(start_idx, end_idx):
            ach = achievements[i]
            row = i - start_idx
            rect = pygame.Rect(15, start_y + row * 76, BASE_WIDTH - 30, 70)

            if ach.unlocked:
                bg_color = (46, 204, 113, 200)
            else:
                bg_color = (60, 60, 80, 200)

            bg_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, bg_color, bg_surf.get_rect(), 0, 10)
            screen.blit(bg_surf, rect)
            pygame.draw.rect(screen, ach.rarity_color, rect, 2, 10)

            icon_x = rect.x + 22
            icon_y = rect.y + 35
            pixel_data = self.get_icon_pixels(ach.icon_type)
            pixel_size = 3
            icon_size = 8 * pixel_size
            icon_rect = pygame.Rect(icon_x - icon_size // 2, icon_y - icon_size // 2, icon_size, icon_size)
            pygame.draw.rect(screen, (30, 30, 50), icon_rect, 0, 4)
            pygame.draw.rect(screen, ach.rarity_color, icon_rect, 1, 4)
            for px in range(8):
                for py in range(8):
                    if pixel_data[py][px]:
                        pr = pygame.Rect(icon_x - icon_size // 2 + px * pixel_size,
                                         icon_y - icon_size // 2 + py * pixel_size, pixel_size, pixel_size)
                        color = ach.rarity_color if ach.unlocked else (80, 80, 100)
                        if ach.unlocked and random.random() < 0.1:
                            color = WHITE
                        pygame.draw.rect(screen, color, pr)

            name_color = RETRO_GOLD if ach.unlocked else RETRO_SILVER
            name_text = font_medium.render(ach.name, True, name_color)
            name_shadow = font_medium.render(ach.name, True, BLACK)
            screen.blit(name_shadow, (rect.x + 56, rect.y + 8))
            screen.blit(name_text, (rect.x + 55, rect.y + 7))

            desc_color = RETRO_WHITE if ach.unlocked else RETRO_SILVER
            desc_text = font_small.render(ach.description, True, desc_color)
            desc_shadow = font_small.render(ach.description, True, BLACK)
            screen.blit(desc_shadow, (rect.x + 56, rect.y + 30))
            screen.blit(desc_text, (rect.x + 55, rect.y + 29))

            rarity_text = font_tiny.render(ach.rarity_name, True, ach.rarity_color)
            rarity_shadow = font_tiny.render(ach.rarity_name, True, BLACK)
            screen.blit(rarity_shadow, (rect.x + 56, rect.y + 51))
            screen.blit(rarity_text, (rect.x + 55, rect.y + 50))

            reward_text = font_tiny.render(f"+{ach.reward_coins}c +{ach.reward_exp}xp", True, RETRO_GOLD)
            reward_shadow = font_tiny.render(f"+{ach.reward_coins}c +{ach.reward_exp}xp", True, BLACK)
            screen.blit(reward_shadow, (rect.right - reward_text.get_width() - 9, rect.y + 51))
            screen.blit(reward_text, (rect.right - reward_text.get_width() - 10, rect.y + 50))

            if ach.unlocked and ach.unlocked_date:
                date_text = font_tiny.render(ach.unlocked_date, True, RETRO_GREEN)
                date_shadow = font_tiny.render(ach.unlocked_date, True, BLACK)
                screen.blit(date_shadow, (rect.right - date_text.get_width() - 9, rect.y + 5))
                screen.blit(date_text, (rect.right - date_text.get_width() - 10, rect.y + 4))
            elif not ach.unlocked:
                progress = min(1.0, ach.progress / ach.target) if ach.target > 0 else 0
                bar_width = 60
                bar_rect = pygame.Rect(rect.right - 70, rect.y + 6, bar_width, 12)
                pygame.draw.rect(screen, (40, 40, 60), bar_rect, 0, 6)
                fill_w = int(bar_width * progress)
                if fill_w > 0:
                    pygame.draw.rect(screen, ach.rarity_color, (bar_rect.x, bar_rect.y, fill_w, bar_rect.height), 0, 6)

        if total_pages > 1:
            prev_rect = pygame.Rect(20, BASE_HEIGHT - 50, 60, 30)
            next_rect = pygame.Rect(BASE_WIDTH - 80, BASE_HEIGHT - 50, 60, 30)
            pygame.draw.rect(screen, RETRO_PURPLE if self.page > 0 else (60, 60, 80), prev_rect, 0, 6)
            pygame.draw.rect(screen, RETRO_PURPLE if self.page < total_pages - 1 else (60, 60, 80), next_rect, 0, 6)
            prev_text = font_small.render("<", True, RETRO_GOLD)
            next_text = font_small.render(">", True, RETRO_GOLD)
            screen.blit(prev_text, (prev_rect.centerx - prev_text.get_width() // 2,
                                    prev_rect.centery - prev_text.get_height() // 2))
            screen.blit(next_text, (next_rect.centerx - next_text.get_width() // 2,
                                    next_rect.centery - next_text.get_height() // 2))
            page_text = font_small.render(f"{self.page + 1}/{total_pages}", True, RETRO_GOLD)
            screen.blit(page_text, (BASE_WIDTH // 2 - page_text.get_width() // 2, BASE_HEIGHT - 45))

        self.back_rect = pygame.Rect(BASE_WIDTH // 2 - 80, BASE_HEIGHT - 35, 160, 30)
        pygame.draw.rect(screen, RETRO_PURPLE, self.back_rect, 0, 8)
        pygame.draw.rect(screen, RETRO_SILVER, self.back_rect, 2, 8)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow, (self.back_rect.centerx - back_text.get_width() // 2 + 1,
                                  self.back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text, (self.back_rect.centerx - back_text.get_width() // 2,
                                self.back_rect.centery - back_text.get_height() // 2))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)

    def get_icon_pixels(self, icon_type):
        icons = {
            "tennis": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "racket": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0]
            ],
            "ball": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [1, 0, 0, 1, 1, 0, 0, 1],
                [1, 0, 0, 1, 1, 0, 0, 1],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "basketball": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [1, 0, 0, 1, 1, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "hoop": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "trophy": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0]
            ],
            "star": [
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "crown": [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0, 1, 0, 1],
                [0, 0, 1, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "fire": [
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "lightning": [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 0],
                [0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0]
            ]
        }
        return icons.get(icon_type, icons["star"])

    def handle_click(self, x, y):
        tabs = [("All", "all"), ("Tennis", "tennis"), ("Basketball", "basketball")]
        tab_width = 95
        tab_start_x = BASE_WIDTH // 2 - (tab_width * 3 + 10) // 2
        for i, (name, key) in enumerate(tabs):
            tab_rect = pygame.Rect(tab_start_x + i * (tab_width + 5), 42, tab_width, 26)
            if tab_rect.collidepoint(x, y):
                self.category = key
                self.page = 0
                if self.sound_manager:
                    self.sound_manager.play_button()
                return None

        achievements = self.get_filtered_achievements()
        per_page = 6
        total_pages = max(1, (len(achievements) + per_page - 1) // per_page)

        prev_rect = pygame.Rect(20, BASE_HEIGHT - 50, 60, 30)
        next_rect = pygame.Rect(BASE_WIDTH - 80, BASE_HEIGHT - 50, 60, 30)
        if prev_rect.collidepoint(x, y) and self.page > 0:
            self.page -= 1
            if self.sound_manager:
                self.sound_manager.play_button()
            return None
        if next_rect.collidepoint(x, y) and self.page < total_pages - 1:
            self.page += 1
            if self.sound_manager:
                self.sound_manager.play_button()
            return None

        if self.back_rect and self.back_rect.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            return "back"

        return None

    def handle_scroll(self, y):
        self.scroll_offset = max(0, min(500, self.scroll_offset + y))


class StoryDisplay:
    def __init__(self, sound_manager=None):
        self.text = ""
        self.lines = []
        self.visible = False
        self.timer = 0
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 22)
        self.sound_manager = sound_manager
        self.waiting_for_input = False
        self.is_after_match = False

    def show(self, text, is_after_match=False):
        self.text = text
        self.lines = self._wrap_text(text)
        self.visible = True
        self.waiting_for_input = True
        self.timer = 0
        self.is_after_match = is_after_match

    def _wrap_text(self, text):
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_surf = self.font.render(test_line, True, RETRO_GOLD)
            if text_surf.get_width() < BASE_WIDTH - 80:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def handle_input(self):
        if self.visible and self.waiting_for_input:
            if self.sound_manager:
                self.sound_manager.play_button()
            self.visible = False
            self.waiting_for_input = False
            return True
        return False

    def is_visible(self):
        return self.visible

    def draw(self, screen):
        if not self.visible:
            return
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        total_height = len(self.lines) * 32 + 80
        box_width = BASE_WIDTH - 60
        box_height = min(total_height, BASE_HEIGHT - 100)
        bg_rect = pygame.Rect(
            BASE_WIDTH // 2 - box_width // 2,
            BASE_HEIGHT // 2 - box_height // 2,
            box_width,
            box_height
        )
        bg_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 20, 40, 240), bg_surf.get_rect(), 0, 15)
        pygame.draw.rect(bg_surf, RETRO_GOLD, bg_surf.get_rect(), 3, 15)
        screen.blit(bg_surf, bg_rect)
        y_offset = 30
        for line in self.lines:
            text_surf = self.font.render(line, True, RETRO_GOLD)
            text_shadow = self.font.render(line, True, BLACK)
            screen.blit(text_shadow, (bg_rect.x + 31, bg_rect.y + y_offset + 1))
            screen.blit(text_surf, (bg_rect.x + 30, bg_rect.y + y_offset))
            y_offset += 30
        if self.is_after_match:
            hint = self.small_font.render("Tap to continue...", True, RETRO_SILVER)
        else:
            hint = self.small_font.render("Tap to start match...", True, RETRO_SILVER)
        hint_shadow = self.small_font.render("Tap to continue...", True, BLACK)
        screen.blit(hint_shadow,
                    (bg_rect.x + box_width // 2 - hint.get_width() // 2 + 1, bg_rect.y + box_height - 34))
        screen.blit(hint, (bg_rect.x + box_width // 2 - hint.get_width() // 2, bg_rect.y + box_height - 35))


class Particle:
    def __init__(self, x, y, color, angle=0, speed=0):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        if angle == 0 and speed == 0:
            self.speed_x = random.uniform(-3, 3)
            self.speed_y = random.uniform(-5, -2)
        else:
            self.speed_x = math.cos(angle) * speed
            self.speed_y = math.sin(angle) * speed
        self.gravity = 0.2
        self.life = random.randint(25, 50)
        self.max_life = self.life

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        size = max(1, int(self.size))
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        if len(self.color) == 3:
            color_with_alpha = (*self.color, alpha)
        else:
            color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
        screen.blit(particle_surf, (int(self.x - size), int(self.y - size)))


class ScreenManager:
    def __init__(self):
        self.original_width = BASE_WIDTH
        self.original_height = BASE_HEIGHT
        self.current_width = BASE_WIDTH
        self.current_height = BASE_HEIGHT
        self.scale_factor = 1.0
        self.aspect_ratio = BASE_WIDTH / BASE_HEIGHT
        self.fullscreen = False
        self.screen = None
        self.virtual_screen = None
        self.virtual_rect = None
        self.shake_amount = 0
        self.shake_duration = 0
        self.graphics_quality = 2

    def init_screen(self, fullscreen=False):
        self.fullscreen = fullscreen
        if fullscreen or IS_ANDROID:
            info = pygame.display.Info()
            self.current_width = info.current_w
            self.current_height = info.current_h
            flags = pygame.FULLSCREEN if (fullscreen or IS_ANDROID) else pygame.RESIZABLE
            self.screen = pygame.display.set_mode((self.current_width, self.current_height), flags)
        else:
            self.current_width = BASE_WIDTH
            self.current_height = BASE_HEIGHT
            self.screen = pygame.display.set_mode((self.current_width, self.current_height), pygame.RESIZABLE)
        self.virtual_screen = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        self._update_virtual_rect()

    def _update_virtual_rect(self):
        target_aspect = BASE_WIDTH / BASE_HEIGHT
        screen_aspect = self.current_width / self.current_height
        if screen_aspect > target_aspect:
            new_width = int(self.current_height * target_aspect)
            self.scale_factor = self.current_height / BASE_HEIGHT
            self.virtual_rect = pygame.Rect((self.current_width - new_width) // 2, 0, new_width, self.current_height)
        else:
            new_height = int(self.current_width / target_aspect)
            self.scale_factor = self.current_width / BASE_WIDTH
            self.virtual_rect = pygame.Rect(0, (self.current_height - new_height) // 2, self.current_width, new_height)

    def handle_resize(self, new_width, new_height):
        self.current_width = new_width
        self.current_height = new_height
        self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
        self._update_virtual_rect()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.init_screen(self.fullscreen)

    def set_graphics_quality(self, quality):
        self.graphics_quality = quality

    def scale_value(self, value):
        return int(value * self.scale_factor)

    def unscale_position(self, x, y):
        if not self.virtual_rect:
            return x, y
        x -= self.virtual_rect.x
        y -= self.virtual_rect.y
        x = int(x / self.scale_factor)
        y = int(y / self.scale_factor)
        x = max(0, min(x, BASE_WIDTH))
        y = max(0, min(y, BASE_HEIGHT))
        return x, y

    def clear_screen(self):
        self.screen.fill(BLACK)

    def add_shake(self, amount, duration):
        self.shake_amount = amount
        self.shake_duration = duration

    def update_shake(self):
        if self.shake_duration > 0:
            self.shake_duration -= 1
            if self.shake_duration <= 0:
                self.shake_amount = 0

    def apply_graphics_quality(self, surface):
        if self.graphics_quality == 1:
            small = pygame.transform.scale(surface, (BASE_WIDTH // 3, BASE_HEIGHT // 3))
            return pygame.transform.scale(small, (BASE_WIDTH, BASE_HEIGHT))
        else:
            small = pygame.transform.scale(surface, (BASE_WIDTH // 2, BASE_HEIGHT // 2))
            return pygame.transform.scale(small, (BASE_WIDTH, BASE_HEIGHT))

    def blit_virtual_screen(self):
        if self.virtual_rect:
            processed = self.apply_graphics_quality(self.virtual_screen)
            if self.shake_duration > 0 and self.shake_amount > 0:
                shake_x = random.randint(-self.shake_amount, self.shake_amount)
                shake_y = random.randint(-self.shake_amount, self.shake_amount)
                scaled = pygame.transform.scale(processed, (self.virtual_rect.width, self.virtual_rect.height))
                shake_surf = pygame.Surface((self.virtual_rect.width, self.virtual_rect.height))
                shake_surf.blit(scaled, (shake_x, shake_y))
                if shake_x < 0:
                    pygame.draw.rect(shake_surf, BLACK,
                                     (self.virtual_rect.width + shake_x, 0, -shake_x, self.virtual_rect.height))
                elif shake_x > 0:
                    pygame.draw.rect(shake_surf, BLACK, (0, 0, shake_x, self.virtual_rect.height))
                if shake_y < 0:
                    pygame.draw.rect(shake_surf, BLACK,
                                     (0, self.virtual_rect.height + shake_y, self.virtual_rect.width, -shake_y))
                elif shake_y > 0:
                    pygame.draw.rect(shake_surf, BLACK, (0, 0, self.virtual_rect.width, shake_y))
                self.screen.blit(shake_surf, self.virtual_rect)
            else:
                scaled = pygame.transform.scale(processed, (self.virtual_rect.width, self.virtual_rect.height))
                self.screen.blit(scaled, self.virtual_rect)


class PlayerProfile:
    def __init__(self, nickname="Pilot"):
        self.nickname = nickname
        self.first_login = True
        self.total_coins_earned = 0
        self.badges_count = 0
        self.skins_owned = 1
        self.total_play_time = 0
        self.total_games = 0
        self.high_score = 0
        self.max_combo = 0
        self.bird_level = 1
        self.bird_exp = 0
        self.bird_exp_to_next = 100

    def to_dict(self):
        return {
            'nickname': self.nickname,
            'first_login': self.first_login,
            'total_coins_earned': self.total_coins_earned,
            'badges_count': self.badges_count,
            'skins_owned': self.skins_owned,
            'total_play_time': self.total_play_time,
            'total_games': self.total_games,
            'high_score': self.high_score,
            'max_combo': self.max_combo,
            'bird_level': self.bird_level,
            'bird_exp': self.bird_exp,
            'bird_exp_to_next': self.bird_exp_to_next,
        }

    @classmethod
    def from_dict(cls, data):
        profile = cls(data.get('nickname', 'Pilot'))
        profile.first_login = data.get('first_login', True)
        profile.total_coins_earned = data.get('total_coins_earned', 0)
        profile.badges_count = data.get('badges_count', 0)
        profile.skins_owned = data.get('skins_owned', 1)
        profile.total_play_time = data.get('total_play_time', 0)
        profile.total_games = data.get('total_games', 0)
        profile.high_score = data.get('high_score', 0)
        profile.max_combo = data.get('max_combo', 0)
        profile.bird_level = data.get('bird_level', 1)
        profile.bird_exp = data.get('bird_exp', 0)
        profile.bird_exp_to_next = data.get('bird_exp_to_next', 100)
        return profile


class WorldRankingSystem:
    def __init__(self):
        self.players = []
        self.player_positions = {}
        self.update_timer = 0
        self.update_interval = 30 * 60
        self.max_players = 500
        self.generated_names = self.generate_player_names()
        self.current_page = 0
        self.players_per_page = 8
        self.scroll_offset = 0
        self.selected_player = None
        self.animation_timer = 0
        self.live_matches = []
        self.match_timer = 0
        self.match_duration = 0
        self.current_match = None
        self.match_in_progress = False
        self.match_players = []
        self.match_elo_changes = {}
        self.total_players = 0
        self.mode = "all"
        self.rank_changes = {}
        self.last_rankings = {}

        self.generate_initial_players()

    def _ensure_player_fields(self, player):
        if 'tennis_wins' not in player:
            player['tennis_wins'] = 0
        if 'tennis_losses' not in player:
            player['tennis_losses'] = 0
        if 'basketball_wins' not in player:
            player['basketball_wins'] = 0
        if 'basketball_losses' not in player:
            player['basketball_losses'] = 0
        if 'win_streak' not in player:
            player['win_streak'] = 0
        if 'elo_history' not in player:
            player['elo_history'] = [player.get('total_elo', 1000)]
        if 'last_elo_change' not in player:
            player['last_elo_change'] = 0
        if 'previous_rank' not in player:
            player['previous_rank'] = 0
        if 'losses' not in player:
            player['losses'] = 0
        if 'wins' not in player:
            player['wins'] = 0
        if 'matches_played' not in player:
            player['matches_played'] = player.get('wins', 0) + player.get('losses', 0)
        if 'tennis_elo' not in player:
            player['tennis_elo'] = player.get('total_elo', 1000)
        if 'basketball_elo' not in player:
            player['basketball_elo'] = player.get('total_elo', 1000)
        if 'total_elo' not in player:
            player['total_elo'] = (player.get('tennis_elo', 1000) + player.get('basketball_elo', 1000)) // 2
        if 'name' not in player:
            player['name'] = "Unknown"
        if 'rank' not in player:
            player['rank'] = 0
        if 'last_match_time' not in player:
            player['last_match_time'] = datetime.now().strftime("%H:%M")
        if 'avatar_color' not in player:
            player['avatar_color'] = (100, 180, 220)

    def generate_player_names(self):
        return generate_random_nicks(100)

    def generate_initial_players(self):
        num_players = random.randint(80, 200)
        self.players = []

        for i in range(num_players):
            name = random.choice(self.generated_names) if self.generated_names else f"Player{i}"
            if name in self.generated_names:
                self.generated_names.remove(name)

            base_elo = random.randint(800, 3000)
            tennis_elo = base_elo + random.randint(-150, 150)
            basketball_elo = base_elo + random.randint(-150, 150)
            total_elo = (tennis_elo + basketball_elo) // 2

            wins = int((total_elo - 800) / 15) + random.randint(0, 30)
            losses = int(wins * random.uniform(0.3, 0.8))

            tennis_wins = max(0, wins // 2 + random.randint(-3, 3))
            basketball_wins = max(0, wins - tennis_wins)

            player = {
                'name': name,
                'tennis_elo': max(800, tennis_elo),
                'basketball_elo': max(800, basketball_elo),
                'total_elo': total_elo,
                'wins': max(0, wins),
                'losses': max(0, losses),
                'matches_played': wins + losses,
                'win_streak': random.randint(0, 10),
                'rank': 0,
                'last_match_time': datetime.now().strftime("%H:%M"),
                'avatar_color': (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
                'elo_history': [total_elo],
                'last_elo_change': 0,
                'previous_rank': 0,
                'tennis_wins': tennis_wins,
                'tennis_losses': max(0, losses // 2 + random.randint(-3, 3)),
                'basketball_wins': basketball_wins,
                'basketball_losses': max(0, losses - max(0, losses // 2 + random.randint(-3, 3)))
            }
            self.players.append(player)

        self.total_players = len(self.players)
        self.sort_and_rank_players()

        for player in self.players:
            self.last_rankings[player['name']] = player['rank']

    def sort_and_rank_players(self):
        if self.mode == "tennis":
            self.players.sort(key=lambda x: x.get('tennis_elo', 1000), reverse=True)
        elif self.mode == "basketball":
            self.players.sort(key=lambda x: x.get('basketball_elo', 1000), reverse=True)
        else:
            self.players.sort(key=lambda x: x.get('total_elo', 1000), reverse=True)

        self.rank_changes = {}
        for i, player in enumerate(self.players):
            old_rank = player.get('previous_rank', 0)
            new_rank = i + 1
            player['rank'] = new_rank
            if old_rank != new_rank and old_rank > 0:
                change = old_rank - new_rank
                self.rank_changes[player['name']] = change
            player['previous_rank'] = new_rank

        self.player_positions = {player['name']: player['rank'] for player in self.players}

    def update(self):
        self.animation_timer += 1
        self.match_timer += 1

        if not self.match_in_progress:
            if self.match_timer > random.randint(30 * 60, 60 * 60):
                self.match_timer = 0
                self.start_match()
        else:
            self.match_duration -= 1
            if self.match_duration <= 0:
                self.finish_match()

        self.update_timer += 1
        if self.update_timer > self.update_interval:
            self.update_timer = 0
            self.update_rankings()

    def start_match(self):
        available = self.players[:]
        if len(available) < 2:
            return

        available.sort(key=lambda x: x.get('total_elo', 1000))

        idx1 = random.randint(0, len(available) - 2)
        idx2 = idx1 + 1
        for offset in range(1, min(5, len(available) - idx1)):
            if abs(available[idx1].get('total_elo', 1000) - available[idx1 + offset].get('total_elo',
                                                                                        1000)) < 100:
                idx2 = idx1 + offset
                break

        player1 = available[idx1]
        player2 = available[idx2]

        self.match_in_progress = True
        self.match_duration = random.randint(10 * 60, 15 * 60)
        self.match_players = [player1, player2]
        self.current_match = {
            'player1': player1['name'],
            'player2': player2['name'],
            'player1_elo': player1.get('total_elo', 1000),
            'player2_elo': player2.get('total_elo', 1000),
            'progress': 0
        }

    def finish_match(self):
        if not self.match_players or len(self.match_players) < 2:
            self.match_in_progress = False
            return

        player1, player2 = self.match_players[0], self.match_players[1]
        self._ensure_player_fields(player1)
        self._ensure_player_fields(player2)

        elo_diff = player1['total_elo'] - player2['total_elo']
        win_chance = 0.5 + (elo_diff / 600)
        win_chance = max(0.1, min(0.9, win_chance))

        if random.random() < win_chance:
            winner, loser = player1, player2
        else:
            winner, loser = player2, player1

        k_factor = 25 + random.randint(5, 15)
        expected = 1 / (1 + 10 ** ((loser['total_elo'] - winner['total_elo']) / 400))
        elo_change = int(k_factor * (1 - expected))
        elo_change = max(5, min(40, elo_change))

        winner['total_elo'] += elo_change
        loser['total_elo'] -= elo_change

        is_tennis_match = random.random() < 0.5

        if is_tennis_match:
            winner['tennis_elo'] += elo_change
            loser['tennis_elo'] -= elo_change
            winner['tennis_wins'] = winner.get('tennis_wins', 0) + 1
            loser['tennis_losses'] = loser.get('tennis_losses', 0) + 1
        else:
            winner['basketball_elo'] += elo_change
            loser['basketball_elo'] -= elo_change
            winner['basketball_wins'] = winner.get('basketball_wins', 0) + 1
            loser['basketball_losses'] = loser.get('basketball_losses', 0) + 1

        winner['wins'] += 1
        loser['losses'] += 1
        winner['matches_played'] += 1
        loser['matches_played'] += 1

        winner['win_streak'] = winner.get('win_streak', 0) + 1
        loser['win_streak'] = 0

        winner['last_elo_change'] = elo_change
        loser['last_elo_change'] = -elo_change

        winner['elo_history'].append(winner['total_elo'])
        loser['elo_history'].append(loser['total_elo'])
        if len(winner['elo_history']) > 20:
            winner['elo_history'] = winner['elo_history'][-20:]
        if len(loser['elo_history']) > 20:
            loser['elo_history'] = loser['elo_history'][-20:]

        match = {
            'player1': winner['name'],
            'player2': loser['name'],
            'winner': winner['name'],
            'elo_change': elo_change,
            'time': datetime.now().strftime("%H:%M"),
            'player1_elo_before': self.current_match['player1_elo'],
            'player2_elo_before': self.current_match['player2_elo'],
            'mode': "tennis" if is_tennis_match else "basketball"
        }
        self.live_matches.insert(0, match)
        if len(self.live_matches) > 15:
            self.live_matches.pop()

        self.sort_and_rank_players()

        self.match_in_progress = False
        self.match_players = []
        self.current_match = None

    def update_rankings(self):
        for player in random.sample(self.players, min(15, len(self.players))):
            if random.random() < 0.3:
                self._ensure_player_fields(player)
                change = random.randint(-10, 10)
                player['total_elo'] += change
                player['tennis_elo'] += change // 2
                player['basketball_elo'] += change // 2
                player['total_elo'] = max(800, player['total_elo'])
                player['tennis_elo'] = max(800, player['tennis_elo'])
                player['basketball_elo'] = max(800, player['basketball_elo'])
                player['last_elo_change'] = change

                if change > 0:
                    player['win_streak'] = player.get('win_streak', 0) + 1
                else:
                    player['win_streak'] = 0

        self.sort_and_rank_players()

    def get_player_rank(self, player_name):
        return self.player_positions.get(player_name, 999)

    def get_player_by_name(self, name):
        for player in self.players:
            if player['name'] == name:
                return player
        return None

    def get_top_players(self, count=10):
        return self.players[:count]

    def get_players_by_page(self, page=0, per_page=10):
        start = page * per_page
        end = start + per_page
        return self.players[start:end]

    def get_total_pages(self, per_page=10):
        return max(1, (len(self.players) + per_page - 1) // per_page)

    def set_mode(self, mode):
        self.mode = mode
        self.sort_and_rank_players()

    def get_rank_change(self, player_name):
        return self.rank_changes.get(player_name, 0)

    def to_dict(self):
        return {
            'players': self.players,
            'player_positions': self.player_positions,
            'generated_names': self.generated_names,
            'rank_changes': self.rank_changes,
            'update_timer': self.update_timer
        }

    def from_dict(self, data):
        if 'players' in data:
            self.players = data['players']
            for player in self.players:
                self._ensure_player_fields(player)
            self.sort_and_rank_players()
        if 'player_positions' in data:
            self.player_positions = data['player_positions']
        if 'generated_names' in data:
            self.generated_names = data['generated_names']
        if 'rank_changes' in data:
            self.rank_changes = data['rank_changes']
        if 'update_timer' in data:
            self.update_timer = data['update_timer']

        for player in self.players:
            self.last_rankings[player['name']] = player['rank']


class WorldRankingScreen:
    def __init__(self, ranking_system, sound_manager=None, background_manager=None, skin_manager=None):
        self.ranking_system = ranking_system
        self.sound_manager = sound_manager
        self.background_manager = background_manager
        self.skin_manager = skin_manager
        self.page = 0
        self.scroll_offset = 0
        self.selected_player = None
        self.show_player_stats = False
        self.animation = 0
        self.back_rect = None
        self.stats_close_rect = None
        self.elo_change_timer = 0
        self.elo_changes = {}
        self.search_text = ""
        self.search_active = False
        self.search_rect = None
        self.mode = "all"
        self.last_update_time = 0
        self.dragging_scroll = False

    def draw(self, screen):
        self.animation += 0.02

        if self.background_manager:
            bg = self.background_manager.get_random_background()
            if bg:
                screen.blit(bg, (0, 0))
            else:
                screen.fill((20, 25, 35))
        else:
            screen.fill((20, 25, 35))

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        font_title = pygame.font.Font(None, 34)
        font_header = pygame.font.Font(None, 20)
        font_player = pygame.font.Font(None, 19)
        font_small = pygame.font.Font(None, 16)
        font_tiny = pygame.font.Font(None, 13)

        title = font_title.render("WORLD RANKING", True, RETRO_GOLD)
        title_shadow = font_title.render("WORLD RANKING", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 9))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 8))

        time_to_update = max(0, (self.ranking_system.update_interval - self.ranking_system.update_timer) // 60)
        update_text = font_tiny.render(f"Update in: {time_to_update // 60}:{time_to_update % 60:02d}", True,
                                       RETRO_GRAY)
        update_shadow = font_tiny.render(f"Update in: {time_to_update // 60}:{time_to_update % 60:02d}", True, BLACK)
        screen.blit(update_shadow, (BASE_WIDTH - update_text.get_width() - 9, 32))
        screen.blit(update_text, (BASE_WIDTH - update_text.get_width() - 10, 31))

        mode_y = 40
        modes = [("ALL", "all"), ("TENNIS", "tennis"), ("BASKETBALL", "basketball")]
        mode_width = 70
        for i, (name, key) in enumerate(modes):
            mode_rect = pygame.Rect(10 + i * (mode_width + 5), mode_y, mode_width, 22)
            if self.mode == key:
                pygame.draw.rect(screen, RETRO_PURPLE, mode_rect, 0, 5)
                pygame.draw.rect(screen, RETRO_SILVER, mode_rect, 2, 5)
            else:
                pygame.draw.rect(screen, (50, 50, 70), mode_rect, 0, 5)
                pygame.draw.rect(screen, RETRO_GRAY, mode_rect, 2, 5)
            mode_text = font_tiny.render(name, True, RETRO_GOLD if self.mode == key else RETRO_GRAY)
            mode_shadow = font_tiny.render(name, True, BLACK)
            screen.blit(mode_shadow, (
                mode_rect.centerx - mode_text.get_width() // 2 + 1, mode_rect.centery - mode_text.get_height() // 2 + 1))
            screen.blit(mode_text, (
                mode_rect.centerx - mode_text.get_width() // 2, mode_rect.centery - mode_text.get_height() // 2))

        search_y = 68
        search_bg = pygame.Rect(10, search_y, BASE_WIDTH - 80, 24)
        pygame.draw.rect(screen, (40, 40, 55), search_bg, 0, 5)
        pygame.draw.rect(screen, RETRO_SILVER, search_bg, 1, 5)

        search_display = self.search_text if self.search_active else "Search player..."
        search_color = RETRO_GOLD if self.search_active else RETRO_GRAY
        search_text = font_tiny.render(search_display, True, search_color)
        search_shadow = font_tiny.render(search_display, True, BLACK)
        screen.blit(search_shadow, (search_bg.x + 6 + 1, search_bg.centery - search_text.get_height() // 2 + 1))
        screen.blit(search_text, (search_bg.x + 6, search_bg.centery - search_text.get_height() // 2))
        self.search_rect = search_bg

        search_btn = pygame.Rect(BASE_WIDTH - 65, search_y, 55, 24)
        pygame.draw.rect(screen, RETRO_PURPLE, search_btn, 0, 5)
        pygame.draw.rect(screen, RETRO_SILVER, search_btn, 1, 5)
        search_btn_text = font_tiny.render("Find", True, RETRO_GOLD)
        search_btn_shadow = font_tiny.render("Find", True, BLACK)
        screen.blit(search_btn_shadow,
                    (search_btn.centerx - search_btn_text.get_width() // 2 + 1,
                     search_btn.centery - search_btn_text.get_height() // 2 + 1))
        screen.blit(search_btn_text,
                    (search_btn.centerx - search_btn_text.get_width() // 2,
                     search_btn.centery - search_btn_text.get_height() // 2))

        if self.ranking_system.match_in_progress and self.ranking_system.current_match:
            match = self.ranking_system.current_match
            progress = 1.0 - (self.ranking_system.match_duration / (15 * 60))

            match_text = font_small.render(f"{match['player1']} vs {match['player2']}", True, RETRO_GOLD)
            match_shadow = font_small.render(f"{match['player1']} vs {match['player2']}", True, BLACK)
            match_bg = pygame.Surface((match_text.get_width() + 20, 22), pygame.SRCALPHA)
            pygame.draw.rect(match_bg, (0, 0, 0, 200), match_bg.get_rect(), 0, 6)
            screen.blit(match_bg, (BASE_WIDTH // 2 - match_text.get_width() // 2 - 10, 96))
            screen.blit(match_shadow, (BASE_WIDTH // 2 - match_text.get_width() // 2 + 1, 98))
            screen.blit(match_text, (BASE_WIDTH // 2 - match_text.get_width() // 2, 97))

            bar_rect = pygame.Rect(BASE_WIDTH // 2 - 80, 119, 160, 4)
            pygame.draw.rect(screen, (40, 40, 50), bar_rect, 0, 2)
            fill_width = int(160 * progress)
            if fill_width > 0:
                pygame.draw.rect(screen, RETRO_GOLD, (bar_rect.x, bar_rect.y, fill_width, bar_rect.height), 0, 2)

        start_y = 130 if self.ranking_system.match_in_progress else 96
        row_height = 32

        players = self.ranking_system.players
        if self.search_text and self.search_active:
            players = [p for p in players if self.search_text.lower() in p['name'].lower()]

        per_page = 8
        total_pages = max(1, (len(players) + per_page - 1) // per_page)
        if self.page >= total_pages:
            self.page = total_pages - 1
        start_idx = self.page * per_page
        end_idx = min(start_idx + per_page, len(players))

        headers = ["R", "PLAYER", "RATING", "WINS"]
        header_x = [10, 45, 185, 270]
        header_y = start_y

        pygame.draw.line(screen, (60, 60, 80), (5, header_y + 18), (BASE_WIDTH - 5, header_y + 18), 1)

        for i, header in enumerate(headers):
            header_text = font_header.render(header, True, RETRO_SILVER)
            header_shadow = font_header.render(header, True, BLACK)
            screen.blit(header_shadow, (header_x[i] + 1, header_y + 1))
            screen.blit(header_text, (header_x[i], header_y))

        y_offset = start_y + 22
        for i in range(start_idx, end_idx):
            player = players[i]
            row_y = y_offset + (i - start_idx) * row_height

            if row_y > BASE_HEIGHT - 80:
                break

            rank_change = self.ranking_system.get_rank_change(player['name'])

            if i == self.selected_player:
                bg_color = (RETRO_PURPLE[0], RETRO_PURPLE[1], RETRO_PURPLE[2], 100)
            elif i % 2 == 0:
                bg_color = (50, 55, 65, 80)
            else:
                bg_color = (40, 45, 55, 80)

            row_rect = pygame.Rect(5, row_y - 2, BASE_WIDTH - 10, row_height - 2)
            pygame.draw.rect(screen, bg_color, row_rect, 0, 4)

            rank_text = f"{player['rank']}"
            rank_color = RETRO_GRAY

            if player['rank'] == 1:
                rank_text = "1"
                rank_color = DIAMOND
            elif player['rank'] == 2:
                rank_text = "2"
                rank_color = RETRO_SILVER
            elif player['rank'] == 3:
                rank_text = "3"
                rank_color = (205, 127, 50)

            rank_surf = font_player.render(rank_text, True, rank_color)
            rank_shadow = font_player.render(rank_text, True, BLACK)
            screen.blit(rank_shadow, (11, row_y + 2))
            screen.blit(rank_surf, (10, row_y + 1))

            if rank_change > 0:
                change_text = font_tiny.render(f"+{rank_change}", True, RETRO_GREEN)
                change_shadow = font_tiny.render(f"+{rank_change}", True, BLACK)
                screen.blit(change_shadow, (50, row_y + 8))
                screen.blit(change_text, (49, row_y + 7))
            elif rank_change < 0:
                change_text = font_tiny.render(f"{rank_change}", True, RETRO_RED)
                change_shadow = font_tiny.render(f"{rank_change}", True, BLACK)
                screen.blit(change_shadow, (50, row_y + 8))
                screen.blit(change_text, (49, row_y + 7))

            name_x = 45 if rank_change == 0 else 75
            name_color = RETRO_WHITE
            if player['rank'] == 1:
                name_color = DIAMOND
            elif player['rank'] == 2:
                name_color = RETRO_SILVER
            elif player['rank'] == 3:
                name_color = (205, 127, 50)
            elif player.get('win_streak', 0) >= 5:
                name_color = RETRO_ORANGE

            name_text = font_player.render(
                player['name'][:14] + ".." if len(player['name']) > 14 else player['name'], True, name_color)
            name_shadow = font_player.render(
                player['name'][:14] + ".." if len(player['name']) > 14 else player['name'], True, BLACK)
            screen.blit(name_shadow, (name_x + 1, row_y + 2))
            screen.blit(name_text, (name_x, row_y + 1))

            if self.mode == "tennis":
                elo_display = player.get('tennis_elo', 1000)
                wins_display = player.get('tennis_wins', 0)
            elif self.mode == "basketball":
                elo_display = player.get('basketball_elo', 1000)
                wins_display = player.get('basketball_wins', 0)
            else:
                elo_display = player.get('total_elo', 1000)
                wins_display = player.get('wins', 0)

            elo_text = font_player.render(str(elo_display), True, RETRO_GOLD)
            elo_shadow = font_player.render(str(elo_display), True, BLACK)
            screen.blit(elo_shadow, (186, row_y + 2))
            screen.blit(elo_text, (185, row_y + 1))

            if player.get('last_elo_change', 0) != 0:
                change = player['last_elo_change']
                change_color = RETRO_GREEN if change > 0 else RETRO_RED
                change_text = font_tiny.render(f"{'+' if change > 0 else ''}{change}", True, change_color)
                change_shadow = font_tiny.render(f"{'+' if change > 0 else ''}{change}", True, BLACK)
                screen.blit(change_shadow, (236, row_y + 9))
                screen.blit(change_text, (235, row_y + 8))

            wins_text = font_player.render(str(wins_display), True, RETRO_SILVER)
            wins_shadow = font_player.render(str(wins_display), True, BLACK)
            screen.blit(wins_shadow, (271, row_y + 2))
            screen.blit(wins_text, (270, row_y + 1))

            if player.get('win_streak', 0) >= 3:
                streak_text = font_tiny.render(str(player['win_streak']), True, RETRO_ORANGE)
                streak_shadow = font_tiny.render(str(player['win_streak']), True, BLACK)
                screen.blit(streak_shadow, (310, row_y + 9))
                screen.blit(streak_text, (309, row_y + 8))

        pagination_y = BASE_HEIGHT - 45
        if total_pages > 1:
            prev_rect = pygame.Rect(10, pagination_y - 15, 55, 25)
            pygame.draw.rect(screen, RETRO_PURPLE if self.page > 0 else (60, 60, 80), prev_rect, 0, 5)
            pygame.draw.rect(screen, RETRO_SILVER if self.page > 0 else RETRO_GRAY, prev_rect, 1, 5)
            prev_text = font_tiny.render("< Back", True, RETRO_GOLD if self.page > 0 else RETRO_GRAY)
            prev_shadow = font_tiny.render("< Back", True, BLACK)
            screen.blit(prev_shadow, (prev_rect.x + 5 + 1, prev_rect.centery - prev_text.get_height() // 2 + 1))
            screen.blit(prev_text, (prev_rect.x + 5, prev_rect.centery - prev_text.get_height() // 2))

            page_text = font_small.render(f"{self.page + 1}/{total_pages}", True, RETRO_GOLD)
            page_shadow = font_small.render(f"{self.page + 1}/{total_pages}", True, BLACK)
            screen.blit(page_shadow, (BASE_WIDTH // 2 - page_text.get_width() // 2 + 1, pagination_y + 1))
            screen.blit(page_text, (BASE_WIDTH // 2 - page_text.get_width() // 2, pagination_y))

            next_rect = pygame.Rect(BASE_WIDTH - 65, pagination_y - 15, 55, 25)
            pygame.draw.rect(screen, RETRO_PURPLE if self.page < total_pages - 1 else (60, 60, 80), next_rect, 0, 5)
            pygame.draw.rect(screen, RETRO_SILVER if self.page < total_pages - 1 else RETRO_GRAY, next_rect, 1, 5)
            next_text = font_tiny.render("Next >", True, RETRO_GOLD if self.page < total_pages - 1 else RETRO_GRAY)
            next_shadow = font_tiny.render("Next >", True, BLACK)
            screen.blit(next_shadow, (next_rect.x + 5 + 1, next_rect.centery - next_text.get_height() // 2 + 1))
            screen.blit(next_text, (next_rect.x + 5, next_rect.centery - next_text.get_height() // 2))

        self.back_rect = pygame.Rect(BASE_WIDTH // 2 - 70, BASE_HEIGHT - 60, 140, 30)
        pygame.draw.rect(screen, RETRO_PURPLE, self.back_rect, 0, 8)
        pygame.draw.rect(screen, RETRO_SILVER, self.back_rect, 2, 8)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow,
                    (self.back_rect.centerx - back_text.get_width() // 2 + 1,
                     self.back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text,
                    (self.back_rect.centerx - back_text.get_width() // 2,
                     self.back_rect.centery - back_text.get_height() // 2))

        if self.ranking_system.live_matches and self.animation % 8 == 0:
            match = self.ranking_system.live_matches[0]
            match_text = font_tiny.render(f"{match['winner']} +{match['elo_change']} ELO", True, RETRO_GOLD)
            match_shadow = font_tiny.render(f"{match['winner']} +{match['elo_change']} ELO", True, BLACK)
            match_bg = pygame.Surface((match_text.get_width() + 12, 18), pygame.SRCALPHA)
            pygame.draw.rect(match_bg, (0, 0, 0, 180), match_bg.get_rect(), 0, 4)
            screen.blit(match_bg, (BASE_WIDTH // 2 - match_text.get_width() // 2 - 6, 5))
            screen.blit(match_shadow, (BASE_WIDTH // 2 - match_text.get_width() // 2 + 1, 7))
            screen.blit(match_text, (BASE_WIDTH // 2 - match_text.get_width() // 2, 6))

        if self.show_player_stats and self.selected_player is not None and self.selected_player < len(players):
            player = players[self.selected_player]
            self.draw_player_stats(screen, player)

        version_text = font_tiny.render(f"v{GAME_VERSION}", True, RETRO_GRAY)
        version_shadow = font_tiny.render(f"v{GAME_VERSION}", True, BLACK)
        screen.blit(version_shadow, (BASE_WIDTH - version_text.get_width() - 9, BASE_HEIGHT - 24))
        screen.blit(version_text, (BASE_WIDTH - version_text.get_width() - 10, BASE_HEIGHT - 25))

        if control_manager.control_type == ControlType.GAMEPAD:
            indicator = "Gamepad"
            indicator_color = RETRO_BLUE
        elif control_manager.control_type == ControlType.TOUCH:
            indicator = "Touch"
            indicator_color = RETRO_GREEN
        else:
            indicator = "Keyboard"
            indicator_color = RETRO_YELLOW
        indicator_text = font_tiny.render(indicator, True, indicator_color)
        indicator_shadow = font_tiny.render(indicator, True, BLACK)
        screen.blit(indicator_shadow, (BASE_WIDTH - indicator_text.get_width() - 9, 6))
        screen.blit(indicator_text, (BASE_WIDTH - indicator_text.get_width() - 10, 5))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)
        return self.back_rect

    def draw_player_stats(self, screen, player):
        stats_width = 280
        stats_height = 220
        stats_x = BASE_WIDTH // 2 - stats_width // 2
        stats_y = BASE_HEIGHT // 2 - stats_height // 2 - 20

        bg_surf = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 20, 40, 245), bg_surf.get_rect(), 0, 15)
        pygame.draw.rect(bg_surf, RETRO_GOLD, bg_surf.get_rect(), 2, 15)
        screen.blit(bg_surf, (stats_x, stats_y))

        font_medium = pygame.font.Font(None, 22)
        font_small = pygame.font.Font(None, 18)
        font_tiny = pygame.font.Font(None, 15)

        name_text = font_medium.render(player['name'], True, RETRO_WHITE)
        name_shadow = font_medium.render(player['name'], True, BLACK)
        screen.blit(name_shadow, (stats_x + stats_width // 2 - name_text.get_width() // 2 + 1, stats_y + 11))
        screen.blit(name_text, (stats_x + stats_width // 2 - name_text.get_width() // 2, stats_y + 10))

        rank_change = self.ranking_system.get_rank_change(player['name'])
        if rank_change > 0:
            rank_text = font_small.render(f"Rank: {player['rank']} +{rank_change}", True, RETRO_GREEN)
        elif rank_change < 0:
            rank_text = font_small.render(f"Rank: {player['rank']} {rank_change}", True, RETRO_RED)
        else:
            rank_text = font_small.render(f"Rank: {player['rank']}", True, RETRO_GOLD)
        rank_shadow = font_small.render(
            rank_text.get_text() if hasattr(rank_text, 'get_text') else f"Rank: {player['rank']}", True, BLACK)
        screen.blit(rank_shadow, (stats_x + 21, stats_y + 36))
        screen.blit(rank_text, (stats_x + 20, stats_y + 35))

        pygame.draw.line(screen, RETRO_SILVER, (stats_x + 10, stats_y + 58), (stats_x + stats_width - 10, stats_y + 58),
                         1)

        if self.mode == "tennis":
            elo_display = player.get('tennis_elo', 1000)
            wins_display = player.get('tennis_wins', 0)
            losses_display = player.get('tennis_losses', 0)
        elif self.mode == "basketball":
            elo_display = player.get('basketball_elo', 1000)
            wins_display = player.get('basketball_wins', 0)
            losses_display = player.get('basketball_losses', 0)
        else:
            elo_display = player.get('total_elo', 1000)
            wins_display = player.get('wins', 0)
            losses_display = player.get('losses', 0)

        stats = [
            f"Total ELO: {player.get('total_elo', 1000)}",
            f"Tennis ELO: {player.get('tennis_elo', 1000)}",
            f"Basketball ELO: {player.get('basketball_elo', 1000)}",
            f"Wins: {wins_display}  Losses: {losses_display}",
            f"Matches: {wins_display + losses_display}  Winrate: {wins_display / max(1, wins_display + losses_display) * 100:.0f}%",
            f"Win Streak: {player.get('win_streak', 0)}",
            f"Last ELO Change: {player.get('last_elo_change', 0)}"
        ]

        y_offset = 66
        for i, stat in enumerate(stats):
            stat_text = font_tiny.render(stat, True, RETRO_SILVER)
            stat_shadow = font_tiny.render(stat, True, BLACK)
            screen.blit(stat_shadow, (stats_x + 21, stats_y + y_offset + 1))
            screen.blit(stat_text, (stats_x + 20, stats_y + y_offset))
            y_offset += 18

        close_rect = pygame.Rect(stats_x + stats_width - 30, stats_y + 10, 20, 20)
        pygame.draw.rect(screen, RETRO_RED, close_rect, 0, 5)
        pygame.draw.rect(screen, RETRO_SILVER, close_rect, 1, 5)
        close_text = font_tiny.render("X", True, WHITE)
        close_shadow = font_tiny.render("X", True, BLACK)
        screen.blit(close_shadow, (
            close_rect.centerx - close_text.get_width() // 2 + 1,
            close_rect.centery - close_text.get_height() // 2 + 1))
        screen.blit(close_text,
                    (close_rect.centerx - close_text.get_width() // 2,
                     close_rect.centery - close_text.get_height() // 2))

        self.stats_close_rect = close_rect

    def handle_click(self, x, y):
        if self.show_player_stats and self.stats_close_rect:
            if self.stats_close_rect.collidepoint(x, y):
                self.show_player_stats = False
                self.selected_player = None
                if self.sound_manager:
                    self.sound_manager.play_button()
                return None

        if self.search_rect and self.search_rect.collidepoint(x, y):
            self.search_active = True
            if self.sound_manager:
                self.sound_manager.play_button()
            return None

        search_btn = pygame.Rect(BASE_WIDTH - 65, 68, 55, 24)
        if search_btn.collidepoint(x, y):
            self.search_active = True
            if self.sound_manager:
                self.sound_manager.play_button()
            return None

        mode_y = 40
        modes = [("ALL", "all"), ("TENNIS", "tennis"), ("BASKETBALL", "basketball")]
        mode_width = 70
        for i, (name, key) in enumerate(modes):
            mode_rect = pygame.Rect(10 + i * (mode_width + 5), mode_y, mode_width, 22)
            if mode_rect.collidepoint(x, y):
                self.mode = key
                self.ranking_system.set_mode(key)
                self.page = 0
                if self.sound_manager:
                    self.sound_manager.play_button()
                return None

        start_y = 130 if self.ranking_system.match_in_progress else 96
        row_height = 32
        players = self.ranking_system.players
        if self.search_text and self.search_active:
            players = [p for p in players if self.search_text.lower() in p['name'].lower()]

        per_page = 8
        start_idx = self.page * per_page
        end_idx = min(start_idx + per_page, len(players))

        for i in range(start_idx, end_idx):
            row_y = start_y + 22 + (i - start_idx) * row_height
            row_rect = pygame.Rect(5, row_y - 2, BASE_WIDTH - 10, row_height - 2)
            if row_rect.collidepoint(x, y):
                self.selected_player = i
                self.show_player_stats = True
                if self.sound_manager:
                    self.sound_manager.play_button()
                return None

        total_pages = max(1, (len(players) + per_page - 1) // per_page)
        pagination_y = BASE_HEIGHT - 45

        prev_rect = pygame.Rect(10, pagination_y - 15, 55, 25)
        if prev_rect.collidepoint(x, y) and self.page > 0:
            self.page -= 1
            if self.sound_manager:
                self.sound_manager.play_button()
            return None

        next_rect = pygame.Rect(BASE_WIDTH - 65, pagination_y - 15, 55, 25)
        if next_rect.collidepoint(x, y) and self.page < total_pages - 1:
            self.page += 1
            if self.sound_manager:
                self.sound_manager.play_button()
            return None

        if self.back_rect and self.back_rect.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            return "back"

        return None

    def handle_keyboard(self, event):
        if event.type == pygame.KEYDOWN:
            if self.search_active:
                if event.key == pygame.K_RETURN:
                    self.search_active = False
                    return "search_complete"
                elif event.key == pygame.K_ESCAPE:
                    self.search_active = False
                    self.search_text = ""
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.search_text = self.search_text[:-1]
                else:
                    if len(self.search_text) < 20 and event.unicode.isprintable():
                        self.search_text += event.unicode
                return None

        return None

    def handle_mouse_motion(self, x, y):
        pass

    def handle_mouse_up(self):
        self.dragging_scroll = False


class BasketballShotPosition:
    def __init__(self, name, x, y, points, description):
        self.name = name
        self.x = x
        self.y = y
        self.points = points
        self.description = description


SHOT_POSITIONS = [
    BasketballShotPosition("Under the hoop", BASE_WIDTH // 2, BASE_HEIGHT - 60, 1, "Easy shot"),
    BasketballShotPosition("Free throw", BASE_WIDTH // 2, BASE_HEIGHT - 130, 1, "Free throw line"),
    BasketballShotPosition("Left corner", 60, BASE_HEIGHT - 110, 2, "Left corner 2 points"),
    BasketballShotPosition("Right corner", BASE_WIDTH - 60, BASE_HEIGHT - 110, 2, "Right corner 2 points"),
    BasketballShotPosition("Top of the key", BASE_WIDTH // 2, BASE_HEIGHT - 150, 2, "Mid-range shot"),
    BasketballShotPosition("Left wing", 100, BASE_HEIGHT - 140, 2, "Left wing 2 points"),
    BasketballShotPosition("Right wing", BASE_WIDTH - 100, BASE_HEIGHT - 140, 2, "Right wing 2 points"),
    BasketballShotPosition("Left 3pt", 45, BASE_HEIGHT - 170, 3, "Three-pointer left"),
    BasketballShotPosition("Right 3pt", BASE_WIDTH - 45, BASE_HEIGHT - 170, 3, "Three-pointer right"),
    BasketballShotPosition("Center 3pt", BASE_WIDTH // 2, BASE_HEIGHT - 190, 3, "Arc three-pointer"),
    BasketballShotPosition("Deep left", 30, BASE_HEIGHT - 200, 3, "Deep three-pointer"),
    BasketballShotPosition("Deep right", BASE_WIDTH - 30, BASE_HEIGHT - 200, 3, "Deep three-pointer"),
]


class BasketballBadge:
    def __init__(self, level_id, name, description, color, icon_type="basketball"):
        self.level_id = level_id
        self.name = name
        self.description = description
        self.color = color
        self.icon_type = icon_type
        self.earned = False
        self.earned_date = datetime.now().strftime("%d.%m.%Y")
        self.pixel_data = self.generate_icon()

    def generate_icon(self):
        if self.icon_type == "cup":
            return [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [1, 1, 0, 1, 1, 0, 1, 1],
                [1, 1, 0, 1, 1, 0, 1, 1],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0]
            ]
        else:
            return [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0]
            ]

    def to_dict(self):
        return {
            'level_id': self.level_id,
            'name': self.name,
            'description': self.description,
            'color': list(self.color) if isinstance(self.color, tuple) else self.color,
            'icon_type': self.icon_type,
            'earned': self.earned,
            'earned_date': self.earned_date
        }

    @classmethod
    def from_dict(cls, data):
        if isinstance(data['color'], list):
            color = tuple(data['color'])
        else:
            color = data['color']
        badge = cls(data['level_id'], data['name'], data['description'], color, data.get('icon_type', 'basketball'))
        badge.earned = data.get('earned', False)
        badge.earned_date = data.get('earned_date', datetime.now().strftime("%d.%m.%Y"))
        return badge

    @property
    def rarity_color(self):
        return self.color

    @property
    def rarity_name(self):
        return "Legendary" if self.icon_type == "cup" else "Epic"


class BasketballLevel:
    def __init__(self, level_id, chapter, name, opponent_name, description, story_before, story_after, difficulty,
                 target_score, reward_coins, reward_exp, is_final=False):
        self.id = level_id
        self.chapter = chapter
        self.name = name
        self.opponent_name = opponent_name
        self.description = description
        self.story_before = story_before
        self.story_after = story_after
        self.difficulty = difficulty
        self.target_score = target_score
        self.reward_coins = reward_coins
        self.reward_exp = reward_exp
        self.completed = False
        self.stars_earned = 0
        self.best_score = 0
        self.unlocked = False
        self.is_final = is_final
        self.is_ranked = False
        self.badge = None
        self.create_badge()

    def create_badge(self):
        colors = [
            (100, 200, 255), (100, 255, 100), (210, 180, 120), (255, 100, 100),
            (255, 100, 255), (100, 100, 255), (255, 200, 100), (100, 255, 255),
            (255, 150, 50), (200, 100, 255), (50, 200, 100), (200, 200, 50),
            (255, 50, 50), (50, 50, 255), (210, 180, 120)
        ]
        color = colors[self.id % len(colors)]

        if self.is_final:
            self.badge = BasketballBadge(self.id, "Winner", "Championship victory", RETRO_GOLD, "cup")
        elif self.is_ranked:
            self.badge = BasketballBadge(self.id, "Ranked Fighter", "Ranked match victory", RETRO_GOLD, "cup")
        else:
            names = [
                "First Step", "Street Legend", "Night Hunter", "School Talent",
                "City Hero", "Prodigy", "College Fighter", "Spirit of Strength",
                "Star Time", "Dream Come True", "Rookie of the Year", "Playoff Hero",
                "Finalist", "Champion", "Legend"
            ]
            descs = [
                "First basketball match", "Street legend defeated", "Night game victory",
                "Made school team", "City tournament win", "Young star defeated",
                "Veteran defeated", "Tough player defeated", "All-Star MVP",
                "Drafted to pros", "First professional game", "Playoff victory",
                "Conference finals", "Championship victory", "Career completed"
            ]
            if self.id < len(names):
                self.badge = BasketballBadge(self.id, names[self.id], descs[self.id], color)
            else:
                self.badge = BasketballBadge(self.id, f"Level {self.id}", "Completed level", color)

    def to_dict(self):
        data = {
            'id': self.id, 'chapter': self.chapter, 'name': self.name,
            'completed': self.completed, 'unlocked': self.unlocked,
            'best_score': self.best_score, 'stars_earned': self.stars_earned,
            'is_final': self.is_final, 'is_ranked': self.is_ranked
        }
        if self.badge:
            data['badge'] = self.badge.to_dict()
        return data

    @classmethod
    def from_dict(cls, data, template):
        level = cls(template.id, template.chapter, template.name, template.opponent_name,
                    template.description, template.story_before, template.story_after,
                    template.difficulty, template.target_score, template.reward_coins, template.reward_exp,
                    template.is_final)
        level.completed = data.get('completed', False)
        level.unlocked = data.get('unlocked', False)
        level.best_score = data.get('best_score', 0)
        level.stars_earned = data.get('stars_earned', 0)
        level.is_ranked = data.get('is_ranked', False)
        if 'badge' in data:
            level.badge = BasketballBadge.from_dict(data['badge'])
        else:
            level.create_badge()
        return level


class BasketballCampaignManager:
    def __init__(self):
        self.levels = []
        self.current_level = 0
        self.create_campaign()
        self.levels[0].unlocked = True
        self.campaign_completed = False
        self.final_level_completed = False
        self.elo = 1000
        self.best_elo = 1000
        self.matches_played = 0
        self.matches_won = 0
        self.ranked_matches_won = 0
        self.ranked_matches_played = 0
        self.cup_earned = False
        self.cups_earned = []
        self.ranked_unlocked = False
        self.ranked_searching = False
        self.ranked_search_timer = 0
        self.ranked_match_found = False
        self.ranked_match_timer = 0
        self.ranked_match_ready = False
        self.ranked_opponent = "Player"
        self.ranked_opponent_name = "Player"

        self.ranked_opponents = generate_random_nicks(50)

        self.is_ranked_match = False
        self.ranked_level = None
        self.current_streak = 0
        self.best_streak = 0
        self.streak_bonus_earned = 0
        self.streak_threshold = 5
        self.streak_bonus_total = 0
        self.perfect_shots_total = 0
        self.three_pointers_in_match = 0
        self.max_three_pointers_in_match = 0
        self.perfect_game_achieved = False
        self.misses_in_current_game = 0
        self.shots_in_current_game = 0
        self.perfect_shots_in_current_game = 0
        self.current_match_streak = 0

    def create_campaign(self):
        stories_before = [
            "I was a nobody, shy with dreams...",
            "We came to some local training club...",
            "It was awesome! We played, we had a good team...",
            "Me and the captain were sitting on the bench, everyone was playing...",
            "I stayed. That was already too much...",
            "I was in the starting lineup until the end of the season...",
            "I was on the team. Naturally sitting on the bench...",
            "Semifinal. Last minutes...",
            "Final. A very tough series...",
            "France. A beautiful city...",
            "Are you ready to challenge the best basketball players in the world?"
        ]

        stories_after = [
            "I defeated him...",
            "I'm on the team...",
            "We won!",
            "After the game, the captain told me he was leaving...",
            "It was incredible...",
            "I did it...",
            "Another victory!",
            "Final shot. Euphoria...",
            "Boom! The siren!",
            "He told me I'm not bad...",
            "Welcome to the world of ranked basketball!"
        ]

        levels_data = [
            (1, "First Shot", "Local Guy", "Your first basketball game", 1, 11, 30, 40, False),
            (1, "Club Tryout", "Captain", "Your first club tryout", 2, 15, 40, 60, False),
            (1, "Regional Final", "Opponent Team", "First serious final", 2, 15, 50, 80, False),
            (2, "Farewell to Captain", "Captain", "Farewell match with a friend", 2, 15, 60, 100, False),
            (2, "First Start", "Opponent", "First start in the main lineup", 3, 17, 80, 120, False),
            (2, "Higher League Tryout", "Sniper", "Fight for a spot in the higher league", 3, 19, 100, 150, False),
            (3, "Dream on the Court", "Opponent", "You're in the higher league", 3, 21, 120, 180, False),
            (3, "Semifinal", "Opponent", "Decisive semifinal match", 4, 21, 140, 200, False),
            (3, "Championship Final", "Legend", "Final championship match", 4, 21, 160, 250, False),
            (4, "Meeting with Captain", "Captain", "Meeting with a friend in France", 5, 21, 200, 300, True),
            (5, "Ranked Basketball", "Opponent", "Fight the best players in the world!", 5, 21, 250, 400, False),
        ]

        for i, data in enumerate(levels_data):
            story_before = stories_before[i] if i < len(stories_before) else ""
            story_after = stories_after[i] if i < len(stories_after) else ""
            level = BasketballLevel(
                i, data[0], data[1], data[2], data[3],
                story_before, story_after,
                data[4], data[5], data[6], data[7],
                data[8]
            )
            if i == 10:
                level.is_ranked = True
                level.is_final = False
            self.levels.append(level)

    def get_current_level(self):
        if self.is_ranked_match and self.ranked_level:
            return self.ranked_level
        if 0 <= self.current_level < len(self.levels):
            return self.levels[self.current_level]
        return self.levels[0]

    def add_streak_bonus(self, streak_length):
        if streak_length >= self.streak_threshold:
            bonus = (streak_length // self.streak_threshold) * 5
            self.streak_bonus_earned += bonus
            self.streak_bonus_total += bonus
            if streak_length > self.best_streak:
                self.best_streak = streak_length
            return bonus
        return 0

    def reset_streak(self):
        self.current_streak = 0

    def reset_match_stats(self):
        self.misses_in_current_game = 0
        self.shots_in_current_game = 0
        self.perfect_shots_in_current_game = 0
        self.three_pointers_in_match = 0
        self.current_match_streak = 0

    def complete_level(self, player_score, cpu_score):
        streak_bonus = self.streak_bonus_earned
        self.streak_bonus_earned = 0

        if self.is_ranked_match:
            self.ranked_matches_played += 1
            if player_score > cpu_score:
                elo_gain = 25 + streak_bonus
                self.elo += elo_gain
                self.matches_won += 1
                self.matches_played += 1
                self.ranked_matches_won += 1
                self.best_elo = max(self.best_elo, self.elo)
                self.check_cups()
                self.is_ranked_match = False
                self.ranked_level = None
                self.current_streak = 0
                return True, elo_gain, "win", streak_bonus
            else:
                self.elo += streak_bonus
                elo_loss = 20
                self.elo -= elo_loss
                self.matches_played += 1
                self.is_ranked_match = False
                self.ranked_level = None
                self.current_streak = 0
                return True, -elo_loss + streak_bonus, "loss", streak_bonus

        level = self.get_current_level()

        if level.is_ranked:
            self.ranked_matches_played += 1
            if player_score > cpu_score:
                elo_gain = 25 + streak_bonus
                self.elo += elo_gain
                self.matches_won += 1
                self.matches_played += 1
                self.ranked_matches_won += 1
                self.best_elo = max(self.best_elo, self.elo)
                self.check_cups()
                self.current_streak = 0
                return True, elo_gain, "win", streak_bonus
            else:
                self.elo += streak_bonus
                elo_loss = 20
                self.elo -= elo_loss
                self.matches_played += 1
                self.current_streak = 0
                return True, -elo_loss + streak_bonus, "loss", streak_bonus

        if level.is_final:
            level.completed = True
            if level.badge:
                level.badge.earned = True
            self.final_level_completed = True
            self.campaign_completed = True
            self.ranked_unlocked = True
            if len(self.levels) > 10:
                self.levels[10].unlocked = True
            self.current_streak = 0
            return True, 0, "complete", 0

        if player_score >= level.target_score:
            level.completed = True
            if level.badge:
                level.badge.earned = True
            if player_score >= level.target_score + 5:
                level.stars_earned = 3
            elif player_score >= level.target_score + 2:
                level.stars_earned = 2
            else:
                level.stars_earned = 1
            level.best_score = max(level.best_score, player_score)
            next_id = self.current_level + 1
            if next_id < len(self.levels):
                self.levels[next_id].unlocked = True
            if self.current_level == len(self.levels) - 1:
                self.campaign_completed = True
            if self.current_level == 9:
                self.levels[10].unlocked = True
                self.ranked_unlocked = True
            self.matches_won += 1
            self.matches_played += 1
            self.current_streak = 0
            return True, 0, "complete", 0
        self.matches_played += 1
        self.current_streak = 0
        return False, 0, "loss", 0

    def check_cups(self):
        cup_thresholds = [
            (1100, "Bronze Cup", (205, 127, 50)),
            (1200, "Silver Cup", (192, 192, 192)),
            (1300, "Gold Cup", (210, 180, 120)),
            (1500, "Platinum Cup", (229, 228, 226)),
            (1700, "Diamond Cup", (185, 242, 255)),
            (2000, "Champion Cup", (255, 215, 0)),
        ]

        for threshold, name, color in cup_thresholds:
            if self.elo >= threshold:
                if name not in self.cups_earned:
                    self.cups_earned.append(name)
                    self.cup_earned = True
                    return name, color
        return None, None

    def get_current_rank(self):
        if self.elo >= 2000:
            return "Champion"
        elif self.elo >= 1700:
            return "Diamond"
        elif self.elo >= 1500:
            return "Platinum"
        elif self.elo >= 1300:
            return "Gold"
        elif self.elo >= 1200:
            return "Silver"
        elif self.elo >= 1100:
            return "Bronze"
        else:
            return "Rookie"

    def start_ranked_search(self):
        self.ranked_searching = True
        self.ranked_search_timer = 0
        self.ranked_match_found = False
        self.ranked_match_ready = False
        self.ranked_match_timer = 0
        self.ranked_opponent = "Player"
        self.ranked_opponent_name = "Player"
        self.current_streak = 0
        self.best_streak = 0
        return True

    def update_ranked_search(self):
        if not self.ranked_searching:
            return False

        self.ranked_search_timer += 1

        if self.ranked_search_timer > 120:
            self.ranked_searching = False
            self.ranked_match_found = True
            self.ranked_match_ready = True
            self.ranked_match_timer = 15 * 60
            self.ranked_opponent = random.choice(self.ranked_opponents)
            self.ranked_opponent_name = self.ranked_opponent
            return True
        return False

    def update_ranked_match_timer(self):
        if self.ranked_match_ready and self.ranked_match_timer > 0:
            self.ranked_match_timer -= 1
            if self.ranked_match_timer <= 0:
                self.ranked_match_found = False
                self.ranked_match_ready = False
                self.ranked_opponent = "Player"
                self.ranked_opponent_name = "Player"
                return True
        return False

    def accept_ranked_match(self):
        if self.ranked_match_ready and self.ranked_match_found:
            opponent = self.ranked_opponent_name
            self.ranked_level = BasketballLevel(
                999, 5, "Ranked Match", opponent,
                f"Ranked match against {opponent}",
                f"Are you ready to challenge {opponent}?",
                f"Great match against {opponent}!",
                5, 21, 250, 400, False
            )
            self.ranked_level.is_ranked = True
            self.is_ranked_match = True
            self.ranked_match_ready = False
            self.ranked_match_found = False
            self.ranked_searching = False
            self.ranked_match_timer = 0
            self.ranked_opponent = opponent
            return True, opponent
        return False, None

    def to_dict(self):
        return {
            'current_level': self.current_level,
            'campaign_completed': self.campaign_completed,
            'final_level_completed': self.final_level_completed,
            'levels': [level.to_dict() for level in self.levels],
            'elo': self.elo,
            'best_elo': self.best_elo,
            'matches_played': self.matches_played,
            'matches_won': self.matches_won,
            'ranked_matches_won': self.ranked_matches_won,
            'ranked_matches_played': self.ranked_matches_played,
            'cups_earned': self.cups_earned,
            'ranked_unlocked': self.ranked_unlocked,
            'is_ranked_match': self.is_ranked_match,
            'best_streak': self.best_streak,
            'streak_bonus_earned': self.streak_bonus_earned,
            'streak_bonus_total': self.streak_bonus_total,
            'perfect_shots_total': self.perfect_shots_total,
            'max_three_pointers_in_match': self.max_three_pointers_in_match,
            'perfect_game_achieved': self.perfect_game_achieved
        }

    def from_dict(self, data):
        if 'current_level' in data:
            self.current_level = data['current_level']
        if 'campaign_completed' in data:
            self.campaign_completed = data['campaign_completed']
        if 'final_level_completed' in data:
            self.final_level_completed = data['final_level_completed']
        if 'levels' in data:
            for i, level_data in enumerate(data['levels']):
                if i < len(self.levels):
                    self.levels[i] = BasketballLevel.from_dict(level_data, self.levels[i])
        if 'elo' in data:
            self.elo = data['elo']
        if 'best_elo' in data:
            self.best_elo = data['best_elo']
        if 'matches_played' in data:
            self.matches_played = data['matches_played']
        if 'matches_won' in data:
            self.matches_won = data['matches_won']
        if 'ranked_matches_won' in data:
            self.ranked_matches_won = data['ranked_matches_won']
        if 'ranked_matches_played' in data:
            self.ranked_matches_played = data['ranked_matches_played']
        if 'cups_earned' in data:
            self.cups_earned = data['cups_earned']
            if self.cups_earned:
                self.cup_earned = True
        if 'ranked_unlocked' in data:
            self.ranked_unlocked = data['ranked_unlocked']
        if 'is_ranked_match' in data:
            self.is_ranked_match = data['is_ranked_match']
        if 'best_streak' in data:
            self.best_streak = data['best_streak']
        if 'streak_bonus_total' in data:
            self.streak_bonus_total = data['streak_bonus_total']
        if 'perfect_shots_total' in data:
            self.perfect_shots_total = data['perfect_shots_total']
        if 'max_three_pointers_in_match' in data:
            self.max_three_pointers_in_match = data['max_three_pointers_in_match']
        if 'perfect_game_achieved' in data:
            self.perfect_game_achieved = data['perfect_game_achieved']


class BasketballCampaignScreen:
    def __init__(self, campaign_manager, sound_manager=None, background_manager=None, skin_manager=None):
        self.campaign_manager = campaign_manager
        self.sound_manager = sound_manager
        self.background_manager = background_manager
        self.skin_manager = skin_manager
        self.scroll_offset = 0
        self.selected_level = 0
        self.is_ranked_mode = False
        self.scrollbar_rect = None
        self.scroll_handle_rect = None
        self.dragging_scroll = False

    def draw(self, screen):
        if self.background_manager:
            bg = self.background_manager.get_random_background()
            if bg:
                screen.blit(bg, (0, 0))
            else:
                screen.fill((45, 40, 35))
        else:
            screen.fill((45, 40, 35))

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 16)

        show_ranked = self.campaign_manager.ranked_unlocked or self.campaign_manager.campaign_completed
        if len(self.campaign_manager.levels) > 10 and self.campaign_manager.levels[10].unlocked:
            show_ranked = True

        if show_ranked and self.is_ranked_mode:
            self.draw_ranked_mode(screen)
            return

        title = font_large.render("Basketball Campaign", True, RETRO_SILVER)
        title_shadow = font_large.render("Basketball Campaign", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 21))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 20))
        subtitle = font_small.render("Path to Glory", True, RETRO_GOLD)
        subtitle_shadow = font_small.render("Path to Glory", True, BLACK)
        screen.blit(subtitle_shadow, (BASE_WIDTH // 2 - subtitle.get_width() // 2 + 1, 56))
        screen.blit(subtitle, (BASE_WIDTH // 2 - subtitle.get_width() // 2, 55))

        total_height = len(self.campaign_manager.levels[:10]) * 75
        max_scroll = max(0, total_height - (BASE_HEIGHT - 170))

        start_y = 90 - self.scroll_offset

        for i, level in enumerate(self.campaign_manager.levels[:10]):
            rect_y = start_y + i * 75
            if rect_y < 50 or rect_y > BASE_HEIGHT - 110:
                continue
            rect = pygame.Rect(20, rect_y, BASE_WIDTH - 60, 65)

            if level.completed:
                bg_color = (46, 204, 113, 200)
                border_color = RETRO_SILVER
            elif level.unlocked:
                bg_color = (155, 89, 182, 200)
                border_color = RETRO_SILVER
            else:
                bg_color = (80, 80, 80, 200)
                border_color = RETRO_GRAY

            bg_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, bg_color, bg_surf.get_rect(), 0, 10)
            screen.blit(bg_surf, rect)
            pygame.draw.rect(screen, border_color, rect, 2, 10)

            if level.badge and level.badge.earned:
                badge_x = rect.right - 40
                badge_y = rect.y + 8
                pygame.draw.rect(screen, (60, 60, 80), (badge_x - 2, badge_y - 2, 30, 30), 0, 5)
                pygame.draw.rect(screen, level.badge.color, (badge_x - 2, badge_y - 2, 30, 30), 2, 5)
                pixel_size = 3
                for px in range(8):
                    for py in range(8):
                        if level.badge.pixel_data[py][px]:
                            pixel_rect = pygame.Rect(badge_x + px * pixel_size + 2,
                                                     badge_y + py * pixel_size + 2, pixel_size, pixel_size)
                            color = level.badge.color
                            if random.random() < 0.1:
                                color = WHITE
                            pygame.draw.rect(screen, color, pixel_rect)
            else:
                badge_x = rect.right - 40
                badge_y = rect.y + 8
                pygame.draw.rect(screen, (60, 60, 80), (badge_x - 2, badge_y - 2, 28, 28), 0, 5)
                pygame.draw.rect(screen, (100, 100, 120), (badge_x - 2, badge_y - 2, 28, 28), 2, 5)
                lock_text = font_tiny.render("?", True, RETRO_GRAY)
                screen.blit(lock_text, (badge_x + 10, badge_y + 8))

            name_text = font_medium.render(f"{i + 1}. {level.name}", True, RETRO_GOLD)
            name_shadow = font_medium.render(f"{i + 1}. {level.name}", True, BLACK)
            screen.blit(name_shadow, (rect.x + 11, rect.y + 6))
            screen.blit(name_text, (rect.x + 10, rect.y + 5))

            if level.completed:
                if level.is_final:
                    stars = "Complete"
                else:
                    stars = "*" * level.stars_earned + "o" * (3 - level.stars_earned)
                stars_text = font_tiny.render(stars, True, RETRO_GOLD)
                stars_shadow = font_tiny.render(stars, True, BLACK)
                screen.blit(stars_shadow, (rect.x + 11, rect.y + 28))
                screen.blit(stars_text, (rect.x + 10, rect.y + 27))
            elif not level.unlocked:
                lock_text = font_tiny.render("Locked", True, RETRO_GRAY)
                lock_shadow = font_tiny.render("Locked", True, BLACK)
                screen.blit(lock_shadow, (rect.x + 11, rect.y + 28))
                screen.blit(lock_text, (rect.x + 10, rect.y + 27))
            else:
                ready_text = font_tiny.render("Ready", True, RETRO_GREEN)
                ready_shadow = font_tiny.render("Ready", True, BLACK)
                screen.blit(ready_shadow, (rect.x + 11, rect.y + 28))
                screen.blit(ready_text, (rect.x + 10, rect.y + 27))

        if show_ranked:
            level_11_rect = pygame.Rect(20, start_y + 10 * 75, BASE_WIDTH - 60, 65)
            glow_alpha = 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.003))
            glow_surf = pygame.Surface((level_11_rect.width + 10, level_11_rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf,
                             (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], glow_alpha // 2),
                             (5, 5, level_11_rect.width, level_11_rect.height), 0, 10)
            screen.blit(glow_surf, (level_11_rect.x - 5, level_11_rect.y - 5))
            pygame.draw.rect(screen, RETRO_PURPLE, level_11_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_GOLD, level_11_rect, 2, 10)
            level_11_text = font_medium.render("11. Ranked Basketball", True, RETRO_GOLD)
            level_11_shadow = font_medium.render("11. Ranked Basketball", True, BLACK)
            screen.blit(level_11_shadow, (level_11_rect.x + 11, level_11_rect.y + 6))
            screen.blit(level_11_text, (level_11_rect.x + 10, level_11_rect.y + 5))

            elo_text = font_small.render(f"ELO: {self.campaign_manager.elo}", True, RETRO_GOLD)
            elo_shadow = font_small.render(f"ELO: {self.campaign_manager.elo}", True, BLACK)
            screen.blit(elo_shadow, (level_11_rect.x + 11, level_11_rect.y + 28))
            screen.blit(elo_text, (level_11_rect.x + 10, level_11_rect.y + 27))

            rank_text = font_small.render(self.campaign_manager.get_current_rank(), True, RETRO_SILVER)
            rank_shadow = font_small.render(self.campaign_manager.get_current_rank(), True, BLACK)
            screen.blit(rank_shadow, (level_11_rect.right - rank_text.get_width() - 11, level_11_rect.y + 28))
            screen.blit(rank_text, (level_11_rect.right - rank_text.get_width() - 10, level_11_rect.y + 27))

            if self.campaign_manager.best_streak > 0:
                streak_text = font_tiny.render(f"Best Streak: {self.campaign_manager.best_streak}", True, RETRO_GOLD)
                streak_shadow = font_tiny.render(f"Best Streak: {self.campaign_manager.best_streak}", True, BLACK)
                screen.blit(streak_shadow, (level_11_rect.x + 11, level_11_rect.y + 44))
                screen.blit(streak_text, (level_11_rect.x + 10, level_11_rect.y + 43))

            cup_skin = None
            if self.skin_manager:
                cup_skin = self.skin_manager.get_equipped_skin("basketball", is_cup=True)

            if self.campaign_manager.cup_earned and cup_skin and cup_skin.image:
                screen.blit(cup_skin.image, (level_11_rect.right - 45, level_11_rect.y + 5))
            elif self.campaign_manager.cup_earned:
                cup_surf = pygame.Surface((35, 45), pygame.SRCALPHA)
                points = [(8, 30), (4, 20), (31, 20), (27, 30)]
                pygame.draw.polygon(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), points)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (6, 30, 23, 3), 0, 2)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (9, 33, 17, 2), 0, 1)
                screen.blit(cup_surf, (level_11_rect.right - 42, level_11_rect.y + 5))

        if max_scroll > 0:
            scroll_bg = pygame.Rect(BASE_WIDTH - 12, 80, 7, BASE_HEIGHT - 170)
            pygame.draw.rect(screen, (40, 40, 50), scroll_bg, 0, 4)

            scroll_height = max(30, (BASE_HEIGHT - 170) * (BASE_HEIGHT - 170) / total_height)
            scroll_y = 80 + (self.scroll_offset / max_scroll) * (BASE_HEIGHT - 170 - scroll_height)
            self.scroll_handle_rect = pygame.Rect(BASE_WIDTH - 14, scroll_y, 11, scroll_height)
            pygame.draw.rect(screen, RETRO_PURPLE, self.scroll_handle_rect, 0, 5)
            pygame.draw.rect(screen, RETRO_SILVER, self.scroll_handle_rect, 1, 5)
            self.scrollbar_rect = scroll_bg
        else:
            self.scroll_handle_rect = None
            self.scrollbar_rect = None

        back_rect = pygame.Rect(10, 10, 80, 30)
        pygame.draw.rect(screen, RETRO_PURPLE, back_rect, 0, 8)
        pygame.draw.rect(screen, RETRO_SILVER, back_rect, 2, 8)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow, (back_rect.x + 5, back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text, (back_rect.x + 4, back_rect.centery - back_text.get_height() // 2))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)
        return None, back_rect

    def draw_ranked_mode(self, screen):
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 16)

        search_rect = None
        back_rect = None

        back_rect = pygame.Rect(10, 10, 80, 30)
        pygame.draw.rect(screen, RETRO_PURPLE, back_rect, 0, 8)
        pygame.draw.rect(screen, RETRO_SILVER, back_rect, 2, 8)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow, (back_rect.x + 5, back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text, (back_rect.x + 4, back_rect.centery - back_text.get_height() // 2))

        title_glow = pygame.Surface((BASE_WIDTH, 60), pygame.SRCALPHA)
        glow_alpha = 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.003))
        pygame.draw.rect(title_glow, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], glow_alpha // 2),
                         (BASE_WIDTH // 2 - 150, 10, 300, 50), 0, 15)
        screen.blit(title_glow, (0, 0))

        title = font_large.render("RANKED BASKETBALL", True, RETRO_GOLD)
        title_shadow = font_large.render("RANKED BASKETBALL", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 21))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 20))

        cup_x = BASE_WIDTH - 50
        cup_y = 55
        cup_skin = None
        if self.skin_manager:
            cup_skin = self.skin_manager.get_equipped_skin("basketball", is_cup=True)

        if self.campaign_manager.cup_earned and cup_skin and cup_skin.image:
            screen.blit(cup_skin.image, (cup_x - 20, cup_y))
            cup_label = font_tiny.render("CUP", True, RETRO_GOLD)
            cup_shadow = font_tiny.render("CUP", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))
        elif self.campaign_manager.cup_earned:
            cup_surf = pygame.Surface((45, 55), pygame.SRCALPHA)
            glow_alpha = 150 + int(100 * math.sin(time.time() * 0.05))
            points = [(10, 38), (5, 24), (40, 24), (35, 38)]
            pygame.draw.polygon(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), points)
            pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (8, 38, 29, 4), 0, 2)
            pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (12, 42, 21, 3), 0, 1)
            screen.blit(cup_surf, (cup_x - 22, cup_y))
            cup_label = font_tiny.render("CUP", True, RETRO_GOLD)
            cup_shadow = font_tiny.render("CUP", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))
        else:
            if cup_skin and cup_skin.image:
                screen.blit(cup_skin.image, (cup_x - 20, cup_y))
            else:
                cup_surf = pygame.Surface((45, 55), pygame.SRCALPHA)
                points = [(10, 38), (5, 24), (40, 24), (35, 38)]
                pygame.draw.polygon(cup_surf, (DIAMOND[0], DIAMOND[1], DIAMOND[2], 80), points)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (8, 38, 29, 4), 0, 2)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (12, 42, 21, 3), 0, 1)
                screen.blit(cup_surf, (cup_x - 22, cup_y))
            cup_label = font_tiny.render("REACH 2000 ELO", True, RETRO_WHITE)
            cup_shadow = font_tiny.render("REACH 2000 ELO", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))

        elo_color = RETRO_GREEN if self.campaign_manager.elo >= 1500 else RETRO_GOLD if self.campaign_manager.elo >= 1000 else RETRO_RED
        elo_text = font_large.render(f"{self.campaign_manager.elo}", True, elo_color)
        elo_shadow = font_large.render(f"{self.campaign_manager.elo}", True, BLACK)
        screen.blit(elo_shadow, (BASE_WIDTH // 2 - elo_text.get_width() // 2 + 1, 56))
        screen.blit(elo_text, (BASE_WIDTH // 2 - elo_text.get_width() // 2, 55))
        elo_label = font_small.render("ELO", True, RETRO_GRAY)
        elo_label_shadow = font_small.render("ELO", True, BLACK)
        screen.blit(elo_label_shadow, (BASE_WIDTH // 2 - elo_label.get_width() // 2 + 1, 86))
        screen.blit(elo_label, (BASE_WIDTH // 2 - elo_label.get_width() // 2, 85))

        rank_text = font_medium.render(self.campaign_manager.get_current_rank(), True, RETRO_SILVER)
        rank_shadow = font_medium.render(self.campaign_manager.get_current_rank(), True, BLACK)
        screen.blit(rank_shadow, (BASE_WIDTH // 2 - rank_text.get_width() // 2 + 1, 105))
        screen.blit(rank_text, (BASE_WIDTH // 2 - rank_text.get_width() // 2, 104))

        bar_width = BASE_WIDTH - 60
        bar_height = 20
        bar_x = 30
        bar_y = 130
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 35, 30), bar_rect, 0, 10)
        elo_percent = min(1.0, (self.campaign_manager.elo - 800) / 1200)
        fill_width = int(bar_width * max(0, min(1, elo_percent)))
        if fill_width > 0:
            grad_colors = [BEIGE_GREEN, GREEN_YELLOW, BRONZE_GREEN, SILVER_GREEN, GOLD_GREEN, DIAMOND]
            pixel_size = 3
            for i in range(0, fill_width, pixel_size):
                progress = i / bar_width
                color_idx = min(int(progress * len(grad_colors)), len(grad_colors) - 1)
                color = grad_colors[color_idx]
                pygame.draw.rect(screen, color, (bar_x + i, bar_y + 2, pixel_size, bar_height - 4))
        pygame.draw.rect(screen, RETRO_SILVER, bar_rect, 2, 10)

        marks = [800, 1000, 1200, 1400, 1600, 1800, 2000]
        for mark in marks:
            mark_x = bar_x + ((mark - 800) / 1200) * bar_width
            if 0 <= mark_x <= bar_x + bar_width:
                pygame.draw.line(screen, RETRO_SILVER, (mark_x, bar_y - 3), (mark_x, bar_y + bar_height + 3), 2)
                mark_text = font_tiny.render(str(mark), True, RETRO_GRAY)
                mark_shadow = font_tiny.render(str(mark), True, BLACK)
                screen.blit(mark_shadow, (mark_x - mark_text.get_width() // 2 + 1, bar_y + bar_height + 5))
                screen.blit(mark_text, (mark_x - mark_text.get_width() // 2, bar_y + bar_height + 4))

        if self.campaign_manager.ranked_searching:
            dots = "." * ((pygame.time.get_ticks() // 300) % 4)
            search_text = font_medium.render(f"Searching opponent{dots}", True, RETRO_GOLD)
            search_shadow = font_medium.render(f"Searching opponent{dots}", True, BLACK)
            search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 180, 200, 50)
            pygame.draw.rect(screen, RETRO_PURPLE, search_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, search_rect, 2, 10)
            screen.blit(search_shadow, (
                search_rect.centerx - search_text.get_width() // 2 + 1,
                search_rect.centery - search_text.get_height() // 2 + 1))
            screen.blit(search_text, (
                search_rect.centerx - search_text.get_width() // 2,
                search_rect.centery - search_text.get_height() // 2))

        elif self.campaign_manager.ranked_match_ready and self.campaign_manager.ranked_match_found:
            opp_text = font_medium.render(f"OPPONENT: {self.campaign_manager.ranked_opponent}", True, RETRO_GOLD)
            opp_shadow = font_medium.render(f"OPPONENT: {self.campaign_manager.ranked_opponent}", True, BLACK)
            screen.blit(opp_shadow, (BASE_WIDTH // 2 - opp_text.get_width() // 2 + 1, 181))
            screen.blit(opp_text, (BASE_WIDTH // 2 - opp_text.get_width() // 2, 180))

            timer_seconds = self.campaign_manager.ranked_match_timer // 60
            timer_text = font_medium.render(f"Time to accept: {timer_seconds}s", True, RETRO_ORANGE)
            timer_shadow = font_medium.render(f"Time to accept: {timer_seconds}s", True, BLACK)
            screen.blit(timer_shadow, (BASE_WIDTH // 2 - timer_text.get_width() // 2 + 1, 201))
            screen.blit(timer_text, (BASE_WIDTH // 2 - timer_text.get_width() // 2, 200))

            play_rect = pygame.Rect(BASE_WIDTH // 2 - 80, 220, 160, 40)
            pygame.draw.rect(screen, RETRO_GREEN, play_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, play_rect, 2, 10)
            play_text = font_medium.render("ACCEPT FIGHT", True, RETRO_GOLD)
            play_shadow = font_medium.render("ACCEPT FIGHT", True, BLACK)
            screen.blit(play_shadow, (
                play_rect.centerx - play_text.get_width() // 2 + 1,
                play_rect.centery - play_text.get_height() // 2 + 1))
            screen.blit(play_text,
                        (play_rect.centerx - play_text.get_width() // 2,
                         play_rect.centery - play_text.get_height() // 2))
            return play_rect, back_rect

        elif self.campaign_manager.ranked_match_found and not self.campaign_manager.ranked_match_ready:
            opp_text = font_medium.render(f"OPPONENT {self.campaign_manager.ranked_opponent} LEFT", True, RETRO_RED)
            opp_shadow = font_medium.render(f"OPPONENT {self.campaign_manager.ranked_opponent} LEFT", True, BLACK)
            screen.blit(opp_shadow, (BASE_WIDTH // 2 - opp_text.get_width() // 2 + 1, 181))
            screen.blit(opp_text, (BASE_WIDTH // 2 - opp_text.get_width() // 2, 180))

            search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 220, 200, 40)
            pygame.draw.rect(screen, RETRO_GREEN, search_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, search_rect, 2, 10)
            search_text = font_medium.render("SEARCH NEW", True, RETRO_GOLD)
            search_shadow = font_medium.render("SEARCH NEW", True, BLACK)
            screen.blit(search_shadow, (
                search_rect.centerx - search_text.get_width() // 2 + 1,
                search_rect.centery - search_text.get_height() // 2 + 1))
            screen.blit(search_text, (
                search_rect.centerx - search_text.get_width() // 2,
                search_rect.centery - search_text.get_height() // 2))
            return search_rect, back_rect

        else:
            search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 180, 200, 50)
            pygame.draw.rect(screen, RETRO_GREEN, search_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, search_rect, 2, 10)
            search_text = font_medium.render("FIND OPPONENT", True, RETRO_GOLD)
            search_shadow = font_medium.render("FIND OPPONENT", True, BLACK)
            screen.blit(search_shadow, (
                search_rect.centerx - search_text.get_width() // 2 + 1,
                search_rect.centery - search_text.get_height() // 2 + 1))
            screen.blit(search_text, (
                search_rect.centerx - search_text.get_width() // 2,
                search_rect.centery - search_text.get_height() // 2))
            return search_rect, back_rect

        stats_y = 280
        stats = [
            f"Matches: {self.campaign_manager.matches_played}",
            f"Wins: {self.campaign_manager.matches_won}",
            f"Best ELO: {self.campaign_manager.best_elo}"
        ]
        if self.campaign_manager.best_streak > 0:
            stats.append(f"Best Streak: {self.campaign_manager.best_streak}")
        for i, stat in enumerate(stats):
            stat_text = font_small.render(stat, True, RETRO_GOLD)
            stat_shadow = font_small.render(stat, True, BLACK)
            screen.blit(stat_shadow, (BASE_WIDTH // 2 - stat_text.get_width() // 2 + 1, stats_y + i * 25 + 1))
            screen.blit(stat_text, (BASE_WIDTH // 2 - stat_text.get_width() // 2, stats_y + i * 25))

        if self.campaign_manager.cups_earned:
            cups_y = 360
            cups_title = font_small.render("Cups:", True, RETRO_GOLD)
            cups_title_shadow = font_small.render("Cups:", True, BLACK)
            screen.blit(cups_title_shadow, (BASE_WIDTH // 2 - cups_title.get_width() // 2 + 1, cups_y + 1))
            screen.blit(cups_title, (BASE_WIDTH // 2 - cups_title.get_width() // 2, cups_y))

            for i, cup_name in enumerate(self.campaign_manager.cups_earned):
                cup_text = font_tiny.render(f"{cup_name}", True, RETRO_GOLD)
                cup_shadow = font_tiny.render(f"{cup_name}", True, BLACK)
                screen.blit(cup_shadow,
                            (BASE_WIDTH // 2 - cup_text.get_width() // 2 + 1, cups_y + 20 + i * 20 + 1))
                screen.blit(cup_text, (BASE_WIDTH // 2 - cup_text.get_width() // 2, cups_y + 20 + i * 20))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)
        return search_rect, back_rect

    def handle_click(self, x, y):
        if self.scroll_handle_rect and self.scrollbar_rect:
            if self.scroll_handle_rect.collidepoint(x, y):
                self.dragging_scroll = True
                return None

        show_ranked = self.campaign_manager.ranked_unlocked or self.campaign_manager.campaign_completed
        if len(self.campaign_manager.levels) > 10 and self.campaign_manager.levels[10].unlocked:
            show_ranked = True

        if show_ranked and self.is_ranked_mode:
            if self.campaign_manager.ranked_match_ready and self.campaign_manager.ranked_match_found:
                play_rect = pygame.Rect(BASE_WIDTH // 2 - 80, 220, 160, 40)
                if play_rect.collidepoint(x, y):
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    return "ranked_accept"

            if not self.campaign_manager.ranked_searching and not self.campaign_manager.ranked_match_found:
                search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 180, 200, 50)
                if search_rect.collidepoint(x, y):
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    return "ranked_search"

            if self.campaign_manager.ranked_match_found and not self.campaign_manager.ranked_match_ready:
                search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 220, 200, 40)
                if search_rect.collidepoint(x, y):
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    self.campaign_manager.ranked_match_found = False
                    self.campaign_manager.ranked_opponent = "Player"
                    self.campaign_manager.start_ranked_search()
                    return None

            back_rect = pygame.Rect(10, 10, 80, 30)
            if back_rect.collidepoint(x, y):
                if self.sound_manager:
                    self.sound_manager.play_button()
                self.is_ranked_mode = False
                return None
            return None

        start_y = 90 - self.scroll_offset
        for i, level in enumerate(self.campaign_manager.levels[:10]):
            rect_y = start_y + i * 75
            if rect_y < 50 or rect_y > BASE_HEIGHT - 110:
                continue
            rect = pygame.Rect(20, rect_y, BASE_WIDTH - 60, 65)
            if rect.collidepoint(x, y) and level.unlocked and not level.completed:
                if self.sound_manager:
                    self.sound_manager.play_button()
                self.campaign_manager.current_level = i
                return level
            elif rect.collidepoint(x, y) and level.completed:
                if self.sound_manager:
                    self.sound_manager.play_sound('hit')
                return None

        if show_ranked:
            level_11_rect = pygame.Rect(20, start_y + 10 * 75, BASE_WIDTH - 60, 65)
            if level_11_rect.collidepoint(x, y) and not self.campaign_manager.levels[10].completed:
                if self.sound_manager:
                    self.sound_manager.play_button()
                self.is_ranked_mode = True
                return None
            elif level_11_rect.collidepoint(x, y) and self.campaign_manager.levels[10].completed:
                if self.sound_manager:
                    self.sound_manager.play_sound('hit')
                return None

        back_rect = pygame.Rect(10, 10, 80, 30)
        if back_rect.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            return "back"
        return None

    def handle_scroll(self, y):
        total_height = len(self.campaign_manager.levels[:10]) * 75
        max_scroll = max(0, total_height - (BASE_HEIGHT - 170))
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset + y))

    def handle_mouse_motion(self, x, y):
        if self.dragging_scroll and self.scrollbar_rect:
            total_height = len(self.campaign_manager.levels[:10]) * 75
            max_scroll = max(0, total_height - (BASE_HEIGHT - 170))
            if max_scroll > 0:
                scroll_y = y - 80 - 15
                scroll_y = max(0, min(scroll_y, BASE_HEIGHT - 170 - 30))
                self.scroll_offset = (scroll_y / (BASE_HEIGHT - 170 - 30)) * max_scroll
                self.scroll_offset = max(0, min(max_scroll, self.scroll_offset))

    def handle_mouse_up(self):
        self.dragging_scroll = False


class BasketballGame:
    def __init__(self, sound_manager=None, level=None, difficulty=0, is_ranked=False, opponent_name="CPU",
                 bird_skin=None, opponent_skin=None):
        self.sound_manager = sound_manager
        self.active = True
        self.is_ranked = is_ranked
        self.player_score = 0
        self.cpu_score = 0
        self.target_score = 21
        self.game_over = False
        self.player_won = False
        self.is_player_turn = True
        self.waiting_for_shot = False
        self.shot_result = None
        self.result_timer = 0
        self.aim_x = BASE_WIDTH // 2
        self.aim_speed = 4
        self.hoop_x = BASE_WIDTH // 2
        self.hoop_direction = 1
        self.hoop_speed = 1.5
        self.base_hoop_speed = 1.5
        self.hoop_speed_multiplier = 1.0
        self.hoop_move_range = 100
        self.hoop_min_x = BASE_WIDTH // 2 - self.hoop_move_range
        self.hoop_max_x = BASE_WIDTH // 2 + self.hoop_move_range
        self.hoop_speed_increase_timer = 0
        self.current_streak = 0
        self.max_streak = 0

        self.timing_meter_value = 0
        self.timing_meter_direction = 1
        self.timing_meter_speed = 5
        self.timing_meter_max = 100
        self.is_charging = False
        self.perfect_zone_start = 85
        self.perfect_zone_end = 95
        self.good_zone_start = 70
        self.good_zone_end = 100
        self.current_shot_position = None
        self.shot_positions = SHOT_POSITIONS.copy()
        self.ball = None
        self.ball_trajectory = []
        self.is_shooting = False
        self.shot_timer = 0
        self.trajectory_points = []
        self.trajectory_index = 0
        self.ai_aim_x = BASE_WIDTH // 2
        self.ai_timing_value = 0
        self.ai_is_charging = False
        self.ai_charge_timer = 0
        self.particles = []
        self.court_animation = 0
        self.ball_rotation = 0
        self.player_animation = 0
        self.cpu_animation = 0
        self.player_throw_animation = 0
        self.cpu_throw_animation = 0
        self.player_x = BASE_WIDTH // 2
        self.player_y = BASE_HEIGHT - 80
        self.cpu_x = BASE_WIDTH // 2
        self.cpu_y = 80
        self.level = level
        self.level_completed = False
        self.stars_earned = 0
        self.shot_result_message = ""
        self.shot_result_color = WHITE
        self.perfect_releases = 0
        self.bird_skin = bird_skin
        self.opponent_skin = opponent_skin
        self.total_shots_taken = 0
        self.total_misses = 0
        self.three_pointers_scored = 0
        self.perfect_shots_scored = 0
        self.shots_taken_in_game = 0
        self.misses_in_game = 0
        self.three_pointers_in_game = 0
        self.perfect_shots_in_game = 0
        court_colors = [(180, 150, 100), (160, 140, 90), (200, 180, 140), (170, 145, 95), (190, 165, 115)]
        self.court_color = random.choice(court_colors)
        if level:
            self.opponent_name = level.opponent_name
            self.target_score = level.target_score
            self.ai_difficulty = level.difficulty
            self.hoop_speed = 1.0 + difficulty * 0.3
            self.base_hoop_speed = self.hoop_speed
            self.is_final = level.is_final
        else:
            self.opponent_name = opponent_name
            self.target_score = 21
            self.ai_difficulty = difficulty
            self.hoop_speed = 1.5
            self.base_hoop_speed = 1.5
            self.is_final = False
        self.rim_y = 200
        self.rim_radius = 12
        self.backboard_width = 40
        self.backboard_height = 5
        self.select_random_shot_position()
        self.font_small = pygame.font.Font(None, 18)
        self.font_medium = pygame.font.Font(None, 26)
        self.font_large = pygame.font.Font(None, 34)
        self.font_title = pygame.font.Font(None, 24)
        self.reset_ball()

    def draw_player_bird(self, screen, x, y, is_player=True, idle_anim=0, throw_anim=0, skin=None):
        use_skin = skin if skin is not None else (self.bird_skin if is_player else self.opponent_skin)

        if use_skin is not None and hasattr(use_skin, 'image') and use_skin.image is not None:
            rot = math.sin(idle_anim * 2) * 3
            if is_player:
                rot += throw_anim * 10
            rotated = pygame.transform.rotate(use_skin.image, rot)

            if throw_anim > 0:
                glow_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
                glow_alpha = int(150 * throw_anim)
                pygame.draw.circle(glow_surf, (210, 180, 120, glow_alpha), (35, 35), 35)
                screen.blit(glow_surf, (int(x - 35), int(y - 35)))

            screen.blit(rotated, (int(x - rotated.get_width() // 2), int(y - rotated.get_height() // 2)))

            if throw_anim > 0:
                ball_x = x + 20 + throw_anim * 20
                ball_y = y - 20 - throw_anim * 10
                self.draw_stylish_ball(screen, ball_x, ball_y, 8)
            return

        bird_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        primary_color = (100, 150, 200) if is_player else (200, 80, 60)
        secondary_color = (80, 120, 160) if is_player else (160, 60, 40)
        jersey_color = (200, 80, 60) if is_player else (100, 150, 200)
        throw_offset = throw_anim * 30
        for i in range(15, 0, -1):
            t = i / 15
            color = (int(primary_color[0] * t + secondary_color[0] * (1 - t)),
                     int(primary_color[1] * t + secondary_color[1] * (1 - t)),
                     int(primary_color[2] * t + secondary_color[2] * (1 - t)))
            pygame.draw.circle(bird_surf, color, (30, 30), i)
        jersey_rect = pygame.Rect(18, 30, 24, 18)
        pygame.draw.rect(bird_surf, jersey_color, jersey_rect, 0, 3)
        font = pygame.font.Font(None, 12)
        number = font.render("23" if is_player else "AI", True, WHITE)
        bird_surf.blit(number, (23, 33))
        pygame.draw.circle(bird_surf, WHITE, (36, 24), 5)
        pygame.draw.circle(bird_surf, BLACK, (37, 24), 3)
        pygame.draw.circle(bird_surf, WHITE, (38, 23), 1)
        brow_offset = -throw_anim * 2
        pygame.draw.line(bird_surf, BLACK, (32, 20 + brow_offset), (40, 19 + brow_offset), 2)
        if throw_anim > 0:
            beak_points = [(42, 25), (50 + throw_anim * 5, 25), (42, 29)]
        else:
            beak_points = [(42, 25), (48, 25), (42, 29)]
        pygame.draw.polygon(bird_surf, (200, 160, 80), beak_points)
        headband_rect = pygame.Rect(20, 14, 24, 4)
        pygame.draw.rect(bird_surf, (210, 180, 120) if is_player else (200, 0, 0), headband_rect, 0, 2)
        if throw_anim > 0:
            wing_points = [(8, 32), (5 + throw_offset, 25), (15, 40)]
        else:
            wing_y = 30 + math.sin(idle_anim * 3) * 3
            wing_points = [(10, wing_y), (22, wing_y + 5), (15, wing_y + 10)]
        pygame.draw.polygon(bird_surf, secondary_color, wing_points)
        wing2_y = 32 + math.sin(idle_anim * 2) * 2
        wing2_points = [(45, wing2_y), (52, wing2_y + 3), (48, wing2_y + 8)]
        pygame.draw.polygon(bird_surf, secondary_color, wing2_points)
        if throw_anim > 0:
            ball_x = 5 + throw_offset
            ball_y = 25
        else:
            ball_x = 50
            ball_y = 32
        pygame.draw.circle(bird_surf, BASKETBALL_ORANGE, (ball_x, ball_y), 7)
        pygame.draw.line(bird_surf, BLACK, (ball_x - 4, ball_y), (ball_x + 4, ball_y), 1)
        pygame.draw.line(bird_surf, BLACK, (ball_x, ball_y - 4), (ball_x, ball_y + 4), 1)
        leg_offset = math.sin(idle_anim * 4) * 2
        pygame.draw.line(bird_surf, ORANGE, (25, 48), (22, 55 + leg_offset), 2)
        pygame.draw.line(bird_surf, ORANGE, (35, 48), (38, 55 + leg_offset), 2)
        pygame.draw.circle(bird_surf, ORANGE, (22, 55 + leg_offset), 3)
        pygame.draw.circle(bird_surf, ORANGE, (38, 55 + leg_offset), 3)
        screen.blit(bird_surf, (int(x - 30), int(y - 30)))

    def draw_stylish_ball(self, screen, x, y, size=10):
        pygame.draw.circle(screen, (50, 50, 50, 100), (int(x) + 3, int(y) + 3), size)
        pygame.draw.circle(screen, BASKETBALL_ORANGE, (int(x), int(y)), size)
        for i in range(3):
            highlight_size = size - i * 2
            if highlight_size > 0:
                pygame.draw.circle(screen, (255, 200, 100), (int(x) - 1, int(y) - 1), highlight_size, 1)
        rot = self.ball_rotation
        pygame.draw.line(screen, BLACK, (int(x) - size + 2, int(y)), (int(x) + size - 2, int(y)), 2)
        pygame.draw.line(screen, BLACK, (int(x), int(y) - size + 2), (int(x), int(y) + size - 2), 2)
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle + rot * 30)
            dx = math.cos(rad) * size * 0.6
            dy = math.sin(rad) * size * 0.6
            pygame.draw.arc(screen, BLACK, (int(x) - size + 2, int(y) - size + 2, size * 2 - 4, size * 2 - 4),
                            rad - 0.5, rad + 0.5, 1)
        shine_x = int(x) - size // 2
        shine_y = int(y) - size // 2
        pygame.draw.circle(screen, (255, 255, 255, 150), (shine_x, shine_y), size // 3)

    def draw_court(self, screen):
        for y in range(BASE_HEIGHT):
            t = y / BASE_HEIGHT
            r = int(self.court_color[0] * (1 - t) + self.court_color[0] * 0.7 * t)
            g = int(self.court_color[1] * (1 - t) + self.court_color[1] * 0.7 * t)
            b = int(self.court_color[2] * (1 - t) + self.court_color[2] * 0.7 * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (BASE_WIDTH, y))
        line_color = (210, 180, 120)
        glow_alpha = 50 + math.sin(self.court_animation * 2) * 30
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (210, 180, 120, int(glow_alpha)), (60, 60), 60)
        screen.blit(glow_surf, (BASE_WIDTH // 2 - 60, BASE_HEIGHT // 2 - 60))
        pygame.draw.circle(screen, line_color, (BASE_WIDTH // 2, BASE_HEIGHT // 2), 50, 3)
        pygame.draw.line(screen, line_color, (0, BASE_HEIGHT // 2), (BASE_WIDTH, BASE_HEIGHT // 2), 3)
        three_arc = pygame.Rect(BASE_WIDTH // 2 - 100, self.rim_y + 20, 200, 200)
        pygame.draw.arc(screen, line_color, three_arc, math.radians(0), math.radians(180), 3)
        pygame.draw.line(screen, line_color, (BASE_WIDTH // 2 - 60, self.rim_y + 70),
                         (BASE_WIDTH // 2 + 60, self.rim_y + 70), 3)
        pygame.draw.line(screen, line_color, (BASE_WIDTH // 2 - 50, self.rim_y + 70),
                         (BASE_WIDTH // 2 - 50, BASE_HEIGHT), 3)
        pygame.draw.line(screen, line_color, (BASE_WIDTH // 2 + 50, self.rim_y + 70),
                         (BASE_WIDTH // 2 + 50, BASE_HEIGHT), 3)
        backboard_rect = pygame.Rect(self.hoop_x - self.backboard_width // 2, self.rim_y - 20,
                                     self.backboard_width, self.backboard_height)
        backboard_surf = pygame.Surface((backboard_rect.width, backboard_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(backboard_surf, (150, 200, 255, 100), backboard_surf.get_rect(), 0, 2)
        pygame.draw.rect(backboard_surf, WHITE, backboard_surf.get_rect(), 2, 2)
        screen.blit(backboard_surf, backboard_rect)
        rim_glow = pygame.Surface((self.rim_radius * 4, self.rim_radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(rim_glow, (200, 140, 60, 100), (self.rim_radius * 2, self.rim_radius * 2),
                           self.rim_radius + 5)
        screen.blit(rim_glow, (self.hoop_x - self.rim_radius * 2, self.rim_y - self.rim_radius * 2))
        rim_rect = pygame.Rect(self.hoop_x - self.rim_radius, self.rim_y - self.rim_radius // 2,
                               self.rim_radius * 2, self.rim_radius)
        pygame.draw.ellipse(screen, (200, 140, 60), rim_rect, 3)
        pygame.draw.ellipse(screen, (255, 200, 100), rim_rect, 1)
        pygame.draw.circle(screen, (200, 100, 50), (self.hoop_x, self.rim_y), 5)
        net_offset = math.sin(self.court_animation * 5) * 2
        net_points = []
        for i in range(8):
            angle = math.radians(i * 45)
            x = self.hoop_x + math.cos(angle) * (self.rim_radius - 2)
            y = self.rim_y + 3 + net_offset * (i / 8)
            net_points.append((x, y))
        for i in range(len(net_points)):
            next_i = (i + 1) % len(net_points)
            pygame.draw.line(screen, (200, 200, 200), net_points[i], net_points[next_i], 2)
            pygame.draw.line(screen, (200, 200, 200), net_points[i],
                             (self.hoop_x, self.rim_y + 15 + net_offset), 2)
        for x in range(int(self.hoop_min_x), int(self.hoop_max_x) + 1, 15):
            if x % 30 < 15:
                pygame.draw.circle(screen, (255, 100, 100, 100), (x, self.rim_y + 15), 2)
        if self.current_shot_position and not self.is_shooting:
            pos_x = self.current_shot_position.x
            pos_y = self.current_shot_position.y
            glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 200, 255, 100), (20, 20), 20)
            screen.blit(glow_surf, (pos_x - 20, pos_y - 20))
            pygame.draw.circle(screen, (100, 200, 255), (pos_x, pos_y), 15, 3)
            pygame.draw.circle(screen, (100, 200, 255, 100), (pos_x, pos_y), 12)
            font = pygame.font.Font(None, 16)
            label = font.render(self.current_shot_position.name, True, RETRO_GOLD)
            label_shadow = font.render(self.current_shot_position.name, True, BLACK)
            label_bg = pygame.Surface((label.get_width() + 8, label.get_height() + 4), pygame.SRCALPHA)
            pygame.draw.rect(label_bg, (0, 0, 0, 200), label_bg.get_rect(), 0, 4)
            screen.blit(label_bg, (pos_x - label.get_width() // 2 - 4, pos_y - 25))
            screen.blit(label_shadow, (pos_x - label.get_width() // 2 + 1, pos_y - 23 + 1))
            screen.blit(label, (pos_x - label.get_width() // 2, pos_y - 23))
            points_text = font.render(f"{self.current_shot_position.points} PTS", True, RETRO_GOLD)
            points_shadow = font.render(f"{self.current_shot_position.points} PTS", True, BLACK)
            points_bg = pygame.Surface((points_text.get_width() + 6, points_text.get_height() + 2),
                                       pygame.SRCALPHA)
            pygame.draw.rect(points_bg, (0, 0, 0, 180), points_bg.get_rect(), 0, 3)
            screen.blit(points_bg, (pos_x - points_text.get_width() // 2 - 3, pos_y + 8))
            screen.blit(points_shadow, (pos_x - points_text.get_width() // 2 + 1, pos_y + 10 + 1))
            screen.blit(points_text, (pos_x - points_text.get_width() // 2, pos_y + 10))
        if self.current_streak >= 2:
            streak_text = self.font_small.render(f"Streak: {self.current_streak}", True, RETRO_ORANGE)
            streak_shadow = self.font_small.render(f"Streak: {self.current_streak}", True, BLACK)
            screen.blit(streak_shadow,
                        (BASE_WIDTH // 2 - streak_text.get_width() // 2 + 1, self.rim_y - 45))
            screen.blit(streak_text, (BASE_WIDTH // 2 - streak_text.get_width() // 2, self.rim_y - 46))

    def draw_aim_system(self, screen):
        if not self.is_player_turn or self.game_over or self.is_shooting or self.waiting_for_shot:
            return
        if self.hoop_speed_multiplier > 1.0:
            speed_text = self.font_small.render(f"HOOP SPEED x{self.hoop_speed_multiplier:.1f}", True,
                                                RETRO_ORANGE)
            speed_shadow = self.font_small.render(f"HOOP SPEED x{self.hoop_speed_multiplier:.1f}", True, BLACK)
            screen.blit(speed_shadow, (BASE_WIDTH // 2 - speed_text.get_width() // 2 + 1, self.rim_y - 29))
            screen.blit(speed_text, (BASE_WIDTH // 2 - speed_text.get_width() // 2, self.rim_y - 30))
        start_x = self.ball["x"] if self.ball else BASE_WIDTH // 2
        start_y = self.ball["y"] if self.ball else BASE_HEIGHT - 100
        target_x = self.aim_x
        target_y = self.rim_y + 5
        preview_points = self.calculate_trajectory(start_x, start_y, target_x, target_y)
        for i in range(len(preview_points) - 1):
            if self.is_charging and self.timing_meter_value >= self.perfect_zone_start:
                color = (100, 255, 100)
            elif self.is_charging:
                color = (255, 255, 100)
            else:
                color = (100, 200, 255)
            pygame.draw.line(screen, color, preview_points[i], preview_points[i + 1], 3)
        cursor_x = int(self.aim_x)
        cursor_y = int(self.rim_y + 5)
        pygame.draw.circle(screen, (255, 100, 100, 100), (cursor_x, cursor_y), 15, 2)
        pygame.draw.circle(screen, (255, 100, 100), (cursor_x, cursor_y), 10, 2)
        pygame.draw.line(screen, (255, 100, 100), (cursor_x - 20, cursor_y), (cursor_x - 8, cursor_y), 2)
        pygame.draw.line(screen, (255, 100, 100), (cursor_x + 8, cursor_y), (cursor_x + 20, cursor_y), 2)
        pygame.draw.line(screen, (255, 100, 100), (cursor_x, cursor_y - 20), (cursor_x, cursor_y - 8), 2)
        pygame.draw.line(screen, (255, 100, 100), (cursor_x, cursor_y + 8), (cursor_x, cursor_y + 20), 2)
        meter_width = 240
        meter_height = 30
        meter_x = BASE_WIDTH // 2 - meter_width // 2
        meter_y = BASE_HEIGHT - 80
        self.draw_shadow(screen, pygame.Rect(meter_x, meter_y, meter_width, meter_height))
        self.draw_rounded_rect(screen, (30, 30, 50),
                               pygame.Rect(meter_x, meter_y, meter_width, meter_height), 15, 2, RETRO_GOLD)
        perfect_start_x = meter_x + (self.perfect_zone_start / self.timing_meter_max) * meter_width
        perfect_end_x = meter_x + (self.perfect_zone_end / self.timing_meter_max) * meter_width
        pygame.draw.rect(screen, (0, 200, 0),
                         (perfect_start_x + 2, meter_y + 3,
                          perfect_end_x - perfect_start_x - 4, meter_height - 6), 0, 10)
        if self.is_charging:
            indicator_x = meter_x + (self.timing_meter_value / self.timing_meter_max) * meter_width
            pygame.draw.line(screen, WHITE, (indicator_x, meter_y - 5),
                             (indicator_x, meter_y + meter_height + 5), 4)
            pygame.draw.circle(screen, WHITE, (int(indicator_x), meter_y + meter_height // 2), 10)
            if self.timing_meter_value >= self.perfect_zone_start and self.timing_meter_value <= self.perfect_zone_end:
                for _ in range(2):
                    self.particles.append(Particle(indicator_x, meter_y + meter_height // 2, GREEN))
        if self.is_charging:
            label = "Release"
            label_color = GREEN if self.timing_meter_value >= self.perfect_zone_start and self.timing_meter_value <= self.perfect_zone_end else RETRO_YELLOW
        else:
            label = "Timing"
            label_color = RETRO_GRAY
        label_text = self.font_medium.render(label, True, label_color)
        label_shadow = self.font_medium.render(label, True, BLACK)
        label_bg = pygame.Surface((label_text.get_width() + 10, 25), pygame.SRCALPHA)
        pygame.draw.rect(label_bg, (0, 0, 0, 180), label_bg.get_rect(), 0, 8)
        screen.blit(label_bg, (meter_x + meter_width // 2 - label_text.get_width() // 2 - 5, meter_y - 28))
        screen.blit(label_shadow,
                    (meter_x + meter_width // 2 - label_text.get_width() // 2 + 1, meter_y - 24))
        screen.blit(label_text, (meter_x + meter_width // 2 - label_text.get_width() // 2, meter_y - 25))

    def draw_hud(self, screen):
        player_frame = pygame.Rect(15, 10, 90, 65)
        self.draw_shadow(screen, player_frame)
        self.draw_rounded_rect(screen, (100, 150, 200, 200), player_frame, 10, 2, RETRO_SILVER)
        player_label = self.font_small.render("YOU", True, RETRO_GOLD)
        player_label_shadow = self.font_small.render("YOU", True, BLACK)
        screen.blit(player_label_shadow, (
            player_frame.x + player_frame.width // 2 - player_label.get_width() // 2 + 1, player_frame.y + 9))
        screen.blit(player_label,
                    (player_frame.x + player_frame.width // 2 - player_label.get_width() // 2, player_frame.y + 8))
        player_score_color = RETRO_GREEN if self.is_player_turn and not self.game_over else WHITE
        player_score_text = self.font_large.render(str(self.player_score), True, player_score_color)
        player_score_shadow = self.font_large.render(str(self.player_score), True, BLACK)
        screen.blit(player_score_shadow,
                    (player_frame.x + player_frame.width // 2 - player_score_text.get_width() // 2 + 1,
                     player_frame.y + 29))
        screen.blit(player_score_text,
                    (player_frame.x + player_frame.width // 2 - player_score_text.get_width() // 2, player_frame.y + 28))
        cpu_frame = pygame.Rect(BASE_WIDTH - 105, 10, 90, 65)
        self.draw_shadow(screen, cpu_frame)
        self.draw_rounded_rect(screen, (200, 80, 60, 200), cpu_frame, 10, 2, RETRO_SILVER)
        cpu_label = self.font_small.render(self.opponent_name[:6], True, RETRO_GOLD)
        cpu_label_shadow = self.font_small.render(self.opponent_name[:6], True, BLACK)
        screen.blit(cpu_label_shadow, (
            cpu_frame.x + cpu_frame.width // 2 - cpu_label.get_width() // 2 + 1, cpu_frame.y + 9))
        screen.blit(cpu_label,
                    (cpu_frame.x + cpu_frame.width // 2 - cpu_label.get_width() // 2, cpu_frame.y + 8))
        cpu_score_color = RETRO_RED if not self.is_player_turn and not self.game_over else WHITE
        cpu_score_text = self.font_large.render(str(self.cpu_score), True, cpu_score_color)
        cpu_score_shadow = self.font_large.render(str(self.cpu_score), True, BLACK)
        screen.blit(cpu_score_shadow, (cpu_frame.x + cpu_frame.width // 2 - cpu_score_text.get_width() // 2 + 1,
                                       cpu_frame.y + 29))
        screen.blit(cpu_score_text,
                    (cpu_frame.x + cpu_frame.width // 2 - cpu_score_text.get_width() // 2, cpu_frame.y + 28))
        vs_frame = pygame.Rect(BASE_WIDTH // 2 - 30, 15, 60, 30)
        self.draw_rounded_rect(screen, (0, 0, 0, 200), vs_frame, 8, 1, RETRO_GOLD)
        vs_text = self.font_small.render("VS", True, RETRO_GOLD)
        vs_shadow = self.font_small.render("VS", True, BLACK)
        screen.blit(vs_shadow, (BASE_WIDTH // 2 - vs_text.get_width() // 2 + 1, 24))
        screen.blit(vs_text, (BASE_WIDTH // 2 - vs_text.get_width() // 2, 23))
        target_frame = pygame.Rect(BASE_WIDTH // 2 - 60, 50, 120, 22)
        self.draw_rounded_rect(screen, (0, 0, 0, 180), target_frame, 8, 1, RETRO_GOLD)
        target_text = self.font_small.render(f"FIRST TO {self.target_score}", True, RETRO_GOLD)
        target_shadow = self.font_small.render(f"FIRST TO {self.target_score}", True, BLACK)
        screen.blit(target_shadow, (BASE_WIDTH // 2 - target_text.get_width() // 2 + 1, 55))
        screen.blit(target_text, (BASE_WIDTH // 2 - target_text.get_width() // 2, 54))
        if self.ai_difficulty >= 4:
            diff_text = "HARD"
            diff_color = RETRO_RED
        elif self.ai_difficulty >= 2:
            diff_text = "NORMAL"
            diff_color = RETRO_YELLOW
        else:
            diff_text = "EASY"
            diff_color = RETRO_GREEN
        diff_frame = pygame.Rect(BASE_WIDTH // 2 - 40, 75, 80, 20)
        self.draw_rounded_rect(screen, (0, 0, 0, 180), diff_frame, 6, 1, diff_color)
        diff_surf = self.font_small.render(diff_text, True, diff_color)
        diff_shadow = self.font_small.render(diff_text, True, BLACK)
        screen.blit(diff_shadow, (BASE_WIDTH // 2 - diff_surf.get_width() // 2 + 1, 79))
        screen.blit(diff_surf, (BASE_WIDTH // 2 - diff_surf.get_width() // 2, 78))
        speed_frame = pygame.Rect(BASE_WIDTH // 2 - 50, 105, 100, 18)
        self.draw_rounded_rect(screen, (0, 0, 0, 160), speed_frame, 6, 1, RETRO_ORANGE)
        speed_text = self.font_small.render(f"HOOP: {self.hoop_speed:.1f}", True, RETRO_ORANGE)
        speed_shadow = self.font_small.render(f"HOOP: {self.hoop_speed:.1f}", True, BLACK)
        screen.blit(speed_shadow, (BASE_WIDTH // 2 - speed_text.get_width() // 2 + 1, 108))
        screen.blit(speed_text, (BASE_WIDTH // 2 - speed_text.get_width() // 2, 107))
        version_text = self.font_small.render(f"v{GAME_VERSION}", True, RETRO_GRAY)
        version_shadow = self.font_small.render(f"v{GAME_VERSION}", True, BLACK)
        screen.blit(version_shadow, (BASE_WIDTH - version_text.get_width() - 9, BASE_HEIGHT - 24))
        screen.blit(version_text, (BASE_WIDTH - version_text.get_width() - 10, BASE_HEIGHT - 25))
        if control_manager.control_type == ControlType.GAMEPAD:
            indicator = "Gamepad"
            indicator_color = RETRO_BLUE
        elif control_manager.control_type == ControlType.TOUCH:
            indicator = "Touch"
            indicator_color = RETRO_GREEN
        else:
            indicator = "Keyboard"
            indicator_color = RETRO_YELLOW
        indicator_text = self.font_small.render(indicator, True, indicator_color)
        indicator_shadow = self.font_small.render(indicator, True, BLACK)
        screen.blit(indicator_shadow, (BASE_WIDTH - indicator_text.get_width() - 9, 6))
        screen.blit(indicator_text, (BASE_WIDTH - indicator_text.get_width() - 10, 5))

    def draw_rounded_rect(self, screen, color, rect, radius=10, border=0, border_color=None):
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, surf.get_rect(), 0, radius)
        if border > 0 and border_color:
            pygame.draw.rect(surf, border_color, surf.get_rect(), border, radius)
        screen.blit(surf, rect)

    def draw_shadow(self, screen, rect, shadow_size=3):
        shadow_rect = rect.copy()
        shadow_rect.x += shadow_size
        shadow_rect.y += shadow_size
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), 0, 10)
        screen.blit(shadow_surf, shadow_rect)

    def calculate_trajectory(self, start_x, start_y, target_x, target_y):
        points = []
        distance = abs(target_x - start_x)
        arc_height = 80 + distance * 0.3
        arc_height = min(120, arc_height)
        mid_x = (start_x + target_x) / 2
        mid_y = min(start_y, target_y) - arc_height
        steps = 40
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * mid_x + t ** 2 * target_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * mid_y + t ** 2 * target_y
            points.append((int(x), int(y)))
        return points

    def draw(self, screen):
        self.draw_court(screen)
        for i, (tx, ty) in enumerate(self.ball_trajectory):
            alpha = int(100 * (i / len(self.ball_trajectory))) if self.ball_trajectory else 100
            size = 4 + i // 3
            pygame.draw.circle(screen, (255, 140, 50, alpha), (int(tx), int(ty)), size)
        if self.ball:
            self.draw_stylish_ball(screen, self.ball["x"], self.ball["y"], 10)
        for particle in self.particles:
            particle.draw(screen)
        self.draw_player_bird(screen, self.player_x, self.player_y, True,
                              self.player_animation, self.player_throw_animation if self.is_player_turn else 0,
                              self.bird_skin)
        self.draw_player_bird(screen, self.cpu_x, self.cpu_y, False,
                              self.cpu_animation, self.cpu_throw_animation if not self.is_player_turn else 0,
                              self.opponent_skin)
        self.draw_aim_system(screen)
        self.draw_hud(screen)
        if self.result_timer > 0 and hasattr(self, 'shot_result_message'):
            scale = 1 + math.sin(self.result_timer * 0.2) * 0.1
            msg_surf = self.font_medium.render(self.shot_result_message, True, self.shot_result_color)
            msg_surf = pygame.transform.scale(msg_surf,
                                              (int(msg_surf.get_width() * scale), int(msg_surf.get_height() * scale)))
            msg_bg = pygame.Surface((msg_surf.get_width() + 40, 50), pygame.SRCALPHA)
            pygame.draw.rect(msg_bg, (0, 0, 0, 220), msg_bg.get_rect(), 0, 15)
            pygame.draw.rect(msg_bg, self.shot_result_color, msg_bg.get_rect(), 3, 15)
            screen.blit(msg_bg, (BASE_WIDTH // 2 - msg_surf.get_width() // 2 - 20, BASE_HEIGHT // 2 - 75))
            screen.blit(msg_surf, (BASE_WIDTH // 2 - msg_surf.get_width() // 2, BASE_HEIGHT // 2 - 65))
            if hasattr(self, 'shot_result') and self.shot_result and self.shot_result["made"]:
                points_text = self.font_small.render(f"+{self.shot_result['points']} PTS", True, RETRO_GOLD)
                points_shadow = self.font_small.render(f"+{self.shot_result['points']} PTS", True, BLACK)
                screen.blit(points_shadow,
                            (BASE_WIDTH // 2 - points_text.get_width() // 2 + 1, BASE_HEIGHT // 2 - 34))
                screen.blit(points_text, (BASE_WIDTH // 2 - points_text.get_width() // 2, BASE_HEIGHT // 2 - 35))
        if not self.game_over and self.result_timer == 0 and not self.is_shooting:
            turn_text = "YOUR TURN" if self.is_player_turn else "AI TURN"
            turn_color = RETRO_GREEN if self.is_player_turn else RETRO_RED
            pulse = math.sin(self.court_animation * 5) * 3
            turn_surf = self.font_medium.render(turn_text, True, turn_color)
            turn_shadow = self.font_medium.render(turn_text, True, BLACK)
            turn_bg = pygame.Surface((turn_surf.get_width() + 20, 35), pygame.SRCALPHA)
            pygame.draw.rect(turn_bg, (0, 0, 0, 200), turn_bg.get_rect(), 0, 10)
            pygame.draw.rect(turn_bg, turn_color, turn_bg.get_rect(), 2, 10)
            screen.blit(turn_bg, (10 + pulse, 10))
            screen.blit(turn_shadow, (21 + pulse, 19))
            screen.blit(turn_surf, (20 + pulse, 18))
        if self.current_shot_position and not self.is_shooting and self.result_timer == 0:
            pos_info = self.font_small.render(
                f"{self.current_shot_position.name}  {self.current_shot_position.points}PTS", True,
                RETRO_YELLOW)
            pos_info_shadow = self.font_small.render(
                f"{self.current_shot_position.name}  {self.current_shot_position.points}PTS", True, BLACK)
            pos_bg = pygame.Surface((pos_info.get_width() + 15, 25), pygame.SRCALPHA)
            pygame.draw.rect(pos_bg, (0, 0, 0, 180), pos_bg.get_rect(), 0, 8)
            pygame.draw.rect(pos_bg, RETRO_YELLOW, pos_bg.get_rect(), 1, 8)
            screen.blit(pos_bg, (BASE_WIDTH - pos_info.get_width() - 20, 15))
            screen.blit(pos_info_shadow, (BASE_WIDTH - pos_info.get_width() - 14, 21))
            screen.blit(pos_info, (BASE_WIDTH - pos_info.get_width() - 15, 20))

    def update_hoop_position(self):
        if not self.is_shooting and not self.waiting_for_shot:
            self.hoop_x += self.hoop_direction * self.hoop_speed
            if self.hoop_x >= self.hoop_max_x:
                self.hoop_x = self.hoop_max_x
                self.hoop_direction = -1
            elif self.hoop_x <= self.hoop_min_x:
                self.hoop_x = self.hoop_min_x
                self.hoop_direction = 1

        if self.hoop_speed_increase_timer > 0:
            self.hoop_speed_increase_timer -= 1
            if self.hoop_speed_increase_timer <= 0:
                self.reset_hoop_speed()
        self.player_animation += 0.1
        self.cpu_animation += 0.1
        self.ball_rotation += 0.3
        if self.player_throw_animation > 0:
            self.player_throw_animation -= 0.1
        if self.cpu_throw_animation > 0:
            self.cpu_throw_animation -= 0.1

    def update_timing_meter(self):
        if self.is_charging and not self.is_shooting and not self.waiting_for_shot:
            self.timing_meter_value += self.timing_meter_direction * self.timing_meter_speed
            if self.timing_meter_value >= self.timing_meter_max:
                self.timing_meter_value = self.timing_meter_max
                self.timing_meter_direction = -1
            elif self.timing_meter_value <= 0:
                self.timing_meter_value = 0
                self.timing_meter_direction = 1

    def select_random_shot_position(self):
        if self.shot_positions:
            self.current_shot_position = random.choice(self.shot_positions)
        else:
            self.current_shot_position = SHOT_POSITIONS[0]
        self.teleport_bird_to_position()

    def teleport_bird_to_position(self):
        if self.is_player_turn:
            if self.current_shot_position:
                self.player_x = self.current_shot_position.x
                self.player_y = self.current_shot_position.y - 20
            else:
                self.player_x = BASE_WIDTH // 2
                self.player_y = BASE_HEIGHT - 80
        else:
            if self.current_shot_position:
                self.cpu_x = self.current_shot_position.x
                self.cpu_y = self.current_shot_position.y - 20
            else:
                self.cpu_x = BASE_WIDTH // 2
                self.cpu_y = 80

    def return_bird_to_home(self):
        if self.is_player_turn:
            self.player_x = BASE_WIDTH // 2
            self.player_y = BASE_HEIGHT - 80
        else:
            self.cpu_x = BASE_WIDTH // 2
            self.cpu_y = 80

    def reset_ball(self):
        if self.current_shot_position:
            start_x = self.current_shot_position.x
            start_y = self.current_shot_position.y
        else:
            start_x = BASE_WIDTH // 2
            start_y = BASE_HEIGHT - 100
        self.ball = {"x": start_x, "y": start_y, "active": False}
        self.ball_trajectory = []
        self.trajectory_points = []
        self.trajectory_index = 0

    def start_shot(self, aim_x, timing_value):
        if self.is_shooting:
            return
        if self.is_player_turn:
            self.player_throw_animation = 1.0
        else:
            self.cpu_throw_animation = 1.0
        self.is_shooting = True
        self.shot_timer = 0
        start_x = self.ball["x"]
        start_y = self.ball["y"]
        target_x = aim_x
        target_y = self.rim_y + 5
        self.trajectory_points = self.calculate_trajectory(start_x, start_y, target_x, target_y)
        self.trajectory_index = 0
        aim_distance = abs(aim_x - self.hoop_x)
        max_distance = 40
        aim_accuracy = max(0, 1.0 - (aim_distance / max_distance))
        if timing_value >= self.perfect_zone_start and timing_value <= self.perfect_zone_end:
            timing_multiplier = 1.0
            self.shot_quality = "perfect"
            self.perfect_releases += 1
        elif timing_value >= self.good_zone_start and timing_value <= self.good_zone_end:
            timing_multiplier = 0.8
            self.shot_quality = "good"
        else:
            timing_multiplier = 0.4
            self.shot_quality = "bad"
        make_chance = aim_accuracy * timing_multiplier
        if self.ai_difficulty >= 4:
            make_chance *= 1.1
        elif self.ai_difficulty <= 1:
            make_chance *= 0.9
        make_chance = min(0.95, max(0.05, make_chance))
        if self.is_final:
            make_chance = 0.5
        self.will_make_shot = random.random() < make_chance
        if self.is_player_turn:
            self.shots_taken_in_game += 1
            self.total_shots_taken += 1
        for _ in range(15):
            self.particles.append(Particle(start_x, start_y, BASKETBALL_ORANGE))

    def update_shot(self):
        if not self.is_shooting:
            return
        if self.trajectory_index < len(self.trajectory_points):
            point = self.trajectory_points[self.trajectory_index]
            self.ball["x"] = point[0]
            self.ball["y"] = point[1]
            self.ball_trajectory.append((self.ball["x"], self.ball["y"]))
            if len(self.ball_trajectory) > 15:
                self.ball_trajectory.pop(0)
            self.trajectory_index += 1
        else:
            self.is_shooting = False
            if self.trajectory_points:
                last_point = self.trajectory_points[-1]
                dist_to_hoop = math.sqrt(
                    (last_point[0] - self.hoop_x) ** 2 + (last_point[1] - self.rim_y) ** 2)
                if self.will_make_shot and dist_to_hoop < 30:
                    points = self.current_shot_position.points
                    if self.shot_quality == "perfect":
                        points += 1
                        self.shot_result_message = "Perfect shot"
                        self.shot_result_color = RETRO_GOLD
                        self.perfect_shots_in_game += 1
                        if self.is_player_turn:
                            self.perfect_shots_scored += 1
                    elif self.shot_quality == "good":
                        self.shot_result_message = "Good shot"
                        self.shot_result_color = RETRO_GREEN
                    else:
                        self.shot_result_message = "Swish" if points >= 3 else "Good shot"
                        self.shot_result_color = RETRO_GREEN if points >= 2 else RETRO_GOLD
                    self.shot_result = {"made": True, "points": points}
                    self.increase_hoop_speed()
                    if self.current_shot_position.points >= 3 and self.is_player_turn:
                        self.three_pointers_in_game += 1
                        self.three_pointers_scored += 1
                    if self.is_player_turn:
                        self.current_streak += 1
                        if self.current_streak > self.max_streak:
                            self.max_streak = self.current_streak
                    for _ in range(25):
                        self.particles.append(Particle(self.ball["x"], self.ball["y"], RETRO_GOLD))
                    if self.sound_manager:
                        self.sound_manager.play_basketball_score()
                else:
                    self.shot_result = {"made": False, "points": 0}
                    miss_messages = ["Miss", "Off the rim", "Wrong direction", "Hit the rim"]
                    self.shot_result_message = random.choice(miss_messages)
                    self.shot_result_color = RETRO_RED
                    self.reset_hoop_speed()
                    if self.is_player_turn:
                        self.misses_in_game += 1
                        self.total_misses += 1
                    self.current_streak = 0
                    if self.sound_manager:
                        self.sound_manager.play_basketball_miss()
                self.result_timer = 60

    def increase_hoop_speed(self):
        self.hoop_speed_multiplier += 0.15
        self.hoop_speed_multiplier = min(2.5, self.hoop_speed_multiplier)
        self.hoop_speed = self.base_hoop_speed * self.hoop_speed_multiplier
        self.hoop_speed_increase_timer = 180

    def reset_hoop_speed(self):
        self.hoop_speed_multiplier = 1.0
        self.hoop_speed = self.base_hoop_speed
        self.hoop_speed_increase_timer = 0

    def ai_turn_update(self):
        if self.is_player_turn or self.is_shooting or self.waiting_for_shot or self.game_over:
            return
        accuracy = 0.5 + self.ai_difficulty * 0.08
        accuracy = min(0.9, accuracy)
        if self.is_final:
            accuracy = 0.7
        if random.random() < accuracy:
            error = random.randint(-int(15 / (self.ai_difficulty + 1)),
                                   int(15 / (self.ai_difficulty + 1)))
            self.ai_aim_x = self.hoop_x + error
        else:
            self.ai_aim_x = self.hoop_x + random.randint(-60, 60)
        self.ai_aim_x = max(BASE_WIDTH // 2 - 80, min(BASE_WIDTH // 2 + 80, self.ai_aim_x))
        if not self.ai_is_charging:
            self.ai_is_charging = True
            self.ai_charge_timer = 0
        else:
            charge_speed = 4 + self.ai_difficulty * 0.5
            self.ai_charge_timer += charge_speed
            if self.ai_difficulty >= 4:
                release_point = 88 + random.randint(-5, 5)
            elif self.ai_difficulty >= 2:
                release_point = 85 + random.randint(-15, 10)
            else:
                release_point = random.randint(40, 100)
            if self.is_final:
                release_point = 90 + random.randint(-5, 5)
            if self.ai_charge_timer >= release_point:
                self.ai_is_charging = False
                self.start_shot(self.ai_aim_x, self.ai_charge_timer)
                self.waiting_for_shot = True
                self.ai_charge_timer = 0

    def handle_player_input(self):
        if not self.is_player_turn or self.game_over or self.is_shooting or self.waiting_for_shot:
            return

        if control_manager.control_type == ControlType.TOUCH:
            move = touch_controls.get_move_x()
            charging = touch_controls.is_charging_shot()
        else:
            move = control_manager.get_aim_move()
            charging = control_manager.is_charging_shot()

        self.aim_x += move * self.aim_speed
        self.aim_x = max(BASE_WIDTH // 2 - 80, min(BASE_WIDTH // 2 + 80, self.aim_x))
        if charging and not self.is_charging:
            self.is_charging = True
            self.timing_meter_value = 0
            self.timing_meter_direction = 1
        elif not charging and self.is_charging:
            self.is_charging = False
            self.start_shot(self.aim_x, self.timing_meter_value)
            self.waiting_for_shot = True

    def update(self):
        if self.game_over:
            return True
        self.update_hoop_position()
        self.update_timing_meter()
        self.ai_turn_update()
        self.particles = [p for p in self.particles if p.update()]
        self.court_animation += 0.02
        if self.result_timer > 0:
            self.result_timer -= 1
            if self.result_timer <= 0:
                if self.shot_result and self.shot_result["made"]:
                    if self.is_player_turn:
                        self.player_score += self.shot_result["points"]
                        if self.player_score >= self.target_score:
                            self.game_over = True
                            self.player_won = True
                            self.level_completed = True
                    else:
                        self.cpu_score += self.shot_result["points"]
                        if self.cpu_score >= self.target_score:
                            self.game_over = True
                            self.player_won = False
                            self.level_completed = False
                            if self.is_final:
                                self.level_completed = True
                                self.player_won = False
                self.is_player_turn = not self.is_player_turn
                self.shot_result = None
                self.waiting_for_shot = False
                self.is_charging = False
                self.ai_is_charging = False
                self.timing_meter_value = 0
                self.timing_meter_direction = 1
                self.return_bird_to_home()
                self.select_random_shot_position()
                self.reset_ball()
                self.aim_x = self.hoop_x
        if self.is_shooting:
            self.update_shot()
            self.shot_timer += 1
            if self.shot_timer > 120:
                self.is_shooting = False
                self.shot_result = {"made": False, "points": 0}
                self.shot_result_message = "Miss"
                self.shot_result_color = RETRO_RED
                if self.is_player_turn:
                    self.misses_in_game += 1
                self.result_timer = 30
        return False

    def get_match_stats(self):
        return {
            'shots': self.shots_taken_in_game,
            'misses': self.misses_in_game,
            'perfect_shots': self.perfect_shots_in_game,
            'three_pointers': self.three_pointers_in_game,
            'max_streak': self.max_streak,
            'perfect_game': self.misses_in_game == 0 and self.shots_taken_in_game > 0
        }


class TennisRankedSystem:
    def __init__(self):
        self.elo = 1000
        self.matches_played = 0
        self.matches_won = 0
        self.tournaments_won = 0
        self.current_tournament = None
        self.current_round = 0
        self.bracket = []
        self.ranked_badges = []
        self.best_elo = 1000
        self.tournament_history = []
        self.tournament_completed = False
        self.diamond_cup_earned = False
        self.cup_badge = None
        self.is_legends_mode = False

        self.legends_opponents = generate_random_nicks(50)

        self.current_legends_opponent = None
        self.legends_searching = False
        self.legends_search_timer = 0
        self.legends_match_found = False
        self.legends_match_timer = 0
        self.legends_match_ready = False
        self.legends_badges_earned = []
        self.legends_wins = 0
        self.deuce_wins = 0
        self.match_streak = 0
        self.best_match_streak = 0
        self.max_rally_total = 0
        self.ace_master_achieved = False
        self.perfect_set_achieved = False
        self.flawless_tournament_achieved = False
        self.tournament_losses = 0
        self.current_ace_sequence = 0
        self.best_ace_sequence = 0

        self.tournaments = [
            {'name': 'School Tournament', 'required_elo': 0, 'surface': 'clay',
             'rounds': [{'opponent': 'John Smith', 'difficulty': 1, 'reward_elo': 25},
                        {'opponent': 'Emma Wilson', 'difficulty': 1, 'reward_elo': 25}],
             'final_opponent': 'School Champion', 'final_difficulty': 2, 'final_reward': 50},

            {'name': 'District Tournament', 'required_elo': 1020, 'surface': 'grass',
             'rounds': [{'opponent': 'James Miller', 'difficulty': 2, 'reward_elo': 25},
                        {'opponent': 'Patricia Taylor', 'difficulty': 2, 'reward_elo': 25}],
             'final_opponent': 'District Champion', 'final_difficulty': 3, 'final_reward': 50},

            {'name': 'City Championship', 'required_elo': 1060, 'surface': 'hard',
             'rounds': [{'opponent': 'David Jackson', 'difficulty': 3, 'reward_elo': 25},
                        {'opponent': 'Maria Garcia', 'difficulty': 3, 'reward_elo': 25}],
             'final_opponent': 'City Champion', 'final_difficulty': 4, 'final_reward': 50},

            {'name': 'Regional Tournament', 'required_elo': 1120, 'surface': 'clay',
             'rounds': [{'opponent': 'Thomas Lee', 'difficulty': 4, 'reward_elo': 25},
                        {'opponent': 'Daniel Harris', 'difficulty': 4, 'reward_elo': 25}],
             'final_opponent': 'Regional Champion', 'final_difficulty': 5, 'final_reward': 50},

            {'name': 'National Championship', 'required_elo': 1220, 'surface': 'grass',
             'rounds': [{'opponent': 'Paul Walker', 'difficulty': 5, 'reward_elo': 25},
                        {'opponent': 'Nancy Hall', 'difficulty': 5, 'reward_elo': 25}],
             'final_opponent': 'National Champion', 'final_difficulty': 6, 'final_reward': 50},

            {'name': 'International Tournament', 'required_elo': 1360, 'surface': 'hard',
             'rounds': [{'opponent': 'James Wilson', 'difficulty': 6, 'reward_elo': 25},
                        {'opponent': 'Maria Garcia', 'difficulty': 6, 'reward_elo': 25}],
             'final_opponent': 'International Champion', 'final_difficulty': 7, 'final_reward': 50},

            {'name': 'World Championship', 'required_elo': 1550, 'surface': 'clay',
             'rounds': [{'opponent': 'Rafael Santos', 'difficulty': 7, 'reward_elo': 25},
                        {'opponent': 'Yuki Tanaka', 'difficulty': 8, 'reward_elo': 25}],
             'final_opponent': 'World Champion', 'final_difficulty': 9, 'final_reward': 50},

            {'name': 'Legends Tournament', 'required_elo': 0, 'surface': 'hard',
             'rounds': [], 'final_opponent': '', 'final_difficulty': 0, 'final_reward': 0,
             'is_legends': True},
        ]
        self.tournament_bonus = 50
        self.create_cup_badge()
        self.completed_tournaments = set()
        self.tournament_started = False

    def create_cup_badge(self):
        self.cup_badge = {
            'name': 'World Champion',
            'desc': 'World Championship victory',
            'color': DIAMOND,
            'icon': 'cup',
            'pixel_data': [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [1, 1, 0, 1, 1, 0, 1, 1],
                [1, 1, 0, 1, 1, 0, 1, 1],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0]
            ]
        }

    def get_ranked_badges(self):
        badges = []
        rank_data = [
            (2000, 'World Champion', DIAMOND, 'cup'),
            (1900, 'Legend', RETRO_GOLD, 'star'),
            (1700, 'Master', SILVER_GREEN, 'diamond'),
            (1500, 'Expert', GOLD_GREEN, 'shield'),
            (1300, 'Professional', BRONZE_GREEN, 'target'),
            (1100, 'Advanced', BEIGE_GREEN, 'lightning'),
            (900, 'Amateur', RETRO_GREEN, 'wing'),
        ]
        for elo_threshold, name, color, icon in rank_data:
            if self.elo >= elo_threshold:
                badges.append((name, color, icon))
        return badges

    def get_current_rank(self):
        if self.elo >= 2000:
            return "World Champion"
        elif self.elo >= 1900:
            return "Legend"
        elif self.elo >= 1700:
            return "Master"
        elif self.elo >= 1500:
            return "Expert"
        elif self.elo >= 1300:
            return "Professional"
        elif self.elo >= 1100:
            return "Advanced"
        elif self.elo >= 900:
            return "Amateur"
        else:
            return "Rookie"

    def get_current_tournament(self):
        if self.current_tournament is not None and self.current_tournament < len(self.tournaments):
            return self.tournaments[self.current_tournament]
        return None

    def is_tournament_completed(self, index):
        return index in self.completed_tournaments

    def can_start_tournament(self, index):
        if index < 0 or index >= len(self.tournaments):
            return False
        if index in self.completed_tournaments:
            return False
        if self.elo < self.tournaments[index]['required_elo']:
            return False
        return True

    def start_tournament(self, tournament_index):
        if tournament_index < 0 or tournament_index >= len(self.tournaments):
            return False
        if tournament_index in self.completed_tournaments:
            return False
        tournament = self.tournaments[tournament_index]
        if self.elo < tournament['required_elo']:
            return False

        self.current_tournament = tournament_index
        self.current_round = 0
        self.tournament_completed = False
        self.tournament_started = True
        self.is_legends_mode = False
        self.bracket = []
        self.legends_match_ready = False
        self.legends_match_timer = 0
        self.tournament_losses = 0

        if tournament.get('is_legends', False):
            self.is_legends_mode = True
            self.legends_searching = False
            self.current_legends_opponent = None
            self.legends_match_found = False
            self.legends_match_ready = False
            self.legends_match_timer = 0
            return True

        for r in tournament['rounds']:
            self.bracket.append({
                'opponent': r['opponent'],
                'difficulty': r['difficulty'],
                'reward_elo': r['reward_elo'],
                'completed': False,
                'won': False,
                'surface': tournament['surface']
            })
        self.bracket.append({
            'opponent': tournament['final_opponent'],
            'difficulty': tournament['final_difficulty'],
            'reward_elo': tournament['final_reward'],
            'completed': False,
            'won': False,
            'surface': tournament['surface']
        })
        return True

    def start_legends_search(self):
        if not self.is_legends_mode:
            return False
        self.legends_searching = True
        self.legends_search_timer = 0
        self.legends_match_found = False
        self.legends_match_ready = False
        self.legends_match_timer = 0
        return True

    def update_legends_search(self):
        if not self.legends_searching:
            return False

        self.legends_search_timer += 1

        if self.legends_search_timer > 120:
            self.legends_searching = False
            self.legends_match_found = True
            self.legends_match_ready = True
            self.legends_match_timer = 15 * 60
            self.current_legends_opponent = random.choice(self.legends_opponents)
            difficulty = 7 + random.randint(0, 3)
            surfaces = ['hard', 'clay', 'grass']
            surface = random.choice(surfaces)
            self.bracket = [{
                'opponent': self.current_legends_opponent,
                'difficulty': difficulty,
                'reward_elo': 25,
                'completed': False,
                'won': False,
                'surface': surface
            }]
            self.current_round = 0
            return True
        return False

    def update_legends_match_timer(self):
        if self.legends_match_ready and self.legends_match_timer > 0:
            self.legends_match_timer -= 1
            if self.legends_match_timer <= 0:
                self.legends_match_found = False
                self.legends_match_ready = False
                self.bracket = []
                self.current_legends_opponent = None
                self.is_legends_mode = False
                return True
        return False

    def accept_legends_match(self):
        if self.legends_match_ready and self.legends_match_found:
            self.legends_match_ready = False
            self.legends_match_timer = 0
            return True
        return False

    def get_current_match(self):
        if self.is_legends_mode:
            if self.legends_match_found and self.bracket:
                return self.bracket[0]
            return None
        if self.current_tournament is not None and self.current_round < len(self.bracket):
            return self.bracket[self.current_round]
        return None

    def complete_match(self, won):
        if self.is_legends_mode:
            if self.bracket:
                match = self.bracket[0]
                match['completed'] = True
                match['won'] = won
                if won:
                    self.elo += 25
                    self.matches_won += 1
                    self.best_elo = max(self.best_elo, self.elo)
                    self.legends_wins += 1
                    self.match_streak += 1
                    if self.match_streak > self.best_match_streak:
                        self.best_match_streak = self.match_streak
                else:
                    self.elo -= 20
                    self.match_streak = 0
                self.matches_played += 1
                self.current_legends_opponent = None
                self.legends_match_found = False
                self.legends_match_ready = False
                self.legends_searching = False
                self.is_legends_mode = False
                self.bracket = []
                return True
            return False

        if self.current_round >= len(self.bracket):
            return False
        match = self.bracket[self.current_round]
        match['completed'] = True
        match['won'] = won
        if won:
            self.elo += 25
            self.matches_won += 1
            self.best_elo = max(self.best_elo, self.elo)
            self.match_streak += 1
            if self.match_streak > self.best_match_streak:
                self.best_match_streak = self.match_streak
        else:
            self.elo += 10
            self.match_streak = 0
            self.tournament_losses += 1
        self.matches_played += 1
        self.current_round += 1
        if self.current_round >= len(self.bracket):
            all_won = all(m['won'] for m in self.bracket)
            if all_won:
                self.tournaments_won += 1
                self.elo += self.tournament_bonus
                self.best_elo = max(self.best_elo, self.elo)
                self.tournament_completed = True
                self.completed_tournaments.add(self.current_tournament)
                if self.tournament_losses == 0:
                    self.flawless_tournament_achieved = True
                if self.current_tournament == len(self.tournaments) - 2:
                    self.diamond_cup_earned = True
                return True
            else:
                self.tournament_completed = False
                self.current_tournament = None
                self.current_round = 0
                self.bracket = []
                self.tournament_started = False
                return False
        return False

    def update_max_rally(self, rally):
        if rally > self.max_rally_total:
            self.max_rally_total = rally

    def update_ace_sequence(self, sequence):
        if sequence > self.best_ace_sequence:
            self.best_ace_sequence = sequence
        if self.best_ace_sequence >= 10:
            self.ace_master_achieved = True

    def to_dict(self):
        return {
            'elo': self.elo,
            'matches_played': self.matches_played,
            'matches_won': self.matches_won,
            'tournaments_won': self.tournaments_won,
            'best_elo': self.best_elo,
            'current_tournament': self.current_tournament,
            'current_round': self.current_round,
            'bracket': self.bracket,
            'tournament_completed': self.tournament_completed,
            'diamond_cup_earned': self.diamond_cup_earned,
            'completed_tournaments': list(self.completed_tournaments),
            'is_legends_mode': self.is_legends_mode,
            'legends_match_found': self.legends_match_found,
            'current_legends_opponent': self.current_legends_opponent,
            'legends_match_timer': self.legends_match_timer,
            'legends_match_ready': self.legends_match_ready,
            'legends_wins': self.legends_wins,
            'deuce_wins': self.deuce_wins,
            'best_match_streak': self.best_match_streak,
            'max_rally_total': self.max_rally_total,
            'ace_master_achieved': self.ace_master_achieved,
            'perfect_set_achieved': self.perfect_set_achieved,
            'flawless_tournament_achieved': self.flawless_tournament_achieved,
            'best_ace_sequence': self.best_ace_sequence
        }

    def from_dict(self, data):
        if 'elo' in data:
            self.elo = data['elo']
        if 'matches_played' in data:
            self.matches_played = data['matches_played']
        if 'matches_won' in data:
            self.matches_won = data['matches_won']
        if 'tournaments_won' in data:
            self.tournaments_won = data['tournaments_won']
        if 'best_elo' in data:
            self.best_elo = data['best_elo']
        if 'current_tournament' in data:
            self.current_tournament = data['current_tournament']
        if 'current_round' in data:
            self.current_round = data['current_round']
        if 'bracket' in data:
            self.bracket = data['bracket']
        if 'tournament_completed' in data:
            self.tournament_completed = data['tournament_completed']
        if 'diamond_cup_earned' in data:
            self.diamond_cup_earned = data['diamond_cup_earned']
        if 'completed_tournaments' in data:
            self.completed_tournaments = set(data['completed_tournaments'])
        if 'is_legends_mode' in data:
            self.is_legends_mode = data['is_legends_mode']
        if 'legends_match_found' in data:
            self.legends_match_found = data['legends_match_found']
        if 'current_legends_opponent' in data:
            self.current_legends_opponent = data['current_legends_opponent']
        if 'legends_match_timer' in data:
            self.legends_match_timer = data['legends_match_timer']
        if 'legends_match_ready' in data:
            self.legends_match_ready = data['legends_match_ready']
        if 'legends_wins' in data:
            self.legends_wins = data['legends_wins']
        if 'deuce_wins' in data:
            self.deuce_wins = data['deuce_wins']
        if 'best_match_streak' in data:
            self.best_match_streak = data['best_match_streak']
        if 'max_rally_total' in data:
            self.max_rally_total = data['max_rally_total']
        if 'ace_master_achieved' in data:
            self.ace_master_achieved = data['ace_master_achieved']
        if 'perfect_set_achieved' in data:
            self.perfect_set_achieved = data['perfect_set_achieved']
        if 'flawless_tournament_achieved' in data:
            self.flawless_tournament_achieved = data['flawless_tournament_achieved']
        if 'best_ace_sequence' in data:
            self.best_ace_sequence = data['best_ace_sequence']


class TennisRankedScreen:
    def __init__(self, ranked_system, sound_manager=None, background_manager=None, skin_manager=None):
        self.ranked_system = ranked_system
        self.sound_manager = sound_manager
        self.background_manager = background_manager
        self.skin_manager = skin_manager
        self.selected_tournament = 0
        self.scroll_offset = 0
        self.show_bracket = False
        self.show_match = False
        self.current_tournament_index = 0
        self.animation = 0
        self.dragging_scroll = False
        self.scroll_handle_rect = None
        self.scrollbar_rect = None

    def generate_pixel_badge(self, color, icon_type="star"):
        icons = {
            "cup": [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [1, 1, 0, 1, 1, 0, 1, 1],
                [1, 1, 0, 1, 1, 0, 1, 1],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0]
            ],
            "star": [
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "diamond": [
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "shield": [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0]
            ],
            "target": [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [1, 1, 0, 0, 0, 0, 1, 1],
                [1, 1, 0, 0, 0, 0, 1, 1],
                [0, 1, 1, 0, 0, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0]
            ],
            "lightning": [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 1, 1, 1, 1, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 1, 0],
                [0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0]
            ],
            "wing": [
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]
        }
        return icons.get(icon_type, icons["star"])

    def draw_legends_mode(self, screen):
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 16)

        title_glow = pygame.Surface((BASE_WIDTH, 60), pygame.SRCALPHA)
        glow_alpha = 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.003))
        pygame.draw.rect(title_glow, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], glow_alpha // 2),
                         (BASE_WIDTH // 2 - 150, 10, 300, 50), 0, 15)
        screen.blit(title_glow, (0, 0))

        title = font_large.render("LEGENDS TOURNAMENT", True, RETRO_GOLD)
        title_shadow = font_large.render("LEGENDS TOURNAMENT", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 21))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 20))

        cup_x = BASE_WIDTH - 50
        cup_y = 55
        cup_skin = None
        if self.skin_manager:
            cup_skin = self.skin_manager.get_equipped_skin("tennis", is_cup=True)

        if self.ranked_system.diamond_cup_earned and cup_skin and cup_skin.image:
            screen.blit(cup_skin.image, (cup_x - 20, cup_y))
            cup_label = font_tiny.render("CHAMPION", True, DIAMOND)
            cup_shadow = font_tiny.render("CHAMPION", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))
        elif self.ranked_system.diamond_cup_earned:
            cup_surf = pygame.Surface((45, 55), pygame.SRCALPHA)
            glow_alpha = 150 + int(100 * math.sin(self.animation * 0.05))
            points = [(10, 38), (5, 24), (40, 24), (35, 38)]
            pygame.draw.polygon(cup_surf, (DIAMOND[0], DIAMOND[1], DIAMOND[2], 220), points)
            pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (8, 38, 29, 4), 0, 2)
            pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (12, 42, 21, 3), 0, 1)
            screen.blit(cup_surf, (cup_x - 22, cup_y))
            cup_label = font_tiny.render("CHAMPION", True, DIAMOND)
            cup_shadow = font_tiny.render("CHAMPION", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))
        else:
            if cup_skin and cup_skin.image:
                screen.blit(cup_skin.image, (cup_x - 20, cup_y))
            else:
                cup_surf = pygame.Surface((45, 55), pygame.SRCALPHA)
                points = [(10, 38), (5, 24), (40, 24), (35, 38)]
                pygame.draw.polygon(cup_surf, (DIAMOND[0], DIAMOND[1], DIAMOND[2], 80), points)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (8, 38, 29, 4), 0, 2)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (12, 42, 21, 3), 0, 1)
                screen.blit(cup_surf, (cup_x - 22, cup_y))
            cup_label = font_tiny.render("REACH 2000 ELO", True, RETRO_WHITE)
            cup_shadow = font_tiny.render("REACH 2000 ELO", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))

        elo_color = RETRO_GREEN if self.ranked_system.elo >= 1500 else RETRO_GOLD if self.ranked_system.elo >= 1000 else RETRO_RED
        elo_text = font_large.render(f"{self.ranked_system.elo}", True, elo_color)
        elo_shadow = font_large.render(f"{self.ranked_system.elo}", True, BLACK)
        screen.blit(elo_shadow, (BASE_WIDTH // 2 - elo_text.get_width() // 2 + 1, 56))
        screen.blit(elo_text, (BASE_WIDTH // 2 - elo_text.get_width() // 2, 55))
        elo_label = font_small.render("ELO", True, RETRO_GRAY)
        elo_label_shadow = font_small.render("ELO", True, BLACK)
        screen.blit(elo_label_shadow, (BASE_WIDTH // 2 - elo_label.get_width() // 2 + 1, 86))
        screen.blit(elo_label, (BASE_WIDTH // 2 - elo_label.get_width() // 2, 85))

        rank_text = font_medium.render(self.ranked_system.get_current_rank(), True, RETRO_SILVER)
        rank_shadow = font_medium.render(self.ranked_system.get_current_rank(), True, BLACK)
        screen.blit(rank_shadow, (BASE_WIDTH // 2 - rank_text.get_width() // 2 + 1, 105))
        screen.blit(rank_text, (BASE_WIDTH // 2 - rank_text.get_width() // 2, 104))

        bar_width = BASE_WIDTH - 60
        bar_height = 20
        bar_x = 30
        bar_y = 130
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 35, 30), bar_rect, 0, 10)
        elo_percent = min(1.0, (self.ranked_system.elo - 800) / 1200)
        fill_width = int(bar_width * max(0, min(1, elo_percent)))
        if fill_width > 0:
            grad_colors = [BEIGE_GREEN, GREEN_YELLOW, BRONZE_GREEN, SILVER_GREEN, GOLD_GREEN, DIAMOND]
            pixel_size = 3
            for i in range(0, fill_width, pixel_size):
                progress = i / bar_width
                color_idx = min(int(progress * len(grad_colors)), len(grad_colors) - 1)
                color = grad_colors[color_idx]
                pygame.draw.rect(screen, color, (bar_x + i, bar_y + 2, pixel_size, bar_height - 4))
        pygame.draw.rect(screen, RETRO_SILVER, bar_rect, 2, 10)

        marks = [800, 1000, 1200, 1400, 1600, 1800, 2000]
        for mark in marks:
            mark_x = bar_x + ((mark - 800) / 1200) * bar_width
            if 0 <= mark_x <= bar_x + bar_width:
                pygame.draw.line(screen, RETRO_SILVER, (mark_x, bar_y - 3), (mark_x, bar_y + bar_height + 3), 2)
                mark_text = font_tiny.render(str(mark), True, RETRO_GRAY)
                mark_shadow = font_tiny.render(str(mark), True, BLACK)
                screen.blit(mark_shadow, (mark_x - mark_text.get_width() // 2 + 1, bar_y + bar_height + 5))
                screen.blit(mark_text, (mark_x - mark_text.get_width() // 2, bar_y + bar_height + 4))

        if self.ranked_system.legends_searching:
            dots = "." * ((pygame.time.get_ticks() // 300) % 4)
            search_text = font_medium.render(f"Searching opponent{dots}", True, RETRO_GOLD)
            search_shadow = font_medium.render(f"Searching opponent{dots}", True, BLACK)
            search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 180, 200, 50)
            pygame.draw.rect(screen, RETRO_PURPLE, search_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, search_rect, 2, 10)
            screen.blit(search_shadow, (
                search_rect.centerx - search_text.get_width() // 2 + 1,
                search_rect.centery - search_text.get_height() // 2 + 1))
            screen.blit(search_text, (
                search_rect.centerx - search_text.get_width() // 2,
                search_rect.centery - search_text.get_height() // 2))
        elif self.ranked_system.legends_match_ready and self.ranked_system.legends_match_found and self.ranked_system.bracket:
            match = self.ranked_system.bracket[0]
            opp_text = font_medium.render(f"OPPONENT: {match['opponent']}", True, RETRO_GOLD)
            opp_shadow = font_medium.render(f"OPPONENT: {match['opponent']}", True, BLACK)
            screen.blit(opp_shadow, (BASE_WIDTH // 2 - opp_text.get_width() // 2 + 1, 181))
            screen.blit(opp_text, (BASE_WIDTH // 2 - opp_text.get_width() // 2, 180))

            timer_seconds = self.ranked_system.legends_match_timer // 60
            timer_text = font_medium.render(f"Time to accept: {timer_seconds}s", True, RETRO_ORANGE)
            timer_shadow = font_medium.render(f"Time to accept: {timer_seconds}s", True, BLACK)
            screen.blit(timer_shadow, (BASE_WIDTH // 2 - timer_text.get_width() // 2 + 1, 201))
            screen.blit(timer_text, (BASE_WIDTH // 2 - timer_text.get_width() // 2, 200))

            play_rect = pygame.Rect(BASE_WIDTH // 2 - 80, 220, 160, 40)
            pygame.draw.rect(screen, RETRO_GREEN, play_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, play_rect, 2, 10)
            play_text = font_medium.render("ACCEPT FIGHT", True, RETRO_GOLD)
            play_shadow = font_medium.render("ACCEPT FIGHT", True, BLACK)
            screen.blit(play_shadow, (
                play_rect.centerx - play_text.get_width() // 2 + 1,
                play_rect.centery - play_text.get_height() // 2 + 1))
            screen.blit(play_text,
                        (play_rect.centerx - play_text.get_width() // 2,
                         play_rect.centery - play_text.get_height() // 2))
        elif self.ranked_system.legends_match_found and self.ranked_system.bracket:
            match = self.ranked_system.bracket[0]
            opp_text = font_medium.render(f"OPPONENT {match['opponent']} LEFT", True, RETRO_RED)
            opp_shadow = font_medium.render(f"OPPONENT {match['opponent']} LEFT", True, BLACK)
            screen.blit(opp_shadow, (BASE_WIDTH // 2 - opp_text.get_width() // 2 + 1, 181))
            screen.blit(opp_text, (BASE_WIDTH // 2 - opp_text.get_width() // 2, 180))

            search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 220, 200, 40)
            pygame.draw.rect(screen, RETRO_GREEN, search_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, search_rect, 2, 10)
            search_text = font_medium.render("SEARCH NEW", True, RETRO_GOLD)
            search_shadow = font_medium.render("SEARCH NEW", True, BLACK)
            screen.blit(search_shadow, (
                search_rect.centerx - search_text.get_width() // 2 + 1,
                search_rect.centery - search_text.get_height() // 2 + 1))
            screen.blit(search_text, (
                search_rect.centerx - search_text.get_width() // 2,
                search_rect.centery - search_text.get_height() // 2))
        else:
            search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 180, 200, 50)
            pygame.draw.rect(screen, RETRO_GREEN, search_rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, search_rect, 2, 10)
            search_text = font_medium.render("FIND OPPONENT", True, RETRO_GOLD)
            search_shadow = font_medium.render("FIND OPPONENT", True, BLACK)
            screen.blit(search_shadow, (
                search_rect.centerx - search_text.get_width() // 2 + 1,
                search_rect.centery - search_text.get_height() // 2 + 1))
            screen.blit(search_text, (
                search_rect.centerx - search_text.get_width() // 2,
                search_rect.centery - search_text.get_height() // 2))

        stats_y = 280
        stats = [
            f"Matches: {self.ranked_system.matches_played}",
            f"Wins: {self.ranked_system.matches_won}",
            f"Legends Wins: {self.ranked_system.legends_wins}",
            f"Best ELO: {self.ranked_system.best_elo}"
        ]
        for i, stat in enumerate(stats):
            stat_text = font_small.render(stat, True, RETRO_GOLD)
            stat_shadow = font_small.render(stat, True, BLACK)
            screen.blit(stat_shadow, (BASE_WIDTH // 2 - stat_text.get_width() // 2 + 1, stats_y + i * 25 + 1))
            screen.blit(stat_text, (BASE_WIDTH // 2 - stat_text.get_width() // 2, stats_y + i * 25))

        back_rect = pygame.Rect(10, 10, 80, 30)
        pygame.draw.rect(screen, RETRO_PURPLE, back_rect, 0, 8)
        pygame.draw.rect(screen, RETRO_SILVER, back_rect, 2, 8)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow, (back_rect.x + 5, back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text, (back_rect.x + 4, back_rect.centery - back_text.get_height() // 2))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)
        return back_rect

    def draw(self, screen):
        self.animation += 0.02

        if self.show_bracket:
            back_btn = self.draw_bracket(screen)
            if control_manager.control_type == ControlType.GAMEPAD:
                pixel_cursor.draw(screen)
            return back_btn

        if self.background_manager:
            bg = self.background_manager.get_random_background()
            if bg:
                screen.blit(bg, (0, 0))
            else:
                screen.fill((45, 40, 35))
        else:
            screen.fill((45, 40, 35))

        font_large = pygame.font.Font(None, 38)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 16)
        retro_font = pygame.font.Font(None, 34)

        if self.ranked_system.is_legends_mode:
            back_rect = self.draw_legends_mode(screen)
            return back_rect

        retro_title = retro_font.render("RANKED TENNIS", True, RETRO_WHITE)
        retro_shadow = retro_font.render("RANKED TENNIS", True, BLACK)
        screen.blit(retro_shadow, (BASE_WIDTH // 2 - retro_title.get_width() // 2 + 1, 11))
        screen.blit(retro_title, (BASE_WIDTH // 2 - retro_title.get_width() // 2, 10))
        pygame.draw.line(screen, RETRO_SILVER, (20, 45), (BASE_WIDTH - 20, 45), 2)

        cup_x = BASE_WIDTH - 50
        cup_y = 55
        cup_skin = None
        if self.skin_manager:
            cup_skin = self.skin_manager.get_equipped_skin("tennis", is_cup=True)

        if self.ranked_system.diamond_cup_earned and cup_skin and cup_skin.image:
            screen.blit(cup_skin.image, (cup_x - 20, cup_y))
            cup_label = font_tiny.render("CHAMPION", True, DIAMOND)
            cup_shadow = font_tiny.render("CHAMPION", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))
        elif self.ranked_system.diamond_cup_earned:
            cup_surf = pygame.Surface((45, 55), pygame.SRCALPHA)
            glow_alpha = 150 + int(100 * math.sin(self.animation * 0.05))
            glow_surf = pygame.Surface((55, 65), pygame.SRCALPHA)
            for i in range(3):
                radius = 22 + i * 8
                alpha = glow_alpha - i * 40
                pygame.draw.circle(glow_surf, (185, 242, 255, max(0, alpha)), (27, 32), radius)
            cup_surf.blit(glow_surf, (-5, -5), special_flags=pygame.BLEND_RGBA_ADD)
            points = [(10, 38), (5, 24), (40, 24), (35, 38)]
            pygame.draw.polygon(cup_surf, (DIAMOND[0], DIAMOND[1], DIAMOND[2], 220), points)
            pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (8, 38, 29, 4), 0, 2)
            pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (12, 42, 21, 3), 0, 1)
            pygame.draw.arc(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (2, 20, 16, 20),
                            math.radians(90), math.radians(270), 2)
            pygame.draw.arc(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 220), (27, 20, 16, 20),
                            math.radians(-90), math.radians(90), 2)
            screen.blit(cup_surf, (cup_x - 22, cup_y))
            cup_label = font_tiny.render("CHAMPION", True, DIAMOND)
            cup_shadow = font_tiny.render("CHAMPION", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))
        else:
            if cup_skin and cup_skin.image:
                screen.blit(cup_skin.image, (cup_x - 20, cup_y))
            else:
                cup_surf = pygame.Surface((45, 55), pygame.SRCALPHA)
                points = [(10, 38), (5, 24), (40, 24), (35, 38)]
                pygame.draw.polygon(cup_surf, (DIAMOND[0], DIAMOND[1], DIAMOND[2], 80), points)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (8, 38, 29, 4), 0, 2)
                pygame.draw.rect(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (12, 42, 21, 3), 0, 1)
                pygame.draw.arc(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (2, 20, 16, 20),
                                math.radians(90), math.radians(270), 2)
                pygame.draw.arc(cup_surf, (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], 80), (27, 20, 16, 20),
                                math.radians(-90), math.radians(90), 2)
                screen.blit(cup_surf, (cup_x - 22, cup_y))
            cup_label = font_tiny.render("REACH 2000 ELO", True, RETRO_WHITE)
            cup_shadow = font_tiny.render("REACH 2000 ELO", True, BLACK)
            screen.blit(cup_shadow, (cup_x - cup_label.get_width() // 2 + 1, cup_y + 53))
            screen.blit(cup_label, (cup_x - cup_label.get_width() // 2, cup_y + 52))

        elo_color = RETRO_GREEN if self.ranked_system.elo >= 1500 else RETRO_GOLD if self.ranked_system.elo >= 1000 else RETRO_RED
        elo_text = font_large.render(f"{self.ranked_system.elo}", True, elo_color)
        elo_shadow = font_large.render(f"{self.ranked_system.elo}", True, BLACK)
        screen.blit(elo_shadow, (BASE_WIDTH // 2 - elo_text.get_width() // 2 + 1, 56))
        screen.blit(elo_text, (BASE_WIDTH // 2 - elo_text.get_width() // 2, 55))
        elo_label = font_small.render("ELO", True, RETRO_GRAY)
        elo_label_shadow = font_small.render("ELO", True, BLACK)
        screen.blit(elo_label_shadow, (BASE_WIDTH // 2 - elo_label.get_width() // 2 + 1, 91))
        screen.blit(elo_label, (BASE_WIDTH // 2 - elo_label.get_width() // 2, 90))

        rank_text = font_medium.render(self.ranked_system.get_current_rank(), True, RETRO_SILVER)
        rank_glow = font_medium.render(self.ranked_system.get_current_rank(), True, SILVER_GLOW)
        rank_glow.set_alpha(50)
        rank_shadow = font_medium.render(self.ranked_system.get_current_rank(), True, BLACK)
        screen.blit(rank_shadow, (BASE_WIDTH // 2 - rank_text.get_width() // 2 + 1, 111))
        screen.blit(rank_glow, (BASE_WIDTH // 2 - rank_text.get_width() // 2 + 1, 110 + 1))
        screen.blit(rank_text, (BASE_WIDTH // 2 - rank_text.get_width() // 2, 110))

        bar_width = BASE_WIDTH - 60
        bar_height = 20
        bar_x = 30
        bar_y = 140
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (40, 35, 30), bar_rect, 0, 10)
        elo_percent = min(1.0, (self.ranked_system.elo - 800) / 1200)
        fill_width = int(bar_width * max(0, min(1, elo_percent)))
        if fill_width > 0:
            grad_colors = [BEIGE_GREEN, GREEN_YELLOW, BRONZE_GREEN, SILVER_GREEN, GOLD_GREEN, DIAMOND]
            pixel_size = 3
            for i in range(0, fill_width, pixel_size):
                progress = i / bar_width
                color_idx = min(int(progress * len(grad_colors)), len(grad_colors) - 1)
                color = grad_colors[color_idx]
                pygame.draw.rect(screen, color, (bar_x + i, bar_y + 2, pixel_size, bar_height - 4))
        pygame.draw.rect(screen, RETRO_SILVER, bar_rect, 2, 10)
        marks = [800, 1000, 1200, 1400, 1600, 1800, 2000]
        for mark in marks:
            mark_x = bar_x + ((mark - 800) / 1200) * bar_width
            if 0 <= mark_x <= bar_x + bar_width:
                pygame.draw.line(screen, RETRO_SILVER, (mark_x, bar_y - 3), (mark_x, bar_y + bar_height + 3), 2)
                mark_text = font_tiny.render(str(mark), True, RETRO_GRAY)
                mark_shadow = font_tiny.render(str(mark), True, BLACK)
                screen.blit(mark_shadow, (mark_x - mark_text.get_width() // 2 + 1, bar_y + bar_height + 5))
                screen.blit(mark_text, (mark_x - mark_text.get_width() // 2, bar_y + bar_height + 4))

        start_y = 175
        for i, tournament in enumerate(self.ranked_system.tournaments):
            rect_y = start_y + i * 55 - self.scroll_offset
            if rect_y < start_y - 5 or rect_y > BASE_HEIGHT - 80:
                continue
            rect = pygame.Rect(20, rect_y, BASE_WIDTH - 40, 50)
            is_locked = self.ranked_system.elo < tournament['required_elo']
            is_completed = self.ranked_system.is_tournament_completed(i)
            is_available = not is_locked and not is_completed

            if tournament.get('is_legends', False):
                is_locked = False
                is_available = True

            if tournament.get('is_legends', False):
                glow_alpha = 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.003))
                glow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf,
                                 (RETRO_GOLD[0], RETRO_GOLD[1], RETRO_GOLD[2], glow_alpha // 2),
                                 (5, 5, rect.width, rect.height), 0, 10)
                screen.blit(glow_surf, (rect.x - 5, rect.y - 5))
                bg_color = (155, 89, 182, 200)
            elif i == self.selected_tournament and is_available:
                bg_color = RETRO_PURPLE
            elif is_completed:
                bg_color = (46, 204, 113, 200)
            elif is_locked:
                bg_color = (40, 35, 30)
            else:
                bg_color = (50, 45, 40)

            pygame.draw.rect(screen, bg_color, rect, 0, 10)
            pygame.draw.rect(screen, RETRO_SILVER, rect, 2, 10)

            surface_colors = {'clay': TENNIS_CLAY, 'grass': TENNIS_GRASS, 'hard': TENNIS_HARD}
            surface_color = surface_colors.get(tournament.get('surface', 'hard'), RETRO_GOLD)

            if tournament.get('is_legends', False):
                pygame.draw.circle(screen, RETRO_GOLD, (rect.x + 20, rect.y + 25), 8)
            else:
                pygame.draw.circle(screen, surface_color, (rect.x + 20, rect.y + 25), 8)

            name_text = font_medium.render(tournament['name'], True,
                                           RETRO_GOLD if not is_locked else RETRO_GRAY)
            name_shadow = font_medium.render(tournament['name'], True, BLACK)
            screen.blit(name_shadow, (rect.x + 41, rect.y + 6))
            screen.blit(name_text, (rect.x + 40, rect.y + 5))

            if tournament.get('is_legends', False):
                req_text = font_tiny.render("ALWAYS AVAILABLE", True, RETRO_GOLD)
                req_shadow = font_tiny.render("ALWAYS AVAILABLE", True, BLACK)
                screen.blit(req_shadow, (rect.x + 41, rect.y + 29))
                screen.blit(req_text, (rect.x + 40, rect.y + 28))
            else:
                req_text = font_tiny.render(f"Required ELO: {tournament['required_elo']}", True, RETRO_GRAY)
                req_shadow = font_tiny.render(f"Required ELO: {tournament['required_elo']}", True, BLACK)
                screen.blit(req_shadow, (rect.x + 41, rect.y + 29))
                screen.blit(req_text, (rect.x + 40, rect.y + 28))

            if is_locked and not tournament.get('is_legends', False):
                lock_text = font_small.render("Locked", True, RETRO_RED)
                lock_shadow = font_small.render("Locked", True, BLACK)
                screen.blit(lock_shadow, (rect.right - lock_text.get_width() - 10, rect.y + 12))
                screen.blit(lock_text, (rect.right - lock_text.get_width() - 11, rect.y + 11))
            elif is_completed:
                complete_text = font_small.render("Complete", True, RETRO_GREEN)
                complete_shadow = font_small.render("Complete", True, BLACK)
                screen.blit(complete_shadow, (rect.right - complete_text.get_width() - 10, rect.y + 12))
                screen.blit(complete_text, (rect.right - complete_text.get_width() - 11, rect.y + 11))
            elif i == self.selected_tournament:
                select_text = font_small.render("Play", True, RETRO_SILVER)
                select_shadow = font_small.render("Play", True, BLACK)
                screen.blit(select_shadow, (rect.right - select_text.get_width() - 10, rect.y + 12))
                screen.blit(select_text, (rect.right - select_text.get_width() - 11, rect.y + 11))

        total_height = len(self.ranked_system.tournaments) * 55
        max_scroll = max(0, total_height - (BASE_HEIGHT - 230))
        if max_scroll > 0:
            scroll_bg = pygame.Rect(BASE_WIDTH - 12, 175, 7, BASE_HEIGHT - 230)
            pygame.draw.rect(screen, (40, 40, 50), scroll_bg, 0, 4)
            scroll_height = max(30, (BASE_HEIGHT - 230) * (BASE_HEIGHT - 230) / total_height)
            scroll_y = 175 + (self.scroll_offset / max_scroll) * (BASE_HEIGHT - 230 - scroll_height)
            self.scroll_handle_rect = pygame.Rect(BASE_WIDTH - 14, scroll_y, 11, scroll_height)
            pygame.draw.rect(screen, RETRO_PURPLE, self.scroll_handle_rect, 0, 5)
            pygame.draw.rect(screen, RETRO_SILVER, self.scroll_handle_rect, 1, 5)
            self.scrollbar_rect = scroll_bg

        back_rect = pygame.Rect(10, 10, 80, 30)
        pygame.draw.rect(screen, RETRO_PURPLE, back_rect, 0, 8)
        pygame.draw.rect(screen, RETRO_SILVER, back_rect, 2, 8)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow, (back_rect.x + 5, back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text, (back_rect.x + 4, back_rect.centery - back_text.get_height() // 2))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)
        return back_rect

    def draw_tournament_list(self, screen):
        pass

    def draw_bracket(self, screen):
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 16)

        if self.background_manager:
            bg = self.background_manager.get_random_background()
            if bg:
                screen.blit(bg, (0, 0))
            else:
                screen.fill((45, 40, 35))
        else:
            screen.fill((45, 40, 35))

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if self.selected_tournament >= len(self.ranked_system.tournaments):
            back_btn = pygame.Rect(10, 10, 80, 30)
            return back_btn

        tournament = self.ranked_system.tournaments[self.selected_tournament]
        bracket = self.ranked_system.bracket

        title = font_medium.render(f"BRACKET: {tournament['name']}", True, RETRO_SILVER)
        title_shadow = font_medium.render(f"BRACKET: {tournament['name']}", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 21))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 20))

        surface_colors = {'clay': TENNIS_CLAY, 'grass': TENNIS_GRASS, 'hard': TENNIS_HARD}
        surface_color = surface_colors.get(tournament['surface'], RETRO_GRAY)
        surf_text = font_small.render(f"Surface: {tournament['surface'].upper()}", True, surface_color)
        surf_shadow = font_small.render(f"Surface: {tournament['surface'].upper()}", True, BLACK)
        screen.blit(surf_shadow, (BASE_WIDTH // 2 - surf_text.get_width() // 2 + 1, 56))
        screen.blit(surf_text, (BASE_WIDTH // 2 - surf_text.get_width() // 2, 55))

        start_y = 90
        all_won = True
        for i, match in enumerate(bracket):
            rect_y = start_y + i * 55
            if rect_y > BASE_HEIGHT - 80:
                break
            rect = pygame.Rect(20, rect_y, BASE_WIDTH - 40, 50)
            if match['completed']:
                if match['won']:
                    bg_color = (46, 204, 113, 200)
                else:
                    bg_color = (231, 76, 60, 200)
                    all_won = False
            else:
                bg_color = (50, 45, 40)
            pygame.draw.rect(screen, bg_color, rect, 0, 8)
            if self.ranked_system.tournament_completed and all_won and i == len(bracket) - 1:
                pygame.draw.rect(screen, RETRO_GREEN, rect, 3, 8)
            else:
                pygame.draw.rect(screen, RETRO_SILVER if not match['completed'] else WHITE, rect, 2, 8)
            round_text = font_small.render(f"Round {i + 1}", True, RETRO_GOLD)
            round_shadow = font_small.render(f"Round {i + 1}", True, BLACK)
            screen.blit(round_shadow, (rect.x + 11, rect.y + 5))
            screen.blit(round_text, (rect.x + 10, rect.y + 4))
            opp_text = font_small.render(f"vs {match['opponent']}", True, RETRO_GOLD)
            opp_shadow = font_small.render(f"vs {match['opponent']}", True, BLACK)
            screen.blit(opp_shadow, (rect.x + 81, rect.y + 5))
            screen.blit(opp_text, (rect.x + 80, rect.y + 4))
            if match['completed']:
                result_text = "WIN" if match['won'] else "LOSS"
                result_color = RETRO_GREEN if match['won'] else RETRO_RED
                result_surf = font_small.render(result_text, True, result_color)
                result_shadow = font_small.render(result_text, True, BLACK)
                screen.blit(result_shadow, (rect.x + 81, rect.y + 25))
                screen.blit(result_surf, (rect.x + 80, rect.y + 24))
                if match['won']:
                    elo_text = font_small.render(f"+25 ELO", True, RETRO_SILVER)
                    elo_shadow = font_small.render(f"+25 ELO", True, BLACK)
                    screen.blit(elo_shadow, (rect.right - 79, rect.y + 25))
                    screen.blit(elo_text, (rect.right - 80, rect.y + 24))
                else:
                    elo_text = font_small.render(f"+10 ELO", True, RETRO_GRAY)
                    elo_shadow = font_small.render(f"+10 ELO", True, BLACK)
                    screen.blit(elo_shadow, (rect.right - 79, rect.y + 25))
                    screen.blit(elo_text, (rect.right - 80, rect.y + 24))
            else:
                if i == self.ranked_system.current_round:
                    play_text = font_small.render("PLAY", True, RETRO_SILVER)
                    play_shadow = font_small.render("PLAY", True, BLACK)
                    screen.blit(play_shadow, (rect.right - 69, rect.y + 13))
                    screen.blit(play_text, (rect.right - 70, rect.y + 12))

        if self.ranked_system.tournament_completed and all_won:
            complete_text = font_medium.render("TOURNAMENT COMPLETE +50 ELO", True, RETRO_GREEN)
            complete_shadow = font_medium.render("TOURNAMENT COMPLETE +50 ELO", True, BLACK)
            screen.blit(complete_shadow,
                        (BASE_WIDTH // 2 - complete_text.get_width() // 2 + 1, start_y + len(bracket) * 55 + 11))
            screen.blit(complete_text,
                        (BASE_WIDTH // 2 - complete_text.get_width() // 2, start_y + len(bracket) * 55 + 10))
        elif not all_won and self.ranked_system.current_round >= len(bracket):
            fail_text = font_medium.render("TOURNAMENT FAILED", True, RETRO_RED)
            fail_shadow = font_medium.render("TOURNAMENT FAILED", True, BLACK)
            screen.blit(fail_shadow,
                        (BASE_WIDTH // 2 - fail_text.get_width() // 2 + 1, start_y + len(bracket) * 55 + 11))
            screen.blit(fail_text,
                        (BASE_WIDTH // 2 - fail_text.get_width() // 2, start_y + len(bracket) * 55 + 10))
            restart_text = font_small.render("Start tournament again", True, RETRO_GRAY)
            restart_shadow = font_small.render("Start tournament again", True, BLACK)
            screen.blit(restart_shadow,
                        (BASE_WIDTH // 2 - restart_text.get_width() // 2 + 1, start_y + len(bracket) * 55 + 31))
            screen.blit(restart_text,
                        (BASE_WIDTH // 2 - restart_text.get_width() // 2, start_y + len(bracket) * 55 + 30))

        back_btn = pygame.Rect(10, 10, 80, 30)
        pygame.draw.rect(screen, RETRO_PURPLE, back_btn, 0, 8)
        pygame.draw.rect(screen, RETRO_SILVER, back_btn, 2, 8)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow, (back_btn.x + 5, back_btn.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text, (back_btn.x + 4, back_btn.centery - back_text.get_height() // 2))
        return back_btn

    def handle_click(self, x, y):
        if self.ranked_system.is_legends_mode:
            back_rect = pygame.Rect(10, 10, 80, 30)
            if back_rect.collidepoint(x, y):
                if self.sound_manager:
                    self.sound_manager.play_button()
                self.ranked_system.is_legends_mode = False
                self.ranked_system.legends_searching = False
                self.ranked_system.legends_match_found = False
                self.ranked_system.legends_match_ready = False
                return None

            if self.ranked_system.legends_match_ready and self.ranked_system.legends_match_found and self.ranked_system.bracket:
                play_rect = pygame.Rect(BASE_WIDTH // 2 - 80, 220, 160, 40)
                if play_rect.collidepoint(x, y):
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    if self.ranked_system.accept_legends_match():
                        return 'start_legends_match'

            if self.ranked_system.legends_match_found and not self.ranked_system.legends_match_ready and self.ranked_system.bracket:
                search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 220, 200, 40)
                if search_rect.collidepoint(x, y):
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    self.ranked_system.legends_match_found = False
                    self.ranked_system.bracket = []
                    self.ranked_system.current_legends_opponent = None
                    self.ranked_system.start_legends_search()
                    return None

            if not self.ranked_system.legends_searching and not self.ranked_system.legends_match_found:
                search_rect = pygame.Rect(BASE_WIDTH // 2 - 100, 180, 200, 50)
                if search_rect.collidepoint(x, y):
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    self.ranked_system.start_legends_search()
                    return None
            return None

        if self.show_bracket:
            back_btn = pygame.Rect(10, 10, 80, 30)
            if back_btn.collidepoint(x, y):
                if self.sound_manager:
                    self.sound_manager.play_button()
                self.show_bracket = False
                return None

            bracket = self.ranked_system.bracket
            start_y = 90
            for i, match in enumerate(bracket):
                rect_y = start_y + i * 55
                rect = pygame.Rect(20, rect_y, BASE_WIDTH - 40, 50)
                if rect.collidepoint(x, y) and not match['completed'] and i == self.ranked_system.current_round:
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    return 'start_match'
            return None

        start_y = 175
        for i in range(len(self.ranked_system.tournaments)):
            rect_y = start_y + i * 55 - self.scroll_offset
            rect = pygame.Rect(20, rect_y, BASE_WIDTH - 40, 50)
            if rect.collidepoint(x, y):
                if self.ranked_system.tournaments[i].get('is_legends', False):
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    self.selected_tournament = i
                    self.ranked_system.start_tournament(i)
                    self.ranked_system.is_legends_mode = True
                    self.show_bracket = False
                    return None

                if self.ranked_system.is_tournament_completed(i):
                    if self.sound_manager:
                        self.sound_manager.play_sound('hit')
                    return None
                if self.ranked_system.elo < self.ranked_system.tournaments[i]['required_elo']:
                    if self.sound_manager:
                        self.sound_manager.play_sound('hit')
                    return None
                if self.sound_manager:
                    self.sound_manager.play_button()
                self.selected_tournament = i

                if (not self.ranked_system.bracket or
                        self.selected_tournament != self.ranked_system.current_tournament or
                        self.ranked_system.tournament_completed or
                        (self.ranked_system.current_round >= len(self.ranked_system.bracket) and
                         not self.ranked_system.tournament_completed)):
                    self.ranked_system.start_tournament(i)
                self.show_bracket = True
                return None

        back_rect = pygame.Rect(10, 10, 80, 30)
        if back_rect.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            return 'back'
        return None

    def handle_scroll(self, y):
        total_height = len(self.ranked_system.tournaments) * 55
        max_scroll = max(0, total_height - (BASE_HEIGHT - 230))
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset + y))

    def handle_mouse_motion(self, x, y):
        if self.dragging_scroll and self.scroll_handle_rect and self.scrollbar_rect:
            total_height = len(self.ranked_system.tournaments) * 55
            max_scroll = max(0, total_height - (BASE_HEIGHT - 230))
            if max_scroll > 0:
                scroll_y = y - 175 - 15
                scroll_y = max(0, min(scroll_y, BASE_HEIGHT - 230 - 30))
                self.scroll_offset = (scroll_y / (BASE_HEIGHT - 230 - 30)) * max_scroll
                self.scroll_offset = max(0, min(max_scroll, self.scroll_offset))

    def handle_mouse_up(self):
        self.dragging_scroll = False

    def update(self):
        if self.ranked_system.is_legends_mode and self.ranked_system.legends_searching:
            self.ranked_system.update_legends_search()

        if self.ranked_system.is_legends_mode and self.ranked_system.legends_match_ready:
            if self.ranked_system.update_legends_match_timer():
                self.ranked_system.legends_match_found = False
                self.ranked_system.bracket = []
                self.ranked_system.current_legends_opponent = None


class TennisRankedGame:
    def __init__(self, sound_manager=None, ranked_system=None, match_data=None, bird_skin=None, opponent_skin=None,
                 is_legends=False):
        self.sound_manager = sound_manager
        self.ranked_system = ranked_system
        self.match_data = match_data
        self.bird_skin = bird_skin
        self.opponent_skin = opponent_skin
        self.is_legends = is_legends
        self.active = True
        self.player_games = 0
        self.ai_games = 0
        self.player_points = 0
        self.ai_points = 0
        self.target_games = 2
        self.game_over = False
        self.won = False
        self.deuce = False
        self.advantage = None
        self.rally_count = 0
        self.max_rally = 0
        self.ace_sequence = 0
        self.best_ace_sequence = 0
        self.points_won_in_row = 0
        self.deuce_wins_this_match = 0
        self.perfect_shots = 0
        self.three_pointer_count = 0
        self.perfect_releases = 0

        difficulty = match_data['difficulty'] if match_data else 1
        self.ai_difficulty = difficulty

        self.surface = match_data.get('surface', 'hard') if match_data else 'hard'

        if match_data and 'rank' in match_data:
            rank = match_data['rank']
            if rank <= 10:
                difficulty = 8 + (10 - rank) * 0.2
            elif rank <= 50:
                difficulty = 6 + (50 - rank) * 0.04
            else:
                difficulty = 4
            self.ai_difficulty = difficulty

        self.ai_speed_base = 3.0 + difficulty * 0.15
        self.ai_aggression = 0.7 + difficulty * 0.05
        self.ai_accuracy = 0.3 + difficulty * 0.05
        self.ai_error_chance = 0.15 - difficulty * 0.005
        self.ai_consistency = 0.5 + difficulty * 0.03
        self.ai_react_time_base = 4.5 + difficulty * 0.1
        self.ai_react_time_variation = 4
        self.ai_power_charge_speed = 5.0 + difficulty * 0.5
        self.ai_power_multiplier = 1.0

        self.player_paddle = pygame.Rect(BASE_WIDTH // 2 - 35, BASE_HEIGHT - 55, 70, 12)
        self.ai_paddle = pygame.Rect(BASE_WIDTH // 2 - 35, 35, 70, 12)
        self.ball = pygame.Rect(BASE_WIDTH // 2 - 6, BASE_HEIGHT // 2 - 6, 12, 12)
        self.ball_dx = random.choice([-4, 4])
        self.ball_dy = -4
        self.ball_spin = 0
        self.serving = True
        self.serve_timer = 0
        self.serving_player = 'player'
        self.trail = []
        self.particles = []
        self.hit_effects = []
        self.power_meter = 0
        self.power_charging = False
        self.power_charge_speed = 1.5
        self.player_left_shot = False
        self.player_right_shot = False
        self.player_slice = False
        self.player_straight = False
        self.player_curve = False
        self.ball_curve_active = False
        self.ball_curve_direction = 0
        self.ball_curve_intensity = 0.0

        self.player_anim_image = None
        self.player_anim_timer = 0
        self.opponent_anim_image = None
        self.opponent_anim_timer = 0
        self.SHOT_ANIM_DURATION = 90

        self.ai_shot_type = None
        self.ai_react_time = 0
        self.ai_target_x = BASE_WIDTH // 2
        self.ai_aim_direction = 1
        self.ai_aim_speed = 3
        self.player_speed = 8
        self.ai_random_off_position = 0
        self.ai_error_timer = 0
        self.ai_aggressive_timer = 0
        self.font_small = pygame.font.Font(None, 18)
        self.font_medium = pygame.font.Font(None, 26)
        self.font_large = pygame.font.Font(None, 34)

        self.player_velocity_x = 0
        self.player_inertia = 0.5
        self.player_friction = 0.75

        if self.surface == 'clay':
            self.court_color = (193, 100, 67)
            self.court_line_color = (220, 180, 120)
            self.player_friction = 0.7
        elif self.surface == 'grass':
            self.court_color = (68, 148, 74)
            self.court_line_color = (200, 255, 200)
            self.player_friction = 0.8
        else:
            self.court_color = (77, 88, 96)
            self.court_line_color = (150, 170, 190)
            self.player_friction = 0.75

    def draw_bird_paddle(self, screen, rect, color, is_player=True, skin=None):
        use_skin = skin if skin is not None else (self.bird_skin if is_player else self.opponent_skin)

        anim_img = None
        if is_player and self.player_anim_image is not None and self.player_anim_timer > 0:
            anim_img = self.player_anim_image
        elif (not is_player) and self.opponent_anim_image is not None and self.opponent_anim_timer > 0:
            anim_img = self.opponent_anim_image

        if anim_img is not None:
            screen.blit(anim_img, (rect.x - 5, rect.y - 5))
            return

        if use_skin is not None and hasattr(use_skin, 'image') and use_skin.image is not None:
            bird_surf = use_skin.image.copy()
            screen.blit(bird_surf, (rect.x - 5, rect.y - 5))
            return

        bird_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(bird_surf, color, (5, 2, rect.width - 10, rect.height - 4))
        pygame.draw.circle(bird_surf, color, (rect.width - 8, rect.height // 2), 8)
        pygame.draw.circle(bird_surf, WHITE, (rect.width - 5, rect.height // 2 - 2), 3)
        pygame.draw.circle(bird_surf, BLACK, (rect.width - 4, rect.height // 2 - 2), 1)
        beak_points = [(rect.width - 2, rect.height // 2), (rect.width + 5, rect.height // 2),
                       (rect.width - 2, rect.height // 2 + 4)]
        pygame.draw.polygon(bird_surf, ORANGE, beak_points)
        screen.blit(bird_surf, (rect.x - 5, rect.y - 5))

    def _trigger_shot_animation(self, is_player, shot_side):
        skin = self.bird_skin if is_player else self.opponent_skin
        if skin is None or not getattr(skin, 'has_animation', False):
            return
        img = None
        if shot_side == "right":
            img = skin.image_right
        elif shot_side == "left":
            img = skin.image_left
        elif shot_side == "curve":
            img = skin.image_right or skin.image_left
        if img is not None:
            if is_player:
                self.player_anim_image = img
                self.player_anim_timer = self.SHOT_ANIM_DURATION
            else:
                self.opponent_anim_image = img
                self.opponent_anim_timer = self.SHOT_ANIM_DURATION

    def _trigger_random_hit_animation(self, is_player):
        skin = self.bird_skin if is_player else self.opponent_skin
        if skin is None or not getattr(skin, 'has_animation', False):
            return
        candidates = []
        if getattr(skin, 'image_right', None) is not None:
            candidates.append(skin.image_right)
        if getattr(skin, 'image_left', None) is not None:
            candidates.append(skin.image_left)
        if not candidates:
            return
        img = random.choice(candidates)
        if is_player:
            self.player_anim_image = img
            self.player_anim_timer = self.SHOT_ANIM_DURATION
        else:
            self.opponent_anim_image = img
            self.opponent_anim_timer = self.SHOT_ANIM_DURATION

    def calculate_hit_angle(self, ball_center, paddle_center, paddle_rect):
        hit_pos = (ball_center - paddle_center) / (paddle_rect.width / 2)
        hit_pos = max(-1, min(1, hit_pos))
        return hit_pos

    def play_hit_sound(self, is_player):
        if is_player:
            if self.sound_manager:
                self.sound_manager.play_tennis_player_hit()
        else:
            if self.sound_manager:
                self.sound_manager.play_tennis_opponent_hit()

    def update(self):
        if self.player_anim_timer > 0:
            self.player_anim_timer -= 1
            if self.player_anim_timer <= 0:
                self.player_anim_image = None
        if self.opponent_anim_timer > 0:
            self.opponent_anim_timer -= 1
            if self.opponent_anim_timer <= 0:
                self.opponent_anim_image = None

        if self.game_over:
            return True
        if self.serving:
            self.serve_timer += 1
            if self.serve_timer > 60:
                self.serving = False
            return False

        if control_manager.control_type == ControlType.TOUCH:
            move_x = touch_controls.get_move_x()
            if abs(move_x) < 0.15:
                move_x = 0
        else:
            move_x = control_manager.get_move_x()

        if move_x != 0:
            self.player_velocity_x += move_x * 0.35
            self.player_velocity_x = max(-self.player_speed, min(self.player_speed, self.player_velocity_x))
        else:
            self.player_velocity_x *= self.player_friction
            if abs(self.player_velocity_x) < 0.2:
                self.player_velocity_x = 0

        self.player_paddle.x += self.player_velocity_x
        self.player_paddle.left = max(0, min(self.player_paddle.left, BASE_WIDTH - self.player_paddle.width))

        if control_manager.control_type == ControlType.TOUCH:
            self.player_left_shot = touch_controls.is_topspin_pressed()
            self.player_right_shot = touch_controls.is_dropshot_pressed()
            self.player_slice = touch_controls.is_slice_pressed()
            self.player_straight = touch_controls.is_straight_pressed()
            self.player_curve = touch_controls.is_curve_pressed()
            charging = touch_controls.is_charging_shot()
        else:
            self.player_left_shot = control_manager.is_topspin_pressed()
            self.player_right_shot = control_manager.is_dropshot_pressed()
            self.player_slice = control_manager.is_slice_pressed()
            self.player_straight = control_manager.is_straight_pressed()
            self.player_curve = control_manager.is_curve_pressed()
            charging = control_manager.is_charging_shot()

        if charging and not self.power_charging:
            self.power_charging = True
            self.power_meter = 0
        elif not charging and self.power_charging:
            self.power_charging = False
        if self.power_charging:
            self.power_meter = min(100, self.power_meter + self.power_charge_speed)

        self.ai_react_time += 1
        react_delay = self.ai_react_time_base + random.randint(0, self.ai_react_time_variation)

        if self.ai_react_time >= react_delay:
            self.ai_react_time = 0
            if abs(self.ball_dy) > 0:
                frames_to_reach = abs((self.ai_paddle.y - self.ball.y) / self.ball_dy) if self.ball_dy != 0 else 100
                predicted_x = self.ball.x + self.ball_dx * frames_to_reach

                error_range = 10 - (self.ai_accuracy * 20) + random.randint(-5, 5)
                error_range = max(3, min(30, error_range))

                if random.random() < self.ai_error_chance:
                    error_range = random.randint(25, 60)
                    if random.random() < 0.3:
                        predicted_x = BASE_WIDTH // 2 + random.choice([-50, 50])
                    if random.random() < 0.15:
                        predicted_x = random.randint(0, BASE_WIDTH)

                if random.random() < 0.1 * (1 - self.ai_accuracy):
                    predicted_x += random.randint(-40, 40)

                predicted_x += random.uniform(-error_range, error_range)
                self.ai_target_x = max(35, min(BASE_WIDTH - 35, predicted_x))

        if random.random() < self.ai_aggression:
            self.ai_shot_type = random.choice(["topspin", "slice", "straight", "lob", "nadal"])
            if self.rally_count > 5 and random.random() < 0.3:
                self.ai_shot_type = random.choice(["topspin", "straight", "nadal"])
            if self.rally_count > 10 and random.random() < 0.2:
                self.ai_shot_type = "lob"
            if random.random() < 0.15 + self.ai_difficulty * 0.02:
                self.ai_shot_type = "nadal"
        else:
            self.ai_shot_type = "normal"

        ai_power_charging = False
        ai_power_meter = 0
        if random.random() < self.ai_aggression * 0.8:
            ai_power_charging = True
            ai_power_meter = random.randint(60, 100)
            self.ai_power_multiplier = 1.0 + (ai_power_meter / 100) * 0.7

        if random.random() > (0.1 - self.ai_consistency * 0.05):
            if random.random() < 0.1:
                self.ai_random_off_position = random.randint(-10, 10)

            target = self.ai_target_x + self.ai_random_off_position

            if self.ai_paddle.centerx < target - 3 and self.ai_paddle.right < BASE_WIDTH:
                self.ai_paddle.x += self.ai_speed_base + random.uniform(-0.3, 0.3)
            elif self.ai_paddle.centerx > target + 3 and self.ai_paddle.left > 0:
                self.ai_paddle.x -= self.ai_speed_base + random.uniform(-0.3, 0.3)

        if self.ball_curve_active:
            self.ball_dx += self.ball_curve_direction * self.ball_curve_intensity
            self.ball_curve_intensity *= 0.98
            if abs(self.ball_curve_intensity) < 0.05:
                self.ball_curve_active = False
                self.ball_curve_intensity = 0.0

        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy
        self.ball_dx += self.ball_spin * 0.05
        self.ball_dx = max(-7, min(7, self.ball_dx))
        self.ball_spin *= 0.98

        self.trail.append((self.ball.centerx, self.ball.centery))
        if len(self.trail) > 15:
            self.trail.pop(0)

        if self.ball.left <= 0:
            self.ball.left = 1
            self.ball_dx = abs(self.ball_dx)
            self.ball_spin = random.uniform(-1, 1)
            if self.sound_manager:
                self.sound_manager.play_tennis_wall()
        if self.ball.right >= BASE_WIDTH:
            self.ball.right = BASE_WIDTH - 1
            self.ball_dx = -abs(self.ball_dx)
            self.ball_spin = random.uniform(-1, 1)
            if self.sound_manager:
                self.sound_manager.play_tennis_wall()

        if self.ball.colliderect(self.player_paddle) and self.ball_dy > 0:
            self.ball_dy = -5
            hit_angle = self.calculate_hit_angle(self.ball.centerx, self.player_paddle.centerx,
                                                 self.player_paddle)

            power_mult = 1 + (self.power_meter / 100) * 0.8

            self.rally_count += 1
            if self.rally_count > self.max_rally:
                self.max_rally = self.rally_count

            any_attack_pressed = (self.player_left_shot or self.player_right_shot or
                                  self.player_slice or self.player_straight or self.player_curve)

            if self.player_left_shot:
                self.ball_dx = -abs(hit_angle) * 5 - 2
                self.ball_dy = -5 * (1.2 + power_mult * 0.3)
                self.ball_spin = -2
                effect_color = (255, 100, 100)
                self._trigger_shot_animation(True, "left")
            elif self.player_right_shot:
                self.ball_dx = abs(hit_angle) * 5 + 2
                self.ball_dy = -5 * (1.2 + power_mult * 0.3)
                self.ball_spin = 2
                effect_color = (255, 200, 100)
                self._trigger_shot_animation(True, "right")
            elif self.player_slice:
                self.ball_dx = hit_angle * 4
                self.ball_dy = -4
                self.ball_spin = hit_angle * -2
                effect_color = (100, 100, 255)
                self._trigger_shot_animation(True, "left")
            elif self.player_straight:
                self.ball_dx = 0
                self.ball_dy = -7 * (1.2 + power_mult * 0.3)
                self.ball_spin = hit_angle * 0.5
                effect_color = (255, 215, 0)
                self._trigger_shot_animation(True, "right")
            elif self.player_curve:
                self.ball_dx = hit_angle * 3.2
                self.ball_dy = -6.0 * (0.9 + power_mult * 0.3)
                self.ball_spin = -6.0
                self.ball_curve_active = True
                self.ball_curve_direction = 1 if hit_angle >= 0 else -1
                self.ball_curve_intensity = 0.45
                effect_color = (230, 120, 60)
                self._trigger_shot_animation(True, "curve")
                for _ in range(8):
                    self.particles.append(Particle(
                        self.ball.centerx, self.ball.centery + 5,
                        (180, 90, 40), angle=random.uniform(0, math.pi), speed=2
                    ))
            else:
                self.ball_dx += hit_angle * 4 * power_mult
                self.ball_dy = -5 * (1.0 + power_mult * 0.3)
                self.ball_spin = hit_angle * 1.5
                effect_color = RETRO_GOLD
                self._trigger_random_hit_animation(True)

            self.ball_dx = max(-8, min(8, self.ball_dx))

            self.play_hit_sound(True)

            for _ in range(10):
                self.particles.append(Particle(self.ball.centerx, self.ball.centery, effect_color))
            self.hit_effects.append({"x": self.ball.centerx, "y": self.ball.centery, "life": 10})
            self.power_meter = 0
            self.power_charging = False

        if self.ball.colliderect(self.ai_paddle) and self.ball_dy < 0:
            self.ball_dy = 5
            hit_angle = self.calculate_hit_angle(self.ball.centerx, self.ai_paddle.centerx, self.ai_paddle)

            error_factor = random.uniform(0.8, 1.2)
            ai_power_mult = self.ai_power_multiplier

            self.rally_count += 1
            if self.rally_count > self.max_rally:
                self.max_rally = self.rally_count

            if self.ai_shot_type == "topspin":
                self.ball_dx = -abs(hit_angle) * 5 * error_factor * ai_power_mult
                self.ball_dy = 5 * 1.2 * ai_power_mult
                self.ball_spin = -2
                effect_color = (255, 100, 100)
                self._trigger_shot_animation(False, "left")
                if random.random() < 0.3:
                    self.ball_dx *= 1.2
                    self.ball_dy *= 1.1
            elif self.ai_shot_type == "slice":
                self.ball_dx = hit_angle * 4 * error_factor
                self.ball_dy = 4
                self.ball_spin = hit_angle * -2
                effect_color = (100, 100, 255)
                self._trigger_shot_animation(False, "left")
            elif self.ai_shot_type == "straight":
                self.ball_dx = 0
                self.ball_dy = 6 * ai_power_mult
                self.ball_spin = hit_angle * 0.3
                effect_color = (255, 215, 0)
                self._trigger_shot_animation(False, "right")
                if random.random() < 0.2:
                    self.ball_dy *= 1.3
            elif self.ai_shot_type == "lob":
                self.ball_dx = hit_angle * 3
                self.ball_dy = 7 * ai_power_mult
                self.ball_spin = hit_angle * 0.5
                effect_color = (255, 255, 100)
                self._trigger_shot_animation(False, "right")
            elif self.ai_shot_type == "nadal":
                self.ball_dx = hit_angle * 2.5
                self.ball_dy = 5.2 * (0.85 + (ai_power_mult - 1.0) * 0.3)
                self.ball_spin = 6.0
                self.ball_curve_active = True
                self.ball_curve_direction = 1 if hit_angle >= 0 else -1
                self.ball_curve_intensity = 0.35
                effect_color = (230, 120, 60)
                self._trigger_shot_animation(False, "curve")
                for _ in range(6):
                    self.particles.append(Particle(
                        self.ball.centerx, self.ball.centery - 5,
                        (180, 90, 40), angle=random.uniform(math.pi, math.pi * 2), speed=2
                    ))
            elif self.ai_shot_type == "bad":
                self.ball_dx = random.choice([-7, 7]) * random.uniform(0.4, 0.9) * ai_power_mult
                self.ball_dy = 5 * random.uniform(0.5, 1.5) * ai_power_mult
                self.ball_spin = random.uniform(-2, 2)
                effect_color = (255, 200, 100)
                self._trigger_random_hit_animation(False)
            else:
                self.ball_dx += hit_angle * 4 * error_factor * ai_power_mult
                self.ball_dy = 5 * (1.0 + (ai_power_mult - 1.0) * 0.7)
                self.ball_spin = hit_angle * 1.5
                effect_color = RETRO_RED
                self._trigger_random_hit_animation(False)

            self.ball_dx = max(-8, min(8, self.ball_dx))

            self.play_hit_sound(False)

            for _ in range(8):
                self.particles.append(Particle(self.ball.centerx, self.ball.centery, effect_color))
            self.hit_effects.append({"x": self.ball.centerx, "y": self.ball.centery, "life": 10})
            self.ai_power_multiplier = 1.0

        if self.ball.top <= 0:
            self.rally_count = 0
            self.player_points += 1
            self.points_won_in_row += 1
            if self.points_won_in_row > self.best_ace_sequence:
                self.best_ace_sequence = self.points_won_in_row
            self.check_point_win()
            self.reset_ball('player')
            self.serving = True
            self.serve_timer = 0
            self.serving_player = 'player'
            if self.sound_manager:
                self.sound_manager.play_tennis_point_win()
        elif self.ball.bottom >= BASE_HEIGHT:
            self.rally_count = 0
            self.ai_points += 1
            self.points_won_in_row = 0
            self.check_point_win()
            self.reset_ball('ai')
            self.serving = True
            self.serve_timer = 0
            self.serving_player = 'ai'
            if self.sound_manager:
                self.sound_manager.play_tennis_point_lose()

        self.particles = [p for p in self.particles if p.update()]
        self.hit_effects = [e for e in self.hit_effects if e["life"] > 0]
        for e in self.hit_effects:
            e["life"] -= 1

        if self.player_games >= self.target_games:
            self.game_over = True
            self.won = True
            return True
        elif self.ai_games >= self.target_games:
            self.game_over = True
            self.won = False
            return True
        return False

    def check_point_win(self):
        if self.player_points >= 3 and self.ai_points >= 3:
            if self.player_points > self.ai_points and self.player_points - self.ai_points >= 2:
                self.player_games += 1
                self.player_points = 0
                self.ai_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0
                self.deuce_wins_this_match += 1
            elif self.ai_points > self.player_points and self.ai_points - self.player_points >= 2:
                self.ai_games += 1
                self.player_points = 0
                self.ai_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0
            else:
                self.deuce = True
                if self.player_points > self.ai_points:
                    self.advantage = 'player'
                elif self.ai_points > self.player_points:
                    self.advantage = 'ai'
                else:
                    self.advantage = None
        else:
            if self.player_points >= 4 and self.player_points - self.ai_points >= 2:
                self.player_games += 1
                self.player_points = 0
                self.ai_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0
            elif self.ai_points >= 4 and self.ai_points - self.player_points >= 2:
                self.ai_games += 1
                self.player_points = 0
                self.ai_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0

    def reset_ball(self, server):
        self.ball.centerx = BASE_WIDTH // 2
        self.ball.centery = BASE_HEIGHT // 2
        self.ball_dx = random.choice([-3, 3])
        self.ball_dy = -4 if server == 'player' else 4
        self.trail.clear()
        self.ball_spin = 0
        self.ball_curve_active = False
        self.ball_curve_intensity = 0.0

    def draw(self, screen):
        screen.fill(self.court_color)
        pygame.draw.line(screen, self.court_line_color, (0, BASE_HEIGHT // 2), (BASE_WIDTH, BASE_HEIGHT // 2), 3)
        pygame.draw.line(screen, self.court_line_color, (BASE_WIDTH // 2, 0), (BASE_WIDTH // 2, BASE_HEIGHT), 3)
        pygame.draw.circle(screen, self.court_line_color, (BASE_WIDTH // 2, BASE_HEIGHT // 2), 40, 3)

        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail))) if self.trail else 100
            pygame.draw.circle(screen,
                               (self.court_line_color[0], self.court_line_color[1], self.court_line_color[2],
                                alpha), (int(tx), int(ty)), 3)

        glow_size = 10 + math.sin(pygame.time.get_ticks() * 0.01) * 3
        if self.player_left_shot:
            pygame.draw.circle(screen, (255, 100, 100, 150), self.ball.center, int(glow_size + 5))
        elif self.player_right_shot:
            pygame.draw.circle(screen, (255, 200, 100, 150), self.ball.center, int(glow_size + 5))
        elif self.player_slice:
            pygame.draw.circle(screen, (100, 100, 255, 150), self.ball.center, int(glow_size + 5))
        elif self.player_straight:
            pygame.draw.circle(screen, (255, 215, 0, 150), self.ball.center, int(glow_size + 5))
        elif self.player_curve:
            pygame.draw.circle(screen, (230, 120, 60, 150), self.ball.center, int(glow_size + 5))
        else:
            pygame.draw.circle(screen,
                               (self.court_line_color[0], self.court_line_color[1], self.court_line_color[2],
                                150), self.ball.center, int(glow_size))
        pygame.draw.circle(screen, RETRO_GOLD, self.ball.center, 6)

        for e in self.hit_effects:
            alpha = int(150 * (e["life"] / 10))
            pygame.draw.circle(screen,
                               (self.court_line_color[0], self.court_line_color[1], self.court_line_color[2],
                                alpha), (int(e["x"]), int(e["y"])), 15)

        for particle in self.particles:
            particle.draw(screen)

        self.draw_bird_paddle(screen, self.player_paddle, RETRO_BLUE, True, self.bird_skin)
        self.draw_bird_paddle(screen, self.ai_paddle, RETRO_RED, False, self.opponent_skin)

        if self.player_left_shot:
            left_text = self.font_small.render("LEFT [LB/Q]", True, (255, 100, 100))
            left_shadow = self.font_small.render("LEFT [LB/Q]", True, BLACK)
            screen.blit(left_shadow, (11, BASE_HEIGHT - 29))
            screen.blit(left_text, (10, BASE_HEIGHT - 30))
        elif self.player_right_shot:
            right_text = self.font_small.render("RIGHT [RB/E]", True, (255, 200, 100))
            right_shadow = self.font_small.render("RIGHT [RB/E]", True, BLACK)
            screen.blit(right_shadow, (11, BASE_HEIGHT - 29))
            screen.blit(right_text, (10, BASE_HEIGHT - 30))
        elif self.player_slice:
            slice_text = self.font_small.render("SLICE [X/F]", True, (100, 100, 255))
            slice_shadow = self.font_small.render("SLICE [X/F]", True, BLACK)
            screen.blit(slice_shadow, (11, BASE_HEIGHT - 29))
            screen.blit(slice_text, (10, BASE_HEIGHT - 30))
        elif self.player_straight:
            straight_text = self.font_small.render("STRAIGHT [W/Y]", True, (255, 215, 0))
            straight_shadow = self.font_small.render("STRAIGHT [W/Y]", True, BLACK)
            screen.blit(straight_shadow, (11, BASE_HEIGHT - 29))
            screen.blit(straight_text, (10, BASE_HEIGHT - 30))
        elif self.player_curve:
            curve_text = self.font_small.render("NADAL TOPSPIN [RT/R]", True, (230, 120, 60))
            curve_shadow = self.font_small.render("NADAL TOPSPIN [RT/R]", True, BLACK)
            screen.blit(curve_shadow, (11, BASE_HEIGHT - 29))
            screen.blit(curve_text, (10, BASE_HEIGHT - 30))

        games_text = self.font_large.render(f"{self.player_games}  -  {self.ai_games}", True, RETRO_SILVER)
        games_shadow = self.font_large.render(f"{self.player_games}  -  {self.ai_games}", True, BLACK)
        games_bg = pygame.Surface((games_text.get_width() + 20, 50), pygame.SRCALPHA)
        pygame.draw.rect(games_bg, (0, 0, 0, 200), games_bg.get_rect(), 0, 10)
        screen.blit(games_bg, (BASE_WIDTH // 2 - games_text.get_width() // 2 - 10, BASE_HEIGHT // 2 - 60))
        screen.blit(games_shadow, (BASE_WIDTH // 2 - games_text.get_width() // 2 + 1, BASE_HEIGHT // 2 - 54))
        screen.blit(games_text, (BASE_WIDTH // 2 - games_text.get_width() // 2, BASE_HEIGHT // 2 - 55))

        if self.rally_count > 0:
            rally_text = self.font_small.render(f"Rally: {self.rally_count}", True, RETRO_GOLD)
            rally_shadow = self.font_small.render(f"Rally: {self.rally_count}", True, BLACK)
            rally_bg = pygame.Surface((rally_text.get_width() + 16, 20), pygame.SRCALPHA)
            pygame.draw.rect(rally_bg, (0, 0, 0, 180), rally_bg.get_rect(), 0, 6)
            screen.blit(rally_bg, (BASE_WIDTH // 2 - rally_text.get_width() // 2 - 8, BASE_HEIGHT // 2 - 82))
            screen.blit(rally_shadow,
                        (BASE_WIDTH // 2 - rally_text.get_width() // 2 + 1, BASE_HEIGHT // 2 - 81 + 1))
            screen.blit(rally_text, (BASE_WIDTH // 2 - rally_text.get_width() // 2, BASE_HEIGHT // 2 - 82))

        point_names = ["0", "15", "30", "40"]
        p1_pts = min(self.player_points, 3)
        p2_pts = min(self.ai_points, 3)
        points_text = self.font_medium.render(f"{point_names[p1_pts]} - {point_names[p2_pts]}", True,
                                              RETRO_SILVER)
        points_shadow = self.font_medium.render(f"{point_names[p1_pts]} - {point_names[p2_pts]}", True, BLACK)
        points_bg = pygame.Surface((points_text.get_width() + 30, 35), pygame.SRCALPHA)
        pygame.draw.rect(points_bg, (0, 0, 0, 200), points_bg.get_rect(), 0, 10)
        screen.blit(points_bg, (BASE_WIDTH // 2 - points_text.get_width() // 2 - 15, BASE_HEIGHT // 2 - 25))
        screen.blit(points_shadow,
                    (BASE_WIDTH // 2 - points_text.get_width() // 2 + 1, BASE_HEIGHT // 2 - 19))
        screen.blit(points_text, (BASE_WIDTH // 2 - points_text.get_width() // 2, BASE_HEIGHT // 2 - 20))

        if self.deuce:
            if self.advantage == 'player':
                adv_text = self.font_medium.render("ADVANTAGE PLAYER", True, RETRO_GREEN)
                adv_shadow = self.font_medium.render("ADVANTAGE PLAYER", True, BLACK)
                screen.blit(adv_shadow, (BASE_WIDTH // 2 - adv_text.get_width() // 2 + 1, BASE_HEIGHT // 2 + 21))
                screen.blit(adv_text, (BASE_WIDTH // 2 - adv_text.get_width() // 2, BASE_HEIGHT // 2 + 20))
            elif self.advantage == 'ai':
                adv_text = self.font_medium.render("ADVANTAGE OPPONENT", True, RETRO_RED)
                adv_shadow = self.font_medium.render("ADVANTAGE OPPONENT", True, BLACK)
                screen.blit(adv_shadow, (BASE_WIDTH // 2 - adv_text.get_width() // 2 + 1, BASE_HEIGHT // 2 + 21))
                screen.blit(adv_text, (BASE_WIDTH // 2 - adv_text.get_width() // 2, BASE_HEIGHT // 2 + 20))
            else:
                deuce_text = self.font_medium.render("DEUCE", True, RETRO_YELLOW)
                deuce_shadow = self.font_medium.render("DEUCE", True, BLACK)
                screen.blit(deuce_shadow, (BASE_WIDTH // 2 - deuce_text.get_width() // 2 + 1, BASE_HEIGHT // 2 + 21))
                screen.blit(deuce_text, (BASE_WIDTH // 2 - deuce_text.get_width() // 2, BASE_HEIGHT // 2 + 20))

        if self.power_charging:
            meter_width = 60
            meter_height = 8
            meter_x = BASE_WIDTH // 2 - meter_width // 2
            meter_y = BASE_HEIGHT - 35
            pygame.draw.rect(screen, DARK_GRAY, (meter_x, meter_y, meter_width, meter_height), 0, 4)
            fill_width = int(meter_width * (self.power_meter / 100))
            if self.power_meter < 30:
                color = (0, 200, 255)
            elif self.power_meter < 60:
                color = (100, 255, 100)
            elif self.power_meter < 85:
                color = (255, 255, 0)
            else:
                color = (255, 100, 0)
            pygame.draw.rect(screen, color, (meter_x, meter_y, fill_width, meter_height), 0, 4)
            if self.power_meter >= 90:
                glow_alpha = 100 + int(80 * math.sin(pygame.time.get_ticks() * 0.05))
                pygame.draw.rect(screen, (255, 200, 50, glow_alpha),
                                 (meter_x + fill_width - 4, meter_y - 2, 8, meter_height + 4), 0, 2)

        if self.match_data:
            opp_text = self.font_small.render(f"vs {self.match_data['opponent']}", True, RETRO_SILVER)
            opp_shadow = self.font_small.render(f"vs {self.match_data['opponent']}", True, BLACK)
            screen.blit(opp_shadow, (BASE_WIDTH // 2 - opp_text.get_width() // 2 + 1, 11))
            screen.blit(opp_text, (BASE_WIDTH // 2 - opp_text.get_width() // 2, 10))

        if self.is_legends:
            legends_text = self.font_small.render("LEGENDS TOURNAMENT", True, RETRO_GOLD)
            legends_shadow = self.font_small.render("LEGENDS TOURNAMENT", True, BLACK)
            screen.blit(legends_shadow, (BASE_WIDTH // 2 - legends_text.get_width() // 2 + 1, 26))
            screen.blit(legends_text, (BASE_WIDTH // 2 - legends_text.get_width() // 2, 25))

        version_text = self.font_small.render(f"v{GAME_VERSION}", True, RETRO_GRAY)
        version_shadow = self.font_small.render(f"v{GAME_VERSION}", True, BLACK)
        screen.blit(version_shadow, (BASE_WIDTH - version_text.get_width() - 9, BASE_HEIGHT - 24))
        screen.blit(version_text, (BASE_WIDTH - version_text.get_width() - 10, BASE_HEIGHT - 25))
        if control_manager.control_type == ControlType.GAMEPAD:
            indicator = "Gamepad"
            indicator_color = RETRO_BLUE
        elif control_manager.control_type == ControlType.TOUCH:
            indicator = "Touch"
            indicator_color = RETRO_GREEN
        else:
            indicator = "Keyboard"
            indicator_color = RETRO_YELLOW
        indicator_text = self.font_small.render(indicator, True, indicator_color)
        indicator_shadow = self.font_small.render(indicator, True, BLACK)
        screen.blit(indicator_shadow, (BASE_WIDTH - indicator_text.get_width() - 9, 6))
        screen.blit(indicator_text, (BASE_WIDTH - indicator_text.get_width() - 10, 5))

        if control_manager.control_type == ControlType.TOUCH:
            touch_controls.draw(screen)

    def get_match_stats(self):
        return {
            'max_rally': self.max_rally,
            'best_ace_sequence': self.best_ace_sequence,
            'deuce_wins': self.deuce_wins_this_match,
            'perfect_set': self.won and self.ai_games == 0
        }


class ShopScreen:
    def __init__(self, skin_manager, sound_manager=None):
        self.skin_manager = skin_manager
        self.page = 0
        self.selected_skin = None
        self.animation = 0
        self.back_rect = None
        self.sound_manager = sound_manager
        self.mode_filter = "all"
        self.coins = 0
        self.show_tape_shop = False
        self.tape_shop = None

    def set_tape_shop(self, tape_shop):
        self.tape_shop = tape_shop

    def draw(self, screen, coins):
        self.coins = coins

        if self.show_tape_shop and self.tape_shop:
            return self.tape_shop.draw(screen, coins)

        self.animation += 0.05

        if self.skin_manager and hasattr(self.skin_manager, 'bg_shop'):
            bg = self.skin_manager.bg_shop.get_random_background()
            if bg:
                screen.blit(bg, (0, 0))
            else:
                screen.fill((60, 55, 48))
        else:
            screen.fill((60, 55, 48))

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 40, 220))
        screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 22)
        font_tiny = pygame.font.Font(None, 18)
        title = font_large.render("Shop", True, RETRO_SILVER)
        title_shadow = font_large.render("Shop", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 21))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 20))
        coins_text = font_medium.render(f"Coins: {coins}", True, RETRO_GOLD)
        coins_shadow = font_medium.render(f"Coins: {coins}", True, BLACK)
        screen.blit(coins_shadow, (BASE_WIDTH // 2 - coins_text.get_width() // 2 + 1, 61))
        screen.blit(coins_text, (BASE_WIDTH // 2 - coins_text.get_width() // 2, 60))

        tab_width = 100
        tab_x = BASE_WIDTH // 2 - tab_width - 10
        tab_y = 90

        skins_tab = pygame.Rect(tab_x, tab_y, tab_width, 25)
        if not self.show_tape_shop:
            pygame.draw.rect(screen, RETRO_PURPLE, skins_tab, 0, 5)
            pygame.draw.rect(screen, RETRO_SILVER, skins_tab, 2, 5)
        else:
            pygame.draw.rect(screen, (60, 60, 80), skins_tab, 0, 5)
            pygame.draw.rect(screen, RETRO_GRAY, skins_tab, 2, 5)
        skins_text = font_tiny.render("Skins", True, RETRO_GOLD)
        skins_shadow = font_tiny.render("Skins", True, BLACK)
        screen.blit(skins_shadow, (
            skins_tab.centerx - skins_text.get_width() // 2 + 1, skins_tab.centery - skins_text.get_height() // 2 + 1))
        screen.blit(skins_text,
                    (skins_tab.centerx - skins_text.get_width() // 2, skins_tab.centery - skins_text.get_height() // 2))

        tapes_tab = pygame.Rect(tab_x + tab_width + 20, tab_y, tab_width, 25)
        if self.show_tape_shop:
            pygame.draw.rect(screen, RETRO_PURPLE, tapes_tab, 0, 5)
            pygame.draw.rect(screen, RETRO_SILVER, tapes_tab, 2, 5)
        else:
            pygame.draw.rect(screen, (60, 60, 80), tapes_tab, 0, 5)
            pygame.draw.rect(screen, RETRO_GRAY, tapes_tab, 2, 5)
        tapes_text = font_tiny.render("Tapes", True, RETRO_GOLD)
        tapes_shadow = font_tiny.render("Tapes", True, BLACK)
        screen.blit(tapes_shadow, (
            tapes_tab.centerx - tapes_text.get_width() // 2 + 1, tapes_tab.centery - tapes_text.get_height() // 2 + 1))
        screen.blit(tapes_text,
                    (tapes_tab.centerx - tapes_text.get_width() // 2, tapes_tab.centery - tapes_text.get_height() // 2))

        if self.show_tape_shop:
            return tapes_tab, skins_tab, None

        all_skins = []
        tennis_skins = self.skin_manager.tennis_skins.skins
        basketball_skins = self.skin_manager.basketball_skins.skins

        for s in tennis_skins:
            s.mode_display = "Tennis"
            s.mode_key = "tennis"
            all_skins.append(s)
        for s in basketball_skins:
            s.mode_display = "Basketball"
            s.mode_key = "basketball"
            all_skins.append(s)

        if self.mode_filter != "all":
            all_skins = [s for s in all_skins if s.mode_key == self.mode_filter]

        if len(all_skins) == 0:
            empty_text = font_medium.render("No skins in this section", True, RETRO_GRAY)
            empty_shadow = font_medium.render("No skins in this section", True, BLACK)
            screen.blit(empty_shadow, (BASE_WIDTH // 2 - empty_text.get_width() // 2 + 1, 201))
            screen.blit(empty_text, (BASE_WIDTH // 2 - empty_text.get_width() // 2, 200))
        else:
            pages = (len(all_skins) + 3) // 4
            page_text = font_small.render(f"Page {self.page + 1}/{pages}", True, RETRO_GOLD)
            page_shadow = font_small.render(f"Page {self.page + 1}/{pages}", True, BLACK)
            screen.blit(page_shadow, (BASE_WIDTH // 2 - page_text.get_width() // 2 + 1, 121))
            screen.blit(page_text, (BASE_WIDTH // 2 - page_text.get_width() // 2, 120))

            tab_width_f = 50
            tab_x_f = BASE_WIDTH // 2 - tab_width_f * 2.5
            tab_y_f = 130
            tabs = [("All", "all"), ("Ten", "tennis"), ("Bas", "basketball")]
            for i, (tab_name, tab_key) in enumerate(tabs):
                tab_rect = pygame.Rect(tab_x_f + i * (tab_width_f + 2), tab_y_f, tab_width_f - 2, 18)
                if self.mode_filter == tab_key:
                    pygame.draw.rect(screen, RETRO_PURPLE, tab_rect, 0, 4)
                    pygame.draw.rect(screen, RETRO_SILVER, tab_rect, 2, 4)
                else:
                    pygame.draw.rect(screen, (60, 60, 80), tab_rect, 0, 4)
                    pygame.draw.rect(screen, RETRO_GRAY, tab_rect, 2, 4)
                tab_text = font_tiny.render(tab_name, True, RETRO_GOLD)
                tab_shadow = font_tiny.render(tab_name, True, BLACK)
                screen.blit(tab_shadow,
                            (tab_rect.centerx - tab_text.get_width() // 2 + 1,
                             tab_rect.centery - tab_text.get_height() // 2 + 1))
                screen.blit(tab_text, (
                    tab_rect.centerx - tab_text.get_width() // 2, tab_rect.centery - tab_text.get_height() // 2))

            start_idx = self.page * 4
            end_idx = min(start_idx + 4, len(all_skins))
            cols = 2
            rows = 2
            cell_width = 150
            cell_height = 155
            start_x = (BASE_WIDTH - (cell_width * cols + 20)) // 2
            start_y = 160

            page_nav_y = BASE_HEIGHT - 100
            if self.page > 0:
                left_arrow = pygame.Rect(20, page_nav_y, 40, 40)
                pygame.draw.polygon(screen, RETRO_PURPLE, [(left_arrow.right - 5, left_arrow.top + 5),
                                                           (left_arrow.left + 5, left_arrow.centery),
                                                           (left_arrow.right - 5, left_arrow.bottom - 5)])
                pygame.draw.polygon(screen, RETRO_SILVER, [(left_arrow.right - 5, left_arrow.top + 5),
                                                           (left_arrow.left + 5, left_arrow.centery),
                                                           (left_arrow.right - 5, left_arrow.bottom - 5)], 2)
            if self.page < pages - 1:
                right_arrow = pygame.Rect(BASE_WIDTH - 60, page_nav_y, 40, 40)
                pygame.draw.polygon(screen, RETRO_PURPLE, [(right_arrow.left + 5, right_arrow.top + 5),
                                                           (right_arrow.right - 5, right_arrow.centery),
                                                           (right_arrow.left + 5, right_arrow.bottom - 5)])
                pygame.draw.polygon(screen, RETRO_SILVER, [(right_arrow.left + 5, right_arrow.top + 5),
                                                           (right_arrow.right - 5, right_arrow.centery),
                                                           (right_arrow.left + 5, right_arrow.bottom - 5)], 2)

            for i in range(start_idx, end_idx):
                skin = all_skins[i]
                grid_i = i - start_idx
                row = grid_i // cols
                col = grid_i % cols
                x = start_x + col * (cell_width + 20)
                y = start_y + row * (cell_height + 20)
                rect = pygame.Rect(x, y, cell_width, cell_height)
                if skin.owned and skin.equipped:
                    pulse = math.sin(self.animation * 2) * 3
                else:
                    pulse = 0
                bg_color = skin.rarity_color if skin.owned else (60, 60, 80)
                glow_rect = rect.inflate(pulse + 5, pulse + 5)
                pygame.draw.rect(screen, (*bg_color, 200), glow_rect, 0, 15)
                pygame.draw.rect(screen, RETRO_SILVER if skin.owned else RETRO_GRAY, rect, 2, 10)
                bird_x = rect.centerx
                bird_y = rect.y + 30
                self.draw_bird_preview(screen, bird_x, bird_y, skin, self.animation + i)
                name_text = font_small.render(skin.name, True, RETRO_GOLD)
                name_shadow = font_small.render(skin.name, True, BLACK)
                screen.blit(name_shadow, (rect.centerx - name_text.get_width() // 2 + 1, rect.y + 65))
                screen.blit(name_text, (rect.centerx - name_text.get_width() // 2, rect.y + 64))
                mode_text = font_tiny.render(skin.mode_display, True, RETRO_SILVER)
                mode_shadow = font_tiny.render(skin.mode_display, True, BLACK)
                screen.blit(mode_shadow, (rect.centerx - mode_text.get_width() // 2 + 1, rect.y + 80))
                screen.blit(mode_text, (rect.centerx - mode_text.get_width() // 2, rect.y + 79))
                rarity_text = font_tiny.render(skin.rarity.capitalize(), True, RETRO_GOLD)
                rarity_shadow = font_tiny.render(skin.rarity.capitalize(), True, BLACK)
                screen.blit(rarity_shadow, (rect.centerx - rarity_text.get_width() // 2 + 1, rect.y + 93))
                screen.blit(rarity_text, (rect.centerx - rarity_text.get_width() // 2, rect.y + 92))
                if skin.owned:
                    if skin.equipped:
                        equip_text = font_small.render("Equipped", True, RETRO_GREEN)
                        equip_shadow = font_small.render("Equipped", True, BLACK)
                        screen.blit(equip_shadow, (rect.centerx - equip_text.get_width() // 2 + 1, rect.y + 110))
                        screen.blit(equip_text, (rect.centerx - equip_text.get_width() // 2, rect.y + 109))
                    else:
                        equip_text = font_tiny.render("Equip", True, RETRO_YELLOW)
                        equip_shadow = font_tiny.render("Equip", True, BLACK)
                        screen.blit(equip_shadow, (rect.centerx - equip_text.get_width() // 2 + 1, rect.y + 110))
                        screen.blit(equip_text, (rect.centerx - equip_text.get_width() // 2, rect.y + 109))
                else:
                    price_text = font_small.render(f"{skin.price}", True, RETRO_GOLD)
                    price_shadow = font_small.render(f"{skin.price}", True, BLACK)
                    screen.blit(price_shadow, (rect.centerx - price_text.get_width() // 2 + 1, rect.y + 110))
                    screen.blit(price_text, (rect.centerx - price_text.get_width() // 2, rect.y + 109))

        self.back_rect = pygame.Rect(BASE_WIDTH // 2 - 100, BASE_HEIGHT - 50, 200, 40)
        pygame.draw.rect(screen, RETRO_PURPLE, self.back_rect, 0, 10)
        pygame.draw.rect(screen, RETRO_SILVER, self.back_rect, 2, 10)
        back_text = font_medium.render("Back", True, RETRO_GOLD)
        back_shadow = font_medium.render("Back", True, BLACK)
        screen.blit(back_shadow,
                    (self.back_rect.centerx - back_text.get_width() // 2 + 1,
                     self.back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text,
                    (self.back_rect.centerx - back_text.get_width() // 2,
                     self.back_rect.centery - back_text.get_height() // 2))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)
        return tapes_tab, skins_tab, self.back_rect

    def draw_bird_preview(self, screen, x, y, skin, animation):
        if hasattr(skin, 'image') and skin.image is not None:
            rot = math.sin(animation * 0.1) * 5
            rotated = pygame.transform.rotate(skin.image, rot)
            screen.blit(rotated, (x - rotated.get_width() // 2, y - rotated.get_height() // 2))
            if hasattr(skin, 'rarity'):
                rarity_color = skin.rarity_color
                pygame.draw.circle(screen, rarity_color, (x, y), 32, 3)
            return

        bird_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(bird_surf, (100, 180, 220), (20, 20), 12)
        pygame.draw.circle(bird_surf, WHITE, (25, 17), 5)
        pygame.draw.circle(bird_surf, BLACK, (26, 17), 2)
        beak_points = [(30, 20), (34, 20), (30, 23)]
        pygame.draw.polygon(bird_surf, (200, 160, 80), beak_points)
        wing_y = 20 + math.sin(animation * 3) * 3
        pygame.draw.ellipse(bird_surf, (150, 150, 150), (12, wing_y, 10, 8))
        screen.blit(bird_surf, (x - 20, y - 20))

    def handle_click(self, x, y, coins):
        self.coins = coins

        if self.show_tape_shop and self.tape_shop:
            result = self.tape_shop.handle_click(x, y, coins)
            if result:
                action, value = result
                if action == "back":
                    self.show_tape_shop = False
                    return None
                elif action == "equip":
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    return ("tape_equip", value)
                elif action == "buy":
                    if self.sound_manager:
                        self.sound_manager.play_powerup()
                    return ("tape_buy", value)
                elif action == "not_enough_coins":
                    if self.sound_manager:
                        self.sound_manager.play_sound('hit')
                    return ("tape_not_enough", value)
                elif action == "already_equipped":
                    return None
            return None

        tab_width = 100
        tab_x = BASE_WIDTH // 2 - tab_width - 10
        tab_y = 90
        tapes_tab = pygame.Rect(tab_x + tab_width + 20, tab_y, tab_width, 25)
        skins_tab = pygame.Rect(tab_x, tab_y, tab_width, 25)

        if tapes_tab.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            self.show_tape_shop = True
            return None
        if skins_tab.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            self.show_tape_shop = False
            return None

        tab_width_f = 50
        tab_x_f = BASE_WIDTH // 2 - tab_width_f * 2.5
        tab_y_f = 130
        tabs = [("All", "all"), ("Ten", "tennis"), ("Bas", "basketball")]
        for i, (tab_name, tab_key) in enumerate(tabs):
            tab_rect = pygame.Rect(tab_x_f + i * (tab_width_f + 2), tab_y_f, tab_width_f - 2, 18)
            if tab_rect.collidepoint(x, y):
                if self.sound_manager:
                    self.sound_manager.play_button()
                self.mode_filter = tab_key
                self.page = 0
                return None

        all_skins = []
        tennis_skins = self.skin_manager.tennis_skins.skins
        basketball_skins = self.skin_manager.basketball_skins.skins

        for s in tennis_skins:
            s.mode_display = "Tennis"
            s.mode_key = "tennis"
            all_skins.append(s)
        for s in basketball_skins:
            s.mode_display = "Basketball"
            s.mode_key = "basketball"
            all_skins.append(s)

        if self.mode_filter != "all":
            all_skins = [s for s in all_skins if s.mode_key == self.mode_filter]

        if len(all_skins) == 0:
            return None

        start_idx = self.page * 4
        end_idx = min(start_idx + 4, len(all_skins))
        cols = 2
        rows = 2
        cell_width = 150
        cell_height = 155
        start_x = (BASE_WIDTH - (cell_width * cols + 20)) // 2
        start_y = 160

        for i in range(start_idx, end_idx):
            skin = all_skins[i]
            grid_i = i - start_idx
            row = grid_i // cols
            col = grid_i % cols
            x_pos = start_x + col * (cell_width + 20)
            y_pos = start_y + row * (cell_height + 20)
            rect = pygame.Rect(x_pos, y_pos, cell_width, cell_height)
            if rect.collidepoint(x, y):
                if self.sound_manager:
                    self.sound_manager.play_button()

                if skin.owned:
                    if skin.mode_key == "tennis":
                        manager = self.skin_manager.tennis_skins
                    elif skin.mode_key == "basketball":
                        manager = self.skin_manager.basketball_skins
                    else:
                        manager = self.skin_manager.tennis_skins

                    if manager.equip_skin(skin.id):
                        return ("equip", skin.mode_key)
                    return None
                else:
                    if skin.mode_key == "tennis":
                        manager = self.skin_manager.tennis_skins
                    elif skin.mode_key == "basketball":
                        manager = self.skin_manager.basketball_skins
                    else:
                        manager = self.skin_manager.tennis_skins

                    if manager.buy_skin(skin.id, self.coins):
                        return ("buy", skin.mode_key)
                    else:
                        return ("not_enough_coins", skin.mode_key)

        pages = (len(all_skins) + 3) // 4
        page_nav_y = BASE_HEIGHT - 100
        left_arrow = pygame.Rect(20, page_nav_y, 40, 40)
        if left_arrow.collidepoint(x, y) and self.page > 0:
            if self.sound_manager:
                self.sound_manager.play_button()
            self.page -= 1
            return None
        right_arrow = pygame.Rect(BASE_WIDTH - 60, page_nav_y, 40, 40)
        if right_arrow.collidepoint(x, y) and self.page < pages - 1:
            if self.sound_manager:
                self.sound_manager.play_button()
            self.page += 1
            return None

        self.back_rect = pygame.Rect(BASE_WIDTH // 2 - 100, BASE_HEIGHT - 50, 200, 40)
        if self.back_rect.collidepoint(x, y):
            return "back"
        return None


class SettingsMenu:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.active = False
        self.selected_option = 0
        self.options = [
            {"name": "Volume", "type": "slider", "value": 0.7, "min": 0.0, "max": 1.0, "step": 0.05},
            {"name": "Music", "type": "slider", "value": 0.2, "min": 0.0, "max": 1.0, "step": 0.05},
            {"name": "Sound Effects", "type": "toggle", "value": True},
            {"name": "Background Music", "type": "toggle", "value": True},
            {"name": "Graphics Quality", "type": "select", "value": "Smooth", "options": ["Pixelated", "Smooth"],
             "values": [1, 2]},
            {"name": "Controls", "type": "select", "value": "Keyboard" if not IS_ANDROID else "Touch",
             "options": ["Keyboard", "Gamepad"] + (["Touch"] if IS_ANDROID else []),
             "values": [ControlType.KEYBOARD.value, ControlType.GAMEPAD.value] + (
                 [ControlType.TOUCH.value] if IS_ANDROID else [])},
            {"name": "Back", "type": "button", "value": None}
        ]
        self.rect = pygame.Rect(50, 80, BASE_WIDTH - 100, BASE_HEIGHT - 160)
        self.slider_dragging = False
        self.dragged_option = -1
        self.screen_manager = None

    def update_from_manager(self):
        self.options[0]["value"] = self.sound_manager.sound_volume
        self.options[1]["value"] = self.sound_manager.music_volume
        self.options[2]["value"] = self.sound_manager.sound_enabled
        self.options[3]["value"] = self.sound_manager.music_enabled
        if self.screen_manager:
            current_graphics = self.screen_manager.graphics_quality
            if current_graphics == 1:
                self.options[4]["value"] = "Pixelated"
            else:
                self.options[4]["value"] = "Smooth"
        if control_manager.control_type == ControlType.KEYBOARD:
            self.options[5]["value"] = "Keyboard"
        elif control_manager.control_type == ControlType.GAMEPAD:
            self.options[5]["value"] = "Gamepad"
        else:
            self.options[5]["value"] = "Touch"

    def get_graphics_quality(self):
        for opt in self.options:
            if opt["name"] == "Graphics Quality":
                if opt["value"] == "Pixelated":
                    return 1
                else:
                    return 2
        return 2

    def get_control_type(self):
        if self.options[5]["value"] == "Keyboard":
            return ControlType.KEYBOARD
        elif self.options[5]["value"] == "Gamepad":
            return ControlType.GAMEPAD
        else:
            return ControlType.TOUCH

    def handle_event(self, event, mouse_x, mouse_y):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return "close"
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self.sound_manager.play_button()
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self.sound_manager.play_button()
            elif event.key == pygame.K_LEFT:
                option = self.options[self.selected_option]
                if option["type"] == "slider":
                    new_value = option["value"] - option["step"]
                    new_value = max(option["min"], min(option["max"], new_value))
                    self.change_setting(self.selected_option, new_value)
                elif option["type"] == "select":
                    current_idx = option["options"].index(option["value"])
                    new_idx = (current_idx - 1) % len(option["options"])
                    self.change_setting(self.selected_option, option["options"][new_idx])
            elif event.key == pygame.K_RIGHT:
                option = self.options[self.selected_option]
                if option["type"] == "slider":
                    new_value = option["value"] + option["step"]
                    new_value = max(option["min"], min(option["max"], new_value))
                    self.change_setting(self.selected_option, new_value)
                elif option["type"] == "select":
                    current_idx = option["options"].index(option["value"])
                    new_idx = (current_idx + 1) % len(option["options"])
                    self.change_setting(self.selected_option, option["options"][new_idx])
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                option = self.options[self.selected_option]
                if option["type"] == "toggle":
                    new_value = not option["value"]
                    self.change_setting(self.selected_option, new_value)
                elif option["type"] == "button" and option["name"] == "Back":
                    self.sound_manager.play_button()
                    self.active = False
                    return "close"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, option in enumerate(self.options):
                    if option["type"] == "slider":
                        slider_rect = self.get_slider_rect(i)
                        if slider_rect.collidepoint(mouse_x, mouse_y):
                            self.slider_dragging = True
                            self.dragged_option = i
                            self.update_slider_from_mouse(i, mouse_x)
                            break
                    elif option["type"] == "select":
                        select_rect = self.get_select_rect(i)
                        if select_rect.collidepoint(mouse_x, mouse_y):
                            current_idx = option["options"].index(option["value"])
                            new_idx = (current_idx + 1) % len(option["options"])
                            self.change_setting(i, option["options"][new_idx])
                            break
                    elif option["type"] == "toggle":
                        toggle_rect = self.get_toggle_rect(i)
                        if toggle_rect.collidepoint(mouse_x, mouse_y):
                            new_value = not option["value"]
                            self.change_setting(i, new_value)
                            break
                    elif option["type"] == "button" and option["name"] == "Back":
                        button_rect = self.get_button_rect(i)
                        if button_rect.collidepoint(mouse_x, mouse_y):
                            self.sound_manager.play_button()
                            self.active = False
                            return "close"
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.slider_dragging = False
                self.dragged_option = -1
        elif event.type == pygame.MOUSEMOTION:
            if self.slider_dragging and self.dragged_option >= 0:
                self.update_slider_from_mouse(self.dragged_option, mouse_x)
        return None

    def get_slider_rect(self, index):
        y = self.rect.y + 60 + index * 45
        return pygame.Rect(self.rect.x + 150, y - 10, 150, 20)

    def get_toggle_rect(self, index):
        y = self.rect.y + 60 + index * 45
        return pygame.Rect(self.rect.x + 150, y - 15, 40, 30)

    def get_button_rect(self, index):
        y = self.rect.y + 60 + index * 45
        return pygame.Rect(self.rect.x + 150, y - 15, 100, 30)

    def get_select_rect(self, index):
        y = self.rect.y + 60 + index * 45
        return pygame.Rect(self.rect.x + 150, y - 15, 150, 30)

    def update_slider_from_mouse(self, index, mouse_x):
        option = self.options[index]
        slider_rect = self.get_slider_rect(index)
        rel_x = max(0, min(slider_rect.width, mouse_x - slider_rect.x))
        new_value = option["min"] + (rel_x / slider_rect.width) * (option["max"] - option["min"])
        new_value = round(new_value / option["step"]) * option["step"]
        new_value = max(option["min"], min(option["max"], new_value))
        self.change_setting(index, new_value)

    def change_setting(self, index, new_value):
        option = self.options[index]
        option["value"] = new_value
        if option["name"] == "Volume":
            self.sound_manager.set_sound_volume(new_value)
        elif option["name"] == "Music":
            self.sound_manager.set_music_volume(new_value)
        elif option["name"] == "Sound Effects":
            self.sound_manager.sound_enabled = new_value
        elif option["name"] == "Background Music":
            self.sound_manager.music_enabled = new_value
            if new_value:
                self.sound_manager.play_menu_music()
            else:
                self.sound_manager.stop_music()
        elif option["name"] == "Graphics Quality":
            if new_value == "Pixelated":
                graphics_val = 1
            else:
                graphics_val = 2
            if self.screen_manager:
                self.screen_manager.set_graphics_quality(graphics_val)
        elif option["name"] == "Controls":
            if new_value == "Keyboard":
                control_manager.set_control_type(ControlType.KEYBOARD)
            elif new_value == "Gamepad":
                control_manager.set_control_type(ControlType.GAMEPAD)
            else:
                control_manager.set_control_type(ControlType.TOUCH)
        self.sound_manager.play_button()

    def draw(self, screen):
        if not self.active:
            return
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, DARK_PURPLE, self.rect, 0, 15)
        pygame.draw.rect(screen, RETRO_SILVER, self.rect, 3, 15)
        font_large = pygame.font.Font(None, 38)
        title = font_large.render("Settings", True, RETRO_SILVER)
        title_shadow = font_large.render("Settings", True, BLACK)
        screen.blit(title_shadow, (self.rect.centerx - title.get_width() // 2 + 1, self.rect.y + 16))
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 15))
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        for i, option in enumerate(self.options):
            y = self.rect.y + 60 + i * 45
            name_color = RETRO_SILVER if i == self.selected_option else RETRO_GOLD
            name_text = font_medium.render(option["name"], True, name_color)
            name_shadow = font_medium.render(option["name"], True, BLACK)
            screen.blit(name_shadow, (self.rect.x + 21, y - 9))
            screen.blit(name_text, (self.rect.x + 20, y - 10))
            if option["type"] == "slider":
                slider_rect = pygame.Rect(self.rect.x + 150, y - 5, 150, 10)
                pygame.draw.rect(screen, RETRO_GRAY, slider_rect, 0, 5)
                fill_percent = (option["value"] - option["min"]) / (option["max"] - option["min"])
                fill_width = int(150 * fill_percent)
                fill_rect = pygame.Rect(self.rect.x + 150, y - 5, fill_width, 10)
                pygame.draw.rect(screen, RETRO_PURPLE, fill_rect, 0, 5)
                handle_x = self.rect.x + 150 + fill_width - 5
                pygame.draw.circle(screen, RETRO_GOLD, (handle_x, y), 8)
                pygame.draw.circle(screen, RETRO_SILVER, (handle_x, y), 6)
                value_text = font_small.render(f"{option['value']:.2f}", True, RETRO_GOLD)
                value_shadow = font_small.render(f"{option['value']:.2f}", True, BLACK)
                screen.blit(value_shadow, (self.rect.x + 311, y - 14))
                screen.blit(value_text, (self.rect.x + 310, y - 15))
            elif option["type"] == "toggle":
                toggle_rect = pygame.Rect(self.rect.x + 150, y - 15, 40, 30)
                bg_color = RETRO_GREEN if option["value"] else RETRO_RED
                pygame.draw.rect(screen, bg_color, toggle_rect, 0, 8)
                pygame.draw.rect(screen, RETRO_SILVER, toggle_rect, 2, 8)
                indicator_x = self.rect.x + 160 + (20 if option["value"] else 0)
                pygame.draw.circle(screen, RETRO_GOLD, (indicator_x, y), 10)
                status = "ON" if option["value"] else "OFF"
                status_text = font_small.render(status, True, RETRO_GOLD)
                status_shadow = font_small.render(status, True, BLACK)
                screen.blit(status_shadow, (self.rect.x + 201, y - 11))
                screen.blit(status_text, (self.rect.x + 200, y - 12))
            elif option["type"] == "select":
                select_rect = pygame.Rect(self.rect.x + 150, y - 15, 150, 30)
                pygame.draw.rect(screen, RETRO_PURPLE, select_rect, 0, 8)
                pygame.draw.rect(screen, RETRO_SILVER, select_rect, 2, 8)
                display_value = str(option["value"]) if not isinstance(option["value"], str) else option["value"]
                select_text = font_small.render(display_value, True, RETRO_GOLD)
                select_shadow = font_small.render(display_value, True, BLACK)
                screen.blit(select_shadow,
                            (select_rect.centerx - select_text.get_width() // 2 + 1,
                             select_rect.centery - select_text.get_height() // 2 + 1))
                screen.blit(select_text, (
                    select_rect.centerx - select_text.get_width() // 2,
                    select_rect.centery - select_text.get_height() // 2))
                pygame.draw.polygon(screen, RETRO_SILVER,
                                    [(select_rect.right - 20, select_rect.centery - 5),
                                     (select_rect.right - 10, select_rect.centery + 5),
                                     (select_rect.right - 30, select_rect.centery + 5)])
                pygame.draw.polygon(screen, RETRO_SILVER,
                                    [(select_rect.left + 20, select_rect.centery - 5),
                                     (select_rect.left + 30, select_rect.centery + 5),
                                     (select_rect.left + 10, select_rect.centery + 5)])
            elif option["type"] == "button":
                button_rect = pygame.Rect(self.rect.x + 150, y - 15, 100, 30)
                pygame.draw.rect(screen, RETRO_PURPLE, button_rect, 0, 8)
                pygame.draw.rect(screen, RETRO_SILVER, button_rect, 2, 8)
                button_text = font_small.render(option["name"], True, RETRO_GOLD)
                button_shadow = font_small.render(option["name"], True, BLACK)
                screen.blit(button_shadow, (button_rect.centerx - button_text.get_width() // 2 + 1,
                                            button_rect.centery - button_text.get_height() // 2 + 1))
                screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                                          button_rect.centery - button_text.get_height() // 2))
        hint = font_small.render("Use ARROWS to navigate, ENTER to change, ESC to exit", True, RETRO_GRAY)
        hint_shadow = font_small.render("Use ARROWS to navigate, ENTER to change, ESC to exit", True, BLACK)
        screen.blit(hint_shadow, (self.rect.centerx - hint.get_width() // 2 + 1, self.rect.bottom - 24))
        screen.blit(hint, (self.rect.centerx - hint.get_width() // 2, self.rect.bottom - 25))
        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)


class NicknameScreen:
    def __init__(self, sound_manager=None):
        self.active = True
        self.nickname = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.error_message = ""
        self.error_timer = 0
        self.sound_manager = sound_manager
        self.must_complete = True

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        if self.error_timer > 0:
            self.error_timer -= 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.nickname) >= 2:
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    self.active = False
                    return self.nickname
                else:
                    self.error_message = "Minimum 2 characters"
                    self.error_timer = 120
            elif event.key == pygame.K_BACKSPACE:
                self.nickname = self.nickname[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.error_message = "Please enter a nickname!"
                self.error_timer = 120
                if self.sound_manager:
                    self.sound_manager.play_sound('hit')
            else:
                if len(self.nickname) < 15 and event.unicode.isprintable():
                    self.nickname += event.unicode
        return None

    def draw(self, screen):
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        font_large = pygame.font.Font(None, 42)
        font_medium = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 22)
        title = font_large.render("Welcome to", True, RETRO_SILVER)
        title_shadow = font_large.render("Welcome to", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 151))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 150))
        game_title = font_large.render("SKYWING", True, LAKERS_YELLOW)
        game_shadow = font_large.render("SKYWING", True, BLACK)
        screen.blit(game_shadow, (BASE_WIDTH // 2 - game_title.get_width() // 2 + 1, 191))
        screen.blit(game_title, (BASE_WIDTH // 2 - game_title.get_width() // 2, 190))
        input_bg = pygame.Rect(50, 280, BASE_WIDTH - 100, 50)
        pygame.draw.rect(screen, (60, 60, 80), input_bg, 0, 10)
        pygame.draw.rect(screen, RETRO_SILVER if self.cursor_visible else RETRO_GOLD, input_bg, 3, 10)
        if self.nickname:
            name_text = font_medium.render(self.nickname, True, RETRO_GOLD)
            name_shadow = font_medium.render(self.nickname, True, BLACK)
        else:
            name_text = font_medium.render("Enter your nickname", True, RETRO_GRAY)
            name_shadow = font_medium.render("Enter your nickname", True, BLACK)
        screen.blit(name_shadow, (71, 296))
        screen.blit(name_text, (70, 295))
        if self.cursor_visible and len(self.nickname) < 15:
            cursor_x = 70 + name_text.get_width() + 2
            pygame.draw.line(screen, RETRO_GOLD, (cursor_x, 295), (cursor_x, 325), 2)
        instruction = font_small.render("Press ENTER to confirm", True, RETRO_GRAY)
        instruction_shadow = font_small.render("Press ENTER to confirm", True, BLACK)
        screen.blit(instruction_shadow, (BASE_WIDTH // 2 - instruction.get_width() // 2 + 1, 351))
        screen.blit(instruction, (BASE_WIDTH // 2 - instruction.get_width() // 2, 350))
        limit_text = font_small.render("Maximum 15 characters", True, RETRO_GRAY)
        limit_shadow = font_small.render("Maximum 15 characters", True, BLACK)
        screen.blit(limit_shadow, (BASE_WIDTH // 2 - limit_text.get_width() // 2 + 1, 381))
        screen.blit(limit_text, (BASE_WIDTH // 2 - limit_text.get_width() // 2, 380))
        if self.error_timer > 0:
            error_text = font_small.render(self.error_message, True, RETRO_RED)
            error_shadow = font_small.render(self.error_message, True, BLACK)
            screen.blit(error_shadow, (BASE_WIDTH // 2 - error_text.get_width() // 2 + 1, 421))
            screen.blit(error_text, (BASE_WIDTH // 2 - error_text.get_width() // 2, 420))
        version_text = font_small.render(f"v{GAME_VERSION}", True, RETRO_GRAY)
        version_shadow = font_small.render(f"v{GAME_VERSION}", True, BLACK)
        screen.blit(version_shadow, (BASE_WIDTH - version_text.get_width() - 9, BASE_HEIGHT - 24))
        screen.blit(version_text, (BASE_WIDTH - version_text.get_width() - 10, BASE_HEIGHT - 25))
        if control_manager.control_type == ControlType.GAMEPAD:
            indicator = "Gamepad"
            indicator_color = RETRO_BLUE
        elif control_manager.control_type == ControlType.TOUCH:
            indicator = "Touch"
            indicator_color = RETRO_GREEN
        else:
            indicator = "Keyboard"
            indicator_color = RETRO_YELLOW
        indicator_text = font_small.render(indicator, True, indicator_color)
        indicator_shadow = font_small.render(indicator, True, BLACK)
        screen.blit(indicator_shadow, (BASE_WIDTH - indicator_text.get_width() - 9, 6))
        screen.blit(indicator_text, (BASE_WIDTH - indicator_text.get_width() - 10, 5))


class ControlsScreen:
    def __init__(self, sound_manager=None):
        self.sound_manager = sound_manager
        self.active = True
        self.scroll_offset = 0
        self.back_rect = None
        self.animation = 0

    def draw(self, screen):
        self.animation += 0.02

        for y in range(BASE_HEIGHT):
            t = y / BASE_HEIGHT
            r = int(25 * (1 - t) + 40 * t)
            g = int(22 * (1 - t) + 35 * t)
            b = int(30 * (1 - t) + 50 * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (BASE_WIDTH, y))

        for i in range(5):
            x = (i * 90 + self.animation * 30) % (BASE_WIDTH + 60) - 30
            y = 80 + i * 100
            pulse = math.sin(self.animation * 2 + i) * 0.5 + 0.5
            alpha = int(40 + 30 * pulse)
            glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 150, 200, alpha), (40, 40), 40)
            screen.blit(glow_surf, (x - 40, y - 40))

        title_bg = pygame.Rect(BASE_WIDTH // 2 - 130, 10, 260, 45)
        title_surf = pygame.Surface((title_bg.width, title_bg.height), pygame.SRCALPHA)
        pygame.draw.rect(title_surf, (20, 20, 40, 220), title_surf.get_rect(), 0, 15)
        pygame.draw.rect(title_surf, RETRO_GOLD, title_surf.get_rect(), 2, 15)
        screen.blit(title_surf, title_bg)

        font_title = pygame.font.Font(None, 34)
        font_header = pygame.font.Font(None, 26)
        font_text = pygame.font.Font(None, 22)
        font_small = pygame.font.Font(None, 18)

        title = font_title.render("Game Controls", True, RETRO_GOLD)
        title_shadow = font_title.render("Game Controls", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 18))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 17))

        start_y = 70 - self.scroll_offset
        y = start_y

        if IS_ANDROID:
            section_y = y
            section_height = 180
            section_rect = pygame.Rect(15, section_y, BASE_WIDTH - 30, section_height)
            section_surf = pygame.Surface((section_rect.width, section_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(section_surf, (30, 40, 60, 180), section_surf.get_rect(), 0, 12)
            pygame.draw.rect(section_surf, RETRO_GREEN, section_surf.get_rect(), 2, 12)
            screen.blit(section_surf, section_rect)

            header = font_header.render("TOUCH CONTROLS", True, RETRO_GREEN)
            header_shadow = font_header.render("TOUCH CONTROLS", True, BLACK)
            screen.blit(header_shadow, (28, section_y + 10))
            screen.blit(header, (27, section_y + 9))

            touch_controls_list = [
                "Left thumb: virtual joystick",
                "Right buttons: actions",
                "Tennis: move with joystick, tap action buttons",
                "Basketball: aim with joystick, hold & release SHOOT",
                "All buttons have visual feedback",
            ]
            y_off = section_y + 40
            for line in touch_controls_list:
                text = font_text.render(line, True, RETRO_SILVER)
                text_shadow = font_text.render(line, True, BLACK)
                screen.blit(text_shadow, (28 + 1, y_off + 1))
                screen.blit(text, (28, y_off))
                y_off += 24

            y = section_y + section_height + 15

        section_y = y
        section_height = 220
        section_rect = pygame.Rect(15, section_y, BASE_WIDTH - 30, section_height)
        section_surf = pygame.Surface((section_rect.width, section_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(section_surf, (30, 40, 60, 180), section_surf.get_rect(), 0, 12)
        pygame.draw.rect(section_surf, RETRO_BLUE, section_surf.get_rect(), 2, 12)
        screen.blit(section_surf, section_rect)

        header = font_header.render("TENNIS", True, RETRO_BLUE)
        header_shadow = font_header.render("TENNIS", True, BLACK)
        screen.blit(header_shadow, (28, section_y + 10))
        screen.blit(header, (27, section_y + 9))

        tennis_controls = [
            ("Keyboard:", "Arrows - Movement"),
            ("Q - Left Shot", "E - Right Shot"),
            ("F - Slice", "W - Straight"),
            ("R - Nadal Topspin", "(slow, heavy spin)"),
            ("SPACE - Charge", ""),
            ("Gamepad:", "Left Stick - Move"),
            ("LB - Left Shot", "RB - Right Shot"),
            ("X - Slice", "Y - Straight"),
            ("RT - Nadal Topspin", "(curved shot)"),
        ]

        y_off = section_y + 40
        for line1, line2 in tennis_controls:
            if y_off + 20 > 0:
                if line1:
                    if line1 in ["Keyboard:", "Gamepad:"]:
                        text_color = RETRO_GOLD
                    else:
                        text_color = RETRO_SILVER
                    text1 = font_text.render(line1, True, text_color)
                    text1_shadow = font_text.render(line1, True, BLACK)
                    screen.blit(text1_shadow, (28 + 1, y_off + 1))
                    screen.blit(text1, (28, y_off))
                if line2:
                    text2 = font_small.render(line2, True, RETRO_GRAY)
                    text2_shadow = font_small.render(line2, True, BLACK)
                    screen.blit(text2_shadow, (180 + 1, y_off + 3))
                    screen.blit(text2, (180, y_off + 2))
                y_off += 22

        y = section_y + section_height + 15

        section_y = y
        section_height = 140
        section_rect = pygame.Rect(15, section_y, BASE_WIDTH - 30, section_height)
        section_surf = pygame.Surface((section_rect.width, section_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(section_surf, (60, 40, 25, 180), section_surf.get_rect(), 0, 12)
        pygame.draw.rect(section_surf, RETRO_ORANGE, section_surf.get_rect(), 2, 12)
        screen.blit(section_surf, section_rect)

        header = font_header.render("BASKETBALL", True, RETRO_ORANGE)
        header_shadow = font_header.render("BASKETBALL", True, BLACK)
        screen.blit(header_shadow, (28, section_y + 10))
        screen.blit(header, (27, section_y + 9))

        basketball_controls = [
            ("Keyboard:", "Arrows - Aim"),
            ("SPACE - Shoot", ""),
            ("Gamepad:", "Left Stick - Aim"),
            ("A - Shoot", ""),
        ]

        y_off = section_y + 40
        for line1, line2 in basketball_controls:
            if y_off + 20 > 0:
                if line1:
                    if line1 in ["Keyboard:", "Gamepad:"]:
                        text_color = RETRO_GOLD
                    else:
                        text_color = RETRO_SILVER
                    text1 = font_text.render(line1, True, text_color)
                    text1_shadow = font_text.render(line1, True, BLACK)
                    screen.blit(text1_shadow, (28 + 1, y_off + 1))
                    screen.blit(text1, (28, y_off))
                if line2:
                    text2 = font_small.render(line2, True, RETRO_GRAY)
                    text2_shadow = font_small.render(line2, True, BLACK)
                    screen.blit(text2_shadow, (180 + 1, y_off + 3))
                    screen.blit(text2, (180, y_off + 2))
                y_off += 22

        y = section_y + section_height + 15

        section_y = y
        section_height = 90
        section_rect = pygame.Rect(15, section_y, BASE_WIDTH - 30, section_height)
        section_surf = pygame.Surface((section_rect.width, section_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(section_surf, (30, 50, 35, 180), section_surf.get_rect(), 0, 12)
        pygame.draw.rect(section_surf, RETRO_GREEN, section_surf.get_rect(), 2, 12)
        screen.blit(section_surf, section_rect)

        header = font_header.render("TIPS", True, RETRO_GREEN)
        header_shadow = font_header.render("TIPS", True, BLACK)
        screen.blit(header_shadow, (28, section_y + 10))
        screen.blit(header, (27, section_y + 9))

        tips = [
            "Release shot in green zone for perfect hit",
            "Perfect shots give bonus points",
            "Win matches to earn coins and XP",
        ]
        y_off = section_y + 40
        for tip in tips:
            tip_text = font_small.render(f"* {tip}", True, RETRO_SILVER)
            tip_shadow = font_small.render(f"* {tip}", True, BLACK)
            screen.blit(tip_shadow, (28 + 1, y_off + 1))
            screen.blit(tip_text, (28, y_off))
            y_off += 18

        y = section_y + section_height + 15

        version_text = font_small.render(f"v{GAME_VERSION}", True, RETRO_GRAY)
        version_shadow = font_small.render(f"v{GAME_VERSION}", True, BLACK)
        screen.blit(version_shadow, (BASE_WIDTH - version_text.get_width() - 9, BASE_HEIGHT - 24))
        screen.blit(version_text, (BASE_WIDTH - version_text.get_width() - 10, BASE_HEIGHT - 25))

        if control_manager.control_type == ControlType.GAMEPAD:
            indicator = "Gamepad"
            indicator_color = RETRO_BLUE
        elif control_manager.control_type == ControlType.TOUCH:
            indicator = "Touch"
            indicator_color = RETRO_GREEN
        else:
            indicator = "Keyboard"
            indicator_color = RETRO_YELLOW
        indicator_text = font_small.render(indicator, True, indicator_color)
        indicator_shadow = font_small.render(indicator, True, BLACK)
        screen.blit(indicator_shadow, (BASE_WIDTH - indicator_text.get_width() - 9, 6))
        screen.blit(indicator_text, (BASE_WIDTH - indicator_text.get_width() - 10, 5))

        self.back_rect = pygame.Rect(BASE_WIDTH // 2 - 100, BASE_HEIGHT - 55, 200, 40)
        back_surf = pygame.Surface((self.back_rect.width, self.back_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(back_surf, (RETRO_PURPLE[0], RETRO_PURPLE[1], RETRO_PURPLE[2], 230),
                         back_surf.get_rect(), 0, 12)
        pygame.draw.rect(back_surf, RETRO_SILVER, back_surf.get_rect(), 2, 12)
        screen.blit(back_surf, self.back_rect)

        back_text = font_text.render("Back", True, RETRO_GOLD)
        back_shadow = font_text.render("Back", True, BLACK)
        screen.blit(back_shadow, (
            self.back_rect.centerx - back_text.get_width() // 2 + 1,
            self.back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text,
                    (self.back_rect.centerx - back_text.get_width() // 2,
                     self.back_rect.centery - back_text.get_height() // 2))

        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)
        return self.back_rect

    def handle_scroll(self, y):
        self.scroll_offset = max(0, min(500, self.scroll_offset + y))

    def handle_click(self, x, y):
        if self.back_rect and self.back_rect.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            return "back"
        return None


class DuelSetupScreen:
    def __init__(self, sound_manager=None):
        self.sound_manager = sound_manager
        self.stage = "skins"
        self.back_rect = None
        self.animation = 0
        self.p1_control = "keyboard"
        self.p2_control = "gamepad"
        self.p1_skin = None
        self.p2_skin = None
        self.court = None
        self.skin_page = 0
        self.scroll_offset = 0
        self.skin_cursor_p1 = 0
        self.skin_cursor_p2 = 0
        self.skin_selection_done_p1 = False
        self.skin_selection_done_p2 = False
        self.available_skins = []
        self.p1_nav_cooldown = 0
        self.p2_nav_cooldown = 0
        self.p1_confirm_cooldown = 0
        self.p2_confirm_cooldown = 0
        self.background_manager = None
        self.dragging_scrollbar = False
        self.scrollbar_rect = None
        self.scroll_handle_rect = None
        self.skins_per_row = 5
        self.cell_size = 52
        self.pool_start_y = 262
        self.pool_height = 268

    def reset(self):
        self.stage = "skins"
        self.p1_control = "keyboard"
        self.p2_control = "gamepad" if len(joysticks) > 0 else "keyboard"
        self.p1_skin = None
        self.p2_skin = None
        self.court = None
        self.skin_page = 0
        self.scroll_offset = 0
        self.skin_cursor_p1 = 0
        self.skin_cursor_p2 = 0
        self.skin_selection_done_p1 = False
        self.skin_selection_done_p2 = False
        self.p1_confirm_cooldown = 0
        self.p2_confirm_cooldown = 0
        self.dragging_scrollbar = False
        self.scrollbar_rect = None
        self.scroll_handle_rect = None

    def set_available_skins(self, skins):
        self.available_skins = skins

    def _get_max_scroll(self):
        if not self.available_skins:
            return 0
        skins_per_row = self.skins_per_row
        total_rows = (len(self.available_skins) + skins_per_row - 1) // skins_per_row
        total_height = total_rows * (self.cell_size + 8)
        visible_height = self.pool_height - 28
        return max(0, total_height - visible_height)

    def _get_row_for_cursor(self, cursor):
        return cursor // self.skins_per_row

    def _ensure_cursor_visible(self, cursor, is_p1=True):
        max_scroll = self._get_max_scroll()
        if max_scroll <= 0:
            self.scroll_offset = 0
            return
        row = self._get_row_for_cursor(cursor)
        cursor_y = row * (self.cell_size + 8)
        visible_height = self.pool_height - 28
        if cursor_y < self.scroll_offset:
            self.scroll_offset = cursor_y
        elif cursor_y + self.cell_size > self.scroll_offset + visible_height:
            self.scroll_offset = cursor_y + self.cell_size - visible_height
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset))

    def update(self):
        if self.stage == "skins":
            if self.p1_nav_cooldown > 0:
                self.p1_nav_cooldown -= 1
            if self.p2_nav_cooldown > 0:
                self.p2_nav_cooldown -= 1
            if self.p1_confirm_cooldown > 0:
                self.p1_confirm_cooldown -= 1
            if self.p2_confirm_cooldown > 0:
                self.p2_confirm_cooldown -= 1

            if not self.skin_selection_done_p1:
                keys = pygame.key.get_pressed()
                if self.p1_nav_cooldown == 0:
                    if keys[pygame.K_d] and not keys[pygame.K_a]:
                        self.skin_cursor_p1 = (self.skin_cursor_p1 + 1) % max(1, len(self.available_skins))
                        self.p1_nav_cooldown = 10
                        self._ensure_cursor_visible(self.skin_cursor_p1, True)
                        if self.sound_manager:
                            self.sound_manager.play_button()
                    elif keys[pygame.K_a] and not keys[pygame.K_d]:
                        self.skin_cursor_p1 = (self.skin_cursor_p1 - 1) % max(1, len(self.available_skins))
                        self.p1_nav_cooldown = 10
                        self._ensure_cursor_visible(self.skin_cursor_p1, True)
                        if self.sound_manager:
                            self.sound_manager.play_button()
                    elif keys[pygame.K_s] and not keys[pygame.K_w]:
                        new_cursor = self.skin_cursor_p1 + self.skins_per_row
                        if new_cursor < len(self.available_skins):
                            self.skin_cursor_p1 = new_cursor
                        else:
                            self.skin_cursor_p1 = len(self.available_skins) - 1
                        self.p1_nav_cooldown = 10
                        self._ensure_cursor_visible(self.skin_cursor_p1, True)
                        if self.sound_manager:
                            self.sound_manager.play_button()
                    elif keys[pygame.K_w] and not keys[pygame.K_s]:
                        new_cursor = self.skin_cursor_p1 - self.skins_per_row
                        if new_cursor >= 0:
                            self.skin_cursor_p1 = new_cursor
                        else:
                            self.skin_cursor_p1 = 0
                        self.p1_nav_cooldown = 10
                        self._ensure_cursor_visible(self.skin_cursor_p1, True)
                        if self.sound_manager:
                            self.sound_manager.play_button()

                if keys[pygame.K_SPACE] and self.p1_confirm_cooldown == 0:
                    if self.available_skins:
                        self.p1_skin = self.available_skins[self.skin_cursor_p1]
                        self.skin_selection_done_p1 = True
                        self.p1_confirm_cooldown = 20
                        if self.sound_manager:
                            self.sound_manager.play_button()

            if not self.skin_selection_done_p2 and len(joysticks) > 0:
                gamepad = joysticks[0]
                if self.p2_nav_cooldown == 0:
                    try:
                        hat = gamepad.get_hat(0)
                        axis_x = gamepad.get_axis(0)
                        axis_y = gamepad.get_axis(1)
                        nav = False
                        if hat[0] > 0 or axis_x > 0.5:
                            self.skin_cursor_p2 = (self.skin_cursor_p2 + 1) % max(1, len(self.available_skins))
                            nav = True
                        elif hat[0] < 0 or axis_x < -0.5:
                            self.skin_cursor_p2 = (self.skin_cursor_p2 - 1) % max(1, len(self.available_skins))
                            nav = True
                        elif hat[1] < 0 or axis_y > 0.5:
                            new_cursor = self.skin_cursor_p2 + self.skins_per_row
                            if new_cursor < len(self.available_skins):
                                self.skin_cursor_p2 = new_cursor
                            else:
                                self.skin_cursor_p2 = len(self.available_skins) - 1
                            nav = True
                        elif hat[1] > 0 or axis_y < -0.5:
                            new_cursor = self.skin_cursor_p2 - self.skins_per_row
                            if new_cursor >= 0:
                                self.skin_cursor_p2 = new_cursor
                            else:
                                self.skin_cursor_p2 = 0
                            nav = True
                        if nav:
                            self.p2_nav_cooldown = 10
                            self._ensure_cursor_visible(self.skin_cursor_p2, False)
                            if self.sound_manager:
                                self.sound_manager.play_button()
                    except:
                        pass

                try:
                    if gamepad.get_numbuttons() > 0 and gamepad.get_button(0) and self.p2_confirm_cooldown == 0:
                        if self.available_skins:
                            skin = self.available_skins[self.skin_cursor_p2]
                            if self.skin_selection_done_p1:
                                if skin != self.p1_skin:
                                    self.p2_skin = skin
                                    self.skin_selection_done_p2 = True
                                    self.p2_confirm_cooldown = 20
                                    if self.sound_manager:
                                        self.sound_manager.play_button()
                            else:
                                self.p2_skin = skin
                                self.skin_selection_done_p2 = True
                                self.p2_confirm_cooldown = 20
                                if self.sound_manager:
                                    self.sound_manager.play_button()
                except:
                    pass

            if self.skin_selection_done_p1 and self.skin_selection_done_p2:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN] and self.p1_confirm_cooldown == 0:
                    self.stage = "court"
                    self.p1_confirm_cooldown = 20
                    if self.sound_manager:
                        self.sound_manager.play_button()

    def _draw_default_bg(self, screen):
        for y in range(BASE_HEIGHT):
            t = y / BASE_HEIGHT
            r = int(30 * (1 - t) + 50 * t)
            g = int(35 * (1 - t) + 45 * t)
            b = int(60 * (1 - t) + 70 * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (BASE_WIDTH, y))

    def draw_court_icon(self, screen, rect, surface):
        inner = rect.inflate(-8, -8)
        if surface == 'clay':
            pygame.draw.rect(screen, (193, 100, 67), inner, 0, 6)
            line_color = (245, 225, 200)
        elif surface == 'grass':
            pygame.draw.rect(screen, (68, 148, 74), inner, 0, 6)
            line_color = (220, 255, 220)
        else:
            pygame.draw.rect(screen, (77, 88, 96), inner, 0, 6)
            line_color = (200, 215, 230)
        pygame.draw.rect(screen, line_color, inner, 1, 6)
        pygame.draw.line(screen, line_color, (inner.centerx, inner.top + 4),
                         (inner.centerx, inner.bottom - 4), 1)
        pygame.draw.line(screen, line_color, (inner.left + 4, inner.centery),
                         (inner.right - 4, inner.centery), 1)
        net_offset = 3
        pygame.draw.line(screen, line_color,
                         (inner.left + 4, inner.centery - 2),
                         (inner.right - 4, inner.centery - 2), 1)
        for x in range(inner.left + 4, inner.right - 4, 3):
            pygame.draw.line(screen, (line_color[0], line_color[1], line_color[2], 150),
                             (x, inner.centery - 2), (x, inner.centery + 2), 1)

    def draw(self, screen):
        self.animation += 0.02

        if self.background_manager:
            bg = self.background_manager.get_random_background()
            if bg:
                screen.blit(bg, (0, 0))
            else:
                self._draw_default_bg(screen)
        else:
            self._draw_default_bg(screen)

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 38)
        font_medium = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 15)

        title_bg = pygame.Rect(BASE_WIDTH // 2 - 110, 8, 220, 40)
        title_surf = pygame.Surface((title_bg.width, title_bg.height), pygame.SRCALPHA)
        pygame.draw.rect(title_surf, (20, 20, 40, 220), title_surf.get_rect(), 0, 15)
        pygame.draw.rect(title_surf, RETRO_GOLD, title_surf.get_rect(), 2, 15)
        screen.blit(title_surf, title_bg)
        title = font_large.render("DUEL MODE", True, RETRO_GOLD)
        title_shadow = font_large.render("DUEL MODE", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title.get_width() // 2 + 1, 13))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 12))

        if self.stage == "skins":
            subtitle = font_medium.render("SELECT YOUR SKIN", True, RETRO_SILVER)
            subtitle_shadow = font_medium.render("SELECT YOUR SKIN", True, BLACK)
            screen.blit(subtitle_shadow, (BASE_WIDTH // 2 - subtitle.get_width() // 2 + 1, 54))
            screen.blit(subtitle, (BASE_WIDTH // 2 - subtitle.get_width() // 2, 53))

            p1_panel = pygame.Rect(10, 80, 165, 170)
            p1_panel_surf = pygame.Surface((p1_panel.width, p1_panel.height), pygame.SRCALPHA)
            pygame.draw.rect(p1_panel_surf, (20, 40, 30, 230), p1_panel_surf.get_rect(), 0, 12)
            pygame.draw.rect(p1_panel_surf, RETRO_GREEN if self.skin_selection_done_p1 else RETRO_SILVER,
                             p1_panel_surf.get_rect(), 2, 12)
            screen.blit(p1_panel_surf, p1_panel)

            p1_header = font_small.render("PLAYER 1", True, RETRO_GREEN)
            p1_header_shadow = font_small.render("PLAYER 1", True, BLACK)
            screen.blit(p1_header_shadow, (p1_panel.centerx - p1_header.get_width() // 2 + 1, p1_panel.y + 6))
            screen.blit(p1_header, (p1_panel.centerx - p1_header.get_width() // 2, p1_panel.y + 5))

            p1_dev = font_tiny.render("[KEYBOARD]", True, RETRO_GRAY)
            screen.blit(p1_dev, (p1_panel.centerx - p1_dev.get_width() // 2, p1_panel.y + 22))

            p1_img_frame = pygame.Rect(p1_panel.centerx - 35, p1_panel.y + 40, 70, 70)
            pygame.draw.rect(screen, (10, 25, 20), p1_img_frame, 0, 10)
            pygame.draw.rect(screen, RETRO_GREEN if self.skin_selection_done_p1 else RETRO_GRAY, p1_img_frame, 2,
                             10)
            if self.p1_skin and hasattr(self.p1_skin, 'image') and self.p1_skin.image is not None:
                img = pygame.transform.scale(self.p1_skin.image, (60, 60))
                screen.blit(img, (p1_img_frame.centerx - 30, p1_img_frame.centery - 30))
            elif self.available_skins and not self.skin_selection_done_p1:
                preview_skin = self.available_skins[self.skin_cursor_p1]
                if hasattr(preview_skin, 'image') and preview_skin.image is not None:
                    img = pygame.transform.scale(preview_skin.image, (60, 60))
                    screen.blit(img, (p1_img_frame.centerx - 30, p1_img_frame.centery - 30))

            if self.p1_skin:
                p1_name = font_small.render(self.p1_skin.name[:14], True, RETRO_GOLD)
                p1_name_shadow = font_small.render(self.p1_skin.name[:14], True, BLACK)
                screen.blit(p1_name_shadow, (p1_panel.centerx - p1_name.get_width() // 2 + 1, p1_panel.y + 115))
                screen.blit(p1_name, (p1_panel.centerx - p1_name.get_width() // 2, p1_panel.y + 114))
            else:
                p1_name = font_small.render("CHOOSING...", True, RETRO_YELLOW)
                screen.blit(p1_name, (p1_panel.centerx - p1_name.get_width() // 2, p1_panel.y + 114))

            p1_status = font_tiny.render("READY" if self.skin_selection_done_p1 else "WASD + SPACE",
                                         True, RETRO_GREEN if self.skin_selection_done_p1 else RETRO_GRAY)
            screen.blit(p1_status, (p1_panel.centerx - p1_status.get_width() // 2, p1_panel.bottom - 20))

            p2_panel = pygame.Rect(BASE_WIDTH - 175, 80, 165, 170)
            p2_panel_surf = pygame.Surface((p2_panel.width, p2_panel.height), pygame.SRCALPHA)
            pygame.draw.rect(p2_panel_surf, (40, 20, 20, 230), p2_panel_surf.get_rect(), 0, 12)
            pygame.draw.rect(p2_panel_surf, RETRO_RED if self.skin_selection_done_p2 else RETRO_SILVER,
                             p2_panel_surf.get_rect(), 2, 12)
            screen.blit(p2_panel_surf, p2_panel)

            p2_header = font_small.render("PLAYER 2", True, RETRO_RED)
            p2_header_shadow = font_small.render("PLAYER 2", True, BLACK)
            screen.blit(p2_header_shadow, (p2_panel.centerx - p2_header.get_width() // 2 + 1, p2_panel.y + 6))
            screen.blit(p2_header, (p2_panel.centerx - p2_header.get_width() // 2, p2_panel.y + 5))

            if len(joysticks) > 0:
                p2_dev = font_tiny.render("[GAMEPAD]", True, RETRO_GRAY)
            else:
                p2_dev = font_tiny.render("[NO GAMEPAD]", True, RETRO_RED)
            screen.blit(p2_dev, (p2_panel.centerx - p2_dev.get_width() // 2, p2_panel.y + 22))

            p2_img_frame = pygame.Rect(p2_panel.centerx - 35, p2_panel.y + 40, 70, 70)
            pygame.draw.rect(screen, (25, 10, 10), p2_img_frame, 0, 10)
            pygame.draw.rect(screen, RETRO_RED if self.skin_selection_done_p2 else RETRO_GRAY, p2_img_frame, 2, 10)
            if self.p2_skin and hasattr(self.p2_skin, 'image') and self.p2_skin.image is not None:
                img = pygame.transform.scale(self.p2_skin.image, (60, 60))
                screen.blit(img, (p2_img_frame.centerx - 30, p2_img_frame.centery - 30))
            elif self.available_skins and not self.skin_selection_done_p2:
                preview_skin = self.available_skins[self.skin_cursor_p2]
                if hasattr(preview_skin, 'image') and preview_skin.image is not None:
                    img = pygame.transform.scale(preview_skin.image, (60, 60))
                    screen.blit(img, (p2_img_frame.centerx - 30, p2_img_frame.centery - 30))

            if self.p2_skin:
                p2_name = font_small.render(self.p2_skin.name[:14], True, RETRO_GOLD)
                p2_name_shadow = font_small.render(self.p2_skin.name[:14], True, BLACK)
                screen.blit(p2_name_shadow, (p2_panel.centerx - p2_name.get_width() // 2 + 1, p2_panel.y + 115))
                screen.blit(p2_name, (p2_panel.centerx - p2_name.get_width() // 2, p2_panel.y + 114))
            else:
                p2_name = font_small.render("CHOOSING...", True, RETRO_YELLOW)
                screen.blit(p2_name, (p2_panel.centerx - p2_name.get_width() // 2, p2_panel.y + 114))

            p2_status = font_tiny.render("READY" if self.skin_selection_done_p2 else "D-PAD + A",
                                         True, RETRO_GREEN if self.skin_selection_done_p2 else RETRO_GRAY)
            screen.blit(p2_status, (p2_panel.centerx - p2_status.get_width() // 2, p2_panel.bottom - 20))

            vs_x = BASE_WIDTH // 2
            vs_y = 155
            vs_circle = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(vs_circle, (30, 30, 50, 240), (20, 20), 20)
            pygame.draw.circle(vs_circle, RETRO_GOLD, (20, 20), 20, 2)
            screen.blit(vs_circle, (vs_x - 20, vs_y - 20))
            vs_text = font_medium.render("VS", True, RETRO_GOLD)
            vs_shadow = font_medium.render("VS", True, BLACK)
            screen.blit(vs_shadow, (vs_x - vs_text.get_width() // 2 + 1, vs_y - vs_text.get_height() // 2 + 1))
            screen.blit(vs_text, (vs_x - vs_text.get_width() // 2, vs_y - vs_text.get_height() // 2))

            pool_y = self.pool_start_y
            pool_height = self.pool_height
            pool_rect = pygame.Rect(8, pool_y, BASE_WIDTH - 8, pool_height)
            pool_surf = pygame.Surface((pool_rect.width, pool_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(pool_surf, (20, 20, 40, 230), pool_surf.get_rect(), 0, 14)
            pygame.draw.rect(pool_surf, RETRO_GOLD, pool_surf.get_rect(), 2, 14)
            screen.blit(pool_surf, pool_rect)

            pool_title = font_small.render(f"ALL TENNIS SKINS ({len(self.available_skins)})", True, RETRO_GOLD)
            pool_title_shadow = font_small.render(f"ALL TENNIS SKINS ({len(self.available_skins)})", True, BLACK)
            screen.blit(pool_title_shadow, (BASE_WIDTH // 2 - pool_title.get_width() // 2 + 1, pool_y + 7))
            screen.blit(pool_title, (BASE_WIDTH // 2 - pool_title.get_width() // 2, pool_y + 6))

            skins_area = pygame.Rect(10, pool_y + 24, BASE_WIDTH - 24, pool_height - 30)
            clip_prev = screen.get_clip()
            screen.set_clip(skins_area)

            skins_per_row = self.skins_per_row
            cell_size = self.cell_size
            start_x = 15
            start_y = pool_y + 28 - self.scroll_offset

            for i, skin in enumerate(self.available_skins):
                row = i // skins_per_row
                col = i % skins_per_row
                x = start_x + col * (cell_size + 8)
                y = start_y + row * (cell_size + 8)

                if y + cell_size < pool_y + 24 or y > pool_y + pool_height - 6:
                    continue

                skin_rect = pygame.Rect(x, y, cell_size, cell_size)

                if not self.skin_selection_done_p1 and self.skin_cursor_p1 == i:
                    pygame.draw.rect(screen, RETRO_GREEN, skin_rect.inflate(6, 6), 0, 8)
                if not self.skin_selection_done_p2 and self.skin_cursor_p2 == i:
                    pygame.draw.rect(screen, RETRO_RED, skin_rect.inflate(12, 12), 0, 10)

                if skin.image is not None:
                    img = pygame.transform.scale(skin.image, (cell_size, cell_size))
                    screen.blit(img, skin_rect)
                else:
                    pygame.draw.rect(screen, (80, 80, 100), skin_rect, 0, 6)
                    txt = font_tiny.render(skin.name[:5], True, RETRO_GOLD)
                    screen.blit(txt, (skin_rect.centerx - txt.get_width() // 2,
                                      skin_rect.centery - txt.get_height() // 2))

                pygame.draw.rect(screen, skin.rarity_color, skin_rect, 2, 8)

            screen.set_clip(clip_prev)

            max_scroll = self._get_max_scroll()
            if max_scroll > 0:
                scrollbar_bg = pygame.Rect(BASE_WIDTH - 14, pool_y + 24, 8, pool_height - 30)
                pygame.draw.rect(screen, (40, 40, 55), scrollbar_bg, 0, 4)
                visible_height = pool_height - 30
                content_height = visible_height + max_scroll
                handle_height = max(28, int(visible_height * (visible_height / content_height)))
                if handle_height > visible_height:
                    handle_height = visible_height
                handle_y = pool_y + 24 + int((self.scroll_offset / max_scroll) * (visible_height - handle_height))
                self.scroll_handle_rect = pygame.Rect(BASE_WIDTH - 14, handle_y, 8, handle_height)
                pygame.draw.rect(screen, RETRO_GOLD, self.scroll_handle_rect, 0, 4)
                pygame.draw.rect(screen, RETRO_SILVER, self.scroll_handle_rect, 1, 4)
                self.scrollbar_rect = scrollbar_bg
            else:
                self.scroll_handle_rect = None
                self.scrollbar_rect = None

            if self.skin_selection_done_p1 and self.skin_selection_done_p2:
                ready = font_medium.render("PRESS ENTER TO CONTINUE", True, RETRO_GOLD)
                ready_shadow = font_medium.render("PRESS ENTER TO CONTINUE", True, BLACK)
                pulse = math.sin(self.animation * 5) * 3
                ready_bg = pygame.Surface((ready.get_width() + 30, 34), pygame.SRCALPHA)
                pygame.draw.rect(ready_bg, (0, 0, 0, 220), ready_bg.get_rect(), 0, 10)
                pygame.draw.rect(ready_bg, RETRO_GOLD, ready_bg.get_rect(), 2, 10)
                screen.blit(ready_bg, (BASE_WIDTH // 2 - ready.get_width() // 2 - 15,
                                       BASE_HEIGHT - 68 + pulse))
                screen.blit(ready_shadow, (
                    BASE_WIDTH // 2 - ready.get_width() // 2 + 1, BASE_HEIGHT - 61 + pulse))
                screen.blit(ready, (BASE_WIDTH // 2 - ready.get_width() // 2, BASE_HEIGHT - 62 + pulse))

        elif self.stage == "court":
            subtitle = font_medium.render("SELECT COURT", True, RETRO_SILVER)
            subtitle_shadow = font_medium.render("SELECT COURT", True, BLACK)
            screen.blit(subtitle_shadow, (BASE_WIDTH // 2 - subtitle.get_width() // 2 + 1, 65))
            screen.blit(subtitle, (BASE_WIDTH // 2 - subtitle.get_width() // 2, 64))

            courts = [
                ("Hard Court", "hard", TENNIS_HARD, "Fast and balanced surface"),
                ("Clay Court", "clay", TENNIS_CLAY, "Slow surface, high bounce"),
                ("Grass Court", "grass", TENNIS_GRASS, "Fast and low bounce"),
            ]

            for i, (name, key, color, desc) in enumerate(courts):
                y = 130 + i * 115
                rect = pygame.Rect(30, y, BASE_WIDTH - 60, 90)
                selected = self.court == key

                rect_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                if selected:
                    pygame.draw.rect(rect_surf, (155, 89, 182, 245), rect_surf.get_rect(), 0, 14)
                    glow_color = RETRO_GOLD
                else:
                    pygame.draw.rect(rect_surf, (35, 35, 50, 235), rect_surf.get_rect(), 0, 14)
                    glow_color = RETRO_GRAY
                screen.blit(rect_surf, rect)

                if selected:
                    pulse = math.sin(self.animation * 4) * 2
                    pygame.draw.rect(screen, glow_color, rect.inflate(pulse, pulse), 3, 14)
                else:
                    pygame.draw.rect(screen, glow_color, rect, 2, 14)

                icon_frame = pygame.Rect(rect.x + 10, rect.y + 15, 60, 60)
                pygame.draw.rect(screen, (15, 15, 25), icon_frame, 0, 8)
                pygame.draw.rect(screen, glow_color, icon_frame, 2, 8)

                inner_rect = icon_frame.inflate(-8, -8)
                if key == 'clay':
                    pygame.draw.rect(screen, (193, 100, 67), inner_rect, 0, 4)
                    line_color = (245, 225, 200)
                elif key == 'grass':
                    pygame.draw.rect(screen, (68, 148, 74), inner_rect, 0, 4)
                    line_color = (220, 255, 220)
                else:
                    pygame.draw.rect(screen, (77, 88, 96), inner_rect, 0, 4)
                    line_color = (200, 215, 230)

                pygame.draw.rect(screen, line_color, inner_rect, 1, 4)
                pygame.draw.line(screen, line_color, (inner_rect.centerx, inner_rect.top + 2),
                                 (inner_rect.centerx, inner_rect.bottom - 2), 1)
                pygame.draw.line(screen, line_color, (inner_rect.left + 2, inner_rect.centery),
                                 (inner_rect.right - 2, inner_rect.centery), 1)
                for x in range(inner_rect.left + 2, inner_rect.right - 2, 4):
                    pygame.draw.line(screen, line_color, (x, inner_rect.centery - 3),
                                     (x, inner_rect.centery + 3), 1)
                pygame.draw.circle(screen, line_color, (inner_rect.centerx, inner_rect.centery - 6), 5, 1)
                pygame.draw.circle(screen, line_color, (inner_rect.centerx, inner_rect.centery + 6), 5, 1)

                court_text = font_medium.render(name, True, RETRO_GOLD if selected else RETRO_SILVER)
                court_shadow = font_medium.render(name, True, BLACK)
                screen.blit(court_shadow, (rect.x + 81, rect.y + 19))
                screen.blit(court_text, (rect.x + 80, rect.y + 18))

                court_desc = font_tiny.render(desc, True, RETRO_GRAY)
                court_desc_shadow = font_tiny.render(desc, True, BLACK)
                screen.blit(court_desc_shadow, (rect.x + 81, rect.y + 46))
                screen.blit(court_desc, (rect.x + 80, rect.y + 45))

                surface_label = key.upper() + " SURFACE"
                label_color = color
                surface_text = font_tiny.render(surface_label, True, label_color)
                surface_shadow = font_tiny.render(surface_label, True, BLACK)
                screen.blit(surface_shadow, (rect.x + 81, rect.y + 66))
                screen.blit(surface_text, (rect.x + 80, rect.y + 65))

                if selected:
                    check_circle = pygame.Surface((28, 28), pygame.SRCALPHA)
                    pygame.draw.circle(check_circle, RETRO_GREEN, (14, 14), 13)
                    pygame.draw.circle(check_circle, RETRO_WHITE, (14, 14), 13, 2)
                    screen.blit(check_circle, (rect.right - 42, rect.centery - 14))
                    pygame.draw.line(screen, RETRO_WHITE,
                                     (rect.right - 35, rect.centery),
                                     (rect.right - 31, rect.centery + 5), 3)
                    pygame.draw.line(screen, RETRO_WHITE,
                                     (rect.right - 31, rect.centery + 5),
                                     (rect.right - 22, rect.centery - 5), 3)

            hint = font_small.render("CLICK TO SELECT", True, RETRO_GOLD)
            hint_shadow = font_small.render("CLICK TO SELECT", True, BLACK)
            screen.blit(hint_shadow, (BASE_WIDTH // 2 - hint.get_width() // 2 + 1, BASE_HEIGHT - 38))
            screen.blit(hint, (BASE_WIDTH // 2 - hint.get_width() // 2, BASE_HEIGHT - 39))

        elif self.stage == "start":
            subtitle = font_medium.render("READY TO DUEL?", True, RETRO_SILVER)
            subtitle_shadow = font_medium.render("READY TO DUEL?", True, BLACK)
            screen.blit(subtitle_shadow, (BASE_WIDTH // 2 - subtitle.get_width() // 2 + 1, 105))
            screen.blit(subtitle, (BASE_WIDTH // 2 - subtitle.get_width() // 2, 104))

            p1_name = self.p1_skin.name if self.p1_skin else "P1"
            p2_name = self.p2_skin.name if self.p2_skin else "P2"

            p1_showcase = pygame.Rect(20, 160, 150, 180)
            p1_surf = pygame.Surface((p1_showcase.width, p1_showcase.height), pygame.SRCALPHA)
            pygame.draw.rect(p1_surf, (20, 40, 30, 240), p1_surf.get_rect(), 0, 14)
            pygame.draw.rect(p1_surf, RETRO_GREEN, p1_surf.get_rect(), 2, 14)
            screen.blit(p1_surf, p1_showcase)
            if self.p1_skin and self.p1_skin.image:
                img = pygame.transform.scale(self.p1_skin.image, (80, 80))
                screen.blit(img, (p1_showcase.centerx - 40, p1_showcase.y + 30))
            p1_name_surf = font_small.render(p1_name[:14], True, RETRO_GOLD)
            screen.blit(p1_name_surf, (p1_showcase.centerx - p1_name_surf.get_width() // 2, p1_showcase.y + 130))
            p1_label = font_tiny.render("PLAYER 1", True, RETRO_GREEN)
            screen.blit(p1_label, (p1_showcase.centerx - p1_label.get_width() // 2, p1_showcase.y + 150))

            p2_showcase = pygame.Rect(BASE_WIDTH - 170, 160, 150, 180)
            p2_surf = pygame.Surface((p2_showcase.width, p2_showcase.height), pygame.SRCALPHA)
            pygame.draw.rect(p2_surf, (40, 20, 20, 240), p2_surf.get_rect(), 0, 14)
            pygame.draw.rect(p2_surf, RETRO_RED, p2_surf.get_rect(), 2, 14)
            screen.blit(p2_surf, p2_showcase)
            if self.p2_skin and self.p2_skin.image:
                img = pygame.transform.scale(self.p2_skin.image, (80, 80))
                screen.blit(img, (p2_showcase.centerx - 40, p2_showcase.y + 30))
            p2_name_surf = font_small.render(p2_name[:14], True, RETRO_GOLD)
            screen.blit(p2_name_surf, (p2_showcase.centerx - p2_name_surf.get_width() // 2, p2_showcase.y + 130))
            p2_label = font_tiny.render("PLAYER 2", True, RETRO_RED)
            screen.blit(p2_label, (p2_showcase.centerx - p2_label.get_width() // 2, p2_showcase.y + 150))

            vs_x = BASE_WIDTH // 2
            vs_y = 250
            vs_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(vs_surf, (30, 30, 50, 240), (30, 30), 28)
            pygame.draw.circle(vs_surf, RETRO_GOLD, (30, 30), 28, 3)
            screen.blit(vs_surf, (vs_x - 30, vs_y - 30))
            vs_text = font_large.render("VS", True, RETRO_GOLD)
            vs_shadow = font_large.render("VS", True, BLACK)
            screen.blit(vs_shadow, (vs_x - vs_text.get_width() // 2 + 1, vs_y - vs_text.get_height() // 2 + 1))
            screen.blit(vs_text, (vs_x - vs_text.get_width() // 2, vs_y - vs_text.get_height() // 2))

            court_names = {"hard": "HARD COURT", "clay": "CLAY COURT", "grass": "GRASS COURT"}
            court_display = court_names.get(self.court, "UNKNOWN")
            court_bg = pygame.Surface((200, 30), pygame.SRCALPHA)
            pygame.draw.rect(court_bg, (0, 0, 0, 200), court_bg.get_rect(), 0, 8)
            pygame.draw.rect(court_bg, RETRO_GOLD, court_bg.get_rect(), 1, 8)
            screen.blit(court_bg, (BASE_WIDTH // 2 - 100, 360))
            court_text = font_small.render(court_display, True, RETRO_GOLD)
            screen.blit(court_text, (BASE_WIDTH // 2 - court_text.get_width() // 2, 366))

            start_rect = pygame.Rect(BASE_WIDTH // 2 - 120, 420, 240, 60)
            pulse = math.sin(self.animation * 3) * 5
            start_rect_inflated = start_rect.inflate(pulse, pulse)
            start_surf = pygame.Surface((start_rect_inflated.width, start_rect_inflated.height), pygame.SRCALPHA)
            pygame.draw.rect(start_surf, (46, 204, 113, 240), start_surf.get_rect(), 0, 16)
            pygame.draw.rect(start_surf, RETRO_GOLD, start_surf.get_rect(), 3, 16)
            screen.blit(start_surf, (start_rect_inflated.x, start_rect_inflated.y))
            start_text = font_large.render("START DUEL", True, RETRO_GOLD)
            start_shadow = font_large.render("START DUEL", True, BLACK)
            screen.blit(start_shadow,
                        (start_rect.centerx - start_text.get_width() // 2 + 1,
                         start_rect.centery - start_text.get_height() // 2 + 1))
            screen.blit(start_text,
                        (start_rect.centerx - start_text.get_width() // 2,
                         start_rect.centery - start_text.get_height() // 2))

        self.back_rect = pygame.Rect(10, 10, 70, 28)
        back_surf = pygame.Surface((self.back_rect.width, self.back_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(back_surf, (155, 89, 182, 230), back_surf.get_rect(), 0, 8)
        pygame.draw.rect(back_surf, RETRO_SILVER, back_surf.get_rect(), 2, 8)
        screen.blit(back_surf, self.back_rect)
        back_text = font_small.render("Back", True, RETRO_GOLD)
        back_shadow = font_small.render("Back", True, BLACK)
        screen.blit(back_shadow, (self.back_rect.centerx - back_text.get_width() // 2 + 1,
                                  self.back_rect.centery - back_text.get_height() // 2 + 1))
        screen.blit(back_text, (self.back_rect.centerx - back_text.get_width() // 2,
                                self.back_rect.centery - back_text.get_height() // 2))

    def handle_click(self, x, y):
        if self.back_rect and self.back_rect.collidepoint(x, y):
            if self.sound_manager:
                self.sound_manager.play_button()
            if self.stage == "court":
                self.stage = "skins"
                return None
            elif self.stage == "start":
                self.stage = "court"
                return None
            return "back"

        if self.stage == "skins":
            skins_per_row = self.skins_per_row
            cell_size = self.cell_size
            start_x = 15
            start_y = self.pool_start_y + 28 - self.scroll_offset

            skins_area = pygame.Rect(10, self.pool_start_y + 24, BASE_WIDTH - 24, self.pool_height - 30)
            if not skins_area.collidepoint(x, y):
                if y > self.pool_start_y and y < self.pool_start_y + self.pool_height:
                    pass
                else:
                    return None

            for i, skin in enumerate(self.available_skins):
                row = i // skins_per_row
                col = i % skins_per_row
                x_pos = start_x + col * (cell_size + 8)
                y_pos = start_y + row * (cell_size + 8)

                if y_pos + cell_size < self.pool_start_y + 24 or y_pos > self.pool_start_y + self.pool_height - 6:
                    continue

                skin_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)
                if skin_rect.collidepoint(x, y):
                    if not self.skin_selection_done_p1:
                        self.p1_skin = skin
                        self.skin_selection_done_p1 = True
                        if self.sound_manager:
                            self.sound_manager.play_button()
                    elif not self.skin_selection_done_p2:
                        if skin != self.p1_skin:
                            self.p2_skin = skin
                            self.skin_selection_done_p2 = True
                            if self.sound_manager:
                                self.sound_manager.play_button()
                    return None

            if self.skin_selection_done_p1 and self.skin_selection_done_p2:
                if y > self.pool_start_y and y < self.pool_start_y + self.pool_height:
                    pass

        elif self.stage == "court":
            courts = ["hard", "clay", "grass"]
            for i, key in enumerate(courts):
                y_pos = 130 + i * 115
                rect = pygame.Rect(30, y_pos, BASE_WIDTH - 60, 90)
                if rect.collidepoint(x, y):
                    self.court = key
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    self.stage = "start"
                    return None

        elif self.stage == "start":
            start_rect = pygame.Rect(BASE_WIDTH // 2 - 120, 420, 240, 60)
            if start_rect.collidepoint(x, y):
                if self.sound_manager:
                    self.sound_manager.play_button()
                return "start_duel"

        return None

    def handle_keyboard(self, event):
        if event.type == pygame.KEYDOWN:
            if self.stage == "skins":
                if self.skin_selection_done_p1 and self.skin_selection_done_p2:
                    if event.key == pygame.K_RETURN:
                        self.stage = "court"
                        if self.sound_manager:
                            self.sound_manager.play_button()
            elif self.stage == "court":
                if event.key == pygame.K_RETURN:
                    if self.court:
                        self.stage = "start"
                        if self.sound_manager:
                            self.sound_manager.play_button()
                elif event.key == pygame.K_UP:
                    courts = ["hard", "clay", "grass"]
                    if self.court:
                        idx = courts.index(self.court)
                        idx = (idx - 1) % 3
                        self.court = courts[idx]
                        if self.sound_manager:
                            self.sound_manager.play_button()
                    else:
                        self.court = "hard"
                elif event.key == pygame.K_DOWN:
                    courts = ["hard", "clay", "grass"]
                    if self.court:
                        idx = courts.index(self.court)
                        idx = (idx + 1) % 3
                        self.court = courts[idx]
                        if self.sound_manager:
                            self.sound_manager.play_button()
                    else:
                        self.court = "hard"
            elif self.stage == "start":
                if event.key == pygame.K_RETURN:
                    if self.sound_manager:
                        self.sound_manager.play_button()
                    return "start_duel"

        if event.type == pygame.JOYBUTTONDOWN:
            if self.stage == "skins":
                if not self.skin_selection_done_p2:
                    if event.button == 0:
                        if self.available_skins:
                            skin = self.available_skins[self.skin_cursor_p2]
                            if self.skin_selection_done_p1:
                                if skin != self.p1_skin:
                                    self.p2_skin = skin
                                    self.skin_selection_done_p2 = True
                                    if self.sound_manager:
                                        self.sound_manager.play_button()
                            else:
                                self.p2_skin = skin
                                self.skin_selection_done_p2 = True
                                if self.sound_manager:
                                    self.sound_manager.play_button()
                elif self.skin_selection_done_p1 and self.skin_selection_done_p2:
                    if event.button == 0:
                        self.stage = "court"
                        if self.sound_manager:
                            self.sound_manager.play_button()

        return None

    def handle_scroll(self, y):
        if self.stage != "skins":
            return
        max_scroll = self._get_max_scroll()
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset + y))

    def handle_mouse_motion(self, x, y):
        if self.stage != "skins":
            return
        if self.dragging_scrollbar and self.scrollbar_rect:
            max_scroll = self._get_max_scroll()
            if max_scroll > 0:
                visible_height = self.pool_height - 30
                handle_height = self.scroll_handle_rect.height if self.scroll_handle_rect else 28
                available = visible_height - handle_height
                if available > 0:
                    rel_y = max(0, min(available, y - self.pool_start_y - 24 - handle_height // 2))
                    self.scroll_offset = int((rel_y / available) * max_scroll)
                    self.scroll_offset = max(0, min(max_scroll, self.scroll_offset))

    def handle_mouse_down(self, x, y):
        if self.stage != "skins":
            return False
        if self.scroll_handle_rect and self.scroll_handle_rect.collidepoint(x, y):
            self.dragging_scrollbar = True
            return True
        return False

    def handle_mouse_up(self):
        self.dragging_scrollbar = False


class TennisDuelGame:
    def __init__(self, sound_manager=None, p1_skin=None, p2_skin=None, court="hard"):
        self.sound_manager = sound_manager
        self.p1_skin = p1_skin
        self.p2_skin = p2_skin
        self.court_type = court
        self.active = True

        self.p1_games = 0
        self.p2_games = 0
        self.p1_points = 0
        self.p2_points = 0
        self.target_games = 2
        self.game_over = False
        self.winner = None
        self.deuce = False
        self.advantage = None
        self.rally_count = 0
        self.max_rally = 0
        self.points_won_in_row_p1 = 0
        self.points_won_in_row_p2 = 0

        self.p1_paddle = pygame.Rect(BASE_WIDTH // 2 - 35, BASE_HEIGHT - 55, 70, 12)
        self.p2_paddle = pygame.Rect(BASE_WIDTH // 2 - 35, 35, 70, 12)
        self.ball = pygame.Rect(BASE_WIDTH // 2 - 6, BASE_HEIGHT // 2 - 6, 12, 12)
        self.ball_dx = random.choice([-4, 4])
        self.ball_dy = -4
        self.ball_spin = 0
        self.serving = True
        self.serve_timer = 0
        self.serving_player = 'p1'
        self.trail = []
        self.particles = []
        self.hit_effects = []

        self.p1_power_meter = 0
        self.p2_power_meter = 0
        self.p1_power_charging = False
        self.p2_power_charging = False
        self.power_charge_speed = 1.5

        self.p1_left_shot = False
        self.p1_right_shot = False
        self.p1_slice = False
        self.p1_straight = False
        self.p1_curve = False

        self.p2_left_shot = False
        self.p2_right_shot = False
        self.p2_slice = False
        self.p2_straight = False
        self.p2_curve = False

        self.ball_curve_active = False
        self.ball_curve_direction = 0
        self.ball_curve_intensity = 0.0

        self.p1_anim_image = None
        self.p1_anim_timer = 0
        self.p2_anim_image = None
        self.p2_anim_timer = 0
        self.SHOT_ANIM_DURATION = 90

        self.p1_velocity_x = 0
        self.p2_velocity_x = 0
        self.player_speed = 8
        self.player_friction = 0.75

        self.p1_is_gamepad = False
        self.p2_is_gamepad = False
        self.p1_gamepad = None
        self.p2_gamepad = None

        if court == 'clay':
            self.court_color = (193, 100, 67)
            self.court_line_color = (220, 180, 120)
            self.player_friction = 0.7
        elif court == 'grass':
            self.court_color = (68, 148, 74)
            self.court_line_color = (200, 255, 200)
            self.player_friction = 0.8
        else:
            self.court_color = (77, 88, 96)
            self.court_line_color = (150, 170, 190)
            self.player_friction = 0.75

        self.font_small = pygame.font.Font(None, 18)
        self.font_medium = pygame.font.Font(None, 26)
        self.font_large = pygame.font.Font(None, 34)

    def set_controls(self, p1_type, p2_type):
        self.p1_is_gamepad = (p1_type == "gamepad")
        self.p2_is_gamepad = (p2_type == "gamepad")
        if self.p1_is_gamepad and len(joysticks) > 0:
            self.p1_gamepad = joysticks[0]
        if self.p2_is_gamepad and len(joysticks) > 0:
            self.p2_gamepad = joysticks[1] if len(joysticks) > 1 else joysticks[0]

    def play_hit_sound(self, is_p1):
        if is_p1:
            if self.sound_manager:
                self.sound_manager.play_tennis_player_hit()
        else:
            if self.sound_manager:
                self.sound_manager.play_tennis_opponent_hit()

    def calculate_hit_angle(self, ball_center, paddle_center, paddle_rect):
        hit_pos = (ball_center - paddle_center) / (paddle_rect.width / 2)
        hit_pos = max(-1, min(1, hit_pos))
        return hit_pos

    def _trigger_p1_anim(self, shot_side):
        skin = self.p1_skin
        if skin is None or not getattr(skin, 'has_animation', False):
            return
        img = None
        if shot_side == "right":
            img = skin.image_right
        elif shot_side == "left":
            img = skin.image_left
        elif shot_side == "curve":
            img = skin.image_right or skin.image_left
        if img is not None:
            self.p1_anim_image = img
            self.p1_anim_timer = self.SHOT_ANIM_DURATION

    def _trigger_p2_anim(self, shot_side):
        skin = self.p2_skin
        if skin is None or not getattr(skin, 'has_animation', False):
            return
        img = None
        if shot_side == "right":
            img = skin.image_right
        elif shot_side == "left":
            img = skin.image_left
        elif shot_side == "curve":
            img = skin.image_right or skin.image_left
        if img is not None:
            self.p2_anim_image = img
            self.p2_anim_timer = self.SHOT_ANIM_DURATION

    def _trigger_random_p1_anim(self):
        skin = self.p1_skin
        if skin is None or not getattr(skin, 'has_animation', False):
            return
        candidates = []
        if getattr(skin, 'image_right', None) is not None:
            candidates.append(skin.image_right)
        if getattr(skin, 'image_left', None) is not None:
            candidates.append(skin.image_left)
        if candidates:
            self.p1_anim_image = random.choice(candidates)
            self.p1_anim_timer = self.SHOT_ANIM_DURATION

    def _trigger_random_p2_anim(self):
        skin = self.p2_skin
        if skin is None or not getattr(skin, 'has_animation', False):
            return
        candidates = []
        if getattr(skin, 'image_right', None) is not None:
            candidates.append(skin.image_right)
        if getattr(skin, 'image_left', None) is not None:
            candidates.append(skin.image_left)
        if candidates:
            self.p2_anim_image = random.choice(candidates)
            self.p2_anim_timer = self.SHOT_ANIM_DURATION

    def update(self):
        if self.p1_anim_timer > 0:
            self.p1_anim_timer -= 1
            if self.p1_anim_timer <= 0:
                self.p1_anim_image = None
        if self.p2_anim_timer > 0:
            self.p2_anim_timer -= 1
            if self.p2_anim_timer <= 0:
                self.p2_anim_image = None

        if self.game_over:
            return True
        if self.serving:
            self.serve_timer += 1
            if self.serve_timer > 60:
                self.serving = False
            return False

        p1_move = 0
        p2_move = 0

        if not self.p1_is_gamepad:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                p1_move -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                p1_move += 1
        elif self.p1_gamepad:
            try:
                axis = self.p1_gamepad.get_axis(0)
                if abs(axis) > 0.2:
                    p1_move = axis
                hat = self.p1_gamepad.get_hat(0)
                if hat[0] != 0:
                    p1_move = hat[0]
            except:
                pass

        if not self.p2_is_gamepad:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                p2_move -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                p2_move += 1
        elif self.p2_gamepad:
            try:
                axis = self.p2_gamepad.get_axis(0)
                if abs(axis) > 0.2:
                    p2_move = axis
                hat = self.p2_gamepad.get_hat(0)
                if hat[0] != 0:
                    p2_move = hat[0]
            except:
                pass

        if p1_move != 0:
            self.p1_velocity_x += p1_move * 0.35
            self.p1_velocity_x = max(-self.player_speed, min(self.player_speed, self.p1_velocity_x))
        else:
            self.p1_velocity_x *= self.player_friction
            if abs(self.p1_velocity_x) < 0.2:
                self.p1_velocity_x = 0

        if p2_move != 0:
            self.p2_velocity_x += p2_move * 0.35
            self.p2_velocity_x = max(-self.player_speed, min(self.player_speed, self.p2_velocity_x))
        else:
            self.p2_velocity_x *= self.player_friction
            if abs(self.p2_velocity_x) < 0.2:
                self.p2_velocity_x = 0

        self.p1_paddle.x += self.p1_velocity_x
        self.p1_paddle.left = max(0, min(self.p1_paddle.left, BASE_WIDTH - self.p1_paddle.width))
        self.p2_paddle.x += self.p2_velocity_x
        self.p2_paddle.left = max(0, min(self.p2_paddle.left, BASE_WIDTH - self.p2_paddle.width))

        if not self.p1_is_gamepad:
            keys = pygame.key.get_pressed()
            self.p1_left_shot = keys[pygame.K_q]
            self.p1_right_shot = keys[pygame.K_e]
            self.p1_slice = keys[pygame.K_f]
            self.p1_straight = keys[pygame.K_w] and not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d])
            self.p1_curve = keys[pygame.K_r]
            p1_charging = keys[pygame.K_SPACE]
        elif self.p1_gamepad:
            try:
                self.p1_left_shot = self.p1_gamepad.get_button(4) if self.p1_gamepad.get_numbuttons() > 4 else False
                self.p1_right_shot = self.p1_gamepad.get_button(5) if self.p1_gamepad.get_numbuttons() > 5 else False
                self.p1_slice = self.p1_gamepad.get_button(2) if self.p1_gamepad.get_numbuttons() > 2 else False
                self.p1_straight = self.p1_gamepad.get_button(3) if self.p1_gamepad.get_numbuttons() > 3 else False
                rt_val = self.p1_gamepad.get_axis(5) if self.p1_gamepad.get_numaxes() > 5 else 0
                self.p1_curve = rt_val > 0.5
                p1_charging = self.p1_gamepad.get_button(1) if self.p1_gamepad.get_numbuttons() > 1 else False
            except:
                p1_charging = False
        else:
            p1_charging = False

        if not self.p2_is_gamepad:
            keys = pygame.key.get_pressed()
            self.p2_left_shot = keys[pygame.K_u]
            self.p2_right_shot = keys[pygame.K_o]
            self.p2_slice = keys[pygame.K_j]
            self.p2_straight = keys[pygame.K_i]
            self.p2_curve = keys[pygame.K_p]
            p2_charging = keys[pygame.K_h]
        elif self.p2_gamepad:
            try:
                self.p2_left_shot = self.p2_gamepad.get_button(4) if self.p2_gamepad.get_numbuttons() > 4 else False
                self.p2_right_shot = self.p2_gamepad.get_button(5) if self.p2_gamepad.get_numbuttons() > 5 else False
                self.p2_slice = self.p2_gamepad.get_button(2) if self.p2_gamepad.get_numbuttons() > 2 else False
                self.p2_straight = self.p2_gamepad.get_button(3) if self.p2_gamepad.get_numbuttons() > 3 else False
                rt_val = self.p2_gamepad.get_axis(5) if self.p2_gamepad.get_numaxes() > 5 else 0
                self.p2_curve = rt_val > 0.5
                p2_charging = self.p2_gamepad.get_button(1) if self.p2_gamepad.get_numbuttons() > 1 else False
            except:
                p2_charging = False
        else:
            p2_charging = False

        if p1_charging and not self.p1_power_charging:
            self.p1_power_charging = True
            self.p1_power_meter = 0
        elif not p1_charging and self.p1_power_charging:
            self.p1_power_charging = False
        if self.p1_power_charging:
            self.p1_power_meter = min(100, self.p1_power_meter + self.power_charge_speed)

        if p2_charging and not self.p2_power_charging:
            self.p2_power_charging = True
            self.p2_power_meter = 0
        elif not p2_charging and self.p2_power_charging:
            self.p2_power_charging = False
        if self.p2_power_charging:
            self.p2_power_meter = min(100, self.p2_power_meter + self.power_charge_speed)

        if self.ball_curve_active:
            self.ball_dx += self.ball_curve_direction * self.ball_curve_intensity
            self.ball_curve_intensity *= 0.98
            if abs(self.ball_curve_intensity) < 0.05:
                self.ball_curve_active = False
                self.ball_curve_intensity = 0.0

        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy
        self.ball_dx += self.ball_spin * 0.05
        self.ball_dx = max(-7, min(7, self.ball_dx))
        self.ball_spin *= 0.98

        self.trail.append((self.ball.centerx, self.ball.centery))
        if len(self.trail) > 15:
            self.trail.pop(0)

        if self.ball.left <= 0:
            self.ball.left = 1
            self.ball_dx = abs(self.ball_dx)
            self.ball_spin = random.uniform(-1, 1)
            if self.sound_manager:
                self.sound_manager.play_tennis_wall()
        if self.ball.right >= BASE_WIDTH:
            self.ball.right = BASE_WIDTH - 1
            self.ball_dx = -abs(self.ball_dx)
            self.ball_spin = random.uniform(-1, 1)
            if self.sound_manager:
                self.sound_manager.play_tennis_wall()

        if self.ball.colliderect(self.p1_paddle) and self.ball_dy > 0:
            self.ball_dy = -5
            hit_angle = self.calculate_hit_angle(self.ball.centerx, self.p1_paddle.centerx, self.p1_paddle)
            power_mult = 1 + (self.p1_power_meter / 100) * 0.8

            self.rally_count += 1
            if self.rally_count > self.max_rally:
                self.max_rally = self.rally_count

            effect_color = RETRO_GOLD
            if self.p1_left_shot:
                self.ball_dx = -abs(hit_angle) * 5 - 2
                self.ball_dy = -5 * (1.2 + power_mult * 0.3)
                self.ball_spin = -2
                effect_color = (255, 100, 100)
                self._trigger_p1_anim("left")
            elif self.p1_right_shot:
                self.ball_dx = abs(hit_angle) * 5 + 2
                self.ball_dy = -5 * (1.2 + power_mult * 0.3)
                self.ball_spin = 2
                effect_color = (255, 200, 100)
                self._trigger_p1_anim("right")
            elif self.p1_slice:
                self.ball_dx = hit_angle * 4
                self.ball_dy = -4
                self.ball_spin = hit_angle * -2
                effect_color = (100, 100, 255)
                self._trigger_p1_anim("left")
            elif self.p1_straight:
                self.ball_dx = 0
                self.ball_dy = -7 * (1.2 + power_mult * 0.3)
                self.ball_spin = hit_angle * 0.5
                effect_color = (255, 215, 0)
                self._trigger_p1_anim("right")
            elif self.p1_curve:
                self.ball_dx = hit_angle * 3.2
                self.ball_dy = -6.0 * (0.9 + power_mult * 0.3)
                self.ball_spin = -6.0
                self.ball_curve_active = True
                self.ball_curve_direction = 1 if hit_angle >= 0 else -1
                self.ball_curve_intensity = 0.45
                effect_color = (230, 120, 60)
                self._trigger_p1_anim("curve")
            else:
                self.ball_dx += hit_angle * 4 * power_mult
                self.ball_dy = -5 * (1.0 + power_mult * 0.3)
                self.ball_spin = hit_angle * 1.5
                self._trigger_random_p1_anim()

            self.ball_dx = max(-8, min(8, self.ball_dx))
            self.play_hit_sound(True)

            for _ in range(10):
                self.particles.append(Particle(self.ball.centerx, self.ball.centery, effect_color))
            self.hit_effects.append({"x": self.ball.centerx, "y": self.ball.centery, "life": 10})
            self.p1_power_meter = 0
            self.p1_power_charging = False

        if self.ball.colliderect(self.p2_paddle) and self.ball_dy < 0:
            self.ball_dy = 5
            hit_angle = self.calculate_hit_angle(self.ball.centerx, self.p2_paddle.centerx, self.p2_paddle)
            power_mult = 1 + (self.p2_power_meter / 100) * 0.8

            self.rally_count += 1
            if self.rally_count > self.max_rally:
                self.max_rally = self.rally_count

            effect_color = RETRO_RED
            if self.p2_left_shot:
                self.ball_dx = -abs(hit_angle) * 5 - 2
                self.ball_dy = 5 * (1.2 + power_mult * 0.3)
                self.ball_spin = -2
                effect_color = (255, 100, 100)
                self._trigger_p2_anim("left")
            elif self.p2_right_shot:
                self.ball_dx = abs(hit_angle) * 5 + 2
                self.ball_dy = 5 * (1.2 + power_mult * 0.3)
                self.ball_spin = 2
                effect_color = (255, 200, 100)
                self._trigger_p2_anim("right")
            elif self.p2_slice:
                self.ball_dx = hit_angle * 4
                self.ball_dy = 4
                self.ball_spin = hit_angle * -2
                effect_color = (100, 100, 255)
                self._trigger_p2_anim("left")
            elif self.p2_straight:
                self.ball_dx = 0
                self.ball_dy = 7 * (1.2 + power_mult * 0.3)
                self.ball_spin = hit_angle * 0.5
                effect_color = (255, 215, 0)
                self._trigger_p2_anim("right")
            elif self.p2_curve:
                self.ball_dx = hit_angle * 3.2
                self.ball_dy = 6.0 * (0.9 + power_mult * 0.3)
                self.ball_spin = -6.0
                self.ball_curve_active = True
                self.ball_curve_direction = 1 if hit_angle >= 0 else -1
                self.ball_curve_intensity = 0.45
                effect_color = (230, 120, 60)
                self._trigger_p2_anim("curve")
            else:
                self.ball_dx += hit_angle * 4 * power_mult
                self.ball_dy = 5 * (1.0 + power_mult * 0.3)
                self.ball_spin = hit_angle * 1.5
                self._trigger_random_p2_anim()

            self.ball_dx = max(-8, min(8, self.ball_dx))
            self.play_hit_sound(False)

            for _ in range(10):
                self.particles.append(Particle(self.ball.centerx, self.ball.centery, effect_color))
            self.hit_effects.append({"x": self.ball.centerx, "y": self.ball.centery, "life": 10})
            self.p2_power_meter = 0
            self.p2_power_charging = False

        if self.ball.top <= 0:
            self.rally_count = 0
            self.p1_points += 1
            self.points_won_in_row_p1 += 1
            self.points_won_in_row_p2 = 0
            self.check_point_win()
            self.reset_ball('p1')
            self.serving = True
            self.serve_timer = 0
            self.serving_player = 'p1'
            if self.sound_manager:
                self.sound_manager.play_tennis_point_win()
        elif self.ball.bottom >= BASE_HEIGHT:
            self.rally_count = 0
            self.p2_points += 1
            self.points_won_in_row_p2 += 1
            self.points_won_in_row_p1 = 0
            self.check_point_win()
            self.reset_ball('p2')
            self.serving = True
            self.serve_timer = 0
            self.serving_player = 'p2'
            if self.sound_manager:
                self.sound_manager.play_tennis_point_lose()

        self.particles = [p for p in self.particles if p.update()]
        self.hit_effects = [e for e in self.hit_effects if e["life"] > 0]
        for e in self.hit_effects:
            e["life"] -= 1

        if self.p1_games >= self.target_games:
            self.game_over = True
            self.winner = "p1"
            return True
        elif self.p2_games >= self.target_games:
            self.game_over = True
            self.winner = "p2"
            return True
        return False

    def check_point_win(self):
        if self.p1_points >= 3 and self.p2_points >= 3:
            if self.p1_points > self.p2_points and self.p1_points - self.p2_points >= 2:
                self.p1_games += 1
                self.p1_points = 0
                self.p2_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0
            elif self.p2_points > self.p1_points and self.p2_points - self.p1_points >= 2:
                self.p2_games += 1
                self.p1_points = 0
                self.p2_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0
            else:
                self.deuce = True
                if self.p1_points > self.p2_points:
                    self.advantage = 'p1'
                elif self.p2_points > self.p1_points:
                    self.advantage = 'p2'
                else:
                    self.advantage = None
        else:
            if self.p1_points >= 4 and self.p1_points - self.p2_points >= 2:
                self.p1_games += 1
                self.p1_points = 0
                self.p2_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0
            elif self.p2_points >= 4 and self.p2_points - self.p1_points >= 2:
                self.p2_games += 1
                self.p1_points = 0
                self.p2_points = 0
                self.deuce = False
                self.advantage = None
                self.rally_count = 0

    def reset_ball(self, server):
        self.ball.centerx = BASE_WIDTH // 2
        self.ball.centery = BASE_HEIGHT // 2
        self.ball_dx = random.choice([-3, 3])
        self.ball_dy = -4 if server == 'p1' else 4
        self.trail.clear()
        self.ball_spin = 0
        self.ball_curve_active = False
        self.ball_curve_intensity = 0.0

    def draw_bird_paddle(self, screen, rect, skin, is_p1=True):
        anim_img = self.p1_anim_image if is_p1 else self.p2_anim_image
        anim_timer = self.p1_anim_timer if is_p1 else self.p2_anim_timer

        if anim_img is not None and anim_timer > 0:
            screen.blit(anim_img, (rect.x - 5, rect.y - 5))
            return

        if skin is not None and hasattr(skin, 'image') and skin.image is not None:
            bird_surf = skin.image.copy()
            screen.blit(bird_surf, (rect.x - 5, rect.y - 5))
            return

        color = RETRO_BLUE if is_p1 else RETRO_RED
        bird_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(bird_surf, color, (5, 2, rect.width - 10, rect.height - 4))
        pygame.draw.circle(bird_surf, color, (rect.width - 8, rect.height // 2), 8)
        pygame.draw.circle(bird_surf, WHITE, (rect.width - 5, rect.height // 2 - 2), 3)
        pygame.draw.circle(bird_surf, BLACK, (rect.width - 4, rect.height // 2 - 2), 1)
        beak_points = [(rect.width - 2, rect.height // 2), (rect.width + 5, rect.height // 2),
                       (rect.width - 2, rect.height // 2 + 4)]
        pygame.draw.polygon(bird_surf, ORANGE, beak_points)
        screen.blit(bird_surf, (rect.x - 5, rect.y - 5))

    def draw(self, screen):
        screen.fill(self.court_color)
        pygame.draw.line(screen, self.court_line_color, (0, BASE_HEIGHT // 2), (BASE_WIDTH, BASE_HEIGHT // 2), 3)
        pygame.draw.line(screen, self.court_line_color, (BASE_WIDTH // 2, 0), (BASE_WIDTH // 2, BASE_HEIGHT), 3)
        pygame.draw.circle(screen, self.court_line_color, (BASE_WIDTH // 2, BASE_HEIGHT // 2), 40, 3)

        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail))) if self.trail else 100
            pygame.draw.circle(screen,
                               (self.court_line_color[0], self.court_line_color[1], self.court_line_color[2],
                                alpha), (int(tx), int(ty)), 3)

        pygame.draw.circle(screen, RETRO_GOLD, self.ball.center, 6)

        for e in self.hit_effects:
            alpha = int(150 * (e["life"] / 10))
            pygame.draw.circle(screen,
                               (self.court_line_color[0], self.court_line_color[1], self.court_line_color[2],
                                alpha), (int(e["x"]), int(e["y"])), 15)

        for particle in self.particles:
            particle.draw(screen)

        self.draw_bird_paddle(screen, self.p1_paddle, self.p1_skin, True)
        self.draw_bird_paddle(screen, self.p2_paddle, self.p2_skin, False)

        games_text = self.font_large.render(f"{self.p1_games}  -  {self.p2_games}", True, RETRO_SILVER)
        games_shadow = self.font_large.render(f"{self.p1_games}  -  {self.p2_games}", True, BLACK)
        games_bg = pygame.Surface((games_text.get_width() + 20, 50), pygame.SRCALPHA)
        pygame.draw.rect(games_bg, (0, 0, 0, 200), games_bg.get_rect(), 0, 10)
        screen.blit(games_bg, (BASE_WIDTH // 2 - games_text.get_width() // 2 - 10, BASE_HEIGHT // 2 - 60))
        screen.blit(games_shadow, (BASE_WIDTH // 2 - games_text.get_width() // 2 + 1, BASE_HEIGHT // 2 - 54))
        screen.blit(games_text, (BASE_WIDTH // 2 - games_text.get_width() // 2, BASE_HEIGHT // 2 - 55))

        point_names = ["0", "15", "30", "40"]
        p1_pts = min(self.p1_points, 3)
        p2_pts = min(self.p2_points, 3)
        points_text = self.font_medium.render(f"{point_names[p1_pts]} - {point_names[p2_pts]}", True,
                                              RETRO_SILVER)
        points_shadow = self.font_medium.render(f"{point_names[p1_pts]} - {point_names[p2_pts]}", True, BLACK)
        points_bg = pygame.Surface((points_text.get_width() + 30, 35), pygame.SRCALPHA)
        pygame.draw.rect(points_bg, (0, 0, 0, 200), points_bg.get_rect(), 0, 10)
        screen.blit(points_bg, (BASE_WIDTH // 2 - points_text.get_width() // 2 - 15, BASE_HEIGHT // 2 - 25))
        screen.blit(points_shadow,
                    (BASE_WIDTH // 2 - points_text.get_width() // 2 + 1, BASE_HEIGHT // 2 - 19))
        screen.blit(points_text, (BASE_WIDTH // 2 - points_text.get_width() // 2, BASE_HEIGHT // 2 - 20))

        if self.deuce:
            if self.advantage == 'p1':
                adv_text = self.font_medium.render("ADVANTAGE P1", True, RETRO_GREEN)
                adv_shadow = self.font_medium.render("ADVANTAGE P1", True, BLACK)
                screen.blit(adv_shadow, (BASE_WIDTH // 2 - adv_text.get_width() // 2 + 1, BASE_HEIGHT // 2 + 21))
                screen.blit(adv_text, (BASE_WIDTH // 2 - adv_text.get_width() // 2, BASE_HEIGHT // 2 + 20))
            elif self.advantage == 'p2':
                adv_text = self.font_medium.render("ADVANTAGE P2", True, RETRO_RED)
                adv_shadow = self.font_medium.render("ADVANTAGE P2", True, BLACK)
                screen.blit(adv_shadow, (BASE_WIDTH // 2 - adv_text.get_width() // 2 + 1, BASE_HEIGHT // 2 + 21))
                screen.blit(adv_text, (BASE_WIDTH // 2 - adv_text.get_width() // 2, BASE_HEIGHT // 2 + 20))
            else:
                deuce_text = self.font_medium.render("DEUCE", True, RETRO_YELLOW)
                deuce_shadow = self.font_medium.render("DEUCE", True, BLACK)
                screen.blit(deuce_shadow, (BASE_WIDTH // 2 - deuce_text.get_width() // 2 + 1, BASE_HEIGHT // 2 + 21))
                screen.blit(deuce_text, (BASE_WIDTH // 2 - deuce_text.get_width() // 2, BASE_HEIGHT // 2 + 20))

        if self.rally_count > 0:
            rally_text = self.font_small.render(f"Rally: {self.rally_count}", True, RETRO_GOLD)
            rally_shadow = self.font_small.render(f"Rally: {self.rally_count}", True, BLACK)
            rally_bg = pygame.Surface((rally_text.get_width() + 16, 20), pygame.SRCALPHA)
            pygame.draw.rect(rally_bg, (0, 0, 0, 180), rally_bg.get_rect(), 0, 6)
            screen.blit(rally_bg, (BASE_WIDTH // 2 - rally_text.get_width() // 2 - 8, BASE_HEIGHT // 2 - 82))
            screen.blit(rally_shadow,
                        (BASE_WIDTH // 2 - rally_text.get_width() // 2 + 1, BASE_HEIGHT // 2 - 81 + 1))
            screen.blit(rally_text, (BASE_WIDTH // 2 - rally_text.get_width() // 2, BASE_HEIGHT // 2 - 82))

        p1_label = self.font_small.render("PLAYER 1", True, RETRO_GREEN)
        p1_shadow = self.font_small.render("PLAYER 1", True, BLACK)
        screen.blit(p1_shadow, (11, BASE_HEIGHT - 29))
        screen.blit(p1_label, (10, BASE_HEIGHT - 30))

        p2_label = self.font_small.render("PLAYER 2", True, RETRO_RED)
        p2_shadow = self.font_small.render("PLAYER 2", True, BLACK)
        screen.blit(p2_shadow, (BASE_WIDTH - 10 - p2_label.get_width() + 1, BASE_HEIGHT - 29))
        screen.blit(p2_label, (BASE_WIDTH - 10 - p2_label.get_width(), BASE_HEIGHT - 30))

        version_text = self.font_small.render(f"v{GAME_VERSION}", True, RETRO_GRAY)
        version_shadow = self.font_small.render(f"v{GAME_VERSION}", True, BLACK)
        screen.blit(version_shadow, (BASE_WIDTH - version_text.get_width() - 9, BASE_HEIGHT - 24))
        screen.blit(version_text, (BASE_WIDTH - version_text.get_width() - 10, BASE_HEIGHT - 25))


class Game:
    _instance = None

    def __init__(self):
        Game._instance = self
        self.screen_manager = ScreenManager()
        self.screen_manager.init_screen(IS_ANDROID)
        pygame.display.set_caption(f"{GAME_TITLE} v{GAME_VERSION}")
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 22)
        self.font_medium = pygame.font.Font(None, 30)
        self.font_large = pygame.font.Font(None, 42)
        self.font_title = pygame.font.Font(None, 50)
        self.font_huge = pygame.font.Font(None, 66)

        self.skin_manager = GameSkinManager()
        self.sound_manager = SoundManager()
        self.settings_menu = SettingsMenu(self.sound_manager)

        self.sound_manager.play_menu_music()

        self.tv_player = TVVideoPlayer()
        self.tv_manager = TVVideoManager()
        self.tv_manager.set_player(self.tv_player)
        self.tape_shop = TVTapeShop(self.tv_player)

        self.tennis_ranked_system = TennisRankedSystem()
        self.tennis_ranked_screen = TennisRankedScreen(
            self.tennis_ranked_system,
            self.sound_manager,
            self.skin_manager.get_bg_for_mode("tennis"),
            self.skin_manager
        )
        self.basketball_campaign_manager = BasketballCampaignManager()
        self.basketball_campaign_screen = BasketballCampaignScreen(
            self.basketball_campaign_manager,
            self.sound_manager,
            self.skin_manager.get_bg_for_mode("basketball"),
            self.skin_manager
        )
        self.world_ranking_system = WorldRankingSystem()
        self.world_ranking_screen = WorldRankingScreen(
            self.world_ranking_system,
            self.sound_manager,
            self.skin_manager.get_bg_for_mode("world_ranking"),
            self.skin_manager
        )
        self.shop_screen = ShopScreen(self.skin_manager, self.sound_manager)
        self.shop_screen.set_tape_shop(self.tape_shop)
        self.controls_screen = ControlsScreen(self.sound_manager)
        self.profile = None
        self.nickname_screen = NicknameScreen(self.sound_manager)
        self.current_basketball_game = None
        self.current_tennis_ranked_game = None
        self.current_duel_game = None
        self.duel_screen = DuelSetupScreen(self.sound_manager)
        self.duel_screen.background_manager = self.skin_manager.get_bg_for_mode("main_menu")
        self.high_score = 0
        self.coins = 100
        self.games_played = 0
        self.play_time = 0
        self.total_coins_collected = 0
        self.max_combo = 0
        self.game_mode = None
        self.achievement_manager = AchievementManager(self.sound_manager)
        self.achievement_screen = AchievementScreen(self.achievement_manager, self.sound_manager,
                                                    self.skin_manager.get_bg_for_mode("main_menu"))
        self.load_data()

        if self.profile:
            self.add_player_to_ranking()

        self.show_title = False

        if self.profile and self.profile.first_login:
            self.state = "nickname"
        else:
            self.state = "main_menu"

        self.menu_option = 0
        self.ground_offset = 0
        self.menu_start_y = 245
        self.menu_spacing = 30
        self.menu_buttons = self.create_menu_buttons()
        self.badge_collection_page = 0
        self.double_points_active = False
        self.double_points_timer = 0
        self.clouds = []
        cloud_colors = [(240, 235, 220, 180), (220, 215, 200, 160), (200, 195, 185, 140)]
        for _ in range(12):
            self.clouds.append({'x': random.randint(0, BASE_WIDTH), 'y': random.randint(20, 200),
                                'speed': random.uniform(0.2, 0.5), 'size': random.randint(40, 100),
                                'color': random.choice(cloud_colors),
                                'puff_offset': random.uniform(0, math.pi * 2)})
        self.stars = []
        for _ in range(50):
            self.stars.append({'x': random.randint(0, BASE_WIDTH), 'y': random.randint(0, BASE_HEIGHT - 100),
                               'brightness': random.uniform(0.3, 1.0),
                               'twinkle_speed': random.uniform(0.01, 0.03),
                               'phase': random.uniform(0, math.pi * 2)})
        self.notice = None
        self.notice_timer = 0
        self.animation_time = 0
        self.start_time = time.time()
        self.game_over_option = 0
        self.frame_count = 0
        self.particle_limit = 150
        self.campaign_badges_earned = []
        self.story_display = StoryDisplay(self.sound_manager)
        self.waiting_for_story_continue = False
        self.tennis_ranked_match_data = None
        self.settings_menu.screen_manager = self.screen_manager
        self.basketball_badges_in_collection = []
        self.is_legends_match = False
        self._pending_game_start = None
        self.particles = []
        self.duel_p1_type = None
        self.duel_p2_type = None
        self.duel_p1_skin = None
        self.duel_p2_skin = None
        self.duel_court = None
        self.touch_click_cooldown = 0

    def add_exp_to_profile(self, amount):
        if not self.profile:
            return
        self.profile.bird_exp += amount
        leveled_up = False
        while self.profile.bird_exp >= self.profile.bird_exp_to_next:
            self.profile.bird_exp -= self.profile.bird_exp_to_next
            self.profile.bird_level += 1
            self.profile.bird_exp_to_next = int(self.profile.bird_exp_to_next * 1.5)
            leveled_up = True
        if leveled_up:
            self.add_notice(f"LEVEL UP! Level {self.profile.bird_level}", RETRO_GOLD, 180)
            self.sound_manager.play_level_up()
            self.save_data()

    def add_player_to_ranking(self):
        player_name = self.profile.nickname if self.profile else "Pilot"
        for p in self.world_ranking_system.players:
            if p['name'] == player_name:
                p['tennis_elo'] = self.tennis_ranked_system.elo
                p['basketball_elo'] = self.basketball_campaign_manager.elo
                p['total_elo'] = (p['tennis_elo'] + p['basketball_elo']) // 2
                p['wins'] = self.basketball_campaign_manager.matches_won + self.tennis_ranked_system.matches_won
                p['losses'] = (
                                          self.basketball_campaign_manager.matches_played - self.basketball_campaign_manager.matches_won) + \
                              (self.tennis_ranked_system.matches_played - self.tennis_ranked_system.matches_won)
                p['matches_played'] = self.basketball_campaign_manager.matches_played + self.tennis_ranked_system.matches_played
                p['tennis_wins'] = self.tennis_ranked_system.matches_won
                p['tennis_losses'] = self.tennis_ranked_system.matches_played - self.tennis_ranked_system.matches_won
                p['basketball_wins'] = self.basketball_campaign_manager.matches_won
                p['basketball_losses'] = self.basketball_campaign_manager.matches_played - self.basketball_campaign_manager.matches_won
                self.world_ranking_system.sort_and_rank_players()
                return

        elo = (self.tennis_ranked_system.elo + self.basketball_campaign_manager.elo) // 2
        wins = self.basketball_campaign_manager.matches_won + self.tennis_ranked_system.matches_won
        losses = (self.basketball_campaign_manager.matches_played - self.basketball_campaign_manager.matches_won) + \
                 (self.tennis_ranked_system.matches_played - self.tennis_ranked_system.matches_won)
        player = {
            'name': player_name,
            'tennis_elo': self.tennis_ranked_system.elo,
            'basketball_elo': self.basketball_campaign_manager.elo,
            'total_elo': elo,
            'wins': wins,
            'losses': losses,
            'matches_played': self.basketball_campaign_manager.matches_played + self.tennis_ranked_system.matches_played,
            'win_streak': 0,
            'rank': 0,
            'last_match_time': datetime.now().strftime("%H:%M"),
            'avatar_color': (100, 180, 220),
            'elo_history': [elo],
            'last_elo_change': 0,
            'tennis_wins': self.tennis_ranked_system.matches_won,
            'tennis_losses': self.tennis_ranked_system.matches_played - self.tennis_ranked_system.matches_won,
            'basketball_wins': self.basketball_campaign_manager.matches_won,
            'basketball_losses': self.basketball_campaign_manager.matches_played - self.basketball_campaign_manager.matches_won
        }
        self.world_ranking_system.players.append(player)
        self.world_ranking_system.sort_and_rank_players()

    def check_achievements(self):
        tennis = self.tennis_ranked_system
        basketball = self.basketball_campaign_manager

        if tennis.matches_won >= 1:
            self.unlock_achievement("tennis_first_win")
        if tennis.matches_won >= 5:
            self.unlock_achievement("tennis_5_wins")
        if tennis.matches_won >= 10:
            self.unlock_achievement("tennis_10_wins")
        if tennis.matches_won >= 25:
            self.unlock_achievement("tennis_25_wins")
        if tennis.matches_won >= 50:
            self.unlock_achievement("tennis_50_wins")
        if tennis.elo >= 1200:
            self.unlock_achievement("tennis_elo_1200")
        if tennis.elo >= 1500:
            self.unlock_achievement("tennis_elo_1500")
        if tennis.elo >= 1800:
            self.unlock_achievement("tennis_elo_1800")
        if tennis.elo >= 2000:
            self.unlock_achievement("tennis_world_champion")
        if tennis.tournaments_won >= 1:
            self.unlock_achievement("tennis_tournament_1")
        if tennis.tournaments_won >= 3:
            self.unlock_achievement("tennis_tournament_3")
        if tennis.tournaments_won >= 5:
            self.unlock_achievement("tennis_tournament_5")
        if tennis.diamond_cup_earned:
            self.unlock_achievement("tennis_tournament_all")
        if tennis.legends_wins >= 1:
            self.unlock_achievement("tennis_legends_win")
        if tennis.legends_wins >= 5:
            self.unlock_achievement("tennis_legends_5")
        if tennis.deuce_wins >= 1:
            self.unlock_achievement("tennis_deuce_win")
        if tennis.deuce_wins >= 5:
            self.unlock_achievement("tennis_5_deuce")
        if tennis.best_match_streak >= 5:
            self.unlock_achievement("tennis_streak_5")
        if tennis.best_match_streak >= 10:
            self.unlock_achievement("tennis_streak_10")
        if tennis.max_rally_total >= 10:
            self.unlock_achievement("tennis_rally_10")
        if tennis.max_rally_total >= 20:
            self.unlock_achievement("tennis_rally_20")
        if tennis.max_rally_total >= 30:
            self.unlock_achievement("tennis_rally_30")
        if tennis.ace_master_achieved:
            self.unlock_achievement("tennis_ace_master")
        if tennis.perfect_set_achieved:
            self.unlock_achievement("tennis_perfect_set")
        if tennis.flawless_tournament_achieved:
            self.unlock_achievement("tennis_no_losses")

        if basketball.matches_won >= 1:
            self.unlock_achievement("basketball_first_win")
        if basketball.matches_won >= 5:
            self.unlock_achievement("basketball_5_wins")
        if basketball.matches_won >= 10:
            self.unlock_achievement("basketball_10_wins")
        if basketball.matches_won >= 25:
            self.unlock_achievement("basketball_25_wins")
        if basketball.matches_won >= 50:
            self.unlock_achievement("basketball_50_wins")
        if basketball.elo >= 1200:
            self.unlock_achievement("basketball_elo_1200")
        if basketball.elo >= 1500:
            self.unlock_achievement("basketball_elo_1500")
        if basketball.elo >= 1800:
            self.unlock_achievement("basketball_elo_1800")
        if basketball.elo >= 2000:
            self.unlock_achievement("basketball_elo_2000")

        completed_levels = sum(1 for level in basketball.levels if level.completed)
        if completed_levels >= 1:
            self.unlock_achievement("basketball_campaign_1")
        if completed_levels >= 5:
            self.unlock_achievement("basketball_campaign_5")
        if completed_levels >= 10:
            self.unlock_achievement("basketball_campaign_10")
        if basketball.campaign_completed:
            self.unlock_achievement("basketball_campaign_all")
        if basketball.best_streak >= 5:
            self.unlock_achievement("basketball_streak_bonus")
        if basketball.best_streak >= 5:
            self.unlock_achievement("basketball_streak_5")
        if basketball.best_streak >= 10:
            self.unlock_achievement("basketball_streak_10")
        if basketball.best_streak >= 15:
            self.unlock_achievement("basketball_streak_15")
        if basketball.ranked_matches_won >= 1:
            self.unlock_achievement("basketball_ranked_first")
        if basketball.ranked_matches_won >= 5:
            self.unlock_achievement("basketball_ranked_5")
        if basketball.ranked_matches_won >= 10:
            self.unlock_achievement("basketball_ranked_10")
        if basketball.perfect_game_achieved:
            self.unlock_achievement("basketball_perfect_game")
        if basketball.perfect_shots_total >= 5:
            self.unlock_achievement("basketball_perfect_shot_5")
        if basketball.perfect_shots_total >= 10:
            self.unlock_achievement("basketball_perfect_shot_10")
        if basketball.max_three_pointers_in_match >= 5:
            self.unlock_achievement("basketball_3pt_master")
        if basketball.max_three_pointers_in_match >= 10:
            self.unlock_achievement("basketball_3pt_god")

    def unlock_achievement(self, ach_id):
        ach = self.achievement_manager.get_achievement(ach_id)
        if ach and not ach.unlocked:
            ach.unlocked = True
            ach.unlocked_date = datetime.now().strftime("%d.%m.%Y")
            self.coins += ach.reward_coins
            if self.profile:
                self.add_exp_to_profile(ach.reward_exp)

            badge_entry = {
                'name': ach.name,
                'desc': ach.description,
                'color': ach.rarity_color,
                'date': ach.unlocked_date,
                'icon_type': ach.icon_type,
                'earned': True
            }
            exists = False
            for existing in self.campaign_badges_earned:
                if existing.get('name') == ach.name:
                    exists = True
                    break
            if not exists:
                self.campaign_badges_earned.append(badge_entry)

            self.add_notice(f"Achievement: {ach.name} +{ach.reward_coins}c", ach.rarity_color, 180)
            self.sound_manager.play_level_up()
            self.save_data()

    def create_menu_buttons(self):
        buttons = []
        y_pos = self.menu_start_y
        menu_items = [
            ("Ranked Tennis", "tennis_ranked"),
            ("Basketball Campaign", "basketball_campaign"),
            ("Duel", "duel"),
            ("World Ranking", "world_ranking"),
            ("Achievements", "achievements"),
            ("Shop", "shop"),
            ("Controls", "controls"),
            ("Settings", "settings"),
            ("Exit", "exit")
        ]
        for text, action in menu_items:
            buttons.append({"rect": pygame.Rect(30, y_pos, BASE_WIDTH - 60, 26), "text": text, "action": action})
            y_pos += self.menu_spacing
        return buttons

    def load_data(self):
        try:
            save_path = 'save.json'
            if IS_ANDROID and ANDROID_STORAGE_PATH:
                android_save = os.path.join(ANDROID_STORAGE_PATH, 'save.json')
                if os.path.exists(android_save):
                    save_path = android_save
                elif os.path.exists('save.json'):
                    try:
                        import shutil
                        shutil.copy('save.json', android_save)
                        save_path = android_save
                    except:
                        pass

            if os.path.exists(save_path):
                with open(save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    if not anti_cheat.verify_save_data(data):
                        print("Anti-cheat: Detected attempt to modify data")
                        data = {}

                    if 'profile' in data:
                        self.profile = PlayerProfile.from_dict(data['profile'])
                    else:
                        self.profile = PlayerProfile()

                    if self.profile:
                        leveled = False
                        while self.profile.bird_exp >= self.profile.bird_exp_to_next:
                            self.profile.bird_exp -= self.profile.bird_exp_to_next
                            self.profile.bird_level += 1
                            self.profile.bird_exp_to_next = int(self.profile.bird_exp_to_next * 1.5)
                            leveled = True
                        if leveled:
                            print(f"Profile level adjusted to {self.profile.bird_level}")

                    self.high_score = data.get('high_score', 0)

                    loaded_coins = data.get('coins', 100)
                    ok, msg = anti_cheat.check_coins(loaded_coins, 100, 1000)
                    if ok:
                        self.coins = loaded_coins
                    else:
                        print(f"Anti-cheat: {msg}")
                        self.coins = 100

                    self.games_played = data.get('games_played', 0)
                    self.play_time = data.get('play_time', 0)
                    self.total_coins_collected = data.get('total_coins_collected', 0)
                    self.max_combo = data.get('max_combo', 0)

                    if 'skins' in data:
                        self.skin_manager.from_dict(data['skins'])
                    if 'basketball_campaign' in data:
                        self.basketball_campaign_manager.from_dict(data['basketball_campaign'])
                    if 'tennis_ranked' in data:
                        self.tennis_ranked_system.from_dict(data['tennis_ranked'])
                    if 'campaign_badges' in data:
                        self.campaign_badges_earned = data['campaign_badges']
                    if 'control_settings' in data:
                        control_manager.from_dict(data['control_settings'])
                    if 'basketball_badges' in data:
                        self.basketball_badges_in_collection = data['basketball_badges']
                    if 'world_ranking' in data:
                        self.world_ranking_system.from_dict(data['world_ranking'])
                    if 'tv_tapes' in data:
                        for tape_data in data['tv_tapes']:
                            for tape in self.tv_player.tapes:
                                if tape.id == tape_data['id']:
                                    tape.owned = tape_data.get('owned', False)
                                    tape.equipped = tape_data.get('equipped', False)
                                    break
                    if 'achievements' in data:
                        self.achievement_manager.from_dict(data['achievements'])

                    sound_settings = data.get('sound_settings', {})
                    if sound_settings:
                        self.sound_manager.sound_volume = sound_settings.get('master_volume', 0.7)
                        self.sound_manager.music_volume = sound_settings.get('music_volume', 0.2)
                        self.sound_manager.sound_enabled = sound_settings.get('sound_enabled', True)
                        self.sound_manager.music_enabled = sound_settings.get('music_enabled', True)
                        graphics_quality = sound_settings.get('graphics_quality', 2)
                        self.screen_manager.set_graphics_quality(graphics_quality)
                        for opt in self.settings_menu.options:
                            if opt["name"] == "Graphics Quality":
                                if graphics_quality == 1:
                                    opt["value"] = "Pixelated"
                                elif graphics_quality == 2:
                                    opt["value"] = "Smooth"
                                break
            else:
                self.profile = PlayerProfile()
                self.profile.first_login = True
                self.coins = 100
        except Exception as e:
            print(f"Error loading: {e}")
            self.profile = PlayerProfile()
            self.coins = 100

    def save_data(self):
        try:
            if self.profile:
                self.profile.total_coins_earned = self.total_coins_collected
                all_badges = set()
                for badge in self.campaign_badges_earned:
                    all_badges.add(badge['name'])
                for level in self.basketball_campaign_manager.levels:
                    if level.badge and level.badge.earned:
                        all_badges.add(level.badge.name)
                for badge in self.basketball_badges_in_collection:
                    all_badges.add(badge['name'])
                for badge_tuple in self.tennis_ranked_system.get_ranked_badges():
                    all_badges.add(badge_tuple[0])
                if self.tennis_ranked_system.diamond_cup_earned:
                    all_badges.add("World Champion")
                if hasattr(self.basketball_campaign_manager, 'cups_earned'):
                    for cup in self.basketball_campaign_manager.cups_earned:
                        all_badges.add(cup)
                self.profile.badges_count = len(all_badges)
                self.profile.skins_owned = len(self.skin_manager.tennis_skins.get_owned_skins()) + len(
                    self.skin_manager.basketball_skins.get_owned_skins())
                self.profile.total_games = self.games_played
                self.profile.total_play_time = self.play_time + int(time.time() - self.start_time)
                self.profile.high_score = max(self.profile.high_score, self.high_score)
                self.profile.max_combo = max(self.profile.max_combo, self.max_combo)

            graphics_value = 2
            for opt in self.settings_menu.options:
                if opt["name"] == "Graphics Quality":
                    if opt["value"] == "Pixelated":
                        graphics_value = 1
                    else:
                        graphics_value = 2
                    self.screen_manager.set_graphics_quality(graphics_value)
                    break

            ok, msg = anti_cheat.check_coins(self.coins, 0, 1000)
            if not ok:
                print(f"Anti-cheat: {msg}")
                self.coins = 100

            data = {'profile': self.profile.to_dict() if self.profile else {},
                    'high_score': self.high_score,
                    'coins': self.coins,
                    'games_played': self.games_played,
                    'play_time': self.play_time + int(time.time() - self.start_time),
                    'total_coins_collected': self.total_coins_collected,
                    'max_combo': self.max_combo,
                    'sound_settings': {'master_volume': self.sound_manager.sound_volume,
                                       'music_volume': self.sound_manager.music_volume,
                                       'sound_enabled': self.sound_manager.sound_enabled,
                                       'music_enabled': self.sound_manager.music_enabled,
                                       'graphics_quality': graphics_value},
                    'control_settings': control_manager.to_dict(),
                    'skins': self.skin_manager.to_dict(),
                    'basketball_campaign': self.basketball_campaign_manager.to_dict(),
                    'tennis_ranked': self.tennis_ranked_system.to_dict(),
                    'campaign_badges': self.campaign_badges_earned,
                    'basketball_badges': self.basketball_badges_in_collection,
                    'world_ranking': self.world_ranking_system.to_dict(),
                    'tv_tapes': [tape.to_dict() for tape in self.tv_player.tapes],
                    'achievements': self.achievement_manager.to_dict()}

            data['_hash'] = anti_cheat.generate_hash({k: v for k, v in data.items() if k != '_hash'})

            if IS_ANDROID and ANDROID_STORAGE_PATH:
                save_path = os.path.join(ANDROID_STORAGE_PATH, 'save.json')
            else:
                save_path = 'save.json'

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving: {e}")

    def reset_game(self, game_mode):
        player_skin = None
        opponent_skin = None
        self.is_legends_match = False
        self.game_mode = game_mode

        if game_mode == "tennis_ranked":
            self.sound_manager.stop_music()
            self.sound_manager.play_tennis_music()

            player_skin = self.skin_manager.get_equipped_skin("tennis", is_opponent=False)
            player_skin_id = player_skin.id if player_skin else None
            opponent_skin = self.skin_manager.get_equipped_skin("tennis", is_opponent=True,
                                                                player_skin_id=player_skin_id)

            if self.tennis_ranked_system.is_legends_mode and self.tennis_ranked_system.bracket and self.tennis_ranked_system.legends_match_ready:
                self.is_legends_match = True
                match = self.tennis_ranked_system.bracket[0]
                self.tennis_ranked_match_data = match

                opponent_rank = self.world_ranking_system.get_player_rank(match['opponent'])
                if opponent_rank:
                    self.tennis_ranked_match_data['rank'] = opponent_rank
        elif game_mode == "basketball_campaign":
            self.sound_manager.stop_music()
            self.sound_manager.play_basketball_music()

            player_skin = self.skin_manager.get_equipped_skin("basketball", is_opponent=False)
            player_skin_id = player_skin.id if player_skin else None
            opponent_skin = self.skin_manager.get_equipped_skin("basketball", is_opponent=True,
                                                                player_skin_id=player_skin_id)

            self.basketball_campaign_manager.reset_match_stats()

            level = self.basketball_campaign_manager.get_current_level()

            if self.basketball_campaign_manager.is_ranked_match and self.basketball_campaign_manager.ranked_level:
                opponent_name = self.basketball_campaign_manager.ranked_opponent
                if opponent_name == "Player":
                    opponent_name = "Opponent"

                self.current_basketball_game = BasketballGame(
                    self.sound_manager, self.basketball_campaign_manager.ranked_level,
                    self.basketball_campaign_manager.ranked_level.difficulty, True,
                    opponent_name, player_skin, opponent_skin
                )
                self.state = "play"
                self.games_played += 1
                return
            elif level and level.is_ranked:
                opponent_name = self.basketball_campaign_manager.ranked_opponent
                if opponent_name == "Player":
                    opponent_name = "Opponent"

                self.current_basketball_game = BasketballGame(
                    self.sound_manager, level, level.difficulty, True,
                    opponent_name, player_skin, opponent_skin
                )
                self.state = "play"
                self.games_played += 1
                return

        if game_mode == "basketball_campaign":
            level = self.basketball_campaign_manager.get_current_level()
            if level and level.story_before and not self.basketball_campaign_screen.is_ranked_mode:
                self.story_display.show(level.story_before, False)
                self.waiting_for_story_continue = True
                self.state = "story"
                self._pending_game_start = lambda: self._start_basketball_game(level, player_skin, opponent_skin)
                return
            else:
                self._start_basketball_game(level, player_skin, opponent_skin)
            return
        elif game_mode == "tennis_ranked":
            match = self.tennis_ranked_system.get_current_match()
            if match and not match['completed']:
                self.tennis_ranked_match_data = match
                self._start_tennis_ranked_game(player_skin, opponent_skin)
            else:
                self.state = "tennis_ranked"
            return
        elif game_mode == "duel":
            self.sound_manager.stop_music()
            self.sound_manager.play_tennis_music()
            self.current_duel_game = TennisDuelGame(
                self.sound_manager,
                self.duel_p1_skin,
                self.duel_p2_skin,
                self.duel_court
            )
            self.current_duel_game.set_controls("keyboard", "gamepad" if len(joysticks) > 0 else "keyboard")
            self.state = "play"
            self.games_played += 1
            return

    def _start_basketball_game(self, level, player_skin, opponent_skin):
        if self.basketball_campaign_manager.is_ranked_match and self.basketball_campaign_manager.ranked_level:
            opponent_name = self.basketball_campaign_manager.ranked_opponent
            if opponent_name == "Player":
                opponent_name = "Opponent"

            self.current_basketball_game = BasketballGame(
                self.sound_manager, self.basketball_campaign_manager.ranked_level,
                self.basketball_campaign_manager.ranked_level.difficulty, True,
                opponent_name, player_skin, opponent_skin
            )
        elif level and level.is_ranked:
            opponent_name = self.basketball_campaign_manager.ranked_opponent
            if opponent_name == "Player":
                opponent_name = "Opponent"

            self.current_basketball_game = BasketballGame(
                self.sound_manager, level, level.difficulty, True,
                opponent_name, player_skin, opponent_skin
            )
        else:
            self.current_basketball_game = BasketballGame(
                self.sound_manager, level, level.difficulty, False,
                level.opponent_name, player_skin, opponent_skin
            )
        self.state = "play"
        self.games_played += 1

    def _start_tennis_ranked_game(self, player_skin, opponent_skin):
        if self.tennis_ranked_match_data:
            self.current_tennis_ranked_game = TennisRankedGame(
                self.sound_manager, self.tennis_ranked_system,
                self.tennis_ranked_match_data, player_skin, opponent_skin,
                self.is_legends_match
            )
            self.state = "play"
            self.games_played += 1

    def earn_campaign_badge(self, badge_name, badge_desc, badge_color):
        badge = {
            'name': badge_name,
            'desc': badge_desc,
            'color': badge_color,
            'date': datetime.now().strftime("%d.%m.%Y"),
            'icon_type': 'cup'
        }
        for existing in self.campaign_badges_earned:
            if existing['name'] == badge_name:
                return
        self.campaign_badges_earned.append(badge)
        self.save_data()
        self.add_notice(f"{badge_name}", badge_color, 180)

    def add_basketball_badge_to_collection(self, badge):
        for existing in self.basketball_badges_in_collection:
            if existing['name'] == badge.name:
                return
        self.basketball_badges_in_collection.append({
            'name': badge.name,
            'desc': badge.description,
            'color': badge.color,
            'date': datetime.now().strftime("%d.%m.%Y"),
            'icon_type': 'basketball'
        })
        self.save_data()

    def add_notice(self, text, color=RETRO_GOLD, duration=90):
        self.notice = (text, color)
        self.notice_timer = duration

    def update_notice(self):
        if self.notice_timer > 0:
            self.notice_timer -= 1
            if self.notice_timer <= 0:
                self.notice = None

    def draw_notice(self):
        if self.notice and self.notice_timer > 0:
            text, color = self.notice
            alpha = min(200, self.notice_timer * 3)
            text_surf = self.font_medium.render(text, True, color)
            text_shadow = self.font_medium.render(text, True, BLACK)
            bg_rect = pygame.Rect(BASE_WIDTH // 2 - text_surf.get_width() // 2 - 10, BASE_HEIGHT - 100,
                                  text_surf.get_width() + 20, 30)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, alpha // 2), bg_surf.get_rect(), 0, 8)
            pygame.draw.rect(bg_surf, color + (alpha,), bg_surf.get_rect(), 2, 8)
            self.screen_manager.virtual_screen.blit(bg_surf, bg_rect)
            self.screen_manager.virtual_screen.blit(text_shadow,
                                                     (BASE_WIDTH // 2 - text_surf.get_width() // 2 + 1,
                                                      BASE_HEIGHT - 94))
            self.screen_manager.virtual_screen.blit(text_surf,
                                                     (BASE_WIDTH // 2 - text_surf.get_width() // 2,
                                                      BASE_HEIGHT - 95))

    def draw_background(self):
        screen = self.screen_manager.virtual_screen

        if self.state == "main_menu" or self.state == "nickname" or self.state == "controls":
            bg_manager = self.skin_manager.get_bg_for_mode("main_menu")
        elif self.state in ["shop", "achievements"]:
            bg_manager = self.skin_manager.get_bg_for_mode("shop")
        elif self.state == "world_ranking":
            bg_manager = self.skin_manager.get_bg_for_mode("world_ranking")
        elif self.state == "basketball_campaign":
            bg_manager = self.skin_manager.get_bg_for_mode("basketball")
        elif self.state == "tennis_ranked":
            bg_manager = self.skin_manager.get_bg_for_mode("tennis")
        elif self.state == "duel_setup":
            bg_manager = self.skin_manager.get_bg_for_mode("main_menu")
        else:
            bg_manager = self.skin_manager.get_bg_for_mode("main_menu")

        bg = bg_manager.get_random_background()
        if bg:
            screen.blit(bg, (0, 0))
            return

        if self.state == "main_menu":
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(45 * (1 - t) + 60 * t)
                g = int(40 * (1 - t) + 55 * t)
                b = int(35 * (1 - t) + 48 * t)
                pygame.draw.line(screen, (r, g, b), (0, y), (BASE_WIDTH, y))
        else:
            for y in range(BASE_HEIGHT):
                t = y / BASE_HEIGHT
                r = int(120 * (1 - t) + 70 * t)
                g = int(180 * (1 - t) + 120 * t)
                b = int(220 * (1 - t) + 180 * t)
                pygame.draw.line(screen, (r, g, b), (0, y), (BASE_WIDTH, y))

    def draw_main_menu(self):
        self.draw_background()
        screen = self.screen_manager.virtual_screen

        self.sound_manager.play_menu_music()

        self.tv_player.update()
        self.tv_player.draw(screen, self.tv_manager.tv_x, self.tv_manager.tv_y,
                            self.tv_manager.tv_width, self.tv_manager.tv_height)

        pulse = math.sin(self.animation_time * 0.05) * 5

        title = self.font_huge.render("SKYWING", True, LAKERS_YELLOW)
        title_glow = self.font_huge.render("SKYWING", True, LAKERS_GOLD)
        title_glow.set_alpha(50)
        title_shadow = self.font_huge.render("SKYWING", True, BLACK)
        screen.blit(title_shadow, (BASE_WIDTH // 2 - title_shadow.get_width() // 2 + 3, 13 + pulse))
        screen.blit(title_glow, (BASE_WIDTH // 2 - title_glow.get_width() // 2 + 1, 10 + pulse + 1))
        screen.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 10 + pulse))

        subtitle = self.font_medium.render("TENNIS and BASKETBALL", True, RETRO_SILVER)
        subtitle_shadow = self.font_medium.render("TENNIS and BASKETBALL", True, BLACK)
        screen.blit(subtitle_shadow, (BASE_WIDTH // 2 - subtitle.get_width() // 2 + 1, 61 + pulse))
        screen.blit(subtitle, (BASE_WIDTH // 2 - subtitle.get_width() // 2, 60 + pulse))

        if self.profile:
            nick_bg = pygame.Rect(BASE_WIDTH // 2 - 80, 85, 160, 28)
            pygame.draw.rect(screen, RETRO_PURPLE, nick_bg, 0, 15)
            pygame.draw.rect(screen, RETRO_SILVER, nick_bg, 2, 15)
            nick_text = self.font_small.render(f"* {self.profile.nickname} *", True, RETRO_GOLD)
            nick_shadow = self.font_small.render(f"* {self.profile.nickname} *", True, BLACK)
            screen.blit(nick_shadow, (BASE_WIDTH // 2 - nick_text.get_width() // 2 + 1, 90))
            screen.blit(nick_text, (BASE_WIDTH // 2 - nick_text.get_width() // 2, 89))

        if self.profile:
            level_text = self.font_small.render(f"Level {self.profile.bird_level}", True, LEVEL_UP_COLOR)
            level_shadow = self.font_small.render(f"Level {self.profile.bird_level}", True, BLACK)
            screen.blit(level_shadow, (BASE_WIDTH // 2 - 99, 118))
            screen.blit(level_text, (BASE_WIDTH // 2 - 100, 117))
            exp_bar_width = 150
            exp_bar_height = 8
            exp_bar_x = BASE_WIDTH // 2 - exp_bar_width // 2
            exp_bar_y = 133
            pygame.draw.rect(screen, RETRO_DARK, (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height), 0, 4)
            exp_percent = self.profile.bird_exp / self.profile.bird_exp_to_next
            fill_width = int(exp_bar_width * min(exp_percent, 1.0))
            if fill_width > 0:
                pygame.draw.rect(screen, EXP_BAR_COLOR, (exp_bar_x, exp_bar_y, fill_width, exp_bar_height), 0, 4)
            exp_text = self.font_small.render(f"{self.profile.bird_exp}/{self.profile.bird_exp_to_next} XP", True,
                                              RETRO_GOLD)
            exp_shadow = self.font_small.render(f"{self.profile.bird_exp}/{self.profile.bird_exp_to_next} XP",
                                                True, BLACK)
            screen.blit(exp_shadow, (BASE_WIDTH // 2 - exp_text.get_width() // 2 + 1, exp_bar_y + 13))
            screen.blit(exp_text, (BASE_WIDTH // 2 - exp_text.get_width() // 2, exp_bar_y + 12))

        menu_skin = self.skin_manager.get_equipped_skin("basketball")
        bird_x = BASE_WIDTH // 2
        bird_y = 195
        menu_bird_frame = self.animation_time * 0.05

        if menu_skin and hasattr(menu_skin, 'image') and menu_skin.image is not None:
            rot = math.sin(menu_bird_frame * 2) * 3
            rotated = pygame.transform.rotate(menu_skin.image, rot)
            screen.blit(rotated, (bird_x - rotated.get_width() // 2, bird_y - rotated.get_height() // 2))
            if hasattr(menu_skin, 'rarity') and menu_skin.rarity == "legendary":
                glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                glow_alpha = 50 + int(30 * math.sin(pygame.time.get_ticks() * 0.003))
                pygame.draw.circle(glow_surf, (210, 180, 120, glow_alpha), (30, 30), 30)
                screen.blit(glow_surf, (bird_x - 30, bird_y - 30))
        else:
            self.draw_default_basketball_player(screen, bird_x, bird_y, menu_bird_frame)

        for i, button in enumerate(self.menu_buttons):
            rect = button["rect"]
            is_selected = (i == self.menu_option)
            if is_selected:
                pygame.draw.rect(screen, RETRO_SILVER, rect, 2, 6)
            font = self.font_medium
            text_surf = font.render(button["text"], True, RETRO_GOLD)
            text_glow = font.render(button["text"], True, SILVER_GLOW)
            text_glow.set_alpha(40)
            shadow_surf = font.render(button["text"], True, BLACK)
            screen.blit(shadow_surf,
                        (rect.centerx - text_surf.get_width() // 2 + 1, rect.centery - text_surf.get_height() // 2 + 1))
            screen.blit(text_glow,
                        (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))
            screen.blit(text_surf,
                        (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))

        version_text = self.font_small.render(f"v{GAME_VERSION}", True, RETRO_GRAY)
        version_shadow = self.font_small.render(f"v{GAME_VERSION}", True, BLACK)
        screen.blit(version_shadow, (BASE_WIDTH - version_text.get_width() - 9, BASE_HEIGHT - 24))
        screen.blit(version_text, (BASE_WIDTH - version_text.get_width() - 10, BASE_HEIGHT - 25))
        if control_manager.control_type == ControlType.GAMEPAD:
            indicator = "Gamepad"
            indicator_color = RETRO_BLUE
        elif control_manager.control_type == ControlType.TOUCH:
            indicator = "Touch"
            indicator_color = RETRO_GREEN
        else:
            indicator = "Keyboard"
            indicator_color = RETRO_YELLOW
        indicator_text = self.font_small.render(indicator, True, indicator_color)
        indicator_shadow = self.font_small.render(indicator, True, BLACK)
        screen.blit(indicator_shadow, (BASE_WIDTH - indicator_text.get_width() - 9, 6))
        screen.blit(indicator_text, (BASE_WIDTH - indicator_text.get_width() - 10, 5))

        pygame.mouse.set_visible(True)
        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)

    def draw_default_basketball_player(self, screen, x, y, animation):
        bird_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        primary_color = (200, 140, 60)
        secondary_color = (160, 100, 50)
        jersey_color = (200, 80, 60)

        for i in range(15, 0, -1):
            t = i / 15
            color = (int(primary_color[0] * t + secondary_color[0] * (1 - t)),
                     int(primary_color[1] * t + secondary_color[1] * (1 - t)),
                     int(primary_color[2] * t + secondary_color[2] * (1 - t)))
            pygame.draw.circle(bird_surf, color, (30, 30), i)

        jersey_rect = pygame.Rect(18, 30, 24, 18)
        pygame.draw.rect(bird_surf, jersey_color, jersey_rect, 0, 3)
        font = pygame.font.Font(None, 12)
        number = font.render("23", True, WHITE)
        bird_surf.blit(number, (23, 33))

        pygame.draw.circle(bird_surf, WHITE, (36, 24), 5)
        pygame.draw.circle(bird_surf, BLACK, (37, 24), 3)
        pygame.draw.circle(bird_surf, WHITE, (38, 23), 1)

        beak_points = [(42, 25), (48, 25), (42, 29)]
        pygame.draw.polygon(bird_surf, (200, 160, 80), beak_points)

        headband_rect = pygame.Rect(20, 14, 24, 4)
        pygame.draw.rect(bird_surf, (210, 180, 120), headband_rect, 0, 2)

        wing_y = 30 + math.sin(animation * 3) * 3
        wing_points = [(10, wing_y), (22, wing_y + 5), (15, wing_y + 10)]
        pygame.draw.polygon(bird_surf, secondary_color, wing_points)

        wing2_y = 32 + math.sin(animation * 2) * 2
        wing2_points = [(45, wing2_y), (52, wing2_y + 3), (48, wing2_y + 8)]
        pygame.draw.polygon(bird_surf, secondary_color, wing2_points)

        ball_x = 50
        ball_y = 32
        pygame.draw.circle(bird_surf, BASKETBALL_ORANGE, (ball_x, ball_y), 7)
        pygame.draw.line(bird_surf, BLACK, (ball_x - 4, ball_y), (ball_x + 4, ball_y), 1)
        pygame.draw.line(bird_surf, BLACK, (ball_x, ball_y - 4), (ball_x, ball_y + 4), 1)

        leg_offset = math.sin(animation * 4) * 2
        pygame.draw.line(bird_surf, ORANGE, (25, 48), (22, 55 + leg_offset), 2)
        pygame.draw.line(bird_surf, ORANGE, (35, 48), (38, 55 + leg_offset), 2)
        pygame.draw.circle(bird_surf, ORANGE, (22, 55 + leg_offset), 3)
        pygame.draw.circle(bird_surf, ORANGE, (38, 55 + leg_offset), 3)

        screen.blit(bird_surf, (x - 30, y - 30))

    def draw_shop(self):
        self.shop_screen.draw(self.screen_manager.virtual_screen, self.coins)
        pygame.mouse.set_visible(True)
        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(self.screen_manager.virtual_screen)

    def draw_game_over(self):
        screen = self.screen_manager.virtual_screen
        if self.game_mode == "tennis_ranked" and self.current_tennis_ranked_game:
            self.current_tennis_ranked_game.draw(screen)
        elif self.game_mode == "basketball_campaign" and self.current_basketball_game:
            self.current_basketball_game.draw(screen)
        elif self.game_mode == "duel" and self.current_duel_game:
            self.current_duel_game.draw(screen)

        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if self.game_mode == "tennis_ranked":
            if self.current_tennis_ranked_game and self.current_tennis_ranked_game.won:
                game_over = self.font_large.render("Match Won", True, RETRO_GREEN)
            else:
                game_over = self.font_large.render("Match Lost", True, RETRO_RED)
        elif self.game_mode == "basketball_campaign":
            if self.current_basketball_game and self.current_basketball_game.level_completed:
                if self.current_basketball_game.is_final:
                    game_over = self.font_large.render("Challenge Complete", True, RETRO_GOLD)
                else:
                    game_over = self.font_large.render("Basketball Won", True, RETRO_GREEN)
            else:
                if self.current_basketball_game and self.current_basketball_game.is_final:
                    game_over = self.font_large.render("Challenge Complete", True, RETRO_GOLD)
                else:
                    game_over = self.font_large.render("Basketball Lost", True, RETRO_RED)
        elif self.game_mode == "duel":
            if self.current_duel_game and self.current_duel_game.winner == "p1":
                game_over = self.font_large.render("PLAYER 1 WINS", True, RETRO_GREEN)
            elif self.current_duel_game and self.current_duel_game.winner == "p2":
                game_over = self.font_large.render("PLAYER 2 WINS", True, RETRO_RED)
            else:
                game_over = self.font_large.render("DUEL OVER", True, RETRO_RED)
        else:
            game_over = self.font_large.render("Game Over", True, RETRO_RED)

        if game_over.get_width() > BASE_WIDTH - 60:
            game_over = self.font_large.render("GAME OVER", True, RETRO_RED)

        game_over_shadow = self.font_large.render(
            game_over.get_text() if hasattr(game_over, 'get_text') else "GAME OVER", True, BLACK)
        screen.blit(game_over_shadow,
                    (BASE_WIDTH // 2 - min(game_over.get_width(), BASE_WIDTH - 60) // 2 + 1, 101))
        screen.blit(game_over, (BASE_WIDTH // 2 - min(game_over.get_width(), BASE_WIDTH - 60) // 2, 100))

        stats_y = 180
        stats = []
        if self.game_mode == "tennis_ranked" and self.current_tennis_ranked_game:
            stats = [
                f"Score {self.current_tennis_ranked_game.player_games} - {self.current_tennis_ranked_game.ai_games}"]
            if self.current_tennis_ranked_game.won:
                if self.is_legends_match:
                    stats.append(f"Victory over legend +25 ELO")
                else:
                    stats.append(f"ELO +25 (match) + tournament bonus")
                    if self.tennis_ranked_system.tournament_completed:
                        stats.append("Tournament complete +50 bonus")
            else:
                if self.is_legends_match:
                    stats.append("Defeat from legend -20 ELO")
                else:
                    stats.append("ELO +10 (defeat)")
        elif self.game_mode == "basketball_campaign" and self.current_basketball_game:
            stats = [
                f"Score {self.current_basketball_game.player_score} - {self.current_basketball_game.cpu_score}"]
            if self.current_basketball_game.level_completed:
                level = self.basketball_campaign_manager.get_current_level()
                if level:
                    if level.is_final:
                        stats.append("Challenge complete +200 coins +300XP")
                    else:
                        stats.append(f"Stars {'*' * level.stars_earned}")
                        stats.append(f"Reward +{level.reward_coins} coins +{level.reward_exp}XP")
            else:
                if self.current_basketball_game and self.current_basketball_game.is_final:
                    stats.append("Challenge complete +200 coins +300XP")
        elif self.game_mode == "duel" and self.current_duel_game:
            stats = [
                f"Score {self.current_duel_game.p1_games} - {self.current_duel_game.p2_games}"]
            p1_name = self.duel_p1_skin.name if self.duel_p1_skin else "Player 1"
            p2_name = self.duel_p2_skin.name if self.duel_p2_skin else "Player 2"
            stats.append(f"{p1_name} vs {p2_name}")

        for i, stat in enumerate(stats[:5]):
            if i >= 4:
                break
            stat_text = self.font_medium.render(stat, True, RETRO_GOLD)
            if stat_text.get_width() > BASE_WIDTH - 60:
                stat_text = self.font_medium.render(stat[:25] + "...", True, RETRO_GOLD)
            stat_shadow = self.font_medium.render(
                stat_text.get_text() if hasattr(stat_text, 'get_text') else stat[:25] + "...", True, BLACK)
            screen.blit(stat_shadow, (BASE_WIDTH // 2 - stat_text.get_width() // 2 + 1, stats_y + i * 30 + 1))
            screen.blit(stat_text, (BASE_WIDTH // 2 - stat_text.get_width() // 2, stats_y + i * 30))

        options = ["Play Again", "Main Menu"]
        start_y = 380
        for i, option in enumerate(options):
            is_selected = (i == self.game_over_option)
            rect = pygame.Rect(BASE_WIDTH // 2 - 100, start_y + i * 70, 200, 50)
            if is_selected:
                pygame.draw.rect(screen, RETRO_SILVER, rect, 2, 10)
            option_text = self.font_medium.render(option, True, RETRO_GOLD)
            option_shadow = self.font_medium.render(option, True, BLACK)
            screen.blit(option_shadow,
                        (rect.centerx - option_text.get_width() // 2 + 1,
                         rect.centery - option_text.get_height() // 2 + 1))
            screen.blit(option_text,
                        (rect.centerx - option_text.get_width() // 2, rect.centery - option_text.get_height() // 2))
        pygame.mouse.set_visible(True)
        if control_manager.control_type == ControlType.GAMEPAD:
            pixel_cursor.draw(screen)

    def draw(self):
        self.screen_manager.clear_screen()

        if self.state == "play":
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

        if self.state == "story" and self.story_display.is_visible():
            self.draw_background()
            self.story_display.draw(self.screen_manager.virtual_screen)
            pygame.mouse.set_visible(True)
            if control_manager.control_type == ControlType.GAMEPAD:
                pixel_cursor.draw(self.screen_manager.virtual_screen)
            self.screen_manager.blit_virtual_screen()
            pygame.display.flip()
            return
        if self.state == "play":
            if self.game_mode == "tennis_ranked" and self.current_tennis_ranked_game:
                self.current_tennis_ranked_game.draw(self.screen_manager.virtual_screen)
            elif self.game_mode == "basketball_campaign" and self.current_basketball_game:
                self.current_basketball_game.draw(self.screen_manager.virtual_screen)
            elif self.game_mode == "duel" and self.current_duel_game:
                self.current_duel_game.draw(self.screen_manager.virtual_screen)
            pygame.mouse.set_visible(False)
        elif self.state == "main_menu":
            self.draw_main_menu()
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "basketball_campaign":
            self.basketball_campaign_screen.draw(self.screen_manager.virtual_screen)
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "tennis_ranked":
            self.tennis_ranked_screen.draw(self.screen_manager.virtual_screen)
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "world_ranking":
            self.world_ranking_screen.draw(self.screen_manager.virtual_screen)
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "shop":
            self.draw_shop()
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "achievements":
            self.achievement_screen.draw(self.screen_manager.virtual_screen)
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "controls":
            self.controls_screen.draw(self.screen_manager.virtual_screen)
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "nickname":
            self.nickname_screen.draw(self.screen_manager.virtual_screen)
        elif self.state == "duel_setup":
            self.duel_screen.background_manager = self.skin_manager.get_bg_for_mode("main_menu")
            self.duel_screen.draw(self.screen_manager.virtual_screen)
            if self.settings_menu.active:
                self.settings_menu.draw(self.screen_manager.virtual_screen)
        elif self.state == "game_over":
            self.draw_game_over()
        self.draw_notice()
        self.screen_manager.blit_virtual_screen()
        pygame.display.flip()

    def update(self):
        self.frame_count += 1
        self.animation_time += 1

        self.screen_manager.update_shake()
        self.particles = [p for p in self.particles if p.update()]
        self.update_notice()

        self.world_ranking_system.update()

        if self.frame_count % 60 == 0:
            self.check_achievements()

        if self.state == "play" or self.state == "main_menu":
            for cloud in self.clouds:
                cloud['x'] -= cloud['speed']
                if cloud['x'] < -cloud['size'] * 2:
                    cloud['x'] = BASE_WIDTH + cloud['size']
                    cloud['y'] = random.randint(20, 200)

        for star in self.stars:
            star['brightness'] = 0.5 + 0.5 * math.sin(self.animation_time * star['twinkle_speed'] + star['phase'])
        if self.double_points_active:
            self.double_points_timer -= 1
            if self.double_points_timer <= 0:
                self.double_points_active = False

        self.tennis_ranked_screen.update()

        if self.state == "duel_setup":
            self.duel_screen.update()

        if self.state == "basketball_campaign":
            if self.basketball_campaign_manager.ranked_searching:
                found = self.basketball_campaign_manager.update_ranked_search()
                if found:
                    self.add_notice(
                        f"Opponent found {self.basketball_campaign_manager.ranked_opponent}",
                        RETRO_GOLD, 120
                    )

            if self.basketball_campaign_manager.ranked_match_ready:
                expired = self.basketball_campaign_manager.update_ranked_match_timer()
                if expired:
                    self.basketball_campaign_manager.ranked_match_found = False
                    self.basketball_campaign_manager.ranked_match_ready = False
                    self.basketball_campaign_manager.ranked_opponent = "Player"
                    self.add_notice("Opponent didn't respond Searching new", RETRO_RED, 60)

        if self.state == "play":
            if self.game_mode == "tennis_ranked":
                if self.current_tennis_ranked_game:
                    done = self.current_tennis_ranked_game.update()
                    if done:
                        won = self.current_tennis_ranked_game.won
                        stats = self.current_tennis_ranked_game.get_match_stats()
                        if stats['max_rally'] > 0:
                            self.tennis_ranked_system.update_max_rally(stats['max_rally'])
                        if stats['best_ace_sequence'] > 0:
                            self.tennis_ranked_system.update_ace_sequence(stats['best_ace_sequence'])
                        if stats['deuce_wins'] > 0:
                            self.tennis_ranked_system.deuce_wins += stats['deuce_wins']
                        if stats['perfect_set']:
                            self.tennis_ranked_system.perfect_set_achieved = True
                        self.tennis_ranked_system.complete_match(won)
                        if self.is_legends_match:
                            if won:
                                self.add_notice(f"Victory over legend +25 ELO", RETRO_GREEN, 180)
                                self.coins += 1500
                            else:
                                self.add_notice(f"Defeat from legend -20 ELO", RETRO_RED, 180)
                            self.is_legends_match = False
                            self.tennis_ranked_system.is_legends_mode = False
                            self.tennis_ranked_system.legends_match_found = False
                            self.tennis_ranked_system.legends_match_ready = False
                            self.tennis_ranked_system.legends_searching = False
                            self.tennis_ranked_system.bracket = []
                        else:
                            if won:
                                self.add_notice(f"Victory +25 ELO", RETRO_GREEN, 180)
                                self.coins += 1500
                                if self.tennis_ranked_system.tournament_completed:
                                    self.add_notice(f"TOURNAMENT COMPLETE +50 ELO", RETRO_GOLD, 240)
                                    self.coins += 200
                                    if self.tennis_ranked_system.current_tournament == len(
                                            self.tennis_ranked_system.tournaments) - 2:
                                        self.add_notice("YOU ARE WORLD CHAMPION", DIAMOND, 300)
                            else:
                                self.add_notice(f"Defeat +10 ELO", RETRO_RED, 180)
                                if self.tennis_ranked_system.current_round >= len(
                                        self.tennis_ranked_system.bracket):
                                    self.add_notice("Tournament failed Start again", RETRO_RED, 180)
                                    self.tennis_ranked_system.current_tournament = None
                                    self.tennis_ranked_system.current_round = 0
                                    self.tennis_ranked_system.bracket = []
                        self.add_player_to_ranking()
                        self.check_achievements()
                        self.current_tennis_ranked_game = None
                        self.tennis_ranked_match_data = None
                        self.state = "tennis_ranked"
                return
            if self.game_mode == "basketball_campaign":
                if self.current_basketball_game:
                    self.current_basketball_game.handle_player_input()
                    done = self.current_basketball_game.update()
                    if done:
                        level = self.basketball_campaign_manager.get_current_level()
                        player_score = self.current_basketball_game.player_score
                        cpu_score = self.current_basketball_game.cpu_score
                        match_stats = self.current_basketball_game.get_match_stats()

                        if match_stats['perfect_shots'] > 0:
                            self.basketball_campaign_manager.perfect_shots_total += match_stats['perfect_shots']
                        if match_stats['three_pointers'] > self.basketball_campaign_manager.max_three_pointers_in_match:
                            self.basketball_campaign_manager.max_three_pointers_in_match = match_stats['three_pointers']
                        if match_stats['perfect_game'] and self.current_basketball_game.player_won:
                            self.basketball_campaign_manager.perfect_game_achieved = True
                        if match_stats['max_streak'] > self.basketball_campaign_manager.best_streak:
                            self.basketball_campaign_manager.best_streak = match_stats['max_streak']

                        if self.basketball_campaign_manager.is_ranked_match or (level and level.is_ranked):
                            streak_bonus = self.basketball_campaign_manager.streak_bonus_earned
                            result, elo_change, outcome, bonus_earned = self.basketball_campaign_manager.complete_level(
                                player_score, cpu_score
                            )
                            if outcome == "win":
                                bonus_text = f" +{bonus_earned} bonus" if bonus_earned > 0 else ""
                                self.add_notice(f"Victory +{elo_change} ELO{bonus_text}", RETRO_GREEN, 180)
                                self.coins += 1500
                                cup_name, cup_color = self.basketball_campaign_manager.check_cups()
                                if cup_name:
                                    self.add_notice(f"{cup_name} earned", cup_color, 240)
                            else:
                                bonus_text = f" +{bonus_earned} bonus" if bonus_earned > 0 else ""
                                self.add_notice(f"Defeat {elo_change} ELO{bonus_text}", RETRO_RED, 180)
                            self.add_player_to_ranking()
                            self.check_achievements()
                            self.current_basketball_game = None
                            self.state = "basketball_campaign"
                            return

                        if self.current_basketball_game.level_completed:
                            if level.is_final:
                                result, elo_change, outcome, bonus_earned = self.basketball_campaign_manager.complete_level(
                                    self.current_basketball_game.player_score,
                                    self.current_basketball_game.cpu_score
                                )
                                self.coins += 200
                                self.add_notice("Challenge complete +200 coins +300XP", RETRO_GOLD, 180)
                                if level.story_after:
                                    self.story_display.show(level.story_after, True)
                                    self.waiting_for_story_continue = True
                                    self.state = "story"
                                    self._pending_game_start = None
                                    self.current_basketball_game = None
                                    return
                            else:
                                result, elo_change, outcome, bonus_earned = self.basketball_campaign_manager.complete_level(
                                    self.current_basketball_game.player_score,
                                    self.current_basketball_game.cpu_score
                                )
                                reward_coins = level.reward_coins
                                reward_exp = level.reward_exp
                                stars = self.basketball_campaign_manager.get_current_level().stars_earned
                                self.coins += reward_coins
                                if self.profile:
                                    self.add_exp_to_profile(reward_exp)
                                stars_display = "*" * stars + "o" * (3 - stars)
                                self.add_notice(
                                    f"Match won +{reward_coins} coins +{reward_exp}XP {stars_display}",
                                    RETRO_GOLD, 180)
                                if level.badge and level.badge.earned:
                                    self.add_basketball_badge_to_collection(level.badge)
                                if level.id == len(self.basketball_campaign_manager.levels) - 1:
                                    self.earn_campaign_badge("Basketball Champion",
                                                             "Completed all basketball campaign", RETRO_GOLD)
                                if level.story_after:
                                    self.story_display.show(level.story_after, True)
                                    self.waiting_for_story_continue = True
                                    self.state = "story"
                                    self._pending_game_start = None
                                    self.current_basketball_game = None
                                    return
                        else:
                            if level.is_final:
                                result, elo_change, outcome, bonus_earned = self.basketball_campaign_manager.complete_level(
                                    self.current_basketball_game.player_score,
                                    self.current_basketball_game.cpu_score
                                )
                                self.coins += 200
                                self.add_notice("Challenge complete +200 coins +300XP", RETRO_GOLD, 180)
                                if level.story_after:
                                    self.story_display.show(level.story_after, True)
                                    self.waiting_for_story_continue = True
                                    self.state = "story"
                                    self._pending_game_start = None
                                    self.current_basketball_game = None
                                    return
                            else:
                                self.add_notice(
                                    f"Match lost {self.current_basketball_game.cpu_score} - {self.current_basketball_game.player_score}",
                                    RETRO_RED, 180)
                        self.add_player_to_ranking()
                        self.check_achievements()
                        self.current_basketball_game = None
                        self.state = "basketball_campaign"
                return
            if self.game_mode == "duel":
                if self.current_duel_game:
                    done = self.current_duel_game.update()
                    if done:
                        self.state = "game_over"
                        self.game_over_option = 0
                return

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        control_manager.update_menu_cooldown()
        if self.touch_click_cooldown > 0:
            self.touch_click_cooldown -= 1

        if self.state != "play":
            pixel_cursor.update_from_gamepad()
            if pixel_cursor.is_clicking():
                click_x, click_y = int(pixel_cursor.x), int(pixel_cursor.y)
                self.handle_click(click_x, click_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_data()
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                self.screen_manager.handle_resize(event.w, event.h)
            if IS_ANDROID and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    virtual_x, virtual_y = self.screen_manager.unscale_position(event.pos[0], event.pos[1])
                    if self.state == "play":
                        touch_controls.handle_touch_down((virtual_x, virtual_y), 0)
                        continue
                elif event.type == pygame.MOUSEBUTTONUP:
                    virtual_x, virtual_y = self.screen_manager.unscale_position(event.pos[0], event.pos[1])
                    if self.state == "play":
                        touch_controls.handle_touch_up((virtual_x, virtual_y), 0)
                        continue
                elif event.type == pygame.MOUSEMOTION:
                    if self.state == "play" and touch_controls.joystick_active:
                        virtual_x, virtual_y = self.screen_manager.unscale_position(event.pos[0], event.pos[1])
                        touch_controls.handle_touch_move((virtual_x, virtual_y), 0)
                        continue

            if event.type == pygame.KEYDOWN:
                if self.state == "world_ranking":
                    result = self.world_ranking_screen.handle_keyboard(event)
                    if result == "search_complete":
                        pass
                    continue

                if self.state == "story" and self.waiting_for_story_continue:
                    if event.key == pygame.K_e or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.story_display.handle_input():
                            if hasattr(self, '_pending_game_start') and self._pending_game_start:
                                self._pending_game_start()
                                self._pending_game_start = None
                                self.waiting_for_story_continue = False
                            else:
                                self.state = "basketball_campaign"
                                self.waiting_for_story_continue = False
                        continue
                if self.settings_menu.active:
                    result = self.settings_menu.handle_event(event, 0, 0)
                    if result == "close":
                        self.settings_menu.active = False
                        self.save_data()
                    continue
                if self.state == "nickname":
                    result = self.nickname_screen.handle_event(event)
                    if result:
                        self.profile.nickname = result
                        self.profile.first_login = False
                        self.add_player_to_ranking()
                        self.state = "main_menu"
                    continue
                if self.state == "duel_setup":
                    result = self.duel_screen.handle_keyboard(event)
                    if result == "start_duel":
                        self.duel_p1_type = "keyboard"
                        self.duel_p2_type = "gamepad" if len(joysticks) > 0 else "keyboard"
                        self.duel_p1_skin = self.duel_screen.p1_skin
                        self.duel_p2_skin = self.duel_screen.p2_skin
                        self.duel_court = self.duel_screen.court
                        self.reset_game("duel")
                    continue
                if event.key == pygame.K_ESCAPE:
                    if self.state == "play":
                        if self.game_mode == "tennis_ranked" and self.current_tennis_ranked_game:
                            self.current_tennis_ranked_game.game_over = True
                            self.current_tennis_ranked_game.won = False
                            if self.is_legends_match:
                                self.tennis_ranked_system.elo -= 20
                                self.add_notice("Match aborted -20 ELO", RETRO_RED, 120)
                            else:
                                self.tennis_ranked_system.elo -= 20
                                self.add_notice("Match aborted -20 ELO", RETRO_RED, 120)
                            self.current_tennis_ranked_game = None
                            self.state = "tennis_ranked"
                            self.add_player_to_ranking()
                        elif self.game_mode == "basketball_campaign" and self.current_basketball_game:
                            self.current_basketball_game.game_over = True
                            self.current_basketball_game.player_won = False
                            self.current_basketball_game.level_completed = False
                            self.basketball_campaign_manager.elo -= 20
                            self.add_notice("Match aborted -20 ELO", RETRO_RED, 120)
                            self.current_basketball_game = None
                            self.state = "basketball_campaign"
                            self.add_player_to_ranking()
                        elif self.game_mode == "duel":
                            self.current_duel_game = None
                            self.state = "main_menu"
                    elif self.state in ["shop", "basketball_campaign",
                                        "tennis_ranked", "world_ranking", "controls", "achievements",
                                        "duel_setup"]:
                        self.state = "main_menu"
                        if self.state == "duel_setup":
                            self.duel_screen.reset()
                    elif self.state == "game_over":
                        self.state = "main_menu"
                elif event.key == pygame.K_UP:
                    if self.state == "main_menu" and control_manager.can_menu_navigate():
                        self.menu_option = (self.menu_option - 1) % len(self.menu_buttons)
                    elif self.state == "game_over":
                        self.game_over_option = (self.game_over_option - 1) % 2
                elif event.key == pygame.K_DOWN:
                    if self.state == "main_menu" and control_manager.can_menu_navigate():
                        self.menu_option = (self.menu_option + 1) % len(self.menu_buttons)
                    elif self.state == "game_over":
                        self.game_over_option = (self.game_over_option + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if self.state == "main_menu":
                        action = self.menu_buttons[self.menu_option]["action"]
                        self.sound_manager.play_button()
                        if action == "tennis_ranked":
                            self.state = "tennis_ranked"
                            self.tennis_ranked_screen.selected_tournament = 0
                        elif action == "basketball_campaign":
                            self.state = "basketball_campaign"
                        elif action == "duel":
                            self.duel_screen.reset()
                            all_tennis_skins = self.skin_manager.tennis_skins.skins
                            available = [s for s in all_tennis_skins if s.image is not None]
                            if not available and all_tennis_skins:
                                available = all_tennis_skins[:]
                            self.duel_screen.set_available_skins(available)
                            self.state = "duel_setup"
                        elif action == "world_ranking":
                            self.state = "world_ranking"
                            self.world_ranking_screen.page = 0
                            self.world_ranking_screen.search_text = ""
                            self.world_ranking_screen.search_active = False
                        elif action == "achievements":
                            self.state = "achievements"
                            self.achievement_screen.page = 0
                            self.achievement_screen.category = "all"
                        elif action == "shop":
                            self.state = "shop"
                            self.shop_screen.page = 0
                            self.shop_screen.mode_filter = "all"
                            self.shop_screen.show_tape_shop = False
                        elif action == "controls":
                            self.state = "controls"
                            self.controls_screen.scroll_offset = 0
                        elif action == "settings":
                            self.settings_menu.active = True
                            self.settings_menu.update_from_manager()
                        elif action == "exit":
                            self.save_data()
                            pygame.quit()
                            sys.exit()
                    elif self.state == "game_over":
                        self.sound_manager.play_button()
                        if self.game_over_option == 0:
                            if self.game_mode == "duel":
                                self.current_duel_game = TennisDuelGame(
                                    self.sound_manager,
                                    self.duel_p1_skin,
                                    self.duel_p2_skin,
                                    self.duel_court
                                )
                                self.current_duel_game.set_controls("keyboard", "gamepad" if len(joysticks) > 0 else "keyboard")
                                self.state = "play"
                            else:
                                self.reset_game(self.game_mode)
                        else:
                            self.state = "main_menu"
            if control_manager.is_menu_up_pressed() and control_manager.can_menu_navigate() and self.state == "main_menu" and not self.settings_menu.active:
                self.menu_option = (self.menu_option - 1) % len(self.menu_buttons)
            if control_manager.is_menu_down_pressed() and control_manager.can_menu_navigate() and self.state == "main_menu" and not self.settings_menu.active:
                self.menu_option = (self.menu_option + 1) % len(self.menu_buttons)
            if control_manager.is_menu_select_pressed() and self.state == "main_menu" and not self.settings_menu.active:
                action = self.menu_buttons[self.menu_option]["action"]
                self.sound_manager.play_button()
                if action == "tennis_ranked":
                    self.state = "tennis_ranked"
                    self.tennis_ranked_screen.selected_tournament = 0
                elif action == "basketball_campaign":
                    self.state = "basketball_campaign"
                elif action == "duel":
                    self.duel_screen.reset()
                    all_tennis_skins = self.skin_manager.tennis_skins.skins
                    available = [s for s in all_tennis_skins if s.image is not None]
                    if not available and all_tennis_skins:
                        available = all_tennis_skins[:]
                    self.duel_screen.set_available_skins(available)
                    self.state = "duel_setup"
                elif action == "world_ranking":
                    self.state = "world_ranking"
                    self.world_ranking_screen.page = 0
                    self.world_ranking_screen.search_text = ""
                    self.world_ranking_screen.search_active = False
                elif action == "achievements":
                    self.state = "achievements"
                    self.achievement_screen.page = 0
                    self.achievement_screen.category = "all"
                elif action == "shop":
                    self.state = "shop"
                    self.shop_screen.page = 0
                    self.shop_screen.mode_filter = "all"
                    self.shop_screen.show_tape_shop = False
                elif action == "controls":
                    self.state = "controls"
                    self.controls_screen.scroll_offset = 0
                elif action == "settings":
                    self.settings_menu.active = True
                    self.settings_menu.update_from_manager()
                elif action == "exit":
                    self.save_data()
                    pygame.quit()
                    sys.exit()
            if control_manager.is_menu_back_pressed() and self.state not in ["play", "main_menu"] and not self.settings_menu.active and self.state != "story":
                if self.state == "duel_setup":
                    self.duel_screen.reset()
                self.state = "main_menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                virtual_x, virtual_y = self.screen_manager.unscale_position(mouse_pos[0], mouse_pos[1])
                if self.state == "duel_setup":
                    if event.button == 1:
                        self.duel_screen.handle_mouse_down(virtual_x, virtual_y)
                self.handle_click(virtual_x, virtual_y)
                if event.button == 4:
                    if self.state == "basketball_campaign":
                        self.basketball_campaign_screen.handle_scroll(-30)
                    elif self.state == "tennis_ranked":
                        self.tennis_ranked_screen.handle_scroll(-30)
                    elif self.state == "controls":
                        self.controls_screen.handle_scroll(-30)
                    elif self.state == "achievements":
                        self.achievement_screen.handle_scroll(-30)
                    elif self.state == "duel_setup":
                        self.duel_screen.handle_scroll(-30)
                    elif self.state == "shop":
                        all_skins = self.skin_manager.tennis_skins.skins + self.skin_manager.basketball_skins.skins
                        if self.shop_screen.mode_filter != "all":
                            all_skins = [s for s in all_skins if s.mode_key == self.shop_screen.mode_filter]
                        max_page = max(0, (len(all_skins) - 1) // 4)
                        self.shop_screen.page = max(0, self.shop_screen.page - 1)
                elif event.button == 5:
                    if self.state == "basketball_campaign":
                        self.basketball_campaign_screen.handle_scroll(30)
                    elif self.state == "tennis_ranked":
                        self.tennis_ranked_screen.handle_scroll(30)
                    elif self.state == "controls":
                        self.controls_screen.handle_scroll(30)
                    elif self.state == "achievements":
                        self.achievement_screen.handle_scroll(30)
                    elif self.state == "duel_setup":
                        self.duel_screen.handle_scroll(30)
                    elif self.state == "shop":
                        all_skins = self.skin_manager.tennis_skins.skins + self.skin_manager.basketball_skins.skins
                        if self.shop_screen.mode_filter != "all":
                            all_skins = [s for s in all_skins if s.mode_key == self.shop_screen.mode_filter]
                        max_page = max(0, (len(all_skins) - 1) // 4)
                        self.shop_screen.page = min(max_page, self.shop_screen.page + 1)
            if event.type == pygame.MOUSEMOTION:
                virtual_x, virtual_y = self.screen_manager.unscale_position(mouse_pos[0], mouse_pos[1])
                if self.state == "duel_setup":
                    self.duel_screen.handle_mouse_motion(virtual_x, virtual_y)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.state == "duel_setup":
                        self.duel_screen.handle_mouse_up()

    def handle_click(self, x, y):
        if self.settings_menu.active:
            result = self.settings_menu.handle_event(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(x, y)), x, y)
            if result == "close":
                self.settings_menu.active = False
                self.save_data()
            return

        if self.state == "world_ranking":
            result = self.world_ranking_screen.handle_click(x, y)
            if result == "back":
                self.state = "main_menu"
            return

        if self.state == "story" and self.waiting_for_story_continue:
            if self.story_display.handle_input():
                if hasattr(self, '_pending_game_start') and self._pending_game_start:
                    self._pending_game_start()
                    self._pending_game_start = None
                    self.waiting_for_story_continue = False
                else:
                    self.state = "basketball_campaign"
                    self.waiting_for_story_continue = False
            return

        if self.state == "controls":
            result = self.controls_screen.handle_click(x, y)
            if result == "back":
                self.state = "main_menu"
            return

        if self.state == "achievements":
            result = self.achievement_screen.handle_click(x, y)
            if result == "back":
                self.state = "main_menu"
            return

        if self.state == "play":
            if self.game_mode == "tennis_ranked" and self.current_tennis_ranked_game:
                pass
            elif self.game_mode == "basketball_campaign" and self.current_basketball_game:
                pass
            elif self.game_mode == "duel" and self.current_duel_game:
                pass
            return

        if self.state == "duel_setup":
            result = self.duel_screen.handle_click(x, y)
            if result == "back":
                self.duel_screen.reset()
                self.state = "main_menu"
                return
            elif result == "start_duel":
                self.duel_p1_type = "keyboard"
                self.duel_p2_type = "gamepad" if len(joysticks) > 0 else "keyboard"
                self.duel_p1_skin = self.duel_screen.p1_skin
                self.duel_p2_skin = self.duel_screen.p2_skin
                self.duel_court = self.duel_screen.court
                self.reset_game("duel")
                return
            return

        if self.state == "main_menu":
            if self.tv_manager.tv_rect and self.tv_manager.tv_rect.collidepoint(x, y):
                self.sound_manager.play_button()
                if self.tv_player.video_files and self.tv_player.video_loaded:
                    equipped = self.tv_player.get_equipped_tape()
                    if equipped:
                        self.add_notice(f"Tape {equipped.name}", RETRO_GOLD, 90)
                    else:
                        self.add_notice("Next video", RETRO_GOLD, 90)
                elif self.tv_player.video_files:
                    self.add_notice("Loading video", RETRO_GOLD, 90)
                else:
                    self.add_notice("No video in tv_videos folder", RETRO_GOLD, 120)
                return

            for i, button in enumerate(self.menu_buttons):
                if button["rect"].collidepoint(x, y):
                    action = button["action"]
                    self.sound_manager.play_button()
                    if action == "tennis_ranked":
                        self.state = "tennis_ranked"
                        self.tennis_ranked_screen.selected_tournament = 0
                    elif action == "basketball_campaign":
                        self.state = "basketball_campaign"
                    elif action == "duel":
                        self.duel_screen.reset()
                        all_tennis_skins = self.skin_manager.tennis_skins.skins
                        available = [s for s in all_tennis_skins if s.image is not None]
                        if not available and all_tennis_skins:
                            available = all_tennis_skins[:]
                        self.duel_screen.set_available_skins(available)
                        self.state = "duel_setup"
                    elif action == "world_ranking":
                        self.state = "world_ranking"
                        self.world_ranking_screen.page = 0
                        self.world_ranking_screen.search_text = ""
                        self.world_ranking_screen.search_active = False
                    elif action == "achievements":
                        self.state = "achievements"
                        self.achievement_screen.page = 0
                        self.achievement_screen.category = "all"
                    elif action == "shop":
                        self.state = "shop"
                        self.shop_screen.page = 0
                        self.shop_screen.mode_filter = "all"
                        self.shop_screen.show_tape_shop = False
                    elif action == "controls":
                        self.state = "controls"
                        self.controls_screen.scroll_offset = 0
                    elif action == "settings":
                        self.settings_menu.active = True
                        self.settings_menu.update_from_manager()
                    elif action == "exit":
                        self.save_data()
                        pygame.quit()
                        sys.exit()
                    break
            return

        if self.state == "basketball_campaign":
            result = self.basketball_campaign_screen.handle_click(x, y)

            if result == "back":
                self.sound_manager.play_button()
                self.state = "main_menu"
                return

            if result == "ranked_accept":
                self.sound_manager.play_button()
                accepted, opponent = self.basketball_campaign_manager.accept_ranked_match()
                if accepted:
                    self.basketball_campaign_manager.ranked_opponent = opponent
                    self.reset_game("basketball_campaign")
                else:
                    self.add_notice("Error accepting match", RETRO_RED, 120)
                return

            if result == "ranked_search":
                if not self.basketball_campaign_manager.ranked_searching and not self.basketball_campaign_manager.ranked_match_found:
                    self.basketball_campaign_manager.start_ranked_search()
                    self.sound_manager.play_button()
                    self.add_notice("Searching for opponent", RETRO_GOLD, 60)
                return

            if result:
                self.reset_game("basketball_campaign")
            return

        if self.state == "tennis_ranked":
            result = self.tennis_ranked_screen.handle_click(x, y)
            if result == 'back':
                self.state = "main_menu"
            elif result == 'start_match' or result == 'start_legends_match':
                self.reset_game("tennis_ranked")
            return

        if self.state == "shop":
            result = self.shop_screen.handle_click(x, y, self.coins)
            if result == "back":
                self.sound_manager.play_button()
                self.state = "main_menu"
                return
            elif result and isinstance(result, tuple):
                action, value = result
                if action == "equip":
                    self.add_notice("Skin equipped", RETRO_GREEN, 120)
                    self.sound_manager.play_button()
                    self.save_data()
                elif action == "buy":
                    self.add_notice("Skin purchased", RETRO_GOLD, 120)
                    self.sound_manager.play_powerup()
                    self.save_data()
                elif action == "not_enough_coins":
                    self.add_notice("Not enough coins", RETRO_RED, 120)
                elif action == "tape_equip":
                    self.add_notice("Tape equipped", RETRO_GREEN, 120)
                    self.sound_manager.play_button()
                    self.save_data()
                elif action == "tape_buy":
                    self.add_notice("Tape purchased", RETRO_GOLD, 120)
                    self.sound_manager.play_powerup()
                    self.save_data()
                elif action == "tape_not_enough":
                    self.add_notice("Not enough coins", RETRO_RED, 120)
            return

        if self.state == "game_over":
            self.handle_game_over_click(x, y)
            return

    def handle_game_over_click(self, x, y):
        start_y = 380
        options = ["Play Again", "Main Menu"]
        for i, option in enumerate(options):
            rect = pygame.Rect(BASE_WIDTH // 2 - 100, start_y + i * 70, 200, 50)
            if rect.collidepoint(x, y):
                self.sound_manager.play_button()
                if i == 0:
                    if self.game_mode == "duel":
                        self.current_duel_game = TennisDuelGame(
                            self.sound_manager,
                            self.duel_p1_skin,
                            self.duel_p2_skin,
                            self.duel_court
                        )
                        self.current_duel_game.set_controls("keyboard", "gamepad" if len(joysticks) > 0 else "keyboard")
                        self.state = "play"
                    else:
                        self.reset_game(self.game_mode)
                elif i == 1:
                    if self.score > self.profile.high_score:
                        self.profile.high_score = self.score
                    self.save_data()
                    self.state = "main_menu"
                break

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    try:
        import pygame._sdl2 as sdl2
    except:
        pass

    game = Game()
    game.run()