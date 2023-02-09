Folder: altimeter_detector

Images of training and testing datasets are stored in folder: images_examples

In altimeter_detector/images_examples, there are training.xml and testing.xml which contain the positions of anotated bounding boxes for training and testing images.
training.xml and testing.xml are both made by imglab, which is a tool in dlib library.

Run train_object_detector.py to train the detector with the training and testing datasets, the trained detector will be stored as detector.svm
