import pygame

class Display:
    def __init__(self, surface):
        self.surface = surface
        self.pixel_size = 16  # Размер одного пикселя
        self.display_size = 16  # 16x16 пикселей
        self.pixel_data = {}  # Теперь храним кортеж (on/off, brightness)
        self.text = ["0"] * 8  # 8 цифр для сегментного дисплея
        
        # Цвета
        self.colors = {
            "on": (0, 255, 0),    # Будет модифицироваться яркостью
            "off": (0, 32, 0)     # Неактивные пиксели не меняются
        }
        
        # Описание сегментов для символов (новый charmap)
        self.segments = {
            0: [1,1,1,1,1,1,0],   # 0
            1: [0,1,1,0,0,0,0],   # 1
            2: [1,1,0,1,1,0,1],   # 2
            3: [1,1,1,1,0,0,1],   # 3
            4: [0,1,1,0,0,1,1],   # 4
            5: [1,0,1,1,0,1,1],   # 5
            6: [1,0,1,1,1,1,1],   # 6
            7: [1,1,1,0,0,0,0],   # 7
            8: [1,1,1,1,1,1,1],   # 8
            9: [1,1,1,1,0,1,1],   # 9
            10: [0,0,0,0,0,0,1],  # - (минус)
            11: [0,0,0,1,0,0,0],  # _ (подчеркивание)
            12: [0,0,0,0,0,0,0],  # пробел
            13: [1,0,1,1,1,0,1],  # E (ESC)
            14: [1,0,0,1,1,1,1],  # d (DEL)
            15: [1,0,0,1,1,1,0],  # n (ENTER)
            16: [0,1,1,0,0,1,1],  # ↑ (вверх)
            17: [1,0,0,1,1,0,1],  # ↓ (вниз)
            18: [1,1,1,0,0,1,1],  # → (вправо)
            19: [1,1,0,0,1,1,1],  # ← (влево)
        }
        
        # Добавляем параметры для клавиатуры
        self.key_size = 40  # Размер клавиши
        self.key_spacing = 5  # Расстояние между клавишами
        self.key_colors = {
            "normal": (60, 60, 60),    # Цвет неактивной клавиши
            "pressed": (100, 100, 100), # Цвет нажатой клавиши
            "text": (0, 255, 0)        # Цвет текста
        }
        self.pressed_keys = set()  # Множество нажатых клавиш
        
        # Описание расположения клавиш с информацией о ширине (в единицах клавиш)
        self.keyboard_layout = [
            [("ESC",1), ("1",1), ("2",1), ("3",1), ("4",1), ("5",1), ("6",1), ("7",1), ("8",1), ("9",1), ("0",1), ("DEL",1)],
            [("",1), ("",1), ("",1), ("",1), ("↑",1), ("",1), ("",1), ("",1), ("",1), ("ENTER",2), ("",1), ("",0)],
            [("",1), ("",1), ("",1), ("←",1), ("↓",1), ("→",1), ("",1), ("",1), ("",1), ("",1), ("",1), ("",0)]
        ]
        
        # Обновляем коды клавиш для соответствия новому charmap
        self.key_codes = {
            "0": 0,     # Теперь используем индексы вместо ASCII
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "-": 10,
            "_": 11,
            " ": 12,
            "ESC": 13,
            "DEL": 14,
            "ENTER": 15,
            "↑": 16,
            "↓": 17,
            "→": 18,
            "←": 19
        }

        self.power_button = pygame.Rect(0, 0, 40, 40)  # Создаем rect для кнопки
        self.power_colors = {
            "on": (0, 255, 0),    # Зеленый когда включен
            "off": (255, 0, 0),   # Красный когда выключен
            "border": (100, 100, 100)  # Серая рамка
        }

        self.powered = False  # Состояние питания
        
        # Цвета для выключенного состояния
        self.colors_off = {
            "on": (0, 32, 0),     # Темно-зеленый для всех элементов
            "off": (0, 16, 0)      # Еще более темный зеленый
        }

        self.default_brightness = 255  # Яркость по умолчанию

        # Добавляем элементы для кассеты
        self.cassette_slot = pygame.Rect(350, 120, 200, 30)  # Шире и под сегментным дисплеем
        self.inject_button = pygame.Rect(350, 160, 95, 30)   # Кнопка INJECT слева
        self.eject_button = pygame.Rect(455, 160, 95, 30)    # Кнопка EJECT справа
        
        self.cassette_inserted = False
        self.current_cassette = None

    def set_brightness(self, value):
        """Установить яркость (0-255)"""
        self.brightness = max(0, min(255, value))
        # Обновляем цвет активных пикселей
        self.colors["on"] = (0, self.brightness, 0)

    def set_pixel(self, x, y, on=True, brightness=None):
        """Установить пиксель на пиксельном дисплее с заданной яркостью"""
        if 0 <= x < self.display_size and 0 <= y < self.display_size:
            if brightness is None:
                brightness = self.default_brightness
            self.pixel_data[(x, y)] = (on, brightness)

    def clear_display(self):
        """Очистить оба дисплея"""
        self.pixel_data = {}
        self.text = ["0"] * 8

    def draw_pixel_display(self, x, y):
        """Отрисовка пиксельного дисплея"""
        # Рисуем рамку
        pygame.draw.rect(self.surface, (100, 100, 100), 
                        (x-2, y-2, 
                         self.display_size * self.pixel_size + 4,
                         self.display_size * self.pixel_size + 4), 2)
        
        # Минимальная яркость для включенных пикселей
        min_brightness = 32
        
        # Рисуем пиксели
        for py in range(self.display_size):
            for px in range(self.display_size):
                pixel_info = self.pixel_data.get((px, py), (False, 0))
                if pixel_info[0]:  # Если пиксель включен
                    if self.powered:
                        # Применяем минимальную яркость
                        brightness = pixel_info[1]
                        actual_brightness = min_brightness + (brightness * (255 - min_brightness) // 255)
                        color = (0, actual_brightness, 0)
                    else:
                        color = self.colors_off["on"]
                else:
                    color = self.colors["off"]  # Цвет выключенного пикселя всегда темно-зеленый
                    
                pygame.draw.rect(self.surface, color,
                               (x + px * self.pixel_size,
                                y + py * self.pixel_size,
                                self.pixel_size - 1,
                                self.pixel_size - 1))

    def draw_segment(self, pos_x, pos_y, segment_data):
        """Отрисовка одного семисегментного индикатора"""
        size = 20  # Размер сегмента
        thickness = 4  # Толщина линии
        
        segments = [
            # a: горизонтальный верхний
            [(pos_x, pos_y), (pos_x + size, pos_y)],
            # b: вертикальный правый верхний
            [(pos_x + size, pos_y), (pos_x + size, pos_y + size)],
            # c: вертикальный правый нижний
            [(pos_x + size, pos_y + size), (pos_x + size, pos_y + 2*size)],
            # d: горизонтальный нижний
            [(pos_x, pos_y + 2*size), (pos_x + size, pos_y + 2*size)],
            # e: вертикальный левый нижний
            [(pos_x, pos_y + size), (pos_x, pos_y + 2*size)],
            # f: вертикальный левый верхний
            [(pos_x, pos_y), (pos_x, pos_y + size)],
            # g: горизонтальный средний
            [(pos_x, pos_y + size), (pos_x + size, pos_y + size)]
        ]
        
        # Выбираем палитру в зависимости от состояния питания
        colors = self.colors if self.powered else self.colors_off
        
        for i, (start, end) in enumerate(segments):
            color = colors["on"] if segment_data[i] else colors["off"]
            pygame.draw.line(self.surface, color, start, end, thickness)

    def draw_text(self, x, y):
        """Отрисовка 7-сегментного дисплея"""
        # Рисуем рамку вокруг всего сегментного дисплея
        total_width = 8 * 30  # 8 цифр по 30 пикселей
        pygame.draw.rect(self.surface, (100, 100, 100),
                        (x-5, y-5, total_width + 10, 50), 2)
        
        # Отрисовка каждой цифры
        for i, digit in enumerate(self.text):
            try:
                # Теперь digit это строка с числом 0-19
                segments = self.segments[int(digit)]
                self.draw_segment(x + i*30, y, segments)  # Передаем сегменты напрямую
            except (ValueError, KeyError):
                # Если что-то пошло не так, показываем выключенный сегмент
                self.draw_segment(x + i*30, y, [0,0,0,0,0,0,0])

    def draw_arrow(self, x, y, direction):
        """Отрисовка стрелки"""
        # Размер стрелки немного меньше размера клавиши
        arrow_size = self.key_size * 0.6
        center_x = x + self.key_size // 2
        center_y = y + self.key_size // 2
        
        if direction == "↑":
            points = [
                (center_x, center_y - arrow_size//2),  # Вершина
                (center_x - arrow_size//2, center_y + arrow_size//2),  # Левый нижний
                (center_x + arrow_size//2, center_y + arrow_size//2)   # Правый нижний
            ]
        elif direction == "↓":
            points = [
                (center_x, center_y + arrow_size//2),  # Вершина
                (center_x - arrow_size//2, center_y - arrow_size//2),  # Левый верхний
                (center_x + arrow_size//2, center_y - arrow_size//2)   # Правый верхний
            ]
        elif direction == "←":
            points = [
                (center_x - arrow_size//2, center_y),  # Вершина
                (center_x + arrow_size//2, center_y - arrow_size//2),  # Верхний правый
                (center_x + arrow_size//2, center_y + arrow_size//2)   # Нижний правый
            ]
        elif direction == "→":
            points = [
                (center_x + arrow_size//2, center_y),  # Вершина
                (center_x - arrow_size//2, center_y - arrow_size//2),  # Верхний левый
                (center_x - arrow_size//2, center_y + arrow_size//2)   # Нижний левый
            ]
        
        pygame.draw.polygon(self.surface, self.key_colors["text"], points)

    def draw_keyboard(self, x, y):
        """Отрисовка виртуальной клавиатуры"""
        font = pygame.font.Font(None, 24)
        
        # Рисуем рамку вокруг клавиатуры
        total_width = 12 * (self.key_size + self.key_spacing)
        total_height = 3 * (self.key_size + self.key_spacing)
        pygame.draw.rect(self.surface, (100, 100, 100),
                        (x-5, y-5, total_width + 10, total_height + 10), 2)

        # Отрисовка каждой клавиши
        for row_idx, row in enumerate(self.keyboard_layout):
            current_x = x  # Позиция X для текущей клавиши
            for key, width in row:
                if not key:  # Пропускаем пустые места
                    current_x += (self.key_size + self.key_spacing) * width
                    continue
                
                # Вычисляем размеры клавиши
                key_width = self.key_size * width + (self.key_spacing * (width - 1))
                
                # Определяем цвет клавиши
                color = self.key_colors["pressed"] if key in self.pressed_keys else self.key_colors["normal"]
                
                # Рисуем клавишу
                pygame.draw.rect(self.surface, color,
                               (current_x, y + row_idx * (self.key_size + self.key_spacing),
                                key_width, self.key_size))
                
                # Рисуем содержимое клавиши
                if key in ["↑", "↓", "←", "→"]:
                    # Рисуем стрелку
                    self.draw_arrow(current_x, y + row_idx * (self.key_size + self.key_spacing), key)
                else:
                    # Рисуем текст
                    text = font.render(key, True, self.key_colors["text"])
                    text_rect = text.get_rect(center=(current_x + key_width/2,
                                                    y + row_idx * (self.key_size + self.key_spacing) + self.key_size/2))
                    self.surface.blit(text, text_rect)
                
                current_x += (self.key_size + self.key_spacing) * width

    def set_key_pressed(self, key, pressed=True):
        """Установить состояние клавиши"""
        if pressed:
            self.pressed_keys.add(key)
        else:
            self.pressed_keys.discard(key) 

    def get_pressed_key(self):
        """Возвращает ASCII код первой нажатой клавиши или 0"""
        for key in self.pressed_keys:
            if key in self.key_codes:
                return self.key_codes[key]
        return 0 

    def draw_power_button(self, x, y, powered):
        """Отрисовка кнопки питания"""
        self.power_button.x = x
        self.power_button.y = y
        
        # Рисуем рамку кнопки
        pygame.draw.rect(self.surface, self.power_colors["border"], 
                        (x-2, y-2, 44, 44), 2)
        
        # Рисуем саму кнопку
        color = self.power_colors["on"] if powered else self.power_colors["off"]
        pygame.draw.rect(self.surface, color, self.power_button)
        
        # Рисуем символ питания
        center = (x + 20, y + 20)
        radius = 15
        pygame.draw.circle(self.surface, (32, 32, 32), center, radius, 2)
        pygame.draw.line(self.surface, (32, 32, 32), 
                        (center[0], center[1] - radius//2),
                        (center[0], center[1] + radius//2), 2) 

    def set_power(self, state):
        """Установить состояние питания"""
        self.powered = state
        if not state:  # Если выключаем
            self.clear_display()  # Очищаем все дисплеи 

    def draw_pixel(self, x, y, brightness=255):
        # Минимальная яркость 32 (темно-зеленый), максимальная 255
        min_brightness = 32
        actual_brightness = min_brightness + (brightness * (255 - min_brightness) // 255)
        color = (0, actual_brightness, 0)
        
        # Вычисляем размер и позицию пикселя
        pixel_size = self.pixel_size
        pixel_x = x * pixel_size
        pixel_y = y * pixel_size
        
        # Рисуем пиксель
        pygame.draw.rect(self.surface, color, (pixel_x, pixel_y, pixel_size, pixel_size)) 

    def draw_cassette_interface(self, x, y):
        """Отрисовка интерфейса кассеты"""
        # Рисуем разъем
        color = (0, 255, 0) if self.cassette_inserted else (32, 32, 32)
        pygame.draw.rect(self.surface, (100, 100, 100), 
                        (x-2, y-2, 204, 34), 2)  # Рамка разъема
        pygame.draw.rect(self.surface, color, self.cassette_slot)
        
        # Рисуем кнопки
        pygame.draw.rect(self.surface, (60, 60, 60), self.inject_button)
        pygame.draw.rect(self.surface, (60, 60, 60), self.eject_button)
        
        # Надписи на кнопках
        font = pygame.font.Font(None, 24)  # Увеличим шрифт
        inject_text = font.render("INJECT", True, (0, 255, 0))
        eject_text = font.render("EJECT", True, (0, 255, 0))
        
        self.surface.blit(inject_text, (self.inject_button.centerx - 30, 
                                       self.inject_button.centery - 8))
        self.surface.blit(eject_text, (self.eject_button.centerx - 25, 
                                      self.eject_button.centery - 8)) 