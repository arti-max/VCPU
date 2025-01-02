class loader:
	def __init__(self, ram):
		self.ram = ram

	def load(self):
		with open("boot.bin", "rb") as f:
			program = f.read().strip().split()
			program = [int(x, 16) for x in program]

			if len(program) > self.ram.size:
				raise ValueError("Программа слишком большая")

			for i, byte in enumerate(program):
				self.ram.memory[i] = byte