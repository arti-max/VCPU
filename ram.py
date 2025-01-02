class ram:
	def __init__(self, size):
		self.size = size
		self.memory = bytearray(size)
		self.bus = 8
		self.bank_size = 256
		self.num_banks = size // self.bank_size
		self.bank_addresses = [i * self.bank_size for i in range(self.num_banks)]
		self.current_bank = 0
		
		# Данные начинаются с середины банка
		self.data_addr = self.bank_size // 2  # 128
		self.min_stack_addr = size-12
		self.stack_addr = size-1

	def get_real_address(self, addr):
		"""Преобразует локальный адрес в реальный с учетом текущего банка"""
		if addr < self.data_addr:  # Если это адрес программы
			return self.bank_addresses[self.current_bank] + addr
		else:  # Если это адрес данных
			return self.bank_addresses[self.current_bank] + addr

	def switch_bank(self, bank):
		"""Переключает текущий банк"""
		if 0 <= bank < self.num_banks:
			self.current_bank = bank
		else:
				raise ValueError(f"Неверный номер банка: {bank}. Доступно банков: {self.num_banks}")