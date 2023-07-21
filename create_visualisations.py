import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import plotly.io as pio
import ast
import base64

def generate_html_report_images(figure_titles, figures, start_date, end_date):
    # Define the HTML template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Ask Alden - RI | SOS - Weekly Analytics: {start_date} to {end_date}</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
        margin: 20px;
    }}
    
    h1 {{
        margin-bottom: 10px;
    }}
    
    hr {{
        margin-top: 20px;
        margin-bottom: 20px;
        border: 0;
        border-top: 1px solid #ddd;
    }}
    
    .plot-container {{
        margin-bottom: 40px;
    }}
    </style>
    </head>
    <body>
    <h1>Ask Alden - RI | SOS - Weekly Analytics: {start_date} to {end_date}</h1>
    {content}
    </body>
    </html>
    """

    # Generate the content for each figure
    figure_content = ''
    for figure, title in zip(figures, figure_titles):
        # Convert the Plotly figure to a base64-encoded image
        img_bytes = figure.to_image(format="png")
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        img_html = f"<img src='data:image/png;base64,{img_base64}'>"

        figure_content += f"<div class='plot-container'><h2>{title}</h2>{img_html}</div><hr>"

    # Format the start and end dates
    start_date_formatted = start_date.strftime("%d %B %Y")
    end_date_formatted = end_date.strftime("%d %B %Y")

    # Combine the content with the HTML template
    html_content = html_template.format(content=figure_content, start_date=start_date_formatted, end_date=end_date_formatted)

    return html_content


def generate_html_report(figure_titles, figures, start_date, end_date):
    # Define the HTML template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Ask Alden - RI | SOS - Weekly Analytics: {start_date} to {end_date}</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
        margin: 20px;
    }}
    
    h1 {{
        margin-bottom: 10px;
    }}
    
    hr {{
        margin-top: 20px;
        margin-bottom: 20px;
        border: 0;
        border-top: 1px solid #ddd;
    }}
    
    .plot-container {{
        margin-bottom: 40px;
    }}
    </style>
    </head>
    <body>
    <h1>Ask Alden - RI | SOS - Weekly Analytics: {start_date} to {end_date}</h1>
    {content}
    </body>
    </html>
    """

    # Generate the content for each figure
    figure_content = ''
    for figure, title in zip(figures, figure_titles):
        figure_html = pio.to_html(figure, full_html=False)
        figure_content += f"<div class='plot-container'><h2>{title}</h2>{figure_html}</div><hr>"

    # Format the start and end dates
    start_date_formatted = start_date.strftime("%d %B %Y")
    end_date_formatted = end_date.strftime("%d %B %Y")

    # Combine the content with the HTML template
    html_content = html_template.format(content=figure_content, start_date=start_date_formatted, end_date=end_date_formatted)

    # # Write the HTML content to a file
    # output_html = 'interactive_plots.html'
    # with open(output_html, 'w') as f:
    #     f.write(html_content)

    return html_content




def plot_component_frequencies_horizontal(df):
    # Convert string representations of dictionaries to actual dictionaries
    df['component_info1'] = df['component_info'].apply(ast.literal_eval)
    
    # Flatten the list of dictionaries in the 'component_info' column
    components = [component for row in df['component_info1'] for component in row]
    
    # Create a DataFrame with component names and their frequencies
    component_df = pd.DataFrame(components)
    component_counts = component_df['component_name'].value_counts().reset_index()
    component_counts.columns = ['Component Name', 'Frequency']
    
    # Create a bar chart using Plotly
    fig = go.Figure(data=go.Bar(x=component_counts['Frequency'], y=component_counts['Component Name'], orientation='h'))
    fig.update_layout(title='Component Name Frequencies', xaxis_title='Frequency', yaxis_title='Component Name')
    fig.update_traces(marker_color='rgb(55, 83, 109)')

    return fig

