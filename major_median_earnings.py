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
    p = figure(x_range=source.data['Major'], plot_width=2000, plot_height=600, title='Median Income by Major')

    p.vbar(source=source, x='Major', width=0.5, bottom=0,
           top='Median', color="firebrick")
    p.yaxis.formatter = NumeralTickFormatter(format="0a")
    # return layout(p, sizing_mode='stretch_both')
    return p

def share_women_by_rank(source, bargraph):
    p = figure(x_range=bargraph.x_range, plot_width=200, plot_height=200, title='Women as Share of Major')
    p.vbar(source=source, x='Major', width=0.5, bottom=0, top='ShareWomen', color='blue')
    p.yaxis.formatter = NumeralTickFormatter(format="0%")

    return p

def set_layout(primary, secondary):
    return layout(primary, secondary, sizing_mode='stretch_both')

def main():
    data_url = 'https://raw.githubusercontent.com/isabelhurley/data/master/college-majors/recent-grads.csv'
    source = setup_datasource(data_url)
    bargraph = simple_bargraph(source)
    curdoc().add_root(set_layout(bargraph, share_women_by_rank(source, bargraph)))

main()

#TODO sort by share women
# regressions?
#stem or not
#show 50% clearly