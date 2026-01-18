import sys
import hexdump
from z3 import *


def xor_strings(s, t):
    """将两个字符串进行xor操作"""
    return "".join(chr(a ^ b) for a, b in zip(s, t))


def read_file(fname):
    """读取二进制文件"""
    file = open(fname, mode='rb')
    content = file.read()
    file.close()
    return content


def chunks(l, n):
    """将输入的数据分成n组"""
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


def print_model(m, KEY_LEN, key, cipher_file):
    """打印模型结果"""
    # 从model中解析key
    test_key = "".join(chr(int(str(m[key[i]]))) for i in range(KEY_LEN))
    print("key=", end="")
    hexdump.hexdump(test_key.encode())

    # 使用解出来的key解密数据
    tmp = chunks(cipher_file, KEY_LEN)
    plain_attempt = "".join(map(lambda x: xor_strings(x, test_key.encode()), tmp))
    print("plain=")
    hexdump.hexdump(plain_attempt.encode())


def evaluate_plaintext_quality(text):
    """评估解密文本的质量"""
    if not text:
        return 0

    # 计算可读字符比例
    letters = sum(1 for c in text if 'a' <= c <= 'z' or 'A' <= c <= 'Z')
    spaces = sum(1 for c in text if c == ' ')

    # 常见英文单词
    common_words = ['the', 'and', 'for', 'that', 'have', 'with', 'this', 'from']
    word_count = 0
    text_lower = text.lower()
    for word in common_words:
        word_count += text_lower.count(word)

    return letters + spaces * 2 + word_count * 10


def try_len(KEY_LEN, cipher_file):
    """尝试特定密钥长度的解密"""
    cipher_len = len(cipher_file)  # 计算密文有多少个字节
    s = Optimize()  # 创建一个优化求解器

    # key的每一个字节对应一个未知数变量
    key = [BitVec('key_%d' % i, 8) for i in range(KEY_LEN)]
    cipher = [BitVec('cipher_%d' % i, 8) for i in range(cipher_len)]
    plain = [BitVec('plain_%d' % i, 8) for i in range(cipher_len)]
    az_in_plain = [Int('az_in_plain_%d' % i) for i in range(cipher_len)]

    for i in range(cipher_len):
        s.add(cipher[i] == cipher_file[i])
        s.add(plain[i] == cipher[i] ^ key[i % KEY_LEN])
        s.add(Or(And(plain[i] >= 0x20, plain[i] <= 0x7E), plain[i] == 0xA, plain[i] == 0xD))
        s.add(az_in_plain[i] == If(And(plain[i] >= ord('a'), plain[i] <= ord('z')), 1, 0))

    s.maximize(Sum(*az_in_plain))

    if s.check() == unsat:
        return None, None

    m = s.model()

    # 获取密钥
    test_key = "".join(chr(int(str(m[key[i]]))) for i in range(KEY_LEN))

    # 解密数据
    plain_attempt = ""
    for i in range(cipher_len):
        plain_attempt += chr(cipher_file[i] ^ ord(test_key[i % KEY_LEN]))

    return test_key, plain_attempt


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python 破解密文.py <密文文件名>")
        print("示例: python 破解密文.py test_cipher.bin")
        sys.exit(1)

    cipher_file = read_file(sys.argv[1])
    print(f"密文文件: {sys.argv[1]}, 大小: {len(cipher_file)} 字节")

    best_score = -1
    best_key = None
    best_plain = None
    best_len = 0

    # 尝试不同的密钥长度
    for i in range(1, 20):
        print(f"尝试密钥长度={i}", end="")
        key, plain = try_len(i, cipher_file)

        if key and plain:
            score = evaluate_plaintext_quality(plain)
            print(f" - 质量评分: {score}")

            if score > best_score:
                best_score = score
                best_key = key
                best_plain = plain
                best_len = i
        else:
            print(" - 无解")

    print("\n" + "=" * 60)
    print("最佳结果:")
    print(f"密钥长度: {best_len}")
    print(f"密钥: {best_key}")
    print(f"密钥(十六进制): {best_key.encode().hex()}")
    print("\n解密文本:")
    print("-" * 60)
    # 显示前500个字符
    display_text = best_plain[:500] + ("..." if len(best_plain) > 500 else "")
    print(display_text)
    print("-" * 60)


if __name__ == "__main__":
    main()