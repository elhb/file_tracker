def offset_name(name,level):
     #offset = ' '.join('' for i in xrange(level))
     _parts = name.split('/')
     start = '|' if level != 0 else ''
     spacer = '/' if level != 0 else ''
     spacer2 = '`- ' if level != 0 else ''
     #return ''.join([ '|'+''.join([' ' for i in range(len(part))])    for part in _parts[1:max(0,level-1)] ]) + \
     return ''.join([ '|'+''.join([' ' for i in range(2)])    for part in _parts[1:max(0,level-1)] ]) + \
     spacer2 + \
     spacer+ '/'.join(_parts[level:])
     #''.join([' ' for i in range(len(_parts[max(0,level-1)]))]) + 

def bytes2humanreadable(b):
     kb =  b/1024.0
     Mb = kb/1024.0
     Gb = Mb/1024.0
     if   Gb >= 1.0: human_size, size_unit = (Gb, 'GB')
     elif Mb >= 1.0: human_size, size_unit = (Mb, 'MB')
     elif kb >= 1.0: human_size, size_unit = (kb, 'kb')
     elif b  >= 1.0: human_size, size_unit = (b , 'b' )
     else: human_size, size_unit = (b , 'b')
     human_size = round(human_size,1)
     return human_size, size_unit