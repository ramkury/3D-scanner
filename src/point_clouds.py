# Visualizes data collected by the script 'scan3d.py'
# and converts it into python 

import matplotlib.pyplot as plt
from random import randrange as rr
from sys import argv
import pickle
from math import sin, cos, pi
import open3d as o3d
import numpy as np
import time

BASELINE = 110
Y_FACTOR = 120 / 2400

def convert_point(point):
    range = point['Range']
    angle = point['Angle'] * pi / 180
    height = point['Height']
    radius = BASELINE - range
    x = radius * sin(angle)
    y = height * Y_FACTOR
    z = radius * cos(angle)
    return (x, y, z)

def create_point_cloud(points):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    return pcd

def plot(pcd):
    o3d.visualization.draw_geometries([pcd], width=600, height=600)

def main():
    if len(argv) < 2:
        exit('Run this script with the following command line: "python3 point_clouds.py file_name.pkl"')
    start = time.time()
    data = None
    with open(argv[1], 'rb') as file:
        data = [d for d in pickle.load(file) if d['Range'] < 150]

    points = [convert_point(p) for p in data] # Converts points to cartesian coordinate system
    print('{} points'.format(len(points)))
    pcd = create_point_cloud(points)
    plot(pcd)

    pcd_filename = argv[1].replace('.pkl', '.pcd')
    print('Writing data to PCD file {}'.format(pcd_filename))
    o3d.io.write_point_cloud(pcd_filename, pcd, write_ascii=True)
    end = time.time()
    print('Done! Run time: {} seconds'.format(end - start))

if __name__ == '__main__':
    main()