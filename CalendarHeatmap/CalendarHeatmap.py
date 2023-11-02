import pandas as pd
import plotly.graph_objs as go

from typing import Tuple, List

class CalendarHeatmap:

    def __init__(
        self,
        data,
        *,
        date_col:str,
        value_col:str,
        language:bool=True
    ):
        """
        Parameters: data : pandas.DataFrame
        
                    {date, value}_col : columns name in data
                                         Variables that specify column name on the date and value.

                    language : bool Default True
                               language choice to write a month and week name.
                               True is Korean
                               False is Englishd
        """
        
        # Instanc Variables
        self.date_col = date_col
        self.value_col = value_col
        self.use_ohter_trace = False

        # Data Preprocessing
        self.data = self.__preprocessing(data)
        
        # Month Position Line setting
        month = self.data[date_col].dt.to_period('M').unique().days_in_month
        month_positions = (month.cumsum() - 15) / 7
        
        # month and week names setting
        if language:
            month_names = [f'{i}월' for i in range(1, 13)]
            week_names = ['월', '화', '수', '목', '금', '토', '일']
        else:
            month_names = [
                'Jan', 'Feb', 'Mar', 'Apr',
                'May', 'Jun', 'Jul', 'Aug',
                'Sep', 'Oct', 'Nov', 'Dec'
            ]
            week_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # layout setting
        self.layout = go.Layout(
            height=250,
            yaxis=dict(
                showline=False, showgrid=False, zeroline=False,
                tickmode='array',
                ticktext=week_names,
                tickvals=[0, 1, 2, 3, 4, 5, 6],
                autorange="reversed",
                tickfont=dict(size=12, color='#9e9e9e'),
            ),
            xaxis=dict(
                showline=False, showgrid=False, zeroline=False,
                tickmode='array',
                ticktext=month_names,
                tickvals=month_positions,
                tickfont=dict(size=14, color='#9e9e9e'),
            ),
            plot_bgcolor=('#fff'),
            margin=dict(t=40),
            showlegend=False,
        )

    def __preprocessing(
        self,
        data:pd.DataFrame,
    ) -> pd.DataFrame:
        
        raw_df = data.copy()
        raw_df[self.date_col] = pd.to_datetime(raw_df[self.date_col]).dt.normalize()
        result = raw_df.groupby([self.date_col]).count().reset_index().loc[:, [self.date_col, self.value_col]]

        # make a full date
        self.years = result[self.date_col].dt.year.unique()
        start_year = self.years[0]
        end_year = self.years[-1]
        date_df = pd.DataFrame(
            columns=[self.date_col],
            data=pd.date_range(
                start=f'{start_year}-01-01',
                end=f'{end_year}-12-31',
            ),
        )
        result = date_df.merge(result, how='outer')
        result[self.value_col].fillna(value=0, inplace=True)
        
        # weekdays(in year)
        result['weekday'] = result[self.date_col].dt.weekday
        
        # week nums(1 to 53)
        result['weeknum'] = result[self.date_col].dt.strftime('%V').astype(int)
        result.loc[(result[self.date_col].dt.month == 1) & (result['weeknum'] >= 52), 'weeknum'] = 0
        result.loc[(result[self.date_col].dt.month == 12) & (result['weeknum'] == 1), 'weeknum'] = 53

        return result
    
    def make_trace(
        self,
        *,
        year:int,
        line_kws:dict=None,
        freq_kws:dict=None,
    ) -> go.Figure:
        """
        Parameters: {line, freq, ev}_kws : dict
                               Dictionaries of keyword arguments.
                               line_kws are passed to the "__month_lines" function,
                               freq_kws are passed to the "__frequency_heatmap" function,
                               
        """
        # check year in data
        if year in self.years:
            self.__year_filter = self.data[self.date_col].dt.year == year
        else:
            raise ValueError(f'"{year}" not in list: {self.years}')
        
        # Month Position Lines Setting
        if line_kws is None:
            line_kws = dict(
                color='#9e9e9e',
                line_pos=0.5,
                line_width=1.5,
            )

        # Frequency Heatmap Setting
        if freq_kws is None:
            freq_kws = dict(
                min_color='#eeeeee',
                max_color='#678fae',
            )

        line_trace = self.__month_lines(**line_kws)
        values_trace = self.__frequency_heatmap(**freq_kws)
        
        if self.use_ohter_trace:
            fig = go.Figure(data=[*line_trace, values_trace, self.event_trace], layout=self.layout)
        else:
            fig = go.Figure(data=[*line_trace, values_trace], layout=self.layout)
        
        return fig
        
    def __month_line_data(
        self,
        *,
        line_pos:float
    ) -> None:       
        
        # Line setting
        filter1 = self.data[self.date_col].dt.day == 1
        filter2 = (filter1) & (self.data['weekday'].astype('bool'))
        
        # First Line
        self.data.loc[filter1, 'first_line_x'] = self.data.loc[filter1, 'weeknum'] - line_pos
        self.data.loc[filter1, 'first_line_y1'] = self.data.loc[filter1, 'weekday'] - line_pos
        self.data.loc[filter1, 'first_line_y2'] = 6 + line_pos
        
        # Second Line
        self.data.loc[filter2, 'second_line_x1'] = self.data.loc[filter2, 'weeknum'] - line_pos
        self.data.loc[filter2, 'second_line_x2'] = self.data.loc[filter2, 'weeknum'] + line_pos
        self.data.loc[filter2, 'second_line_y'] = self.data.loc[filter2, 'weekday'] - line_pos
        
        # Third Line
        self.data.loc[filter2, 'third_line_x'] = self.data.loc[filter2, 'weeknum'] + line_pos
        self.data.loc[filter2, 'third_line_y1'] = self.data.loc[filter2, 'weekday'] - line_pos
        self.data.loc[filter2, 'third_line_y2'] = -line_pos

    def __month_lines(
        self,
        *,
        color:str,
        line_pos:int,
        line_width:int
    ) -> Tuple[go.Scatter, go.Scatter, go.Scatter]:
        
        # make month line data
        self.__month_line_data(line_pos=line_pos)
        
        # line style setting
        line_setting_kwargs = dict(
            mode='lines',
            line=dict(
                color=color,
                width=line_width,
            ),
            hoverinfo='skip',
        )
        # Line setting
        
        # lines
        ax_line1 = go.Scatter(
            x=self.data.loc[self.__year_filter, ['first_line_x', 'first_line_x']].values.flatten(),
            y=self.data.loc[self.__year_filter, ['first_line_y1', 'first_line_y2']].values.flatten(),
            **line_setting_kwargs
        )
        ax_line2 = go.Scatter(
            x=self.data.loc[self.__year_filter, ['second_line_x1', 'second_line_x2']].values.flatten(),
            y=self.data.loc[self.__year_filter, ['second_line_y', 'second_line_y']].values.flatten(),
            **line_setting_kwargs
        )
        ax_line3 = go.Scatter(
            x=self.data.loc[self.__year_filter, ['third_line_x', 'third_line_x']].values.flatten(),
            y=self.data.loc[self.__year_filter, ['third_line_y1', 'third_line_y2']].values.flatten(),
            **line_setting_kwargs
        )
        
        return ax_line1, ax_line2, ax_line3

    def __frequency_heatmap(
        self,
        *,
        min_color:str,
        max_color:str,
    ) -> go.Heatmap:

        ax_heatmap = go.Heatmap(
            x=self.data.loc[self.__year_filter, 'weeknum'],
            y=self.data.loc[self.__year_filter, 'weekday'],
            z=self.data.loc[self.__year_filter, self.value_col],
            xgap=3,
            ygap=3,
            text=self.data[self.date_col].dt.date,
            hovertemplate='%{text}<br>채팅 수 : %{z}',
            hoverlabel= dict(namelength=0),
            colorscale=[
                [0.0, '#ffffff'],
                [0.0, '#ffffff'],
                [0.0001, min_color],
                [1.0, max_color],
            ],
            showscale=False,
        )

        return ax_heatmap
    
    def on_event(
        self,
        event_data:pd.DataFrame=None,
        *,
        date_col:str=None,
        event_col:str=None,
        color:str=None,
        use:bool=True,
    ) -> None:
        """
        event is ordinalencoding and Non event is Nan
    
        Parameters: use : bool Default True
                          Turn on/off event Heatmap
                          True is on
                          False is off
                          
                    color: dict
                           color
        """
        self.use_ohter_trace = use
        self.event_col = event_col
        
        # data processing
        event_data = event_data.copy()
        filter = self.data['date'].isin(event_data['date'])
        self.data.loc[filter, 'event'] = 1
        
        # set color
        if color is None:
            color = '#76cf63'
            
        # Event Heatmap Setting
        event_kws = dict(
            xgap=3,
            ygap=3,
            showscale=False,
            hoverinfo='skip',
            zmin=0,
            zmax=1,
            colorscale=[
                [0, color],
                [1, color]
            ]
        )
        self.event_trace = self.__event_heatmap(event_kws=event_kws)           
        
    def __event_heatmap(
        self,
        *,
        event_kws:dict,
    ) -> go.Heatmap:

        event_heatmap = go.Heatmap(
            x=self.data.loc[self.__year_filter, 'weeknum'],
            y=self.data.loc[self.__year_filter, 'weekday'],
            z=self.data[self.event_col],
            **event_kws
        )
        return event_heatmap
    
    def display(self, *, other):
        """
        planning to apply soon.
        ...
        Support visualization for all years.
        """
        pass
