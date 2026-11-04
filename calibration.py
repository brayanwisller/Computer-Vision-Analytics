import cv2
import numpy as np
import json
import sys
from deepmerge import merge_or_raise
import argparse

def create_trackbars(window_name: str) -> None:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 400, 250)

    def nothing(x): pass

    cv2.createTrackbar('H_min', window_name, 0, 179, nothing)
    cv2.createTrackbar('S_min', window_name, 0, 255, nothing)
    cv2.createTrackbar('V_min', window_name, 0, 255, nothing)
    cv2.createTrackbar('H_max', window_name, 179, 179, nothing)
    cv2.createTrackbar('S_max', window_name, 255, 255, nothing)
    cv2.createTrackbar('V_max', window_name, 255, 255, nothing)

def read_trackbars(window_name: str) -> tuple:
    h_min = cv2.getTrackbarPos('H_min', window_name)
    s_min = cv2.getTrackbarPos('S_min', window_name)
    v_min = cv2.getTrackbarPos('V_min', window_name)
    h_max = cv2.getTrackbarPos('H_max', window_name)
    s_max = cv2.getTrackbarPos('S_max', window_name)
    v_max = cv2.getTrackbarPos('V_max', window_name)
    return [h_min, s_min, v_min], [h_max, s_max, v_max]
    
def create_menu(filter_dict: dict, attempts = 1, max_attempts = 3) -> int:
    print("\nMenu:\n\n (9) Exit\n\n")
    print("Available filters:\n\n (1) Morphology\n (2) Erosion\n (3) Blur\n (4) Unsharping Mask\n (5) No filters\n\n")

    while attempts <= max_attempts:
        try:
            select_number = int(input(f"[{attempts}/{max_attempts}] Select an action or filter: "))
            print(f"\nAction/Filter selected: {select_number}\n")
            if select_number == 9:
                print("\nFinishing operation...\n")
                sys.exit()
            if select_number not in filter_dict or not filter_dict[select_number]:
                print("Filter not found! Trying again...\n")
                attempts += 1
            else:
                break
        except (TypeError, ValueError):
            select_number = None
            print("\nEnter a valid value to select a desired action or filter.\n")
            attempts += 1

    if select_number not in filter_dict or not filter_dict[select_number]:
        print(f"Filter not found after {max_attempts} attempts. Finishing operation...\n")
        sys.exit()

    return select_number

def color_calibration(window_name: str, roi_image: np.ndarray, num_filter: int) -> tuple:
    print(f"Adjust the controls until the desired element turns white for {window_name}")
    print("Press 'Esc' to exit the edit window.\n")
    create_trackbars('Controls')

    while True:
        hsv = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)

        lower_bound, upper_bound = read_trackbars('Controls')

        mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))

        kernel = np.ones((5, 5), np.uint8)

        if num_filter == 1:
            mask_morfologia_open = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask_apply = cv2.morphologyEx(mask_morfologia_open, cv2.MORPH_CLOSE, kernel)
        elif num_filter == 2:
            mask_apply = cv2.erode(mask, kernel, iterations=1)
        else:
            mask_apply = mask

        result = cv2.bitwise_and(roi_image, roi_image, mask=mask_apply)

        cv2.imshow(window_name, mask_apply)
        cv2.imshow('Original Image', result)
            
        if cv2.waitKey(1) & 0xFF == 27:
            cv2.destroyWindow(window_name)
            cv2.destroyWindow('Controls')
            return lower_bound, upper_bound
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", default="grass_img.jpg", help="Path to the image")
    args = parser.parse_args()
    img = cv2.imread(args.img)

    if img is None:
        print("Error in loading image!")
        sys.exit()

    image_blur = cv2.GaussianBlur(img, (3, 3), 0)
    image_unsharping = cv2.addWeighted(img, 1.5, image_blur, -0.5, 0)

    filter_dict = {
        1: {"text_good_color": "Good color with Morphology filter", "text_bad_color": "Bad color with Morphology filter", "analyzed_img": img, "filter": "Morphology"},
        2: {"text_good_color": "Good color with Erosion filter", "text_bad_color": "Bad color with Erosion filter", "analyzed_img": img, "filter": "Erosion"},
        3: {"text_good_color": "Good color with Blur filter", "text_bad_color": "Bad color with Blur filter", "analyzed_img": image_blur, "filter": "Blur"},
        4: {"text_good_color": "Good color with Unsharping Mask filter", "text_bad_color": "Bad color with Unsharping Mask filter", "analyzed_img": image_unsharping, "filter": "Unsharping Mask"},
        5: {"text_good_color": "Good color without filter", "text_bad_color": "Bad color without filter", "analyzed_img": img, "filter": "No filter"}
    }

    selected_number = create_menu(filter_dict)

    # frame_dict = {
    #    1: {"analyzed_img": img},
    #    2: {"analyzed_img": img},
    #    3: {"analyzed_img": image_blur},
    #    4: {"analyzed_img": image_unsharping},
    #    5: {"analyzed_img": img}
    # }

    # try:
    #    result_dict = merge_or_raise.merge(filtro_dict, frame_dict)
    # except Exception as e:
    #    print(f"Raise or merge error: {e}")

    text_good_color = filter_dict[selected_number]["text_good_color"]
    text_bad_color = filter_dict[selected_number]["text_bad_color"]
    analyzed_image = filter_dict[selected_number]["analyzed_img"]
    used_filter = filter_dict[selected_number]["filter"]

    print("Starting image verification...")
    roi_box = cv2.selectROI("Select the reading area", analyzed_image, fromCenter=False)
    x, y, w, h = roi_box

    cv2.destroyWindow("Select the reading area")

    if w > 0 and h > 0:
        roi = analyzed_image[y: y + h, x: x + w]
        print(f"\nROI((y: y + h), (x: x + w)): roi = image [{y}: {y+h}, {x}: {x+w}]\n")
    else:
        roi = analyzed_image
        print("No cut for the ROI")

    try:
        good_color_lower, good_color_upper = color_calibration(text_good_color, roi, selected_number)
        bad_color_lower, bad_color_upper = color_calibration(text_bad_color, roi, selected_number)
        
        settings = {
            "roi": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
            "good_color": {"lower_good": good_color_lower, "upper_good": good_color_upper},
            "bad_color": {"lower_bad": bad_color_lower, "upper_bad": bad_color_upper},
            "analyzed_image": {"filter": used_filter}
        }

        with open('settings_img.json', 'w') as file:
            json.dump(settings, file, indent=4)

        print(f"\nSuccess! The settings were saved to the JSON file.\n")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()