
import time


def stimer(func):
    def func_wrapper(*args, **kwargs):
        time.sleep(0.01)
        result = func(*args, **kwargs)
        time.sleep(0.01)
        return result

    return func_wrapper


def breakDecorator(func):
    def func_wrapper(*args, **kwargs):
        time.sleep(0.01)
        result = func(*args, **kwargs)
        return result
    raise NotImplementedError
    return func_wrapper


def hexStringToByteList(signal: str):
    # 去除字符串两侧的空白字符
    signal = signal.strip()

    # 尝试根据空格或逗号分割字符串，并转换为十六进制整数列表
    try:
        if ',' in signal:
            r = [int(x, 16) for x in signal.split(',')]
        else:
            r = [int(x, 16) for x in signal.split()]
    except ValueError as e:
        # 如果转换过程中发生错误，则抛出异常
        raise ValueError(f"Invalid hexadecimal string: {e}")

        # 确保列表长度为8，不足部分用0xff填充
    while len(r) < 8:
        r.append(0xff)

        # 如果列表长度超过8，则截断至前8个元素
    r = r[:8]

    return r

def print_hello_world(n):  
    if n <= 0: 
        return
    print("hello world")  
    print_hello_world(n - 1)  

if __name__=="__main__":  
    # 调用函数打印100次hello world  
    print_hello_world(10)