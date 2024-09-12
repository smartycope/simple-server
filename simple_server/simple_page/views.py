from datetime import timedelta
from django.shortcuts import render
from django.urls import reverse
import plotly.express as px
import polars as pl
from django.http import HttpResponse, HttpResponseRedirect
import pyautogui as gui
import subprocess
# import pyvolume
import re
import plotly.graph_objects as go
from metpy.calc import dewpoint_from_relative_humidity, heat_index
from pint import Quantity
from metpy.units import units

output = ''
volume_shift = 10
key_output = ''

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print('Running on IP:', s.getsockname()[0])
s.close()

def index(request):
    context = {'output': output, 'key_output': key_output}
    return render(request, template_name='simple_page/index.html', context=context)

def submit(request):
    global output
    try:
        output = subprocess.check_output(request.POST['msg'].split(' '), text=True)
    except:
        output = 'Command failed'

    return HttpResponseRedirect(reverse('index'))

def playpause(request):
    subprocess.run('playerctl play-pause'.split(' '))
    return HttpResponseRedirect(reverse('index'))

# def change_volume(request, add):
#     current = int(re.search(r'(\d+)%', subprocess.check_output('amixer sget Master'.split(' '), text=True)).group(1))
#     if add > 0:
        # pyvolume.custom(min(max(current + volume_shift, 0), 100))
    # else:
        # pyvolume.custom(min(max(current - volume_shift, 0), 100))
    # return HttpResponseRedirect(reverse('index'))

def key(request):
    global key_output
    key = request.POST['key']
    key_output = ''
    if key in gui.KEY_NAMES:
        gui.press(key)
    elif key == 'help':
        key_output = f"{gui.KEY_NAMES}"
    else:
        gui.write(key)
    return HttpResponseRedirect(reverse('index'))

def arrow(request, key):
    gui.press(key)
    return HttpResponseRedirect(reverse('index'))

def temp_graph(request):
    raw = pl.read_csv('/home/zeke/hello/python/weather_data2.csv')
    data = (raw
        .with_columns(
            time=pl.col('time').str.to_datetime(),
            temp_inside=(pl.col('temp_C_inside') * 1.8) + 32,
            temp_outside=(pl.col('temp_C_outside') * 1.8) + 32,
            # heat_index_inside=pl.struct(["temp_C_inside", "humidity_%_inside"]).apply(lambda x: heat_index(x["temp_C_inside"] * units.degC, x["humidity_%_inside"] * units.percent).m[0]),
            # heat_index_outside=pl.struct(["temp_C_outside", "humidity_%_outside"]).apply(lambda x: heat_index(x["temp_C_outside"] * units.degC, x["humidity_%_outside"] * units.percent).m[0]),
            # dewpoint_inside=pl.struct(["temp_C_inside", "humidity_%_inside"]).apply(lambda x: dewpoint_from_relative_humidity(x["temp_C_inside"] * units.degC, x["humidity_%_inside"] * units.percent).m[0]),
            # dewpoint_outside=pl.struct(["temp_C_outside", "humidity_%_outside"]).apply(lambda x: dewpoint_from_relative_humidity(x["temp_C_outside"] * units.degC, x["humidity_%_outside"] * units.percent).m[0]),
        )
        .drop('temp_C_inside', 'temp_C_outside')
        .melt('time', variable_name='sensor', value_name='reading')
    )
    print(pl.struct(["temp_C_inside", "humidity_%_inside"]).apply(lambda x: heat_index(x["temp_C_inside"] * units.degC, x["humidity_%_inside"] * units.percent).m[0]))
    print(data)

    # avgs = (raw
    #     .with_columns(
    #         time=pl.col('time').str.to_datetime(),
    #         temp=(pl.col('temp_C') * 1.8) + 32,
    #         minute=pl.col('time').str.to_datetime().dt.minute(),
    #         # hour=pl.col('time').str.to_datetime().dt.hour(),
    #     )
    #     .drop('temp_C', 'time')
    #     .melt('minute', variable_name='sensor', value_name='reading')
    #     .group_by('minute', 'sensor')
    #     .agg(avg_reading=pl.mean('reading'))
    # )

    current = raw[-1]

    fig = px.line(data, x='time', y='reading', facet_row='sensor', color='sensor',
        # trendline="lowess", trendline_options=dict(frac=0.5), range_y=(data['time'].min(), data['time'].max() + timedelta(hours=1)),
        # opacity=.1,
        # trendline="rolling", trendline_options=dict(window=60*30),
        title=f'''Current
            Outside Temperature: {((current['temp_C_outside'] * 1.8)+32).to_list()[0]:.1f}°F            |
            Outside Pressure: {current['pressure_hPa_outside'].to_list()[0]:.1f} hPa                    |
            Outside Humidity: {current["humidity_%_outside"].to_list()[0]:.1f}%                         |
            Inside Temperature: {((current['temp_C_inside'] * 1.8)+32).to_list()[0]:.1f}°F              |
            Inside Humidity: {current["humidity_%_inside"].to_list()[0]:.1f}%
        ''',
    )
    # fig.add_scatter(x=data['time'], y=data['reading'])
    # fig.update_traces(mode = 'lines')
    # fig.add_
    fig.add_hline(72, 1)
    # fig = go.Figure(data=px.line(avgs, x='minute', y='avg_reading', facet_row='sensor', color='sensor',
    #     # trendline="lowess", trendline_options=dict(frac=0.5), range_y=(data['time'].min(), data['time'].max() + timedelta(hours=1)),
    #     title=f'''Current Temperature: {((current['temp_C'] * 1.8)+32).to_list()[0]}°F                |
    #               Pressure: {current['pressure_hPa'].to_list()[0]} hPa                    |
    #               Humidity: {current["humidity_%"].to_list()[0]}%'''
    # ).data + fig.data)
    fig.update_yaxes(matches=None)
    return HttpResponse(fig.to_html())

def temp_graph2(request):
    raw = pl.read_csv('/home/zeke/hello/python/weather_data.csv')
    data = (raw
        .with_columns(
            time=pl.col('time').str.to_datetime(),
            temp=(pl.col('temp_C') * 1.8) + 32,
            minute=pl.col('time').str.to_datetime().dt.minute(),
            # hour=pl.col('time').str.to_datetime().dt.hour(),
        )
        .drop('temp_C', 'time')
        .melt('minute', variable_name='sensor', value_name='reading')
        .group_by('minute', 'sensor')
        .agg(avg_reading=pl.mean('reading'))
    )
    current = raw[-1]
    fig = px.scatter(data, x='minute', y='avg_reading', facet_row='sensor', color='sensor',
        # trendline="lowess", trendline_options=dict(frac=0.5), range_y=(data['time'].min(), data['time'].max() + timedelta(hours=1)),
        title=f'''Current Temperature: {((current['temp_C'] * 1.8)+32).to_list()[0]}°F                |
                  Pressure: {current['pressure_hPa'].to_list()[0]} hPa                    |
                  Humidity: {current["humidity_%"].to_list()[0]}%'''
    )
    fig.add_hline(72, 1)
    fig.update_yaxes(matches=None)
    return HttpResponse(fig.to_html())
