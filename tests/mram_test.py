import ctypes
import logging as log

log.basicConfig(
    level=log.INFO,  # 设置日志级别
    format="[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s",  # 日志格式
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        log.StreamHandler(),  # 输出到控制台
        log.FileHandler("test.log")
    ],
)

mram_dll = ctypes.CDLL('./libmram_api.so')

H2C_DEVICE = "/dev/xdma0_h2c_0"
C2H_DEVICE = "/dev/xdma0_c2h_0"

def capacity_test():
    # 一次测试4k容量
    batch_size = 4 * 1024
    
    # rows,cols,ips,mrams = 4,4,4,1048576
    rows,cols,ips,mrams = 1,1,1,4096
    for macro_row in range(rows):
        for macro_col in range(cols):
            for ip_addr in range(ips):
                for mram_addr in range(mrams // batch_size):
                    # 顺序写入数据
                    start = macro_row*(4 * 4 * 256) + macro_col*(4*256) + ip_addr*256 + mram_addr
                    send_data = list(range(start,start + batch_size))
                    mram_dll.Send(H2C_DEVICE,macro_row,macro_col,ip_addr,mram_addr,send_data,batch_size)

                    # 读出数据
                    recv_data = (ctypes.c_int32 * batch_size)()
                    mram_dll.Recv(H2C_DEVICE,C2H_DEVICE,macro_row,macro_col,ip_addr,mram_addr,recv_data,batch_size)

                    # 对比数据
                    for i in range(batch_size):
                        if send_data[i] != recv_data[i]:
                            log.error(f"macro({macro_row,macro_col}) ip({ip_addr} mram_addr({mram_addr:0>8X})) idx({i}) write weight:{send_data[i]}, but recv weight: {recv_data[i]}")
                        else:
                            log.info(f"macro({macro_row,macro_col}) ip({ip_addr}) mram_addr({mram_addr:0>8X} ~ {(mram_addr+batch_size):0>8X}) write/read verify success")