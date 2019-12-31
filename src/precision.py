# Performs measurements for VL53L0X precision analysis

import sys
import time

import board
import busio

import adafruit_vl53l0x

# Initialize I2C bus and sensor.
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

def write_results(results, file_name = ''):
    if file_name == '':
        file_name = sys.stdout.fileno()
    with open(file_name, 'w') as file: 
        distances = [d for d in results]
        distances.sort()
        budgets = [b for b in results[distances[0]]]
        budgets.sort()
        n_measurements = len(results[distances[0]][budgets[0]])
        for b in budgets:
            file.write('Budget (ns):\t{}\n'.format(b))
            file.write('Distance (mm):\t{}\n'.format('\t'.join([str(dist) for dist in distances])))
            for n in range(n_measurements):
                values = [str(results[d][b][n]) for d in distances]
                file.write('\t{}\n'.format('\t'.join(values)))

# Optionally adjust the measurement timing budget to change speed and accuracy.
# See the example here for more details:
#   https://github.com/pololu/vl53l0x-arduino/blob/master/examples/Single/Single.ino
# For example a higher speed but less accurate timing budget of 20ms:
#vl53.measurement_timing_budget = 20000
# Or a slower but more accurate timing budget of 200ms:
#vl53.measurement_timing_budget = 200000
# The default timing budget is 33ms, a good compromise of speed and accuracy.

def measure():
    distances = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    timing_budgets = [30000.0, 50000.0, 100000.0, 150000.0, 200000.0, 250000.0, 300000.0]
    n_measurements = 5

    results = {d: {t: [None] * n_measurements for t in timing_budgets} for d in distances}

    print('Starting measurements')

    for d in distances:
        print('Measurements for {}mm. Press any key when ready.'.format(d))
        input()
        for t in timing_budgets:
            print('Timing budget: {}ns ({}ms)'.format(t, t // 1000))
            vl53.measurement_timing_budget = t
            for n in range(n_measurements):
                measured = vl53.range
                print('Measurement {}: {}mm'.format(n+1, measured))
                results[d][t][n] = measured
    print('Done')
    return results

if __name__ == '__main__':
    results = measure()
    write_results(results, 'res.txt')
    exit()
