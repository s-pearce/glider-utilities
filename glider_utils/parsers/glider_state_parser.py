

class GliderStateXML_Parser(object):
    ts_regex = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\+|-)(\d{2})(\d{2})')
    positions = {}
    for glider in gliders:
        glider_name = 'ce_' + glider
        tree = ET.parse('/var/opt/gmc/gliders/' + glider_name + '/gliderState.xml')
        root = tree.getroot()
        track = root.findall('writeTrack')[0]
        pos = []
        timestamps = []
        for report in track.findall('report'):
            time_ = report.findall('time')[0]
            match = ts_regex.match(time_.text)
            if match:
                ts = match.group(1)
                tz_sn = match.group(2)
                tz_hr = match.group(3)
                tz_mn = match.group(4)
            kml_ts = ts + tz_sn + tz_hr + ':' + tz_mn
            dt_ts = dt.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
            if (dt.datetime.now() - dt_ts).days > 7:
                continue
            else:
                timestamps.append(dt_ts)
            
            location = report.findall('location')[0]
            lat = location.findall('lat')[0]
            lon = location.findall('lon')[0]
            lat = float(lat.text)
            lon = float(lon.text)
            lat = '%.3f' % iso2deg(lat)
            lon = '%.3f' % iso2deg(lon)
            
            pos.append((kml_ts, lon, lat))

            
        # remove duplicate points
        pos = np.unique(pos)
        positions[glider] = pos