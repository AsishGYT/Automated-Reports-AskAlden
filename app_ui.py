import requests
import json
import streamlit as st

st.title("Ask Alden - Automated Report")
st.write("Enter the following details to generate the report:")

# Input fields for report generation
start_date = st.text_input("Start Date:", placeholder="YYYY-MM-DD")
end_date = st.text_input("End Date:", placeholder="YYYY-MM-DD")
bot_id = st.text_input("Bot ID:", placeholder="For the bot which you want to generate the analytics report")
bot_user_name = st.text_input("Bot User Name:", placeholder="Name of your Bot")
recipient_emails = st.text_input("Recipient Emails (separated by commas):", placeholder="charles@gmail.com, sebastian@yahoo.com")

# Add some space between the input fields and the button
st.write("")

if st.button("Generate Report"):

    # Convert date inputs to string format
    #start_date_str = start_date.strftime("%Y-%m-%d")
    #end_date_str = end_date.strftime("%Y-%m-%d")

    # Convert recipient_emails to a list
    recipient_emails_list = [email.strip() for email in recipient_emails.split(',')]
    print(recipient_emails_list)

    # Prepare data for API request
    data = {
        "start_date_dashboard": start_date,
        "end_date_dashboard": end_date,
        "bot_id_dashboard": bot_id,
        "name_of_bot_user": bot_user_name,
        "email_recepient_internal_as_list": recipient_emails_list
    }

    print(data)

    # Make API request to FastAPI endpoint
    response = requests.post("http://localhost:8000/generate_report/", json=data)

    # Display progress and comments from the API response
    if response.status_code == 200:
        result = json.loads(response.content)
        st.header("Progress and Comments:")
        for comment in result.get("comments", []):
            st.text(comment)
        st.success(result.get("message"))
    else:
        st.error("Error occurred during report generation.")

