import random

def BANK(cpu):
	bank = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	cpu.ram.switch_bank(bank)

def set(cpu): # SET REG VAL
	reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	val = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	cpu.regs[reg] = val

def mov(cpu): # MOV REG REG
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	# Проверяем существование регистров
	if reg1 not in cpu.regs or reg2 not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{reg1} или R{reg2}")

	cpu.regs[reg1] = cpu.regs[reg2]




def add(cpu):  # ADD REG1 REG2 [result to REG1]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1


	if reg1 not in cpu.regs or reg2 not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{reg1} или R{reg2}")

	result = cpu.regs[reg1] + cpu.regs[reg2]
	mask = (1 << cpu.bits) - 1  # Создаем маску для 8 бит
	cpu.regs[reg1] = result & mask

def sub(cpu): # SUB REG1 REG2 [result to REG1]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	if reg1 not in cpu.regs or reg2 not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{reg1} или R{reg2}")

	result = cpu.regs[reg1] - cpu.regs[reg2]
	mask = (1 << cpu.bits) - 1
	cpu.regs[reg1] = result & mask

def xor(cpu): # XOR REG1 REG2 [result to REG1]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	cpu.regs[reg1] ^= cpu.regs[reg2]

def or_(cpu): # OR REG1 REG2 [result to REG1]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	cpu.regs[reg1] |= cpu.regs[reg2]

def and_(cpu): # AND REG1 REG2 [result to REG1]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	cpu.regs[reg1] &= cpu.regs[reg2]




def loadr(cpu): # LOADR REG ADDR
	reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	addr = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	# Для данных используем вторую половину текущего банка
	real_addr = cpu.ram.bank_addresses[cpu.ram.current_bank] + addr
	cpu.regs[reg] = cpu.ram.memory[real_addr]


def storev(cpu): # STOREV ADDR VAL
	addr = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	val = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	
	# Для данных используем вторую половину текущего банка
	real_addr = cpu.ram.bank_addresses[cpu.ram.current_bank] + addr
	cpu.ram.memory[real_addr] = val

def storer(cpu): # STORER ADDR REG
	addr = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	# Для данных используем вторую половину текущего банка
	real_addr = cpu.ram.bank_addresses[cpu.ram.current_bank] + addr
	cpu.ram.memory[real_addr] = cpu.regs[reg]

def storem(cpu): # STOREM ADDR1 ADDR2
	addr1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	addr2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	# Для данных используем вторую половину текущего банка
	real_addr1 = cpu.ram.bank_addresses[cpu.ram.current_bank] + addr1
	real_addr2 = cpu.ram.bank_addresses[cpu.ram.current_bank] + addr2
	cpu.ram.memory[real_addr1] = cpu.ram.memory[real_addr2]



def cmp_(cpu): # CMP REG1 REG2 [result to ZF - 0x01]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	#print(f"CMP: {cpu.regs[reg1]} ==? {cpu.regs[reg2]}")
	
	# Добавим проверку на существование регистров
	if reg1 not in cpu.regs or reg2 not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{reg1} или R{reg2}")
		
	if cpu.regs[reg1] == cpu.regs[reg2]:
		#print("CMP ==")
		cpu.flags[0x01] = 0
	else:
		#print("CMP !==")
		cpu.flags[0x01] = 1



def jmp(cpu): # JMP ADDR
	addr = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	real_addr = cpu.ram.get_real_address(addr)
	#print("JMP: ",real_addr)
	cpu.ip = real_addr

def je(cpu): # JE ADDR
	addr = cpu.ram.memory[cpu.ip]
	real_addr = cpu.ram.get_real_address(addr)
	cpu.ip += 1

	#print(f"NotJE: {addr} | {real_addr}")

	if cpu.flags[0x01] == 0:  # Если флаг равен 0
		#print("JE: ",real_addr)
		cpu.ip = real_addr

def jne(cpu): # JNE ADDR
	addr = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	if cpu.flags[0x01] == 1:  # Если флаг равен 1
		real_addr = cpu.ram.get_real_address(addr)
		#print("JNE: ",real_addr)
		cpu.ip = real_addr



def push(cpu): # PUSH REG
	value = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	value = cpu.regs[value]

	if cpu.ram.stack_addr == cpu.ram.min_stack_addr:
		raise ValueError("Стек переполнен")
	cpu.ram.stack_addr -= 1
	cpu.ram.memory[cpu.ram.stack_addr] = value

