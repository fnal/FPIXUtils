#!/usr/bin/env python
import sys
import glob
import argparse
import math
import shutil
from PIL import Image, ImageFont, ImageDraw

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--files", nargs='+',
                  help="path to an input file")
args = parser.parse_args()

if not args.files:
    print "please specify input file";
    sys.exit(0)

from moduleSummaryPlottingTools import *

gROOT.SetBatch()

# panel=2 => top, panel=1 => bottom
panels = ["NA","Bottom","Top"]

#zRange = ()
zRange = (0,100)

font = ImageFont.truetype('arial.ttf',40)
fontBig = ImageFont.truetype('arial.ttf',120)


# create one png per module for everything found in the input files
for file in args.files:
    dictionary2D = produce2DHistogramDictionary(file, 'pos')
    save2DSummaryPlots(file, dictionary2D, 'pos', zRange, True)

# takes those pngs and arrange them into half disk layouts
# save a png for each half disk surface (11 + 17 modules)

inputFiles = []
hcList = []
for file in args.files:
    fileList = [path for path in glob.glob(file.split(".root")[0]+"*/*png")]
    inputFiles.extend(fileList)

    module = os.path.basename(path)
    hc = module.split("_")[1]
    if hc not in hcList:
        hcList.append(hc)

REBIN = 10

template = Image.open(inputFiles[0])
width, height = template.size
template.thumbnail((width/REBIN,height/REBIN),Image.ANTIALIAS)
width, height = template.size

nMods = [0,11,17]
radii = [0,1.3,2.4]

total_width = int(2*radii[-1]*width + width)
total_height = int(height/2. + radii[-1]*width + width/2.)

image_width = total_width + width # extra room for labels
image_height = total_height + width # extra room for labels

for hc in hcList:
    for disk in range(1,4):
        for panel in range(1,3):
            inputs = [input for input in inputFiles if "_"+hc+"_D"+str(disk)+"_" in input if "_PNL"+str(panel) in input]

            halfDiskImage = Image.new('RGBA', (image_width, image_height), color=(255,255,255,0))

            for input in inputs:
                module = os.path.basename(input)

                image_raw = Image.open(input)
                image_raw.thumbnail((width,height),Image.ANTIALIAS)
                image_2 = image_raw.convert('RGBA')
                image = image_2.rotate(180)

                splitInfo = module[:-4].split("_")
                blade = int(splitInfo[3][3:])
                ring = int(splitInfo[5][-1])

                x_i = total_width/2. - width/2. - radii[ring]*width + width/2.
                y_i = image_height - height - width/2.

                # rotate such that the modules span 180 degrees
                angle = -180./(nMods[ring]-1)*(blade-1)
                angle_rad = math.radians(angle)
                rotated_im = image.rotate(angle,expand=1)
                # rotating changes center position of the image
                # these values shift the image back
                x_reset = (width - rotated_im.size[0])/2.
                y_reset = (height - rotated_im.size[1])/2.
                # these move the image to its position in the half-circle
                x_offset = radii[ring]*width*(1-math.cos(angle_rad))
                y_offset = radii[ring]*width*math.sin(angle_rad)

                # final position for this image
                x_f = int(x_i + x_reset + x_offset)
                y_f = int(y_i + y_reset + y_offset)
                halfDiskImage.paste(rotated_im, (x_f, y_f), rotated_im)


            # draw labels on image
            draw = ImageDraw.Draw(halfDiskImage)

            # inner disk labels
            for blade in range(1,nMods[1]+1):
                text = str(blade)+panels[panel][0]

                angle = -180./(nMods[1]-1)*(blade-1)
                angle_rad = math.radians(angle)

                x_i = image_width/2. - (radii[1]-0.5)*width
                y_i = image_height - height*0.75 - width/2.

                x_offset = (radii[1]-0.6)*width*(1-math.cos(angle_rad))
                y_offset = (radii[1]-0.6)*width*math.sin(angle_rad)
                draw.text((x_i + x_offset,y_i + y_offset), text, (0,0,0), font=font)

            # outer disk labels
            for blade in range(1,nMods[2]+1):
                text = str(blade)+panels[panel][0]

                angle = -180./(nMods[2]-1)*(blade-1)
                angle_rad = math.radians(angle)

                x_i = image_width/2. - (radii[2]+0.7)*width
                y_i = image_height - height*0.75 - width/2.

                x_offset = (radii[2]+0.6)*width*(1-math.cos(angle_rad))
                y_offset = (radii[2]+0.6)*width*math.sin(angle_rad)
                draw.text((x_i + x_offset,y_i + y_offset), text, (0,0,0), font=font)

            # half cylinder/disk labels
            draw.text((height,height), hc, (0,0,0), font=fontBig)
            draw.text((image_width - 1.25*width,height), "Disk "+str(disk), (0,0,0), font=fontBig)

            # save final image
            outputFileName = hc+"_Disk"+str(disk)+"_"+panels[panel]+".png"
            halfDiskImage.save(outputFileName,quality=85,optimize=True)


for file in args.files:
    dir = file.split(".root")[0]+"_2DModuleSummaryPlots/"
    shutil.rmtree(dir)

