
import numpy as np
import pandas as pd
import datetime
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation


df_flights = pd.read_csv('df_flights.csv')
flight_numbers = np.unique(df_flights['flight'])

departures = []
for i,(date,time) in enumerate(zip(df_flights['date'], df_flights['time'])):
    if (date >= 20220801) and (date < 20230801):
        if df_flights['flight'][i] in flight_numbers:
            flight_numbers = np.delete(flight_numbers, np.where(flight_numbers == df_flights['flight'][i])[0])
        else:
            continue
        date, time = str(date), str(time)
        while len(time) < 4:
            time = '0' + time
        datetime_str = date + ' ' + time
        departures.append(datetime.datetime.strptime(datetime_str, '%Y%m%d %H%M'))
delta = [(departure - datetime.datetime.strptime('20220801 0000', '%Y%m%d %H%M')).days for departure in departures]
hist_n, _, _ = plt.hist(delta, bins=np.arange(365+1))

spot1_dates = {
'departMcM': '10 Nov 22',
'arrivePole': '09 Dec 22',
'departPole': '16 Dec 22',
'arriveMcM': '30 Dec 22',
}
spot2_dates = {
'departMcM': '29 Nov 22',
'arrivePole': '23 Dec 22',
'departPole': '10 Jan 23',
'arriveMcM': '30 Jan 23',
}
spot3_dates = {
'departMcM': '17 Jan 23',
'arrivePole': '12 Feb 23',
'departPole': '16 Feb 23',
'arriveMcM': '07 Mar 23',
}
spot_dates = [spot1_dates, spot2_dates, spot3_dates]
spot_states = [0, 0, 0]

LMG_dates = {
'LMG22-11 beg': '02 Oct 22',
'LMG22-11 end': '20 Oct 22',
'LMG22-13 beg': '28 Nov 22',
'LMG22-13 end': '17 Dec 22',
'LMG23-01 beg': '23 Dec 22',
'LMG23-01 end': '06 Feb 23',
'LMG23-02 beg': '10 Feb 23',
'LMG23-02 end': '20 Mar 23',
'LMG23-04 beg': '15 Apr 23',
'LMG23-04 end': '02 May 23',
'LMG23-05 beg': '08 May 23',
'LMG23-05 end': '27 Jun 23',
'LMG23-06 beg': '01 Jul 23',
'LMG23-06 end': '08 Aug 23',
}
NBP_dates = {
'NBP22-11 beg': '08 Nov 22',
'NBP22-11 end': '09 Dec 22',
'NBP23-01 beg': '26 Dec 22',
'NBP23-01 end': '15 Jan 23',
'NBP23-02 beg': '18 Jan 23',
'NBP23-02 end': '28 Feb 23',
'NBP23-03 beg': '26 Mar 23',
'NBP23-03 end': '05 May 23',
'NBP23-04 beg': '06 May 23',
'NBP23-04 end': '29 May 23',
'NBP23-05 beg': '02 Jun 23',
'NBP23-05 end': '28 Jun 23',
}
vessel_dates = [LMG_dates, NBP_dates]
LMG_strings = ['LMG', '', '', '', '', '', '']
NBP_strings = ['NBP', '', '', '', '', '']
vessel_strings = [LMG_strings, NBP_strings]
vessel_states = [np.zeros(len(LMG_strings), dtype=int), np.zeros(len(NBP_strings), dtype=int)]


