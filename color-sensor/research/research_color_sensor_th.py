# カラーセンサの閾値を調べる
import sys
from pathlib import Path
sys.path.append(
    str(Path(__file__).parent.parent)
)

import time
from smbus2 import SMBus
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

from color_sensor import ColorSensor

FREQ=8 #Hz

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--loop_num",default=100)
    parser.add_argument("--case")
    args=parser.parse_args()

    result_dir=Path(__file__).parent/f"case_{args.case}"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    
    cs=ColorSensor(
        is_switch=False,sensor_addr=0x2a
    )


    rgbi_trj=[]
    plot_data=[]
    band_data=[]
    for i in range(int(args.loop_num)):

        try:
            data=cs.read()
            print(f"idx:{i}",data)

            rgbi_trj.append(
                list(data.values())
            )
            plot_data.append( #それまでの平均をとる
                np.mean(rgbi_trj,axis=0)
            )
            band_data.append( #標準偏差を求める
                np.std(rgbi_trj,axis=0)
            )

        except Exception as e:
            print(e)
            break

        time.sleep(1.0/FREQ)


    plot_data = np.array(plot_data)
    band_data=np.array(band_data)
    time_axis = np.arange(len(plot_data))

    # 各属性のデータをプロット
    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, plot_data[:, 0],color="red", label='Red')
    plt.fill_between(
        time_axis,plot_data[:, 0]-band_data[:,0],
        plot_data[:, 0]+band_data[:,0],alpha=0.5,color="red",
    )
    plt.plot(time_axis, plot_data[:, 1], label='Green',color="green")
    plt.fill_between(
        time_axis,plot_data[:, 1]-band_data[:,1],
        plot_data[:, 1]+band_data[:,1],alpha=0.5,color="green",
    )
    plt.plot(time_axis, plot_data[:, 2], label='Blue',color="blue")
    plt.fill_between(
        time_axis,plot_data[:, 2]-band_data[:,2],
        plot_data[:, 2]+band_data[:,2],alpha=0.5,color="blue",
    )
    plt.plot(time_axis, plot_data[:, 3], label='Infrared',color="orange")
    plt.fill_between(
        time_axis,plot_data[:, 3]-band_data[:,3],
        plot_data[:, 3]+band_data[:,3],alpha=0.5,color="orange",
    )
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Color Sensor Data')
    plt.legend()
    plt.grid(True)
    plt.savefig(
        result_dir/f"fig_{args.case}.png"
    )

    #データ保存
    data_db=pd.DataFrame(
        plot_data,columns=["red","green","blue","infrated"]
    )
    data_db.to_csv(result_dir/f"mean_{args.case}.csv")

    std_db=pd.DataFrame(
        band_data,columns=["red","green","blue","infrated"]
    )
    std_db.to_csv(result_dir/f"std_{args.case}.csv")


if __name__=="__main__":
    main()
