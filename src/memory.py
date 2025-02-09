#!/usr/bin/env python
# encoding: utf-8

import ctypes
import ctypes.wintypes
import platform
import struct
import binascii

if platform.machine().endswith('64'):
    # 64位系统
    IS_64 = True
else:
    # 32位系统
    IS_64 = False
if platform.architecture()[0] == '64bit':
    # 64位python
    IS_PY_64 = True
else:
    # 32位python
    IS_PY_32 = False

# https://msdn.microsoft.com/en-us/library/aa383751#DWORD_PTR
if ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_ulonglong):
    DWORD_PTR = ctypes.c_ulonglong
elif ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_ulong):
    DWORD_PTR = ctypes.c_ulong
PVOID = ctypes.wintypes.LPVOID
SIZE_T = ctypes.c_size_t

NTDLL = ctypes.WinDLL('ntdll.dll')

# 进程权限相关：https://docs.microsoft.com/en-us/windows/desktop/ProcThread/process-security-and-access-rights
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020


def print_error(name):
    print(name, ctypes.WinError(ctypes.get_last_error()))


def float_to_hex(number):
    """
    将单浮点数转为16进制
    """
    return struct.unpack('<I', struct.pack('<f', number))[0]


def double_to_hex(number):
    """
    将双浮点数转为16进制
    """
    return struct.unpack('<Q', struct.pack('<d', number))[0]


def hex_to_float(hex_number):
    """
    将16进制转为单浮点数
    """
    return struct.unpack('<f', struct.pack('<I', hex_number))[0]


def hex_to_double(hex_number):
    """
    将16进制转为双浮点数
    """
    return struct.unpack('<d', struct.pack('<Q', hex_number))[0]


def bytes_to_int(b, size=4, unsigned=True):
    """
    将字节转为整数
    """
    # char
    f = '<B' if unsigned else 'b'
    if size == 8:       # long long
        f = '<Q' if unsigned else 'q'
    if size == 4:       # int
        f = '<I' if unsigned else 'i'
    if size == 2:       # short
        f = '<H' if unsigned else 'h'
    return struct.unpack(f, b)[0]


def int_to_bytes(i, size=4, unsigned=True):
    """将整数转为字节"""
    # char
    f = '<B' if unsigned else 'b'
    if size == 8:       # long long
        f = '<Q' if unsigned else 'q'
    if size == 4:       # int
        f = '<I' if unsigned else 'i'
    if size == 2:       # short
        f = '<H' if unsigned else 'h'
    return struct.pack(f, i)


def bytes_to_hex_str(buf):
    """
    b'\xAB\xCD' => 'ABCD'
    """
    return binascii.hexlify(buf).decode('utf8')


def hex_byte_to_str(data, coding='gbk'):
    """
    将16进制的字节数据转为字符串
    """
    b = bytes.fromhex(data)
    return b.decode(coding)

def str_to_hex_byte(data, coding='gbk'):
    """
    将字符串转为16进制的字节数据
    """
    b = data.encode(coding)
    r = bytes_to_hex_str(b).upper()
    return ' '.join(r[i:i+2] for i in range(0, len(r), 2))

def hex_byte_to_address(data):
    """
    例： "00 34 61 7F" => "7F613400"
    """
    l = data.split()
    l.reverse()
    return ''.join(l)

def address_to_hex_byte(data):
    """
    例：'7F613400' => '0034617F00'
    """
    if len(data) < 8:
        num = 8
    else:
        num = 16
    r = ((num - len(data)) * '0') + data
    l = [r[i:i+2] for i in range(0, len(r), 2)]
    l.reverse()
    return ''.join(l)


def array_to_list(value):
    """将C Array 转为 python list"""
    data = []
    for v in (value):
        if isinstance(v, ctypes.Array):
            data.append(array_to_list(v))
        else:
            data.append(v)
    return data


def get_process_info(pid):
    # https://docs.microsoft.com/en-us/windows/desktop/psapi/enumerating-all-modules-for-a-process
    hProcess = ctypes.windll.kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
        False, pid
    )
    if not hProcess:
        return

    count = 100                       # 仅获取进程执行的文件
    hMods = (ctypes.c_ulong * count)()
    cbNeeded = ctypes.c_ulong()

    ctypes.windll.psapi.EnumProcessModules(
        hProcess,
        ctypes.byref(hMods),
        ctypes.sizeof(hMods),
        ctypes.byref(cbNeeded)
    )
    num = min(cbNeeded.value / ctypes.sizeof(ctypes.c_ulong), count)
    i = 0

    exe_name = ''
    base_addr = {}      # 各个模块的基址
    while i < num:
        szModName = ctypes.c_buffer(100)
        # ret = ctypes.windll.psapi.GetModuleFileNameExA(
            # hProcess,
            # hMods[i],
            # szModName,
            # ctypes.sizeof(szModName)
        # )
        ret = ctypes.windll.psapi.GetModuleBaseNameA(
            hProcess,
            hMods[i],
            szModName,
            ctypes.sizeof(szModName)
        )
        if ret:
            base_addr[szModName.value] = hMods[i]
            print("process: %8d\t%x\t%s" % (pid, hMods[i], szModName.value))
            if i == 0:
                exe_name = szModName.value
        else:
            print("process: %8d\t%x\terror" % (pid, hMods[i]))
            print_error("GetModuleBaseNameA")
        i += 1

    ctypes.windll.kernel32.CloseHandle(hProcess)
    return (pid, exe_name, base_addr)


