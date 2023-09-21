import pandas as pd
import plotly.express as px


DEFAULT_MARGIN = dict(t=10, l=0, r=0, b=0)

def draw_line(data: pd.DataFrame, margin: dict=DEFAULT_MARGIN, **kwargs):
    fig = px.line(data, **kwargs)
    fig.update_layout(
        margin=margin,
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=False, title=None),
        plot_bgcolor='white',
        showlegend=False,
    )
    fig.update_traces(
        line=dict(color='blue'),
    )
    return fig

def draw_stock_chart(close: pd.Series, average_price: float,
                     margin: dict=DEFAULT_MARGIN, **kwargs):
    fig = px.line(close, **kwargs)
    fig.update_layout(
        margin=margin,
        xaxis=dict(title=None),
        yaxis=dict(title=None),
        showlegend=False,
        shapes=[
            dict(
                line=dict(color='gray'),
                x0=0,
                x1=1,
                y0=average_price,
                y1=average_price,
                xref='paper',
                yref='y',
                line_width=1,
            )
        ],
        annotations=[
            dict(
                x=0.01,
                y=average_price,
                xref='paper',
                yref='y',
                showarrow=False,
                yanchor='bottom',
                text='Average Price Paid',
                font=dict(color='gray')
            )
        ],
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label='1m', step='month', stepmode='backward'),
                dict(count=6, label='6m', step='month', stepmode='backward'),
                dict(count=1, label='YTD', step='year', stepmode='todate'),
                dict(count=1, label='1y', step='year', stepmode='backward'),
                dict(step='all')
            ])
        )
    )
    return fig

def draw_pie(data: pd.DataFrame, margin: dict=DEFAULT_MARGIN, **kwargs):
    fig = px.pie(data, **kwargs)
    fig.update_layout(
        margin=margin,
    )
    return fig

def draw_treemap(data: pd.DataFrame, treemap_name: str,
                 section: tuple, label: str, hover_text: str,
                 margin: dict=DEFAULT_MARGIN, **kwargs):
    fig = px.treemap(data, path=[px.Constant(treemap_name), *section], **kwargs)
    fig.update_traces(dict(
        texttemplate=label,
        hovertemplate=hover_text,
        textposition='middle center',
        insidetextfont=dict(family=('Trebuchet MS', 'Arial'), size=20),
    ))
    fig.update_layout(
        margin=margin,
        coloraxis=dict(showscale=False),
    )
    return fig
