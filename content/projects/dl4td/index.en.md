---
title: "DL4TD"
category: python
summary: "Automated data preparation and training for a table detector in document images: five heterogeneous datasets are reduced to a single format, preprocessed and augmented, then packed into TFRecord for fine-tuning Faster R-CNN. Tooling for the TabbyDOC research project, the approach is described in a paper at MIPRO 2020."
date: 2021-04
tags: [computer-vision, dataset, tensorflow, research]
tech: [Python, TensorFlow 2, TF Object Detection API, Faster R-CNN, OpenCV, Pillow, PASCAL VOC, TFRecord, Google Colab]
cover: cover.png
links:
  - { label: "GitHub", url: "https://github.com/tabbydoc/dl4td", icon: github }
  - { label: "Paper (MIPRO 2020)", url: "https://doi.org/10.23919/MIPRO48935.2020.9245241", icon: external }
  - { label: "Colab notebook", url: "https://colab.research.google.com/drive/1TDoXxlxGhrbeZfkID5xK0DNK7ikicbZC", icon: external }
---

## Problem statement

Fine-tuning an object detector to find tables in scanned documents is not difficult in itself: the
architecture and the initial weights are taken ready-made. The bulk of the effort goes into
preparing the data.

Publicly available document collections are annotated in different ways. ICDAR 2017, ICDAR 2019
cTDaR, Marmot, SciTSR and UNLV differ in directory structure, annotation format and the way the
table region is defined. The images then have to be preprocessed, the annotations multiplied by
augmentation while staying consistent with the image, and the result packed into the format of the
training framework. Every new experiment meant repeating this chain by hand, and therefore repeating
its mistakes as well, while an error in data preparation only shows up in the training results.

DL4TD turns the chain into a single run whose composition is described by a configuration file:

```txt
datasets → PASCAL VOC → image preprocessing → augmentation → train.record, val.record → Faster R-CNN
```

The work was done in the laboratory of ISDCT SB RAS as part of the TabbyDOC project supported by the
Russian Science Foundation; the approach and the results are described in a paper at the MIPRO 2020
conference.

## Driving the pipeline from a configuration file

The control script reads `config.ini` and launches the steps as separate processes, passing paths as
command line arguments. Each step is a standalone script with the interface
`-i <input folder> -o <output folder>`, so it can be called on its own, outside the pipeline, and a
questionable result can be reproduced with a single command.

The scheme was chosen for three consequences:

- **The experiment is described by data.** An empty field in the configuration means the step is
  skipped, so a run without augmentation or without preprocessing needs neither flags nor code
  changes. The configuration file fully describes what a particular experiment is made of.
- **Dependencies are separated.** The converter needs only Pillow and the standard library,
  TensorFlow is required only for the last steps. A broken training environment does not prevent
  data preparation.
- **An error names its cause.** A missing script, a nonexistent folder, a nonzero exit code from a
  child process and a failure of a helper module are four different exit codes, and the message
  points not only to the offending path but also to the parameter and the configuration section
  where it is set.

Intermediate directories are recreated at the start of a run. The reason is not convenience but the
cost of a mistake: unnoticed leftovers from a previous experiment inside the training set cost more
than a minute spent rebuilding them.

## Reduction to a common format

Each dataset has its own converter to PASCAL VOC: images, XML annotations in `annotations/xmls` and
a list of names in `trainval.txt`. The source formats do not agree with one another. In ICDAR 2019
cTDaR, for instance, a table is given as a polygon of points, and the converter reduces it to an
axis-aligned rectangle, determining from the image the dimensions that the original annotation does
not carry.

If several datasets are enabled in the configuration, they are merged into a single collection, and
this is the stage where manual assembly most often goes wrong. Colliding file names get a numeric
suffix, and the `filename` field inside the XML is rewritten together with the image name, otherwise
the annotation loses its link to the image with nothing outward to show for it. Annotations without
a single object are removed along with their images, so that empty examples do not reach training.

Adding your own dataset takes one script that emits PASCAL VOC and a section in the configuration.
The rest of the pipeline stays unchanged.

## Preprocessing: distance maps instead of pixels

<figure>
  <img src="/projects/dl4td/assets/data-preparation.png" alt="Example of a transformed image" loading="lazy">
  <figcaption>Image transformation. Left - the original image, right - the image transformed into a distance map</figcaption>
</figure>

Before training, the image is converted to grayscale, after which three distance transforms with
different metrics are computed over it: Euclidean, city block and chessboard. They are assembled
into three channels.

The network therefore receives not the scan itself but the distance to the nearest dark pixel,
computed in three different ways. The reason for the substitution is that what marks a table is the
geometry of the empty space: the ruling, the gaps between columns and the regularity of rows. In a
distance map that structure is represented explicitly, whereas in the original pixels it has to be
inferred from brightness.

## Augmentation with recomputed annotations

Augmentation multiplies each image by nine anisotropic scalings: the factors along the X and Y axes
are set independently in the range 0.8..1.2. The set gains tables with stretched and compressed
proportions, which the original data has few of.

The essential part of the step is not the scaling but the consistent recomputation of the
annotation: the image dimensions and the coordinates of every box in the XML are multiplied by the
same factors and the file name is updated. Losing that synchronization causes no runtime error and
is not visible on inspection, training runs on the wrong correspondence, and the result is a model
of degraded quality whose cause in the data gives no sign of itself.

## Splits and training

The final step converts the collection into the format of the framework: box coordinates are
normalized to the image dimensions, examples are serialized into `tf.train.Example` and written to
`train.record` and `val.record`. The 95/5 split is done with a fixed random seed, so the same input
always yields the same splits and the differences between runs come down to the ones introduced on
purpose. On Marmot this gives 8276 training and 436 validation examples.

Training is moved into a Google Colab notebook: it installs the TensorFlow Object Detection API,
runs the pipeline, pulls the COCO-pretrained `faster_rcnn_resnet50_v1_640x640` checkpoint, fine-tunes
it with the supplied `pipeline.config` (a single class, 640x640 input with aspect ratio preserved,
15,000 steps, momentum with cosine decay and warmup), exports a SavedModel and runs inference on
test pages. The repository therefore covers the whole path from a downloaded dataset archive to a
trained detector.

## Result

<figure>
  <img src="/projects/dl4td/assets/workflow.jpg" alt="Table prediction on a transformed image" loading="lazy">
  <figcaption>Table prediction on a transformed image</figcaption>
</figure>

Adding a new dataset takes one converter script, changing the composition of an experiment takes an
edit to the configuration, and reproducing someone else's result takes running two commands. The
pipeline is built from five converters and three shared steps driven by a single script: Python 3.6,
TensorFlow 2 with the Object Detection API, OpenCV and Pillow for image handling, PASCAL VOC as the
intermediate annotation format and TFRecord as the final one.
