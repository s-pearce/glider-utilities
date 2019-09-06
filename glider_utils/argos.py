def carry_around_add(a, b):
    """
    calculate the carry around sum for the 16 bit binary values
    """
    c = a + b
    return (c & 0xff) + (c >> 16)

def checksum(msg):
    """
    calculate the checksum. documents say sum all the previous bytes and take
    the ones complement. that doesn't work, need to use the carry around.
    """
    s = 0
    for i in msg:
        s = carry_around_add(s,int(i,16))
    return ~s + 1 & 0xff


def twos_comp(hexstr, nbits):
    b = int(hexstr, 16)
    if b >= 1<<nbits-1: b -= 1<<nbits
    return b


def decode(msg):
    pass


def print_decode(msg):
     if isinstance(msg, str):
         msg_dict = decode(msg)
     if isinstance(msg, dict):
         msg_dict = msg

     print("""Decoded Argos message:
     Transmitted checksum: {trans_chk:d}
     Calculated checksum: {calcd_chk:d}
     {chk_msg}

     {timestamp:s}

     Valid Fix {lat_iso:.2f} {lon_iso::.2f} ({lat_deg:.3f} {lon_deg:.3f})
         Age: {age:d} minutes
     Invalid Fix {in_lat_iso:.2f} {in_lon_iso:.2f} {in_age:d} minutes
     Too-Far Fix {tf_lat_iso:.2f} {tf_lon_iso:.2f} {tf_age:d} minutes

     Water currents: {vx:.2f} {vy:.2f}
                     {sp:.2f} {dir:.2f}
     """.format(**msg_dict))