def plot_component_frequencies(df):
    # Convert string representations of dictionaries to actual dictionaries
    df['component_info1'] = df['component_info'].apply(ast.literal_eval)
    
    # Extract component IDs and names from the 'component_info' column
    component_info = df['component_info1'].explode()
    component_ids = component_info.apply(lambda x: x.get('component_id'))
    component_names = component_info.apply(lambda x: x.get('component_name'))

    # Count the frequency of each component ID
    component_id_counts = component_ids.value_counts()

    # Create a bar chart using Plotly
    fig = go.Figure(data=go.Bar(x=component_id_counts.index, y=component_id_counts.values, text=component_names, textposition='auto'))
    fig.update_layout(title='Component ID Frequencies', xaxis_title='Component ID', yaxis_title='Frequency')
    #fig.update_xaxes(tickvals=[], showticklabels=False)
    fig.update_traces(marker_color='rgb(55, 83, 109)')

    return fig


def plot_sessions_by_hour(df):
    # Convert 'created_at_date_central' and 'created_at_time_central' to datetime
    df['created_at_date_central'] = pd.to_datetime(df['created_at_date_central'], format='%Y-%m-%d')
    df['created_at_time_central'] = pd.to_datetime(df['created_at_time_central'], format='%H:%M:%S.%f').dt.time

    # Group the data by hour and count the number of sessions
    sessions_by_hour = df.groupby(df['created_at_time_central'].apply(lambda x: x.hour))['session_id'].count().reset_index()

    # Sort the data by hour
    sessions_by_hour = sessions_by_hour.sort_values('created_at_time_central')

    # Plot the graph
    fig = px.bar(
        sessions_by_hour, 
        x='created_at_time_central', 
        y='session_id', 
        labels={'created_at_time_central': 'Hour', 'session_id': 'Number of Sessions'},
        category_orders={'created_at_time_central': sorted(df['created_at_time_central'].unique())}
    )

    # Customize the axis labels and title
    fig.update_layout(
        xaxis_title='Hour of the Day',
        yaxis_title='Number of Sessions',
        title={
            'text': 'Number of Sessions by Hour of the Day',
            'y': 0.97,
            'x': 0.2,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            tickmode='linear',
            dtick=1
        )
    )

    # Update marker color
    fig.update_traces(marker_color='rgb(55, 83, 109)')

    # Add a line explaining the graph
    explanation_line = "This graph shows the number of sessions that occurred at different hours of the day."
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=1.07,
        text=explanation_line,
        showarrow=False,
        font=dict(size=12, color="black"),
        align="center"
    )
    
    return fig


def create_total_failures_plot(df):
    # Calculate total number of failures
    total_failures = df['fail_counter'].sum()

    # Create the indicator plot
    fig = go.Figure(go.Indicator(mode='number', value=total_failures))

    # Update the layout
    fig.update_layout(title='Total Number of Failures that occured in the sessions throughout the given timeline')

    return fig


def create_total_reports_indicator_plot(df):
    # Count the number of non-empty values in 'report_indices' column
    report_count = df['report_indices'].apply(lambda x: 1 if x != '[]' else 0).sum()

    # Create the indicator plot
    fig = go.Figure(go.Indicator(mode='number', value=report_count))

    # Update the layout
    fig.update_layout(title='Total Number of Reports that were reported throughout the given timeline')

    return fig

def create_total_triggers_indicator_plot(df):
    # Count the number of non-empty values in 'email_triggers' column
    trigger_count = df['email_triggers'].apply(lambda x: 1 if x != '[]' else 0).sum()

    # Create the indicator plot
    fig = go.Figure(go.Indicator(mode='number', value=trigger_count))

    # Update the layout
    fig.update_layout(title='Total Number of Email Triggers that were triggered throughout the given timeline')

    return fig



def create_average_max_consecutive_fails_plot(df):
    # Calculate average value of maximum consecutive fails
    average_max_consecutive_fails = df['max_consecutive_fails'].mean()

    # Create the indicator plot
    fig = go.Figure(go.Indicator(mode='number', value=average_max_consecutive_fails))

    # Update the layout
    fig.update_layout(title='Average Value of Maximum Consecutive Fails for your bot configuration')

    return fig



