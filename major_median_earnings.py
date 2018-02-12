from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, layout
import pandas

def setup_datasource(url):
    dataframe = pandas.read_csv(url)
    datasource = ColumnDataSource(dataframe)
    return datasource


def simple_bargraph(source):
    p = figure(plot_width=400, plot_height=400)
    p.vbar(x=[1, 2, 3], width=0.5, bottom=0,
           top=[1.2, 2.5, 3.7], color="firebrick")
    return layout(p)


def main():
    data_url = 'https://raw.githubusercontent.com/isabelhurley/data/master/college-majors/recent-grads.csv'
    source = setup_datasource(data_url)
    #print(source.data)
    curdoc().add_root(simple_bargraph(source))

main()
