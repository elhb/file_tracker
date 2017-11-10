def offset_name(file_or_dir):

    if 'fullpath' in file_or_dir.__dict__:
        name = file_or_dir.fullpath
    else:
        name = file_or_dir.name
    
    if not file_or_dir.parent_dir: return name
    return name.replace(file_or_dir.parent_dir.name,''.join('-' for i in xrange(len(file_or_dir.parent_dir.name))))

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