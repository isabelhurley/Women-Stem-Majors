import math
from os.path import dirname, join
from Major_info import MajorInfo
from functools import partial
from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Select
from bokeh.models import NumeralTickFormatter, Div, HoverTool
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, layout, widgetbox, row
import pandas


def setup_datasource(url):
    data_frame = pandas.read_csv(url)
    data_frame = data_frame.fillna(0.5)  # this is what notes/assumptions refers to
    data_source = ColumnDataSource(data_frame)
    source = preprocess_datasource(data_source)
    return data_frame, ColumnDataSource(source)


# add columns to datasource to reorder plots by share of women in major
def preprocess_datasource(source):  # CDS
    new_source = dict()
    new_source['x_top'] = list(source.data['Rank'])
    new_source['y_top'] = list(source.data['Median'])
    new_source['x_bottom'] = list(source.data['Rank'])
    new_source['y_bottom'] = list(source.data['ShareWomen'])
    new_source['Rank'] = list(source.data['Rank'])
    new_source['Median'] = list(source.data['Median'])
    new_source['ShareWomen'] = list(source.data['ShareWomen'])
    new_source['Major'] = list(source.data['Major'])
    new_source['Major_category'] = list(source.data['Major_category'])
    new_source['Total'] = list(source.data['Total'])
    new_source['Sample_size'] = list(source.data['Sample_size'])

    rank_share_tuples = []
    rank_median_tuples = []

    for index, share in enumerate(source.data['ShareWomen']):
        y = share if not math.isnan(share) else ""  # shouldn't be necessary after data_frame.fillna(.5)
        rank_share_tuples.append((source.data['Rank'][index], y))

    rank_share_tuples = sorted(rank_share_tuples, key=lambda x: x[1])
    rank_by_share_women = [x[0] for x in rank_share_tuples]
    share_women_sorted = [y[1] for y in rank_share_tuples]
    for index, median in enumerate(source.data['Median']):
        rank_median_tuples.append((rank_by_share_women[index], median))

    rank_median_tuples = sorted(rank_median_tuples, key=lambda x: x[0])
    medians_by_share_women = [y[1] for y in rank_median_tuples]
    new_source['rank_by_share_women'] = rank_by_share_women
    new_source['medians_by_share_women'] = medians_by_share_women
    new_source['share_women_sorted'] = share_women_sorted
    new_source['major_by_share_women'] = []
    new_source['category_by_share_women'] = []
    new_source['total_by_share_women'] = []
    new_source['sample_size_by_share_women'] = []


    major_data_objects = []
    for row, median in source.data['Median']:
        major_data_objects.append(MajorInfo(source.data['Major'][row], source.data['Major_category'][row],
                                            source.data['Major'][row], )


    return new_source


def set_hover_tool():
    return HoverTool(tooltips=[
        ("Major", "@Major"),
        ("Category", "@Major_category"),
        ("Percent Women", "@y_bottom{0%}"),
        ("Median Income", "@y_top{$0a}"),
        ("Grads with Major", "@Total"),
        ("Sample Size for Income", "@Sample_size")
    ])


# format Median income bargraph
def simple_bargraph(source, hover):

    p = figure(plot_width=2000, plot_height=600, title='Median Income by Major', tools=[hover])
    p.vbar(source=source, x='x_top', width=0.5, bottom=0,
           top='y_top', color="firebrick")
    p.yaxis.formatter = NumeralTickFormatter(format="0a")
    p.xaxis.axis_label = 'Major ranked by median income (high to low)'

    return p


# format women as share bargraph
def share_women_by_rank(source, bargraph, hover):

    p = figure(x_range=bargraph.x_range, plot_width=200, plot_height=200, title='Women as Share of Major', tools=[hover])
    p.vbar(source=source, x='x_bottom', width=0.5, bottom=0, top='y_bottom', color='blue')
    p.yaxis.formatter = NumeralTickFormatter(format="0%")
    p.xaxis.axis_label = 'Major ranked by median income (high to low)'

    return p


def sort_selection_bar():
    select = Select(title='Sort by:', value='Median Income (High to Low)', options=['Median Income (High to Low)', 'Share of Women (Low to High)'])

    return select


# callback function for select bar selection change
def reorder_plots(attr, old, new, select, source, median_plot, women_plot):
    new_source = source.data.copy()

    if select.value == select.options[1]:  # rank by share women
        new_source['y_bottom'] = source.data['share_women_sorted']
        # print("y bottom")
        # print(new_source['y_bottom'])
        new_source['x_top'] = source.data['rank_by_share_women']
        # print("x top")
        # print(new_source['x_top'])
        new_source['y_top'] = source.data['medians_by_share_women']
        # print("y top")
        # print(new_source['y_top'])
        median_plot.xaxis.axis_label = "Major ranked by share of women (low to high)"
        women_plot.xaxis.axis_label = "Major ranked by share of women (low to high)"

    elif select.value == select.options[0]:  # rank by income
        new_source['x_top'] = source.data['Rank']
        new_source['y_top'] = source.data['Median']
        new_source['x_bottom'] = source.data['Rank']
        new_source['y_bottom'] = source.data['ShareWomen']
        median_plot.xaxis.axis_label = "Major ranked by median income (high to low)"
        women_plot.xaxis.axis_label = "Major ranked by median income (high to low)"

    source.data = new_source


def set_layout(select, primary, secondary):
    desc = Div(text=open(join(dirname(__file__), "webpage/description.html")).read())

    return layout([
        [desc],
        [widgetbox(select)],
        [primary],
        [secondary],
        ],
        sizing_mode='stretch_both'
    )


def main():
    data_url = 'https://raw.githubusercontent.com/isabelhurley/data/master/college-majors/recent-grads.csv'
    df, source = setup_datasource(data_url)

    hover = set_hover_tool()
    median_bargraph = simple_bargraph(source, hover)
    women_bargraph = share_women_by_rank(source, median_bargraph, hover)
    # median_bargraph = simple_bargraph(source)
    # women_bargraph = share_women_by_rank(source, median_bargraph)
    select = sort_selection_bar()
    select.on_change('value', partial(reorder_plots, select=select, source=source, median_plot=median_bargraph, women_plot=women_bargraph))

    curdoc().add_root(set_layout(select, median_bargraph, women_bargraph))
    curdoc().title = "Median-Income"


main()


#TODO update labels
# Ideas to extend app:
# title, hover tool
# regressions?
# stem vs humanities
# show 50% mark clearly
# within nursing income distribution?
# changes in median income/share women over time?