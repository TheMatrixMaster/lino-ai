import numpy as np
from PIL import Image, ImageChops


def __remove_border(np_image):
    im = Image.fromarray(np.uint8(np_image))
    im_trim = __trim(im)
    return im_trim


def format_images(np_array_images):
    new_np_array_images = []
    for np_image in np_array_images:
        crop_image = __remove_border(np_image)
        resize_image = __crop_in_square(crop_image)
        new_np_array_images.append(np.array(resize_image))
    return new_np_array_images


def __crop_in_square(image):
    height, width = image.size
    multiple_8 = __round_down_multiple_8(min(height, width))
    left = (width - multiple_8) / 2
    top = (height - multiple_8) / 2
    right = (width + multiple_8) / 2
    bottom = (height + multiple_8) / 2
    return image.crop((left, top, right, bottom))


def __round_down_multiple_8(number):
    return number - (number % 8)


def __trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
