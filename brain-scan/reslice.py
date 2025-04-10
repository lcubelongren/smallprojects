import pydicom
import numpy as np
import matplotlib.pyplot as plt
import sys
import glob

import dicom2nifti


# load the DICOM files
files = []
print('glob: {}'.format(sys.argv[1]))
for fname in glob.glob(sys.argv[1], recursive=False):
    print("loading: {}".format(fname))
    files.append(pydicom.dcmread(fname))

print("file count: {}".format(len(files)))

# skip files with no SliceLocation (eg scout views)
slices = []
skipcount = 0
for f in files:
    if hasattr(f, 'SliceLocation'):
        slices.append(f)
    else:
        skipcount = skipcount + 1

print("skipped, no SliceLocation: {}".format(skipcount))

# ensure they are in the correct order
slices = sorted(slices, key=lambda s: s.SliceLocation)

# pixel aspects, assuming all slices are the same
ps = slices[0].PixelSpacing
ss = slices[0].SliceThickness
ax_aspect = ps[1]/ps[0]
sag_aspect = ps[1]/ss
cor_aspect = ss/ps[0]

# create 3D array
img_shape = list(slices[0].pixel_array.shape)
img_shape.append(len(slices))
img3d = np.zeros(img_shape)
print('volume shape: ', img_shape)

# fill 3D array with the images from the files
for i, s in enumerate(slices):
    img2d = s.pixel_array
    img3d[:, :, i] = img2d

# export as nifti for Brainchop web segmentation
dicom_directory = r'C:\Users\lcube\Desktop\mybrain\ccnb_8850_0001'
dicom2nifti.convert_directory(dicom_directory, output_folder=dicom_directory, compression=False)

# plot 3 orthogonal slices
a1 = plt.subplot(2, 2, 1)
plt.imshow(img3d[:, :, img_shape[2]//2])
a1.set_aspect(ax_aspect)

a2 = plt.subplot(2, 2, 2)
plt.imshow(img3d[:, img_shape[1]//2, :])
a2.set_aspect(sag_aspect)

a3 = plt.subplot(2, 2, 3)
plt.imshow(img3d[img_shape[0]//2, :, :].T)
a3.set_aspect(cor_aspect)

plt.show()

#export plot for display
for i in range(img_shape[2]):
    print('saving slice ', i)
    image = img3d[15:,:140,i]
    vmin = 140
    if vmin > np.max(image):
        vmin = np.max(image)
    plt.imsave('export/brain_img-{}.png'.format(i), image, cmap='gray',
               pil_kwargs={'compress_level': 0}, vmin=vmin)

#example run command:
#python reslice.py .\data\ccnb_8850\8850-0001*.dcm