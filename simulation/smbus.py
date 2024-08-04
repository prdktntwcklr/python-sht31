class SMBus():
    def __init__(self, i2c_port):
        pass

    def write_i2c_block_data(self, i2c_addr, register, data, force=None):
        for d in data:
            print(f"Writing {hex(d)} to register {hex(register)} at"
                  f"address {hex(i2c_addr)}")
