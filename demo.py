from manual_dashboard_lambda import lambda_handler
from send_mail import *

test_load = {'body':{"start_date_dashboard": "2023-07-10",
  "end_date_dashboard": "2023-07-17", 
  "bot_id_dashboard": "84e67c6b-fbc9-409e-8a55-333ebfb7b388",
  "name_of_bot_user" : "RI SOS",
  "email_sender_string": "support@gytworkz.com",
  "email_recepient_internal_as_list": ["asishsairam.illa@gytworkz.com", "test@gmail.com"]}
}
 
lambda_handler(test_load, {})

# pdf_key = 'weekly_report_2023-06-25_2023-06-29.pdf'
# xlsx_key = 'weekly_report_2023-06-25_2023-06-29.xlsx'
# file_names = [pdf_key, xlsx_key]
# sender_email = 'asishsairam.illa@gytworkz.com'
# recipients = ["asishsairam.illa@gytworkz.com"]
# subject = 'test mail analytics report'
# body_text = 'Hello! Here are the reports for your {bot_name} Ask Alden Bot between {start_date} & {end_date}.'
# bucket_name = 'weekly-reports-risos'
region = 'us-east-1'

# send_email_with_attachments(sender_email, recipients, subject, body_text, bucket_name, file_names, region) 