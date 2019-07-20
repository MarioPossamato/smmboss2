import guest_access
import smmboss
import gdb
import re
import struct
class GDBGuest(smmboss.MMGuest):
    def __init__(self):
        super().__init__()
        self.inf = gdb.selected_inferior()
        for line in gdb.execute('info shared', to_string=True).split('\n'):
            m = re.match('(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+(No|Yes)\s+(.*)', line.rstrip())
            if m:
                frm, to, syms_read, path = m.groups()
                if path.endswith('main.elf'):
                    self._slide = int(frm, 16)
                    break
        else:
            raise Exception('no file')

    def try_read(self, addr, size):
        return self.inf.read_memory(addr, size)
    def try_write(self, addr, data):
        return self.inf.write_memory(addr, data)

def reg(name):
    return int(gdb.parse_and_eval(name))

class MyBT(gdb.Command):
    def __init__(self):
        super().__init__('my_bt', gdb.COMMAND_USER)
    def invoke(self, arg, from_tty):
        limit = 20
        self.print_frame('pc', reg('$pc'), '')
        self.print_frame('lr', reg('$lr'), '')
        f = reg('$x29')
        for i in range(limit):
            if not f:
                break
            # TODO make this nicer
            new_f, fpc = struct.unpack('<QQ', gdb.selected_inferior().read_memory(f, 16))
            self.print_frame(f'f{i}', fpc, f' [{f:#x}]')
            f = new_f
    def print_frame(self, idx, addr, extra):
        addr = guest.gunslide(addr) if addr else addr
        gdb.write(f'{idx:5}: 0x{addr:016x}{extra}\n')
def add_niceties():
    global guest
    guest = guest_access.CachingGuest(GDBGuest())
    MyBT()
    gdb.parse_and_eval(f'$slide = {guest._gslide:#x}')
add_niceties()


