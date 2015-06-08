"""Calculate the difference between two binary images.

Provide a list of predicted files. In the same directory should
also be the label files.

Usage:
  main.py LIST [--thresh=THRESH] [--debug]
  main.py (-h | --help)
  main.py --version

Options:
  --thresh=THRESH   Threshold for predicted image [default: 100].
  --debug           Write debug output.
  -h --help         Show this screen.
  --version         Show version.
"""

import logging
import copy
import os.path

import numpy as np
import cv2
from docopt import docopt


DEBUG = False


def calculate_diff(label_list, thresh):
    with open(label_list) as f:

        all_fp = 0.0
        all_fn = 0.0
        all_tp = 0.0

        where = os.path.dirname(label_list)
        for line in f:
            pred = os.path.join(where, line.strip())
            fname = os.path.basename(
                pred)[:-14] + "-label.png"
            truth = os.path.join(where, fname)

            if not os.path.isfile(pred) or not os.path.isfile(truth):
                print "Not found:", pred, truth
                continue

            truth = cv2.imread(truth, cv2.CV_LOAD_IMAGE_GRAYSCALE)
            pred = cv2.imread(pred, cv2.CV_LOAD_IMAGE_GRAYSCALE)

            # resize to predicted image size
            h, w = pred.shape
            truth = cv2.resize(truth, (w, h))

            # threshold to get bw image
            _, pred = cv2.threshold(pred, thresh, 255, cv2.THRESH_BINARY)

            # threshold because of scaling interpolation
            _, truth = cv2.threshold(truth, 127, 255, cv2.THRESH_BINARY)

            # dilate to account for almost right predictions
            kernel = np.ones((2, 2), np.uint8)
            truth_dil = cv2.dilate(truth, kernel, iterations=2)
            pred_dil = cv2.dilate(pred, kernel, iterations=2)

            fp = np.sum(pred - truth_dil)
            fn = np.sum(truth - pred_dil)
            tp = np.sum(cv2.bitwise_and(pred, truth))

            all_fp += fp
            all_fn += fn
            all_tp += tp

            if DEBUG:
                print fn, fp, tp

                cv2.imshow('truth', truth)
                cv2.imshow('predicted', pred)

                cv2.imshow('fp', pred - truth_dil)
                cv2.imshow('fn', truth - pred_dil)
                cv2.imshow('tp', cv2.bitwise_and(pred, truth))

                cv2.moveWindow('truth', 100, 10)
                cv2.moveWindow('predicted', 300, 10)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        print "Shape:", h, w
        print all_fp, all_fn, all_tp

        print "Precision:", all_tp / (all_tp + all_fp)
        print "Recall:", all_tp / (all_tp + all_fn)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Tester 1.0')

    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG)
        DEBUG = True

    calculate_diff(arguments['LIST'],
                   int(arguments['--thresh']))