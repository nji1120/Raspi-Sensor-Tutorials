def fix_idm(idm:int):
    """
    libpafe+ctypesで取得したidmの順番が8ビットごとに逆だから並び替える関数  

    論理演算で並び替えているので理解不能だと思う

    ex)
        libpafe+ctypes -> 354A0F8DC0482E01

        本来           -> 012E48C08D0F4A35

    -input-
        idm:
            libpafeで受け取ったidm.value

    -return-
        idm_sorted:
            012E48C08D0F4A35 みたいな感じ
    """


    fixed_idm=0x0000000000000000
    for i in range(8):
        filter=0xff00000000000000>>(4*2*i)
        filtered_idm=idm&filter

        shift=4*(14-4*i)
        if shift>=0:
            fixed_idm|=(filtered_idm>>shift)
        else:
            fixed_idm|=(filtered_idm<<abs(shift))
        # print(hex(filtered_idm)[2:],hex(fixed_idm)[2:])

    return hex(fixed_idm)[2:].upper()