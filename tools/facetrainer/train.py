#!/usr/bin/python
# coding: utf8
"""Based on Raspberry Pi Face Recognition Treasure Box
Face Recognition Training Script
Copyright 2013 Tony DiCola

Run this script to train the face recognition system with training images from multiple people.  
The face recognition model is based on the eigen faces algorithm implemented in OpenCV.  
You can find more details on the algorithm and face recognition here:
http://docs.opencv.org/modules/contrib/doc/facerec/facerec_tutorial.html
"""
import fnmatch
import os

import cv2
import numpy as np

import lib.config as config
import lib.face as face

def walk_files(directory, match='*'):
	"""Generator function to iterate through all files in a directory recursively
	which match the given filename match parameter.
	"""
	for root, dirs, files in os.walk(directory):
		for filename in fnmatch.filter(files, match):
			yield os.path.join(root, filename)

def prepare_image(filename):
	"""Read an image as grayscale and resize it to the appropriate size for
	training the face recognition model.
	"""
	return face.resize(cv2.imread(filename, cv2.IMREAD_GRAYSCALE))

def normalize(X, low, high, dtype=None):
	"""Normalizes a given array in X to a value between low and high.
	Adapted from python OpenCV face recognition example at:
	  https://github.com/Itseez/opencv/blob/2.4/samples/python2/facerec_demo.py
	"""
	X = np.asarray(X)
	minX, maxX = np.min(X), np.max(X)
	# normalize to [0...1].
	X = X - float(minX)
	X = X / float((maxX - minX))
	# scale to [low...high].
	X = X * (high-low)
	X = X + low
	if dtype is None:
		return np.asarray(X)
	return np.asarray(X, dtype=dtype)

if __name__ == '__main__':
	print "Reading training images..."
	print '-' *20
	faces = []
	labels = []
	IMAGE_DIRS_WITH_LABEL = [[0,"negative"]]
	pos_count = 0
	neg_count = 0
	
	IMAGE_DIRS = os.listdir(config.TRAINING_DIR)
	IMAGE_DIRS = [x for x in IMAGE_DIRS if not x.startswith('.') and not x.startswith('negative')]
	
	for i in range(len(IMAGE_DIRS)):
		print "Assign label " + str(i+1) + " to " + IMAGE_DIRS[i]
		IMAGE_DIRS_WITH_LABEL.append([i+1,IMAGE_DIRS[i]])
	print '-' *20
	
	#Für jedes Label/Namen Paar:
	for j in range(0,len(IMAGE_DIRS_WITH_LABEL)):
		#Label zu den Labels hinzufügen / Bilder zu den Gesichtern
		for filename in walk_files(config.TRAINING_DIR + str(IMAGE_DIRS_WITH_LABEL[j][1]), '*.pgm'):
			faces.append(prepare_image(filename))
			labels.append(IMAGE_DIRS_WITH_LABEL[j][0])
			if IMAGE_DIRS_WITH_LABEL[j][0] == 0:
				neg_count += 1
			else:
				pos_count += 1
			
	print 'Read', pos_count, 'positive images and', neg_count, 'negative images.'
	for j in range(1, max(labels) + 1):
		print str(labels.count(j)) + " Bilder von " + config.IMAGE_DIRS[j][1]
	#print np.asarray(labels)
	# Train model
	print '-' *20
	print 'Training model...'
	model = cv2.createEigenFaceRecognizer()
	model.train(np.asarray(faces), np.asarray(labels))

	# Save model results
	model.save(config.TRAINING_FILE)
	print 'Training data saved to', config.TRAINING_FILE
	print
	IMAGE_DIRS.insert(0, "ID-0")
	print "Please add or update (if you added new people not just new images) " + str(IMAGE_DIRS) + " in your config file. You can change the names to whatever you want, just keep the same order and leave the ID-0 as it is and you'll be fine."