def create_total_sessions_indicator_plot(df):
    # Calculate total number of sessions in the entire week
    total_sessions = df['session_id'].nunique()

    # Create the indicator plot
    fig = go.Figure(go.Indicator(mode='number', value=total_sessions))

    # Update the layout
    fig.update_layout(title='Total Number of Sessions through the defined timeline')

    return fig

def create_total_turns_indicator_plot(df):
    # Calculate total number of turns in the entire week
    total_turns = df['turns'].sum()

    # Create the indicator plot
    fig = go.Figure(go.Indicator(mode='number', value=total_turns))

    # Update the layout
    fig.update_layout(title='Total number of Turns performed by the bot through the defined timeline')

    return fig


def create_average_session_length_indicator_plot(df):
    # Calculate average session length throughout the week
    average_session_length = df.groupby('session_id')['turns'].sum().mean()

    # Create the indicator plot
    fig = go.Figure(go.Indicator(mode='number', value=average_session_length))

    # Update the layout
    fig.update_layout(title='Average Session Length (in number of turns) of the bot during the defined timeline')

    return fig




def generate_turns_bar_graph(df):
    # Calculate the total count of turns per day
    turn_counts = df.groupby('created_at_date')['turns'].sum().reset_index()

    # Bar Graph
    bar_graph = px.bar(turn_counts, x='created_at_date', y='turns',
                       labels={'created_at_date': 'Date', 'turns': 'Total Number of Turns'},
                       title='Total Number of Turns per Day')

    # Set the color of the bars
    bar_graph.update_traces(marker_color='rgb(55, 83, 109)')

    # Trend Line
    trend_line = go.Scatter(x=turn_counts['created_at_date'], y=turn_counts['turns'],
                            mode='lines', name='Trend Line')
    bar_graph.add_trace(trend_line)

    # Update layout
    bar_graph.update_layout(showlegend=False)
    bar_graph.update_layout(annotations=[dict(text='Analyzing the total number of turns performed over different dates. '
                                                      'Enables us to understand the overall usage of the bot on each day of the week',
                                              showarrow=False,
                                              xref='paper',
                                              yref='paper',
                                              x=0,
                                              y=1.1)])

    return bar_graph


def generate_session_bar_graph(df):
    # Calculate the count of unique sessions per day
    session_counts = df.groupby('created_at_date')['session_id'].nunique().reset_index()

    # Bar Graph
    bar_graph = px.bar(session_counts, x='created_at_date', y='session_id',
                       labels={'created_at_date': 'Date', 'session_id': 'Number of Unique Sessions'},
                       title='Total Number of Unique Sessions per Day')

    # Set the color of the bars
    bar_graph.update_traces(marker_color='rgb(55, 83, 109)')

    # Trend Line
    trend_line = go.Scatter(x=session_counts['created_at_date'], y=session_counts['session_id'],
                            mode='lines', name='Trend Line')
    bar_graph.add_trace(trend_line)

    # Update layout
    bar_graph.update_layout(showlegend=False)
    bar_graph.update_layout(annotations=[dict(text='Analyzing the total number of unique sessions over different dates. '
                                                      'Helps us understand the traffic to the bot on each day of the week',
                                              showarrow=False,
                                              xref='paper',
                                              yref='paper',
                                              x=0,
                                              y=1.1)])

    return bar_graph


