from datetime import datetime as dt
from glider_utils.geo import iso2deg

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


def checksum2(msg):
     s = 0
     for ii in range(0, len(msg), 2):
        ibyte = msg[ii:ii+2]
        s = carry_around_add(s, int(ibyte, 16))
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


def dev_decode(msg):
    time_hex = msg[0:8]
    lat_hex = msg[8:14]
    lon_hex = msg[14:20]
    fixtime_hex = msg[20:24]
    invlat_hex = msg[24:30]
    invlon_hex = msg[30:36]
    invfixtime_hex = msg[36:40]
    tflat_hex = msg[40:46]
    tflon_hex = msg[46:52]
    tffixtime_hex = msg[52:56]
    vx_hex = msg[56:58]
    vy_hex = msg[58:60]
    timestamp = dt.utcfromtimestamp(int(time_hex, 16))
    val_lat = twos_comp(lat_hex, 4*6)
    val_lon = twos_comp(lon_hex, 4*6)
    val_fix = int(fixtime_hex, 16)
    inv_lat = twos_comp(invlat_hex, 4*6)
    inv_lon = twos_comp(invlon_hex, 4*6)
    inv_fix = int(invfixtime_hex, 16)
    tf_lat = twos_comp(tflat_hex, 4*6)
    tf_lon = twos_comp(tflon_hex, 4*6)
    tf_fix = int(tffixtime_hex, 16)
    vx = twos_comp(vx_hex, 2*4)
    vy = twos_comp(vy_hex, 2*4)
    
    print("{:s}".format(timestamp.isoformat()))
    #print("lat: {:.4f} ({:.4f}), lon: {:.4f} ({:.4f})".format(
    print("Valid lat: {:d}, lon: {:d}, {:d} min ago".format(
        val_lat, val_lon, val_fix))
    print("Invalid lat: {:d}, lon: {:d}, {:d} min ago".format(
        inv_lat, inv_lon, inv_fix))
    print("Too Far lat: {:d}, lon: {:d}, {:d} min ago".format(
        tf_lat, tf_lon, tf_fix))
    print("Water velocity: vx {:f}, vy {:f}".format(vx, vy))