import cv2
import numpy as np
import json
import time
import os
from pathlib import Path
import argparse

def stats_percent(percent: float) -> tuple:
    if percent >= 80:
        stats_color = (0, 255, 0)
    elif percent < 80 and percent >= 50:
        stats_color = (255, 255, 0)
    else:
        stats_color = (0, 0, 255)

    return stats_color

def make_gauge(image_jpg: np.ndarray, percent: float, x=20, y=20, width=230, height=55) -> None:
    percent = max(0.0, min(100.0, percent))

    cv2.rectangle(image_jpg, (x, y), (x + width, y + height), (25, 25, 25), -1)
    cv2.rectangle(image_jpg, (x, y), (x + width, y + height), (80, 80, 80), 1)

    bar_x = x + 12
    bar_y = y + 28
    bar_w = width - 24
    bar_h = 14

    for i in range(bar_w):
        ratio = i / float(bar_w)

        if ratio < 0.5:
            factor = ratio / 0.5
            b, g, r = 0, int(255 * factor), 255
        else:
            factor = (ratio - 0.5) / 0.5
            b, g, r = 0, 255, int(255 * (1.0 - factor))

        cv2.line(image_jpg, (bar_x + i, bar_y), (bar_x + i,  bar_y + bar_h), (b, g, r), 1)

    cv2.rectangle(image_jpg, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (200, 200, 200), 2)

    pointer_x = bar_x + int((percent / 100.0) * bar_w)

    pointers = np.array([
        [pointer_x, bar_y - 2],
        [pointer_x - 5, bar_y - 8],
        [pointer_x + 5, bar_y - 8]
    ], np.int32)

    cv2.drawContours(image_jpg, [pointers], 0, (255, 255, 255), -1)
    cv2.drawContours(image_jpg, [pointers], 0, (0, 0, 0), 1)

    cv2.line(image_jpg, (pointer_x, bar_y), (pointer_x, bar_y + bar_h), (255, 255, 255), 2)

    stats_color = stats_percent(percent)
    text = f"Quality: {percent:.2f}%"
    cv2.putText(image_jpg, text, (x + 12, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 0)

def process_image(image_jpg: np.ndarray, data_config: tuple) -> np.ndarray:
    x, y, w, h = data_config['roi']['x'], data_config['roi']['y'], data_config['roi']['w'], data_config['roi']['h']
    good_lower = np.array(data_config['cor_boa']['lower_good'])
    good_upper = np.array(data_config['cor_boa']['upper_good'])
    bad_lower = np.array(data_config['cor_ruim']['lower_bad'])
    bad_upper = np.array(data_config['cor_ruim']['upper_bad'])

    select_filter = data_config['imagem_analisada']['filtro']

    roi = image_jpg[y: y + h, x: x + w]
    roi_blur = cv2.GaussianBlur(roi, (5, 5), 0)
    roi_unsharping = cv2.addWeighted(roi, 1.5, roi_blur, -0.5, 0)

    if select_filter == "Blur":
        hsv = cv2.cvtColor(roi_blur, cv2.COLOR_BGR2HSV)
        print("hsv = blur")
    if select_filter == "Unsharping Mask":
        hsv = cv2.cvtColor(roi_unsharping, cv2.COLOR_BGR2HSV)
        print("hsv = unsharping mask")
    else:
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        print("hsv = no filter")

    mask_good = cv2.inRange(hsv, good_lower, good_upper)
    mask_bad = cv2.inRange(hsv, bad_lower, bad_upper)

    kernel = np.ones((5, 5), np.uint8)

    if select_filter == "Morphology":
        mask_apply_good = cv2.morphologyEx(mask_good, cv2.MORPH_OPEN, kernel)
        mask_apply_good = cv2.morphologyEx(mask_apply_good, cv2.MORPH_CLOSE, kernel)

        mask_apply_bad = cv2.morphologyEx(mask_bad, cv2.MORPH_OPEN, kernel)
        mask_apply_bad = cv2.morphologyEx(mask_apply_bad, cv2.MORPH_CLOSE, kernel)

        print("mask = morphology\n")
    elif select_filter == "Erosion":
        mask_apply_good = cv2.erode(mask_good, kernel, iterations=1)

        mask_apply_bad = cv2.erode(mask_bad, kernel, iterations=1)

        print("mask = erosion\n")
    else:
        mask_apply_good = mask_good

        mask_apply_bad = mask_bad

        print("mask = no filter\n")

    good_pixels = cv2.countNonZero(mask_apply_good)
    bad_pixels = cv2.countNonZero(mask_apply_bad)
    all_pixels = good_pixels + bad_pixels

    print(f"Good pixels: {good_pixels}\n")
    print(f"Bad pixels: {bad_pixels}\n")
    print(f"All pixels (sum): {all_pixels}\n")

    stats = "Waiting..."
    text_color = (200, 200, 200)

    if all_pixels > 100:
        percent_amount = (good_pixels / all_pixels) * 100

        print("----- Results -----")

        print(f"Percent: {percent_amount:.2f}%\n")
    else:
        print("Don't have enough analyzed pixels.\n")

    make_gauge(image_jpg, percent_amount)
    cv2.rectangle(image_jpg, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return image_jpg
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", default="grass_img.jpg", help="Path to the image")
    args = parser.parse_args()
    image_jpg = cv2.imread(args.img)

    if image_jpg is None:
        print("Error in loading image.\n")
        exit()

    try:
        with open('config_img.json', 'r') as arq:
            data_config = json.load(arq)
    except FileNotFoundError:
        print("Error: File 'config_img.json' not found.\n")
        exit()

    try:
        while True:
            analyzed_frame = process_image(image_jpg, data_config)
            cv2.imshow('Original Image', image_jpg)
            cv2.imshow('Analyzed Image', analyzed_frame)

            print("Press 'Esc' for exit in the window.\n")
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()