import os
import time
import glob
import shutil
import numpy as np
from PIL import Image
from loguru import logger
from jinja2 import Template

time_list = []
start = time.time()

output = os.getcwd()

label_path = os.path.join(output, 'Annotations')
if not os.path.exists(label_path):
    os.mkdir(label_path)
image_path = os.path.join(output, 'JPEGImages')
if not os.path.exists(image_path):
    os.mkdir(image_path)


def running_time(time):
    m = time / 60
    h = m / 60
    if m > 1:
        if h > 1:
            return str('%.2f' % h) + 'h'
        else:
            return str('%.2f' % m) + 'm'
    else:
        return str('%.2f' % time) + 's'


def yolo2voc(width, height, box):
    center_x = box[0] * width
    center_y = box[1] * height
    bbox_width = box[2] * width
    bbox_height = box[3] * height
    xmin = round(center_x - bbox_width / 2)
    ymin = round(center_y - bbox_height / 2)
    xmax = round(center_x + bbox_width / 2)
    ymax = round(center_y + bbox_height / 2)
    new_box = [xmin, ymin, xmax, ymax]
    return new_box


def get_box(image):
    im = Image.open(image)
    width, height = im.size
    path, file = os.path.split(image)
    name, shuffix = os.path.splitext(file)
    label_file = glob.glob(f'{os.getcwd()}/*/*/{name}.txt')
    if not label_file:
        raise ValueError('标注文件为空,请修改获取标注文件的代码')
    words = []
    if label_file:
        with open(label_file[0], 'r') as f:
            for line in f.readlines():
                yolo_datas = line.strip().split(' ')
                label = int(float(yolo_datas[0].strip()))
                center_x = round(float(str(yolo_datas[1]).strip()) * width)
                center_y = round(float(str(yolo_datas[2]).strip()) * height)
                bbox_width = round(float(str(yolo_datas[3]).strip()) * width)
                bbox_height = round(float(str(yolo_datas[4]).strip()) * height)
                xmin = str(int(center_x - bbox_width / 2))
                ymin = str(int(center_y - bbox_height / 2))
                xmax = str(int(center_x + bbox_width / 2))
                ymax = str(int(center_y + bbox_height / 2))
                if label == 0:
                    label = 'block'
                if label == 1:
                    label = 'title'
                data = {'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'label': label}
                words.append(data)
        xml_data = {'words': words, 'dummy_words': [], 'img_path': image, 'img_name': file, 'width': width,
                    'height': height, 'folder_name': os.path.join(output, 'Annotations')}

        with open('exp.xml', "r", encoding="utf-8") as f:
            before_data = f.read()
            t = Template(before_data)

        with open(os.path.join(label_path, name + '.xml'), 'w', encoding="utf-8") as f:
            after_data = t.render(xml_data)
            f.write(after_data)
        shutil.copy(image, os.path.join(image_path, file))

    # logger.debug(name)
    # logger.debug(path)


image_list = glob.glob(f'{os.getcwd()}/*/*/*.jpg')
if not image_list:
    raise ValueError('图片文件为空,请修改获取图片文件的代码')
number = len(image_list)
for image in image_list:
    strats_time = time.time()
    number -= 1
    start_time = time.time()
    get_box(image)
    end_time = time.time()
    now_time = end_time - start_time
    time_list.append(now_time)
    logger.debug(f'已耗时: {running_time(end_time - start)}')
    logger.debug(f'预计耗时: {running_time(np.mean(time_list) * number)}')
