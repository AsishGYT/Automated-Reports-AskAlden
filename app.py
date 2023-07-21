import boto3
import os
from datetime import datetime, timedelta, timezone
import json
import pandas as pd
import tempfile
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from dotenv import load_dotenv
import plotly.io as pio
from PIL import Image
import io

from fastapi import FastAPI, BackgroundTasks

from extract_data import * 
from create_visualisations import * 
from send_mail import *

from typing import List
from pydantic import BaseModel

import secret
from utils import load_env_vars
load_env_vars(secret)

app = FastAPI()

# Load environment variables from .env file
# load_dotenv()

def generate_report_background(
    start_date_dashboard: str,
    end_date_dashboard: str,
    bot_id_dashboard: str,
    name_of_bot_user: str,
    email_recepient_internal_as_list: list):
    
    print('process started')
    
    start_date_dashboard = datetime.strptime(start_date_dashboard, "%Y-%m-%d")
    end_date_dashboard_original = datetime.strptime(end_date_dashboard, "%Y-%m-%d")
    end_date_dashboard = end_date_dashboard_original + timedelta(days=1)

    print(start_date_dashboard, ' to ', end_date_dashboard)

    # Your existing code for report generation
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Create an S3 client
    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    print('s3 client succesful')

    bucket_name = 'core-session-prod'
    prefix_expired = 'expired/'
    prefix_interim = 'interim/'

    # Set the timezone to UTC
    utc_timezone = timezone.utc

    # Get the list of objects in the bucket
    response_expired = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix_expired)
    response_interim = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix_interim)
    print('s3 objects loaded')

    # Extract the desired fields from JSON files and filter by bot_id
    data_expired = extract_data_from_json(response_expired, start_date_dashboard, end_date_dashboard, bot_id_dashboard, bucket_name)
    data_interim = extract_data_from_json(response_interim, start_date_dashboard, end_date_dashboard, bot_id_dashboard, bucket_name)
    print('data extracted')
    # Merge the data into a single list
    data = pd.concat([data_expired, data_interim])
    print(data.head())

    # Rename the columns
    data.columns = ['session_id', 'account_id', 'referrer', 'bot_name', 'bot_id', 'turns', 'created_at', 'is_billable',
                    'is_test', 'confidence_threshold', 'auto_add_threshold_lower', 'auto_add_threshold_upper',
                    'created_at_date', 'created_at_time','fail_counter', 
                    'fail_turn_indices', 'report_indices', 'email_triggers', 'max_consecutive_fails', 
                    'user_conversation', 'component_info', 'created_at_date_central', 'created_at_time_central']

    # Write the DataFrame to a CSV file
    csv_file = '/tmp/sessions.csv'
    data.to_csv(csv_file, index=False)

    print('CSV file created successfully')

    # Load the data from CSV into a DataFrame
    df = pd.read_csv(csv_file)

    print('CSV to DataFrame successful')
    print(len(df))
    print(df.head())
    print(df.columns)

    # Select the desired columns for Excel export
    selected_columns_excel = ['session_id', 'bot_name', 'turns', 'created_at_date_central', 'created_at_time_central',
                              'fail_counter', 'report_indices', 'user_conversation', 'component_info']
    df_selected_excel = df[selected_columns_excel]

    # Export the selected columns to an Excel file
    excel_file = f'/tmp/sessions.xlsx'
    df_selected_excel.to_excel(excel_file, index=False)
    print("excel file created for qna")

    # Upload the Excel file to a new S3 bucket
    new_bucket_name = 'weekly-reports-risos'
    xlsx_new_bucket_key = f"analytics_report_{start_date_dashboard.strftime('%Y-%m-%d')}_{end_date_dashboard_original.strftime('%Y-%m-%d')}.xlsx"
    s3_client.upload_file(excel_file, new_bucket_name, xlsx_new_bucket_key)
    print(f"Excel file of qna uploaded to S3 bucket")

    turns_bar_graph = generate_turns_bar_graph(df)
    print('graphs built 1')
    session_bar_graph = generate_session_bar_graph(df)
    print('graphs built 2')
    gauge_graph = generate_gauge_chart(df)
    print('graphs built 3')
    bar_freq_turns = generate_bar_chart_freq_turns(df)
    print('graphs built 4')
    line_graph = generate_line_chart(df)
    print('graphs built 5')
    stacked_bar_graph = generate_stacked_bar_chart(df)
    print('graphs built 6')
    create_total_sessions_indicator_plot1 = create_total_sessions_indicator_plot(df)
    print('graphs built 7')
    create_total_turns_indicator_plot1 = create_total_turns_indicator_plot(df)
    print('graphs built 8')
    create_average_session_length_indicator_plot1 = create_average_session_length_indicator_plot(df)
    print('graphs built 9')

    fig_failures = create_total_failures_plot(df)
    print('graphs built 10')
    fig_reports = create_total_reports_indicator_plot(df)
    print('graphs built 11')
    fig_email_triggers = create_total_triggers_indicator_plot(df)
    print('graphs built 12')
    fig_avg_max_fails = create_average_max_consecutive_fails_plot(df)
    print('graphs built 13')
    sessions_per_hour_graph = plot_sessions_by_hour(df)
    print('graphs built 14')
    componenet_names_frequency = plot_component_frequencies_horizontal(df)
    print('graphs built 15')

    figure_titles = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
    figures = [create_total_sessions_indicator_plot1, create_total_turns_indicator_plot1, 
               session_bar_graph,sessions_per_hour_graph,line_graph,turns_bar_graph,bar_freq_turns, 
               stacked_bar_graph,componenet_names_frequency,
               gauge_graph, create_average_session_length_indicator_plot1, fig_failures, fig_reports, 
               fig_email_triggers, fig_avg_max_fails ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create the output PDF file path in the temporary directory
        output_pdf_path = "/tmp/output.pdf"
        
        image_paths = []

        for i, fig in enumerate(figures):
            img_path = os.path.join(tmp_dir, f'figure_{i+1}.png')
            fig.write_image(img_path, format='png', width=1700, height=600, scale=2)
            image_paths.append(img_path)

        print('images created')

        # Merge the images into a single PDF
        with open(output_pdf_path, 'wb') as pdf_file:
            c = canvas.Canvas(pdf_file, pagesize=landscape(A4))
            # c.showPage()
            for img_path in image_paths:
                img = ImageReader(img_path)
                img_width, img_height = img.getSize()
                scale_x = A4[1] / img_width
                scale_y = A4[0] / img_height
                scale = min(scale_x, scale_y)

                # Calculate the new image dimensions based on the scaling factor
                new_width = img_width * scale
                new_height = img_height * scale

                # Calculate the position to center the image on the page
                x = (A4[1] - new_width) / 2
                y = (A4[0] - new_height) / 2

                # Add the image to the PDF document with the calculated dimensions and position
                c.drawImage(img_path, x, y, new_width, new_height)
                c.showPage()  # Add a new page after each image

            c.save()
                
        
        print('pdf created')

        pdf_file_key= f"analytics_report_{start_date_dashboard.strftime('%Y-%m-%d')}_{end_date_dashboard_original.strftime('%Y-%m-%d')}.pdf"
        dump_bucket_pdf = 'weekly-reports-risos'
        s3_client.upload_file(output_pdf_path, dump_bucket_pdf, pdf_file_key)
        print('pdf to s3 done')



    # Sending the report via email
    new_bucket_name = 'weekly-reports-risos'
    sender_email = "support@gytworkz.com"
    recipients = email_recepient_internal_as_list
    subject = f'Analytics report for {name_of_bot_user} - Ask alden bot'
    text_body = f"Hello! Here are the reports of your {name_of_bot_user} - Ask alden bot for the requested timeline {start_date_dashboard.strftime('%Y-%m-%d')} to {end_date_dashboard_original.strftime('%Y-%m-%d')}."
    region = 'us-east-1'    
    pdf_file_key= f"analytics_report_{start_date_dashboard.strftime('%Y-%m-%d')}_{end_date_dashboard_original.strftime('%Y-%m-%d')}.pdf"
    xlsx_file_key = f"analytics_report_{start_date_dashboard.strftime('%Y-%m-%d')}_{end_date_dashboard_original.strftime('%Y-%m-%d')}.xlsx"
    file_names_list = [pdf_file_key, xlsx_file_key]
    send_email_with_attachments(sender_email, recipients, subject, text_body, new_bucket_name, file_names_list, region)

    print("Report generation and email sending completed.")

    # Upload the CSV file to a new S3 bucket
    csv_new_bucket_key = f"analytics_report_{start_date_dashboard.strftime('%Y-%m-%d')}_{end_date_dashboard_original.strftime('%Y-%m-%d')}.csv"
    s3_client.upload_file(csv_file, new_bucket_name, csv_new_bucket_key)

    print(f"CSV file uploaded to S3 bucket: s3://{new_bucket_name}/{csv_new_bucket_key}.")

    response = {
        "message": "Finished generating report and sending to mail"
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }


class ReportRequest(BaseModel):
    start_date_dashboard: str
    end_date_dashboard: str
    bot_id_dashboard: str
    name_of_bot_user: str
    email_recepient_internal_as_list: List[str]


@app.post("/generate_report/")
async def generate_report(report_request: ReportRequest, background_tasks: BackgroundTasks):
    # Extract data from the request body
    start_date_dashboard = report_request.start_date_dashboard
    end_date_dashboard = report_request.end_date_dashboard
    bot_id_dashboard = report_request.bot_id_dashboard
    name_of_bot_user = report_request.name_of_bot_user
    email_recepient_internal_as_list = report_request.email_recepient_internal_as_list

    # Instead of directly returning the response, enqueue the report generation task in the background
    background_tasks.add_task(generate_report_background, start_date_dashboard, end_date_dashboard, bot_id_dashboard, name_of_bot_user, email_recepient_internal_as_list)

    return {"message": "Report generation task enqueued. You will be receiving a mail shortly"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
