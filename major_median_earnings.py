from functools import partial
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Select
from bokeh.models import NumeralTickFormatter
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, layout, widgetbox, row
import pandas

def setup_datasource(url):
    dataframe = pandas.read_csv(url)
    datasource = ColumnDataSource(dataframe)
    return datasource


def simple_bargraph(source):
    p = figure(plot_width=2000, plot_height=600, title='Median Income by Major')

    p.vbar(source=source, x='Rank', width=0.5, bottom=0,
           top='Median', color="firebrick")
    p.yaxis.formatter = NumeralTickFormatter(format="0a")
    p.xaxis.axis_label = 'Major ranked by median income'
    # return layout(p, sizing_mode='stretch_both')
    return p

def share_women_by_rank(source, bargraph):
    p = figure(x_range=bargraph.x_range, plot_width=200, plot_height=200, title='Women as Share of Major')
    p.vbar(source=source, x='Rank', width=0.5, bottom=0, top='ShareWomen', color='blue')
    p.yaxis.formatter = NumeralTickFormatter(format="0%")
    p.xaxis.axis_label = 'Major ranked by median income'

    return p

def sort_selection_bar():
    select = Select(title='Sort by:', value='Median Income (High to Low)', options=['Median Income (High to Low)', 'Share of Women (Low to High)'])
    return select

def reorder_plots(attr, old, new, select, source):
    share_women_list = source.data['ShareWomen']
    index_tuple_list = []

    print(select.value)


def set_layout(select, primary, secondary):
    return layout([
        [widgetbox(select)],
        [primary],
        [secondary],
        ],
        sizing_mode='stretch_both'
    )

def main():
    data_url = 'https://raw.githubusercontent.com/isabelhurley/data/master/college-majors/recent-grads.csv'
    source = setup_datasource(data_url)
    bargraph = simple_bargraph(source)
    select = sort_selection_bar()
    select.on_change('value', partial(reorder_plots, select=select, source=source))
    curdoc().add_root(set_layout(select, bargraph, share_women_by_rank(source, bargraph)))

main()

#TODO sort by share women
# regressions?
#stem or not
#show 50% clearly