def pop(cpu): # POP REG
	reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	cpu.regs[reg] = cpu.ram.memory[cpu.ram.stack_addr]
	cpu.ram.memory[cpu.ram.stack_addr] = 0x00
	if cpu.ram.stack_addr < cpu.ram.size-1:
		cpu.ram.stack_addr += 1


def hlt(cpu):
    """Выключает процессор"""
    cpu.powered = False
    cpu.display.set_power(False)

def mul(cpu): # MUL REG1 REG2 [result to REG1]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	result = cpu.regs[reg1] * cpu.regs[reg2]
	mask = (1 << cpu.bits) - 1  # Создаем маску для 8 бит (0xFF)
	cpu.regs[reg1] = result & mask  # Применяем маску для ограничения до 8 бит

def div(cpu): # DIV REG1 REG2 [result to REG1, remainder to R4]
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1

	if cpu.regs[reg2] == 0:
		print("Ошибка: деление на ноль!")
		cpu.ip = cpu.ram.size  # Аварийное завершение
		return

	quotient = cpu.regs[reg1] // cpu.regs[reg2]
	remainder = cpu.regs[reg1] % cpu.regs[reg2]
	
	mask = (1 << cpu.bits) - 1  # Маска для 8 бит
	cpu.regs[reg1] = quotient & mask  # Частное в REG1
	cpu.regs[0x04] = remainder & mask  # Остаток в R4

def setpx(cpu): # SETPX REG1 REG2 [REG3] - установить пиксель (x,y) с яркостью из REG3
	x_reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	y_reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	brightness_reg = cpu.ram.memory[cpu.ip]
	cpu.ip +=1
	
	if x_reg not in cpu.regs or y_reg not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{x_reg} или R{y_reg}")
	if brightness_reg and brightness_reg not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{brightness_reg}")
		
	brightness = cpu.regs[brightness_reg] if brightness_reg else None
	cpu.display.set_pixel(cpu.regs[x_reg], cpu.regs[y_reg], True, brightness)

def clrpx(cpu): # CLRPX REG1 REG2 (x в REG1, y в REG2)
	x_reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	y_reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	
	x = cpu.regs[x_reg]
	y = cpu.regs[y_reg]
	
	if x < 16 and y < 16:
		cpu.display.set_pixel(x, y, False)

def digit(cpu): # DIGIT REG1 REG2 (позиция в REG1, значение в REG2)
	pos_reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	val_reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	
	if pos_reg not in cpu.regs or val_reg not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{pos_reg} или R{val_reg}")
		
	pos = cpu.regs[pos_reg]
	val = cpu.regs[val_reg]
	
	if pos == 0:  # Специальный случай - вывод числа целиком
		# Преобразуем число в строку и дополняем нулями слева до 8 знаков
		val_str = str(val).zfill(8)
		# Выводим каждую цифру в соответствующую позицию
		for i, digit in enumerate(val_str[-8:]):  # Берем последние 8 цифр, если число слишком большое
			cpu.display.text[i] = digit
	else:
		# Обычный случай - вывод одной цифры в указанную позицию
		if 0 <= pos < 8:  # Проверяем границы дисплея
			cpu.display.text[pos] = str(val)

def clear(cpu): # CLEAR
	cpu.display.clear_display()

def getkey(cpu): # GETKEY REG [записывает в REG ASCII код нажатой клавиши или 0]
	reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	
	key_code = cpu.display.get_pressed_key()
	cpu.regs[reg] = key_code

def call(cpu):
	addr = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	real_addr = cpu.ram.get_real_address(addr)

	print(f"CALL: {real_addr} | {cpu.ip}")
	
	if cpu.ram.stack_addr == cpu.ram.min_stack_addr:
		raise ValueError("Стек переполнен")
	cpu.ram.memory[cpu.ram.stack_addr] = cpu.ip
	cpu.ram.stack_addr -= 1
	
	cpu.ip = real_addr

