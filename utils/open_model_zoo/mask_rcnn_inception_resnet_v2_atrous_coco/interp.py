import numpy as np
import cv2


MASK_THRESHOLD = .5
PROBABILITY_THRESHOLD = 0.2


# Ref: https://software.intel.com/en-us/forums/computer-vision/topic/804895
def segm_postprocess(box: list, raw_cls_mask, im_h, im_w, threshold):
    ymin, xmin, ymax, xmax = box

    width = int(abs(xmax - xmin))
    height = int(abs(ymax - ymin))

    result = np.zeros((im_h, im_w), dtype=np.uint8)
    resized_mask = cv2.resize(raw_cls_mask, dsize=(height, width), interpolation=cv2.INTER_CUBIC)

    # extract the ROI of the image
    ymin = int(round(ymin))
    xmin = int(round(xmin))
    ymax = ymin + height
    xmax = xmin + width
    result[xmin:xmax, ymin:ymax] = (resized_mask>threshold).astype(np.uint8) * 255

    return result


for detection in detections:
    frame_number = detection['frame_id']
    height = detection['frame_height']
    width = detection['frame_width']
    detection = detection['detections']

    masks = detection['masks']
    boxes = detection['reshape_do_2d']

    for index, box in enumerate(boxes):
        label = int(box[1])
        obj_value = box[2]
        if obj_value >= PROBABILITY_THRESHOLD:
            x = box[3] * width
            y = box[4] * height
            right = box[5] * width
            bottom = box[6] * height
            mask = masks[index][label]

            mask = segm_postprocess((x, y, right, bottom),
                                    mask,
                                    height,
                                    width,
                                    MASK_THRESHOLD)

            contour, _ = cv2.findContours(mask,
                                          cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_TC89_KCOS)

            contour = contour[0]
            contour = contour.tolist()
            contour = [x[0] for x in contour]

            # NOTE: if you want to see the boxes, uncomment next line
            # results.add_box(x, y, right, bottom, label, frame_number)
            results.add_polygon(contour, label, frame_number)
