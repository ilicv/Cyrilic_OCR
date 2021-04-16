import cv2
from scipy import ndimage

image = cv2.imread('scan\\Dubrovnik0018_crop.tif')


#rotation angle in degree
#rotated = ndimage.rotate(image, 1,  cval=0)
rotated_p1 = ndimage.rotate(image, 0.1,  cval=255)
rotated_p3 = ndimage.rotate(image, 0.3,  cval=255)
rotated_n1 = ndimage.rotate(image, -0.1,  cval=255)
rotated_n3 = ndimage.rotate(image, -0.3,  cval=255)

cv2.imwrite('scan\\Dubrovnik0018_crop_rp01.tif', rotated_p1)
cv2.imwrite('scan\\Dubrovnik0018_crop_rp03.tif', rotated_p3)
cv2.imwrite('scan\\Dubrovnik0018_crop_rn01.tif', rotated_n1)
cv2.imwrite('scan\\Dubrovnik0018_crop_rn03.tif', rotated_n3)

