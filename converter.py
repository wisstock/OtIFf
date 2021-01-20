#!/usr/bin/env python3

""" Copyright © 2021 Borys Olifirov

OIF - tiff converter.
Require oiffile lib.

"""

import sys
import os
import logging
import numpy as np
from skimage.external.tifffile import imsave
import oiffile as oif


class OIFmetha(oif.OifFile):
    """ Inheritance and extension of the functionality
    of the OIFfile class.
    Methods for extracting file metadata.

    """
    @property
    def geometry(self):
        """Return linear size in um from mainfile"""
        size = {
            self.mainfile[f'Axis {i} Parameters Common']['AxisCode']:
            float(self.mainfile[f'Axis {i} Parameters Common']['EndPosition'])
            for i in [0, 1]
        }
        size['Z'] = float(self.mainfile['Axis 3 Parameters Common']['Interval']*self.mainfile['Axis 3 Parameters Common']['MaxSize'] / 1000)

        return tuple(size[ax] for ax in ['X', 'Y', 'Z'])

    @property
    def px_size(self):
        """Return linear px size in nm from mainfile"""
        size = {
            self.mainfile[f'Axis {i} Parameters Common']['AxisCode']:
            float(self.mainfile[f'Axis {i} Parameters Common']['EndPosition'] / self.mainfile[f'Axis {i} Parameters Common']['MaxSize'] * 1000)
            for i in [0, 1]     
        }
        size['Z'] = float(self.mainfile['Axis 3 Parameters Common']['Interval'] / 1000)

        return tuple(size[ax] for ax in ['X', 'Y', 'Z'])

    @property
    def lasers(self):
        """Return active lasers and theyir transmissivity lyst from mainfile"""
        laser = {
            self.mainfile[f'Laser {i} Parameters']['LaserWavelength']:
            int(self.mainfile[f'Laser {i} Parameters']['LaserTransmissivity']/10)
            for i in range(5) 
        }
        laser_enable = [self.mainfile[f'Laser {i} Parameters']['LaserWavelength']
                        for i in range(5)
                        if self.mainfile[f'Laser {i} Parameters']['Laser Enable'] == 1]


        return tuple([i, laser[i]] for i in laser.keys() if i in laser_enable)

    @property
    def channels(self):
        """Return list of active channel (return laser WL and intensity) from minefile"""
        active_ch = [self.mainfile[f'GUI Channel {i} Parameters']['ExcitationWavelength']
                     for i in range(1, 4)
                     if self.mainfile[f'GUI Channel {i} Parameters']['CH Activate'] == 1]
        laser = {
            self.mainfile[f'GUI Channel {i} Parameters']['ExcitationWavelength']:
            int(self.mainfile[f'GUI Channel {i} Parameters']['LaserNDLevel']/10)
            for i in range(1, 4)
        }

        return tuple([ch, laser[ch]] for ch in active_ch)

input_path = os.path.join(sys.path[0], 'input')
output_path = os.path.join(sys.path[0], 'output')
if not os.path.exists(output_path):
    os.makedirs(output_path)
ex_list = ['da', 'd', 'a']
fluo_list = ['tfp', 'yfp']
oifs = {}
for root, dirs, files in os.walk(input_path):  # loop over OIF files
        for file in files:
        	name, ext = file.split('.')[0], file.split('.')[1]
        	if ext == 'oif':
        		oif_path = os.path.join(root, file)
        		oifs.update({name:oif.OibImread(oif_path)})

[[imsave(f'{output_path}/{cell}_{fluo_list[i]}_{ex_list[j]}.tiff', oifs.get(cell)[i,:,j,:,:])
   for i in range(np.shape(oifs.get(cell))[0])
   for j in range(np.shape(oifs.get(cell))[2])]
 for cell in list(oifs.keys())]