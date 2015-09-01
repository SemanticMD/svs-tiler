__author__ = 'sb'

import openslide

svs = openslide.OpenSlide('/home/sb/Downloads/TCGA-CS-4941-01Z-00-DX1.86D516B5-C648-4249-8C6A-7F9A6A56CB4F.svs')

roi = svs.read_region((0,199), 2, (25,25))
print('test')