def ret(cpu):

    if cpu.ram.stack_addr == cpu.ram.size-1:
        print("Стек пуст")
        return
    # Восстанавливаем IP из стека
    ret_addr = cpu.ram.memory[cpu.ram.stack_addr+1]

    print("RET: ",ret_addr)
    
    cpu.ip = ret_addr
    cpu.ram.memory[cpu.ram.stack_addr] = 0x00
    if cpu.ram.stack_addr < cpu.ram.size-1:
        cpu.ram.stack_addr += 1

def rnd(cpu):
    # Получаем регистр и лимит из следующих байтов
    reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    limit = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    
    # Генерируем случайное число от 0 до limit
    value = random.randint(0, limit)
    cpu.regs[reg] = value

def savkey(cpu): # SAVKEY ADDR - устанавливает адрес для сохранения нажатий клавиш
	addr = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	
	# Сохраняем адрес с учетом текущего банка
	cpu.key_save_addr = (cpu.ram.current_bank, addr)

def bright(cpu): # BRIGHT REG - устанавливает яркость из значения в регистре
	reg = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	
	if reg not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{reg}")
		
	# Устанавливаем яркость из значения в регистре
	cpu.display.set_brightness(cpu.regs[reg])

def loadrr(cpu): # LOADRR REG1 REG2 (загрузка в REG1 из адреса в REG2)
	reg1 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	reg2 = cpu.ram.memory[cpu.ip]
	cpu.ip += 1
	
	if reg1 not in cpu.regs or reg2 not in cpu.regs:
		raise ValueError(f"Неверный номер регистра: R{reg1} или R{reg2}")
		
	addr = cpu.regs[reg2]  # Берем адрес из второго регистра
	real_addr = cpu.ram.bank_addresses[cpu.ram.current_bank] + addr
	value = cpu.ram.memory[real_addr]  # Загружаем значение по этому адресу
	cpu.regs[reg1] = value  # Сохраняем в первый регистр

def cread(cpu): # CREAD REG1 REG2 (загрузка секции REG2 в память начиная с адреса REG1)
    addr_reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    section_reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    
    if addr_reg not in cpu.regs or section_reg not in cpu.regs:
        raise ValueError(f"Неверный номер регистра: R{addr_reg} или R{section_reg}")
    
    # Проверяем наличие кассеты
    if not cpu.cassette.is_inserted:
        return
        
    # Читаем секцию
    section_data = cpu.cassette.read_section(cpu.regs[section_reg])
    if section_data is None:
        return
        
    # Записываем данные в память
    start_addr = cpu.ram.get_real_address(cpu.regs[addr_reg])
    for i, byte in enumerate(section_data):
        cpu.ram.memory[start_addr + i] = byte

def cwrite(cpu): # CWRITE REG1 REG2 (запись в секцию REG2 из памяти начиная с адреса REG1)
    addr_reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    section_reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    
    if addr_reg not in cpu.regs or section_reg not in cpu.regs:
        raise ValueError(f"Неверный номер регистра: R{addr_reg} или R{section_reg}")
    
    # Проверяем наличие кассеты
    if not cpu.cassette.is_inserted:
        return
        
    # Собираем данные из памяти
    start_addr = cpu.ram.get_real_address(cpu.regs[addr_reg])
    data = bytearray(cpu.ram.memory[start_addr:start_addr + 256])
    
    # Записываем в кассету
    cpu.cassette.write_section(cpu.regs[section_reg], data)

def cstat(cpu): # CSTAT REG (записать статус кассеты в регистр)
    reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    
    if reg not in cpu.regs:
        raise ValueError(f"Неверный номер регистра: R{reg}")
    
    # Записываем статус (0 - нет кассеты, 1 - есть кассета)
    cpu.regs[reg] = 0x01 if cpu.cassette.is_inserted else 0x00

def cinfo(cpu): # CINFO REG1 REG2 (REG1 - тип информации, результат в REG2)
    type_reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    result_reg = cpu.ram.memory[cpu.ip]
    cpu.ip += 1
    
    if type_reg not in cpu.regs or result_reg not in cpu.regs:
        raise ValueError(f"Неверный номер регистра: R{type_reg} или R{result_reg}")
    
    # Тип информации:
    # 0 - количество секций
    # 1 - максимальный размер
    info_type = cpu.regs[type_reg]
    
    if info_type == 0x00:
        cpu.regs[result_reg] = cpu.cassette.get_sections_count()
    elif info_type == 0x01:
        cpu.regs[result_reg] = cpu.cassette.get_max_size()