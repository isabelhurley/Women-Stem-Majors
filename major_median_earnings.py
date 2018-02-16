import math
from functools import partial
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Select
from bokeh.models import NumeralTickFormatter
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, layout, widgetbox, row
import pandas


def setup_datasource(url):
    data_frame = pandas.read_csv(url)
    data_frame = data_frame.fillna(0.5)  # this is what notes/assumptions refers to
    data_source = ColumnDataSource(data_frame)
    source = preprocess_datasource(data_source)
    print(source)
    return data_frame, ColumnDataSource(source)


def preprocess_datasource(source):  #CDS
    new_source = dict()
    new_source['x_top'] = list(source.data['Rank'])
    new_source['y_top'] = list(source.data['Median'])
    new_source['x_bottom'] = list(source.data['Rank'])
    new_source['y_bottom'] = list(source.data['ShareWomen'])
    new_source['Rank'] = list(source.data['Rank'])
    new_source['Median'] = list(source.data['Median'])
    new_source['ShareWomen'] = list(source.data['ShareWomen'])

    rank_share_tuples = []
    rank_median_tuples = []

    for index, share in enumerate(source.data['ShareWomen']):
        y = share if not math.isnan(share) else ""  # TODO downstream effects?
        rank_share_tuples.append((source.data['Rank'][index], y))

    rank_share_tuples = sorted(rank_share_tuples, key=lambda x: x[1])
    rank_by_share_women = [x[0] for x in rank_share_tuples]
    share_women_sorted = [y[1] for y in rank_share_tuples]
    for index, median in enumerate(source.data['Median']):
        rank_median_tuples.append((rank_by_share_women[index], median))

    rank_median_tuples = sorted(rank_median_tuples, key=lambda x: x[0])
    medians_by_share_women = [y[1] for y in rank_median_tuples]
    new_source['rank_by_share_women'] = rank_by_share_women # just for lower plot's x
    new_source['medians_by_share_women'] = medians_by_share_women
    new_source['share_women_sorted'] = share_women_sorted

    return new_source


def simple_bargraph(source):
    p = figure(plot_width=2000, plot_height=600, title='Median Income by Major')
    p.vbar(source=source, x='x_top', width=0.5, bottom=0,
           top='y_top', color="firebrick")
    p.yaxis.formatter = NumeralTickFormatter(format="0a")
    p.xaxis.axis_label = 'Major ranked by median income'

    return p


def share_women_by_rank(source, bargraph):
    p = figure(x_range=bargraph.x_range, plot_width=200, plot_height=200, title='Women as Share of Major')
    p.vbar(source=source, x='x_bottom', width=0.5, bottom=0, top='y_bottom', color='blue')
    p.yaxis.formatter = NumeralTickFormatter(format="0%")
    p.xaxis.axis_label = 'Major ranked by median income'

    return p


def sort_selection_bar():
    select = Select(title='Sort by:', value='Median Income (High to Low)', options=['Median Income (High to Low)', 'Share of Women (Low to High)'])

    return select


def reorder_plots(attr, old, new, select, source):
    print("source col names")
    print(source.column_names)
    new_source = source.data.copy()
    # print('share women pre-reset')
    # print(source.data['ShareWomen'])
    # already wrong by here
    if select.value == select.options[1]: # share women
        new_source['y_bottom'] = source.data['share_women_sorted']
        new_source['x_top'] = source.data['rank_by_share_women']
        new_source['y_top'] = source.data['medians_by_share_women']

    elif select.value == select.options[0]: # rank by income
        new_source['x_top'] = source.data['Rank']
        new_source['y_top'] = source.data['Median']
        new_source['x_bottom'] = source.data['Rank']
        new_source['y_bottom'] = source.data['ShareWomen']

    source.data = new_source

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
    df, source = setup_datasource(data_url)

    bargraph = simple_bargraph(source)

    select = sort_selection_bar()
    select.on_change('value', partial(reorder_plots, select=select, source=source))

    curdoc().add_root(set_layout(select, bargraph, share_women_by_rank(source, bargraph)))


main()


#TODO sort by share women, update labels
# regressions?
#stem or not
#show 50% clearly