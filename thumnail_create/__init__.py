from PIL import Image
from os.path import dirname, abspath
from timeout import timeout


@timeout(2)
def create_thumbnail(path, name):
    try:
        outname = "/thumb_128x128_" + name + ".jpg"
        outpath = dirname(abspath(path)) + outname

        img = Image.open(path)

        width, height = img.size
        if width < 128 and height < 128:
            return False

        img.thumbnail((128, 128), Image.ANTIALIAS)
        img.save(outpath, 'JPEG', quality=60, optimize=True, progressive=True)
    except Exception as ex:
        print(ex)
        return False

    return outname, name, 128, 128
