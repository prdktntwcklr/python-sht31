class SMBus:
    def __init__(self, i2c_port: int) -> None:
        self.port = i2c_port
        pass

    def write_i2c_block_data(
        self, i2c_addr: int, register: int, data: list[int], force: bool | None = None
    ) -> None:
        if len(data) > 32:
            raise ValueError("SMBus block write length cannot exceed 32 bytes")

        for i, d in enumerate(data):
            print(
                f"Bus {self.port}: Writing {hex(d)} to {hex(i2c_addr)}:reg {hex(register + i)}"
            )

    def read_i2c_block_data(
        self, i2c_addr: int, register: int, length: int
    ) -> list[int]:
        if length > 32:
            raise ValueError("SMBus block read length cannot exceed 32 bytes")

        print(
            f"Bus {self.port}: Reading {length} bytes from {hex(i2c_addr)} starting at {hex(register)}"
        )
        return [0x00] * length  # Returning 0x00 mimics a cleared register
