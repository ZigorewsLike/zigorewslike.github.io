---
title: "noJpg GAN"
category: python
summary: "A conditional GAN following the pix2pix scheme that restores a photograph after heavy JPEG compression with a loss of resolution. The training pairs are built from the photographs themselves and need no annotation: a U-Net generator predicts the original frame, a PatchGAN discriminator scores the result in 34x34 pixel patches."
date: 2021-04
tags: [gan, tensorflow, computer-vision, image-restoration]
tech: [Python, TensorFlow 2, Keras, pix2pix, U-Net, PatchGAN, Pillow, DVC, CUDA]
cover: example1.png
links:
  - { label: "GitHub", url: "https://github.com/ZigorewsLike/noJpg_gan", icon: github }
---

<figure>
  <img src="/projects/nojpg-gan/assets/example1.png" alt="Example of a restored photograph" loading="lazy">
  <figcaption>Input and generator output</figcaption>
</figure>

## Problem statement

JPEG encodes an image in blocks of 8x8 pixels: a discrete cosine transform is applied to each block,
and the resulting coefficients are divided by a quantization matrix and rounded. At low quality most
of the high-frequency coefficients become zero. Two characteristic defects follow: block boundaries
visible on smooth gradients, and ringing along contrasting edges.

A smoothing filter processes a neighbourhood regardless of its content and suppresses the artifact
together with the detail. It does not restore the zeroed coefficients: that requires knowing what an
uncompressed frame looks like, and the filter holds no such knowledge.

That knowledge is extracted from data. Compression is irreversible, yet pairs of "distorted frame,
original" are built without manual work: a photograph is distorted in a controlled way and serves as
the reference for its own distorted version. The task is stated as image-to-image translation and
solved with the pix2pix scheme: a conditional GAN where the generator is fed the distorted frame and
the discriminator scores the pair.

## The distortion model

`collect_data.py` walks a folder of photographs and builds one training pair file from every usable
photograph:

```txt
source frame, both sides at least 600
      │  short side scaled to 512, center crop
      ▼
   512x512  ──────────────────────────────────────────────────►  target
      │
      │  downscale to 256x256, JPEG at quality 20..70, upscale to 512x512
      ▼
   512x512  ──────────────────────────────────────────────────►  input

      pair file 1024x512: left half input, right half target
```

The distortion consists of two parts, and the second one is not compression: the linear resolution
of the input is halved and then restored by interpolation. The network is therefore trained both to
suppress blocking and to reconstruct the detail lost in the downscale, not only to undo the
quantization of coefficients.

The remaining decisions at this stage follow from the quality of the reference:

- **Size filter.** Frames with a side smaller than 600 pixels are skipped, otherwise the 512x512
  target would be produced by upscaling and would carry artifacts of its own.
- **Random quality.** The compression level is drawn from the range 20..70 for every frame. At a
  fixed value the network would learn the artifact statistics of that single level and would perform
  noticeably worse on the rest.
- **Storing the pair essentially without loss.** The pair file is written with quality 100 and
  chroma subsampling off (`subsampling=0`), so the container adds none of the artifacts the network
  is meant to remove to the target.

The split into training and test sets is a random draw of files, with a default test share of 0.15.
The training set was about 4000 photographs of nature and birds.

<figure>
  <img src="/projects/nojpg-gan/assets/example2.jpg" alt="Example image from the training dataset" loading="lazy">
  <figcaption>A 1024x512 training pair file: input on the left, target on the right</figcaption>
</figure>

## Generator

The generator is a U-Net built on 4x4 convolutions with stride 2. The input image is normalized to
the range from minus one to one, and the output layer is closed by `tanh`, so it works in the same
range.

```txt
down  512 → 256 → 128 → 64 → 32 → 16 → 8 → 4 → 2 → 1      filters 32 … 1024
up      1 →   2 →   4 →  8 → 16 → 32 → 64 → 128 → 256 → 512
        every up block is concatenated with the down block of the same size
```

Nine down blocks (strided convolution, batch normalization, LeakyReLU) reduce the frame to a
1x1x1024 vector. The upward path is made of transposed convolutions with batch normalization and
ReLU, with dropout 0.5 in the first three blocks, and the last layer emits three channels. The
output of every down block except the last is concatenated with the matching up block.