def get_process_name(pid):
    hProcess = ctypes.windll.kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
        False, pid
    )
    if not hProcess:
        return
    
    name = ctypes.c_buffer(2024)
    ret = ctypes.windll.psapi.GetProcessImageFileNameA(
        hProcess,
        ctypes.byref(name),
        2024,
    )
    if not ret:
        print_error("GetProcessImageFileNameA")

    ctypes.windll.kernel32.CloseHandle(hProcess)
    try:
        result = name.value.decode("utf8")
    except Exception as e:
        result = name.value.decode("gbk")
    return result

def list_process():
    # https://docs.microsoft.com/en-us/windows/desktop/api/psapi/nf-psapi-enumprocesses
    count = 1024
    lpidProcess = (ctypes.c_ulong * count)()
    lpcbNeeded = ctypes.c_ulong()

    ret = ctypes.windll.psapi.EnumProcesses(
        ctypes.byref(lpidProcess),
        ctypes.sizeof(lpidProcess),
        ctypes.byref(lpcbNeeded)
    )

    if ret != 1:
        print_error('EnumProcesses')
        raise Exception('list_process error')

    num = min(lpcbNeeded.value / ctypes.sizeof(ctypes.c_ulong), count)
    i = 0

    result = {}
    while i < num:
        pid = lpidProcess[i]
        i += 1
        name = get_process_name(pid)
        if name:
            result[pid] = name
    pids = list(result.keys())
    pids.sort()

    data = []
    for i in pids:
        data.append({'pid': i, 'name': result[i]})
    return data


def query_virtual(hProcess, base_addr):
    """
    查询虚拟地址的信息
    """
    MEM_COMMIT = 0x00001000;
    PAGE_READWRITE = 0x04;

    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        """https://msdn.microsoft.com/en-us/library/aa366775"""
        _fields_ = (('BaseAddress', PVOID),
                    ('AllocationBase',    PVOID),
                    ('AllocationProtect', ctypes.wintypes.DWORD),
                    ('RegionSize', SIZE_T),
                    ('State',   ctypes.wintypes.DWORD),
                    ('Protect', ctypes.wintypes.DWORD),
                    ('Type',    ctypes.wintypes.DWORD))

    mbi = MEMORY_BASIC_INFORMATION()
    ret = ctypes.windll.kernel32.VirtualQueryEx(
        hProcess,
        base_addr,
        ctypes.byref(mbi),
        ctypes.sizeof(mbi)
    )
    if not ret:
        print_error('VirtualQueryEx')
        return {}

    return {
        'protect': mbi.Protect == PAGE_READWRITE,
        'state': mbi.State == MEM_COMMIT,
        'size': mbi.RegionSize,
    }


def get_system_info():
    """
    获取系统信息: 可用内存的起始与结束地址
    """
    class SYSTEM_INFO(ctypes.Structure):
        """https://msdn.microsoft.com/en-us/library/ms724958"""
        class _U(ctypes.Union):
            class _S(ctypes.Structure):
                _fields_ = (('wProcessorArchitecture', ctypes.wintypes.WORD),
                            ('wReserved', ctypes.wintypes.WORD))
            _fields_ = (('dwOemId', ctypes.wintypes.DWORD), # obsolete
                        ('_s', _S))
            _anonymous_ = ('_s',)
        _fields_ = (('_u', _U),
                    ('dwPageSize', ctypes.wintypes.DWORD),
                    ('lpMinimumApplicationAddress', ctypes.wintypes.LPVOID),
                    ('lpMaximumApplicationAddress', ctypes.wintypes.LPVOID),
                    ('dwActiveProcessorMask',   DWORD_PTR),
                    ('dwNumberOfProcessors',    ctypes.wintypes.DWORD),
                    ('dwProcessorType',         ctypes.wintypes.DWORD),
                    ('dwAllocationGranularity', ctypes.wintypes.DWORD),
                    ('wProcessorLevel',    ctypes.wintypes.WORD),
                    ('wProcessorRevision', ctypes.wintypes.WORD))
        _anonymous_ = ('_u',)

    sysinfo = SYSTEM_INFO()
    if not ctypes.windll.kernel32.GetSystemInfo(ctypes.byref(sysinfo)):
        print_error('GetSystemInfo')
        return {}

    return {
        'start_addr': sysinfo.lpMinimumApplicationAddress,
        'end_addr': sysinfo.lpMaximumApplicationAddress
    }

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = ctypes.wintypes.HANDLE, ctypes.wintypes.LPCVOID, ctypes.wintypes.LPVOID, SIZE_T, ctypes.POINTER(SIZE_T)
ReadProcessMemory.restype = ctypes.wintypes.BOOL

