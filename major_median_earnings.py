from bokeh.models.sources import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, layout, widgetbox
import pandas

def setup_datasource(url):
    dataframe = pandas.read_csv(url)
    datasource = ColumnDataSource(dataframe)
    return datasource


def simple_bargraph(source):
    p = figure(x_range=source.data['Major'], plot_width=2000, plot_height=600, title='Median income by major')

    p.vbar(source=source, x='Major', width=0.5, bottom=0,
           top='Median', color="firebrick")
    p.yaxis.formatter = NumeralTickFormatter(format="0a")
    return layout(p, sizing_mode='stretch_both')


def main():
    data_url = 'https://raw.githubusercontent.com/isabelhurley/data/master/college-majors/recent-grads.csv'
    source = setup_datasource(data_url)
    #print(source.data)
    curdoc().add_root(simple_bargraph(source))

main()
