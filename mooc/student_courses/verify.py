from PIL import Image
from numpy import matrix
from numpy import loadtxt
from predictOneVsAll import predictOneVsAll


def recognize_cpatcha(pic_file):
    image = Image.open(pic_file).convert("L")
    x_size, y_size = image.size
    y_size -= 5
    piece = (x_size - 22) / 8
    centers = [4 + piece * (2 * i + 1) for i in range(4)]
    mtx = []
    for i, center in enumerate(centers):
        img = image.crop((center - (piece + 2), 1, center + (piece + 2), y_size))
        width, height = img.size
        t = []
        for h in range(0, height):
            for w in range(0, width):
                pixel = img.getpixel((w, h))
                t.append(pixel)
        mtx.append(t)
    all_theta = matrix(loadtxt('/Users/deserts/PycharmProjects/mooc_analysis/mooc/student_courses/theta.dat'))
    X = matrix(mtx) / 255.0
    acc, pred = predictOneVsAll(all_theta, X)
    answers = map(chr, map(lambda x: x + 48 if x <= 9 else x + 87 if x <= 23 else x + 88, pred))
    return ''.join(answers)