def animate(i):
    print(i)
    
    rects[i].set_height(hist_n[i])
    if i:
        vline.set_data([i, i], [0, 100])
    if i >= len(hist_n) - 1:
        vline.set_data([], [])
        
    current_day = datetime.datetime.strptime('20220801 0000', '%Y%m%d %H%M') + datetime.timedelta(days=int(i))
    
    for j,sann in enumerate(s_annotations):
        if spot_states[j] < 4:
            target_day = datetime.datetime.strptime(list(spot_dates[j].values())[spot_states[j]], '%d %b %y')
            spacing = 16 + (j+1)*1.5
            if current_day == target_day:
                print('adding SPOT {} point'.format(j+1))
                if spot_states[j] == 0:
                    sann.set_position((i-5, spacing))
                    sann.xy = (i, spacing)
                spot_states[j] += 1
            if 0 < spot_states[j] < 4:
                sann.xy = (i, spacing)
                
    for k in range(len(vessel_states)):
        for j,(vann,vtext) in enumerate(zip(v_annotations[k], v_text[k])):
            if vessel_states[k][j] < 2:
                date_idx = vessel_states[k][j] + j*2
                target_day = datetime.datetime.strptime(list(vessel_dates[k].values())[date_idx], '%d %b %y')
                spacing = 12.5 + (k+1)*1.5
                if current_day == target_day:
                    print('adding vessel {} point'.format(k+1))
                    if vessel_states[k][j] == 0:
                        vann.set_text(vessel_strings[k][j])
                        vann.set_position((i-5, spacing))
                        vtext.set_text(str(j+1))
                        vtext.set_position((i-2.5, spacing+0.25))
                    vessel_states[k][j] += 1
                if vessel_states[k][j] > 0:
                    vann.xy = (i, spacing)
                    
    return rects, vline, s_annotations, v_annotations, v_text
    
month_list = [datetime_str.strftime('%b') for datetime_str in pd.period_range(start='2022-08-01', end='2023-07-31', freq='m')]
  
fig, ax = plt.subplots(1, 1, figsize=(4.20, 2.61), dpi=500)  # (840, 522) px^2
fig.subplots_adjust(left=0.08, right=0.98, bottom=0.10, top=0.50) 
ax.set_xticks(np.linspace(1, 365, 13), np.append(month_list, ''), ha='left', fontsize='small')

rects = ax.bar(np.arange(len(hist_n)), np.zeros(len(hist_n)), width=0.9, color='k')
vline, = ax.plot([], [], c='k', ls='--', lw=1)
ax.spines[['right', 'top']].set_visible(False)
ax.set_ylim([0, 10.5])
ax.set_xlim([1, 365])
ax.set_title('flight #', loc='left', fontsize='small').set_position((-0.07, 0))
ax.set_yticks([0, 5, 10], [0, 5, 10], fontsize='small')

s_annotations = [ax.annotate('SPOT {}'.format(i+1), xy=(-10, -10), xytext=(-10, -10), fontsize='small',
                             xycoords='data', textcoords='data', annotation_clip=False, va='center', ha='right',
                             arrowprops=dict(arrowstyle='-', fc='k', lw=2, ls='-')) for i in range(len(spot_dates))]
                             
v_annotations = [[ax.annotate('', xy=(-10, -10), xytext=(-10, -10), fontsize='small',
                      xycoords='data', textcoords='data', annotation_clip=False, va='center', ha='right',
                      arrowprops=dict(arrowstyle='-', lw=1, ls=(0, (0.5, 2.0)))) for _ in range(len(vessel_strings[0]))],
                [ax.annotate('', xy=(-10, -10), xytext=(-10, -10), fontsize='small',
                      xycoords='data', textcoords='data', annotation_clip=False, va='center', ha='right',
                      arrowprops=dict(arrowstyle='-', lw=1, ls=(0, (0.5, 2.0)))) for _ in range(len(vessel_strings[1]))]]
v_text = [[ax.text(-10, -10, '', fontsize='x-small') for _ in range(len(vessel_strings[0]))],
          [ax.text(-10, -10, '', fontsize='x-small') for _ in range(len(vessel_strings[1]))]]
                      
ax.annotate('traverse', xy=(30, 19), xytext=(20, 19), annotation_clip=False, 
            arrowprops=dict(arrowstyle='-[', mutation_aspect=1.5), va='center', ha='right', fontsize='small')
ax.annotate('vessels', xy=(25, 14.75), xytext=(15, 14.75), annotation_clip=False,
            arrowprops=dict(arrowstyle='-['), va='center', ha='right', fontsize='small')

plt.savefig('histogram_still_start.png', transparent=False); print('saved still')

frames = 365
ani = animation.FuncAnimation(fig, animate, frames=frames, repeat=False, interval=2000)  # 12fps
#plt.show()

print('saving animation...');  ani.save('histogram.mp4')

fig.savefig('histogram_still_end.png', transparent=False); print('saved still')