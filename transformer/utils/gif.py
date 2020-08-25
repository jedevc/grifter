from PIL import Image

FULL = "full"
PARTIAL = "partial"

def is_transparent(im):
    '''
    Detect if an image has any transparent components.

    Based on https://stackoverflow.com/a/58567453
    '''

    if im.mode == "P":
        transparent = im.info.get("transparency", -1)
        for _, index in im.getcolors():
            if index == transparent:
                return True
    elif im.mode == "RGBA":
        extrema = im.getextrema()
        if extrema[3][0] < 255:
            return True

    return False

def analyze(im):
    '''
    Determine the "mode" of the gif (full or additive).

    Based on https://gist.github.com/almost/d2832d0998ad9dfec2cacef934e7d247
    '''
    
    begin = im.tell()

    mode = FULL
    while True:
        try:
            if is_transparent(im):
                mode = PARTIAL
                break

            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    mode = PARTIAL
                    break
            im.seek(im.tell() + 1)
        except EOFError:
            break

    im.seek(begin)
    return mode

def get_frames(im):
    '''
    Iterate the GIF, extracting each frame.

    Based on https://gist.github.com/almost/d2832d0998ad9dfec2cacef934e7d247
    '''

    mode = analyze(im)

    p = im.getpalette()
    last_frame = im.convert('RGBA')

    while True:
        try:
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.putpalette(p)

            new_frame = Image.new('RGBA', im.size)

            if mode == PARTIAL:
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert('RGBA'))
            yield new_frame

            last_frame = new_frame
            im.seek(im.tell() + 1)
        except EOFError:
            break
