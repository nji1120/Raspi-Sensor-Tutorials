def print_hex(label, data):
    """
    任意のバイト列やリストを16進数で見やすく出力するデバッグ用関数
    """
    # bytes型でなければbytesに変換
    if not isinstance(data, (bytes, bytearray)):
        data = bytes(data)
    hexstr = ' '.join(f'{b:02X}' for b in data)
    print(f"{label}: {hexstr}")