import pygame
from instructions import *
from loader import loader
from ram import ram
from display import Display
from cassette import CassetteManager
from tkinter import filedialog
import tkinter as tk

root = tk.Tk()
root.withdraw()  # Скрываем основное окно tkinter

class VCPU:
	def __init__(self, ram, loader, screen):
		self.ram = ram
		self.loader = loader
		self.regs ={0x01: 0x00, 
					0x02: 0x00,
					0x03: 0x00, 
					0x04: 0x00, 
					0x05: 0x00, 
					0x06: 0x00}
		self.flags = {0x01: 0x0}
		self.ip = 0x0000
		self.bits = 0x08
		self.display = Display(screen)
		self.running = True
		self.powered = False
		self.display.set_power(False)
		self.key_save_addr = None  # адрес для сохранения нажатий
		self.cassette = CassetteManager()

	def run(self):
		clock = pygame.time.Clock()

		while self.running:
			# Обработка событий pygame
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					# Проверяем клик по кнопкам кассеты
					if self.display.inject_button.collidepoint(event.pos):
						# Открываем диалог выбора файла через tkinter
						filename = filedialog.askopenfilename(
							defaultextension=".cas",
							filetypes=[("Cassette files", "*.cas"), ("All files", "*.*")]
						)
						if filename:
							if self.cassette.insert_cassette(filename):
								self.display.cassette_inserted = True
					
					elif self.display.eject_button.collidepoint(event.pos):
						self.cassette.eject_cassette()
						self.display.cassette_inserted = False

					# Проверяем клик по кнопке питания
					if self.display.power_button.collidepoint(event.pos):
						self.powered = not self.powered
						self.display.set_power(self.powered)
						if self.powered:
							self.ip = 0  # Сброс IP при включении
							self.regs = {0x01: 0x00, 0x02: 0x00, 0x03: 0x00, 
									0x04: 0x00, 0x05: 0x00, 0x06: 0x00}
							self.flags = {0x01: 0x0}
							# Перезагружаем программу из boot.bin
							self.loader.load()
						else:
							# Очищаем всю память при выключении
							self.ram.memory = bytearray(self.ram.size)
							self.display.clear_display()
				elif event.type == pygame.KEYDOWN:
					# Маппинг клавиш клавиатуры на новые индексы
					key_mapping = {
						pygame.K_ESCAPE: "ESC",    # 13
						pygame.K_RETURN: "ENTER",  # 15
						pygame.K_BACKSPACE: "DEL", # 14
						pygame.K_LEFT: "←",        # 19
						pygame.K_RIGHT: "→",       # 18
						pygame.K_UP: "↑",          # 16
						pygame.K_DOWN: "↓",        # 17
					}
					# Цифры
					for i in range(10):
						key_mapping[pygame.K_0 + i] = str(i)  # 0-9
					
					if event.key in key_mapping:
						self.display.set_key_pressed(key_mapping[event.key], True)
						
				elif event.type == pygame.KEYUP:
					key_mapping = {
						pygame.K_ESCAPE: "ESC",
						pygame.K_RETURN: "ENTER",
						pygame.K_BACKSPACE: "DEL",
						pygame.K_LEFT: "←",
						pygame.K_RIGHT: "→",
						pygame.K_UP: "↑",
						pygame.K_DOWN: "↓",
					}
					for i in range(10):
						key_mapping[pygame.K_0 + i] = str(i)
					
					if event.key in key_mapping:
						self.display.set_key_pressed(key_mapping[event.key], False)

			# Проверяем нажатие клавиш
			key = self.display.get_pressed_key()
			if key and self.key_save_addr:
				bank, addr = self.key_save_addr
				real_addr = self.ram.bank_addresses[bank] + addr
				self.ram.memory[real_addr] = key

			# Выполнение инструкций только если процессор включен
			if self.powered and self.ip < self.ram.size-1:
				# Получаем реальный адрес с учетом текущего банка
				real_addr = self.ip
				instruction = self.ram.memory[real_addr]
				old_ip = self.ip
				self.ip += 1

				print(f"Bank: {self.ram.current_bank} | IP: {old_ip} -> {self.ip} | " + 
					  f"Instruction: {hex(instruction)} {hex(self.ram.memory[real_addr+1])} {hex(self.ram.memory[real_addr+2])} | " +
					  f"Regs: {self.regs} | Flags: {self.flags}")
				
				# Выполняем инструкцию
				if (instruction == 0x00):    # NOP
					pass
				elif (instruction == 0x01): # SET
					set(self)
				elif (instruction == 0x02): # MOV
					mov(self)
				elif (instruction == 0x03): # ADD
					add(self)
				elif (instruction == 0x04): # SUB
					sub(self)
				elif (instruction == 0x05): # AND
					and_(self)
				elif (instruction == 0x06): # OR
					or_(self)
				elif (instruction == 0x07): # XOR
					xor(self)
				elif (instruction == 0x08): # JMP
					jmp(self)
				elif (instruction == 0x09): # STOREV
					storev(self)
				elif (instruction == 0x0A): # STORER
					storer(self)
				elif (instruction == 0x0B): # STOREM
					storem(self)
				elif (instruction == 0x0C): # LOADR
					loadr(self)
				elif (instruction == 0x0D): # JE
					je(self)
				elif (instruction == 0x0E): # JNE
					jne(self)
				elif (instruction == 0x0F): # CMP
					cmp_(self)
				elif (instruction == 0x10): # PUSH
					push(self)
				elif (instruction == 0x11): # POP
					pop(self)
				elif (instruction == 0x12): # MUL
					mul(self)
				elif (instruction == 0x13): # DIV
					div(self)
				elif (instruction == 0x14): # SETPX
					setpx(self)
				elif (instruction == 0x15): # CLRPX
					clrpx(self)
				elif (instruction == 0x16): # DIGIT
					digit(self)
				elif (instruction == 0x17): # CLEAR
					clear(self)
				elif (instruction == 0x18): # GETKEY
					getkey(self)
				elif (instruction == 0x19): # CALL
					call(self)
				elif (instruction == 0x1A): # RET
					ret(self)
				elif (instruction == 0x1B): # RND
					rnd(self)
				elif (instruction == 0x1C): # BANK
					BANK(self)
				elif (instruction == 0x1D): # SAVKEY
					savkey(self)
				elif (instruction == 0x1E): # BRIGHT
					bright(self)
				elif (instruction == 0x1F): # LOADRR
					loadrr(self)
				elif (instruction == 0xFF): # HLT
					hlt(self)
				elif (instruction == 0x20): # CREAD
					cread(self)
				elif (instruction == 0x21): # CWRITE
					cwrite(self)
				elif (instruction == 0x22): # CSTAT
					cstat(self)
				elif (instruction == 0x23): # CINFO
					cinfo(self)
				else:
					print("Неизвестная инструкция:", hex(instruction))

			# Обновление дисплея (всегда показываем все элементы)
			screen.fill((32, 32, 32))
			self.display.draw_power_button(700, 50, self.powered)
			self.display.draw_pixel_display(50, 50)
			self.display.draw_text(350, 50)
			self.display.draw_keyboard(50, 350)
			self.display.draw_cassette_interface(350, 120)  # Новые координаты
			pygame.display.flip()
			
			clock.tick(120)

# Инициализация pygame и создание окна
pygame.init()
screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("VCPU Display")

# Инициализация VCPU с 512 байтами памяти (2 банка)
ram = ram(2048) # BANK 0 - 7
loader = loader(ram)
loader.load()
vcpu = VCPU(ram, loader, screen)
vcpu.run()

pygame.quit()