def read_process(hProcess, base_addr, byte_num=2):
    """读取特定内存的值"""
    buf = ctypes.c_buffer(b'', byte_num)
    nread = SIZE_T()
    ret = ReadProcessMemory(
        hProcess,
        base_addr,
        ctypes.byref(buf),
        ctypes.sizeof(buf),
        ctypes.byref(nread)
    )
    if not ret:
        print_error('ReadProcessMemory')
        raise Exception('ReadProcessMemory')

    return getattr(buf, 'raw', buf.value)


def read_process64(hProcess, base_addr, byte_num):
    """64位系统读取特定内存地址"""
    if byte_num == 1:
        buf = ctypes.c_byte()
    elif byte_num == 2:
        buf = ctypes.c_short()
    elif byte_num == 4:
        buf = ctypes.c_int32()
    elif byte_num == 8:
        buf = ctypes.c_int64()
    else:
        buf = ctypes.c_buffer(b'', byte_num)
    nread = SIZE_T()
    # 第一个参数是我们通过OpenProcess获取的进程句柄，在python中要记得把这个句柄转换成int类型，默认其实是个句柄类型，不会出错
    # 第二个参数其实就是我们要读取的地址
    # 第三个参数是一个指针，我们通过ctypes中的byref方法可以将一个指针传进去，函数会把读取到的参数放进这个指针指向的地方，里也就是我们的ret中
    # 第四个参数是我们需要读取的长度
    # 第五个参数也是一个指针，存放实际读取的长度，可为NULL
    ret = NTDLL.NtWow64ReadVirtualMemory64(
        int(hProcess),
        ctypes.c_ulonglong(base_addr),
        ctypes.byref(buf),
        ctypes.c_ulonglong(byte_num),
        ctypes.byref(nread)
    )
    if not ret:
        print_error('NtWow64ReadVirtualMemory64')
        raise Exception('NtWow64ReadVirtualMemory64')

    return getattr(buf, 'raw', buf.value)


def write_process(hProcess, base_addr, value, byte_num=2):
    """往特定内存地址写入数据"""
    if byte_num == 1:
        buf = ctypes.c_byte(value)
    elif byte_num == 2:
        buf = ctypes.c_short(value)
    elif byte_num == 4:
        buf = ctypes.c_int32(value)
    elif byte_num == 8:
        buf = ctypes.c_int64(value)
    else:
        buf = ctypes.c_buffer(value, byte_num)
    nwrite = SIZE_T()
    ret = ctypes.windll.kernel32.WriteProcessMemory(
        hProcess,
        base_addr,
        ctypes.byref(buf),
        ctypes.sizeof(buf),
        ctypes.byref(nwrite)
    )

    return not not ret


def write_process64(hProcess, base_addr, value, byte_num):
    """64位系统写入特定内存地址"""
    if byte_num == 1:
        buf = ctypes.c_byte(value)
    elif byte_num == 2:
        buf = ctypes.c_short(value)
    elif byte_num == 4:
        buf = ctypes.c_int32(value)
    elif byte_num == 8:
        buf = ctypes.c_int64(value)
    else:
        buf = ctypes.c_buffer(value, byte_num)
    nwrite = SIZE_T()

    ret = NTDLL.NtWow64WriteVirtualMemory64(
        int(hProcess),
        ctypes.c_ulonglong(base_addr),
        ctypes.byref(buf),
        ctypes.c_ulonglong(byte_num),
        ctypes.byref(nwrite)
    )

    return not not ret


def close_process(hProcess):
    ctypes.windll.kernel32.CloseHandle(hProcess)


def inject_process(pid):
    """
    注入某个进程
    """
    hProcess = ctypes.windll.kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION|PROCESS_VM_READ|PROCESS_VM_OPERATION|PROCESS_VM_WRITE,
        False, pid
    )
    if not hProcess:
        print_error('OpenProcess %s' % (pid))
        return

    return hProcess


def is_process32(hProcess):
    """检查目标进程是否32位"""
    # https://docs.microsoft.com/en-us/windows/win32/api/wow64apiset/nf-wow64apiset-iswow64process?redirectedfrom=MSDN
    ret = ctypes.c_bool()
    ctypes.windll.kernel32.IsWow64Process(hProcess, ctypes.byref(ret))
    return not ret.value

def main():
    for item in list_process():
        print(item)

if __name__ == '__main__':
    main()