The skip connections are what matters most here. Restoration does not change the composition of the
frame: the input and the output coincide almost everywhere, and the differences are concentrated in
the high-frequency component. The skip connections pass the structure through directly, and only
what needs correcting is processed at the bottleneck. The price of the decision is visible in the
size of the model: about 195 million parameters, with the generator weight file taking 747 MB.

## Discriminator

The discriminator follows the PatchGAN scheme. It receives the input and the image under evaluation
concatenated along the channel axis (6 channels), and after two stride-2 blocks and two stride-1
convolutions it returns not a single number but a 126x126 map. Each cell of the map is determined by
a 34x34 pixel area of the source frame.

For compression artifacts this is essential. The defect is local and tied to the block grid, so
scoring by areas forces the generator to correct every region of the frame, whereas a single number
at the output would permit a result that is acceptable on average over the frame.

## Loss

The discriminator loss is the sum of two binary cross-entropies: the real pair against ones and the
generated one against zeros. The generator loss is composed of the adversarial term and the L1
distance to the original with the weight `lambda`, 100 by default.

The terms are responsible for different properties of the result. L1 keeps the output close to the
reference and sets the geometry and the colour, while the adversarial term is responsible for
sharpness and texture. Without L1 the generator restores plausible detail that does not match the
original. Without the adversarial term the minimum of the mean error is reached by a blurred frame,
since averaging over the possible variants of a texture yields exactly that.

## Training

Adam with a step of 2e-4 and `beta_1 = 0.5` for both networks, a batch of one image, a shuffle
buffer of 400, and 150 epochs by default.

Augmentation is applied not to the input and the target separately but to the tensor stacked from
them, so both halves get the same geometric transform. The transform that actually changes the frame
is the horizontal flip with probability 0.5: the resize to 512x512 and the random crop are set to
the size of the frame. Losing the synchronization within a pair would raise no runtime error and
would not be visible on inspection, while training would run on a correspondence that does not exist
and the losses would keep decreasing.

The loss terms are written to TensorBoard separately rather than as a single sum: a combined plot
does not tell which of the two networks stopped learning, whereas the three generator curves and the
one discriminator curve show which way the balance shifted. Checkpoints are saved every second
epoch, and the `-r` flag resumes training from the latest one, so a run moves to another machine
without losing its result.

The weights and the training set are versioned with DVC on a Google Drive remote: it tracks a 6.4 GB
data folder and the weight file, while Git holds only the pointers that tie a version of the data to
a commit.

## Applying the trained model

The generator takes a fixed 512x512 input, so `test_val.py` scales the shot by its long side to 512
with the aspect ratio preserved, pads it to a square, runs it through the model and crops the
padding back to the original dimensions. Stretching the frame to a square would change the
proportions and the scale of the artifacts relative to what the network was trained on.

The generator is called with `training=True`, as is customary in pix2pix. In that mode batch
normalization uses the statistics of the current image rather than the accumulated running means.
With a batch of one image the accumulated statistics describe not the distribution of the data but a
sequence of individual frames, and switching to inference mode changes the result noticeably.

## Limitations

The training set consists of photographs of nature and birds. On portraits and on machinery the
result is noticeably worse: a frame of a class absent from training is restored using statistics that
do not correspond to it.

The window is fixed at 512x512. A larger shot is downscaled to that size, and processing at the
original resolution would require splitting it into blocks with the boundaries stitched together,
which the project does not implement.

The quality range 20..70 and the twofold downscale are fixed at the data collection stage. The model
is tuned to that distribution of distortions, and on a lightly compressed shot it performs a
transformation the shot does not call for.

Quality is assessed visually, on the "input, result" pair: metrics such as PSNR and SSIM are not
computed, and the test set is used to display an example after every epoch. Training relies on CUDA
and requires an NVIDIA graphics card, and the dependency versions are pinned to TensorFlow 2.4.0 and
Python 3.7.

The project is exploratory: it confirms that the approach works and identifies the directions of
further work needed to apply it to arbitrary photographs.