def generate_gauge_chart(df):
    # Calculate the average values for lower and upper thresholds
    lower_threshold = df['auto_add_threshold_lower'].mean()
    upper_threshold = df['auto_add_threshold_upper'].mean()

    # Define the color scale for the gauge chart
    colorscale = [[0, 'lightgray'], [lower_threshold / 100, 'lightgray'],
                  [lower_threshold / 100, 'rgb(255, 255, 0)'], [upper_threshold / 100, 'rgb(255, 255, 0)'],
                  [upper_threshold / 100, 'rgb(255, 0, 0)'], [1, 'rgb(255, 0, 0)']]

    # Gauge Chart
    gauge_chart = go.Figure(go.Indicator(
        mode='gauge+number',
        value=df['confidence_threshold'].mean(),
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, lower_threshold], 'color': 'lightgray', 'name': f'Lower Limit: {lower_threshold}'},
                {'range': [lower_threshold, upper_threshold], 'color': 'rgb(255, 255, 0)'},
                {'range': [upper_threshold, 100], 'color': 'lightgray', 'name': f'Upper Limit: {upper_threshold}'}
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 2},
                'thickness': 0.75,
                'value': df['confidence_threshold'].mean()
            },
            'bgcolor': 'white',
            'bar': {'color': 'rgb(55, 83, 109)'}
        }
    ))

    gauge_chart.update_layout(
        title='Average Confidence Threshold with Auto Add Limits',
        annotations=[dict(
            text='Analyzing the average confidence threshold with auto add limits for all sessions of the bot.',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0,
            y=-0.2
        )]
    )

    return gauge_chart


def generate_bar_chart_freq_turns(df):
    # Calculate the count of each number of turns
    turn_counts = df['turns'].value_counts().sort_index()

    # Bar Chart
    bar_chart = go.Figure(data=go.Bar(x=turn_counts.index, y=turn_counts))
    bar_chart.update_layout(
        title='Distribution of Number of Turns',
        xaxis_title='Number of Turns',
        yaxis_title='Count',
        annotations=[dict(
            text='Understanding the typical conversation length and identifying outliers. Helps us understand how long a typical user converses with the bot',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0,
            y=1.1
        )],
        bargap=0.2
    )
    bar_chart.update_traces(marker_color='rgb(55, 83, 109)', texttemplate='%{y}', textposition='auto')

    return bar_chart

def generate_line_chart(df):
    # Calculate average number of turns per day
    average_turns = df.groupby('created_at_date')['turns'].mean().reset_index()

    # Line Chart
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(x=average_turns['created_at_date'], y=average_turns['turns'], mode='lines'))
    line_chart.update_layout(title='Average Number of Turns per Day',
                             xaxis_title='Date',
                             yaxis_title='Average Number of Turns')
    line_chart.update_layout(annotations=[dict(text='Analyzing the average user engagement with the chatbot on different dates.',
                                               showarrow=False,
                                               xref='paper',
                                               yref='paper',
                                               x=0,
                                               y=1.1)])

    # Set the color of the line
    line_chart.update_traces(line=dict(color='rgb(55, 83, 109)', width=2),
                             text=average_turns['turns'], textposition='top center')

    return line_chart


def generate_stacked_bar_chart(df):
    # Preprocess the data and sort the turns within each stack
    turn_counts = df.groupby(['created_at_date', 'turns']).size().unstack().fillna(0)
    sorted_turns = turn_counts.columns.sort_values().tolist()
    turn_counts = turn_counts.reindex(columns=sorted_turns)

    # Define the color palette
    color_palette = px.colors.qualitative.Dark2

    # Create the stacked bar chart
    stacked_bar_chart = go.Figure()

    for i, turn in enumerate(turn_counts.columns):
        stacked_bar_chart.add_trace(
            go.Bar(
                x=turn_counts.index,
                y=turn_counts[turn],
                name=turn,
                text=turn_counts[turn],
                textposition='auto',
                marker_color=color_palette[i % len(color_palette)]
            )
        )

    # Update layout
    stacked_bar_chart.update_layout(
        barmode='stack',
        title='Distribution of Conversation Lengths over Time',
        xaxis_title='Date',
        yaxis_title='Count',
        bargap=0.2
    )

    stacked_bar_chart.update_layout(
        annotations=[dict(
            text='Analyzing the distribution of conversation lengths over different dates. Shows number of sessions that happened w.r.t number of turns on each day',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0,
            y=1.1
        )]
    )

    return stacked_bar_chart

