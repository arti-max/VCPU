import pickle
import os

class CassetteManager:
    def __init__(self):
        self.current_cassette = None
        self.is_inserted = False

    def insert_cassette(self, filename):
        """Загрузка кассеты"""
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.current_cassette = data
                self.is_inserted = True
                return True
        except Exception as e:
            print(f"Ошибка загрузки кассеты: {str(e)}")
            return False

    def eject_cassette(self):
        """Извлечение кассеты"""
        self.current_cassette = None
        self.is_inserted = False

    def read_section(self, section):
        """Чтение секции кассеты"""
        if not self.is_inserted:
            return None
        if section >= self.current_cassette['header']['sections']:
            return None
        start = section * 256
        end = start + 256
        return self.current_cassette['data'][start:end]

    def write_section(self, section, data):
        """Запись секции кассеты"""
        if not self.is_inserted:
            return False
        if section >= self.current_cassette['header']['sections']:
            return False
        if len(data) > 256:
            return False
        start = section * 256
        end = start + len(data)
        self.current_cassette['data'][start:end] = data
        return True 

    def get_sections_count(self):
        """Получить количество секций из заголовка"""
        if not self.is_inserted:
            return 0
        return self.current_cassette['header']['sections']

    def get_max_size(self):
        """Получить максимальный размер из заголовка"""
        if not self.is_inserted:
            return 0
        return self.current_cassette['header']['max_size']

    def get_name(self):
        """Получить имя кассеты"""
        if not self.is_inserted:
            return ""
        return self.current_cassette['header']['name'] 