import streamlit as st
from openai import OpenAI
import json
import pandas as pd
import matplotlib.pyplot as plt

# Set your OpenAI API key here
client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])


def get_disease_info(disease_name):
    """
    Function to query OpenAI and return structured information about a disease.
    """
    medication_format = '''"name":""
    "side_effects":[
    0:""
    1:""
    ...
    ]
    "dosage":""'''
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"Please provide information on the following aspects for {disease_name}: 1. Key Statistics, 2. Recovery Options, 3. Recommended Medications, 4. Global Distribution. Format the response in JSON with keys for 'name', 'statistics', 'total_cases', 'recovery_rate', 'mortality_rate', 'recovery_options', 'medication' (always use this json format for medication: {medication_format}), and 'global_distribution'."}
        ]
    )
    return response.choices[0].message.content


def display_disease_info(disease_info):
    """
    Function to display the disease information in a structured way using Streamlit.
    """
    try:
        info = json.loads(disease_info)

        recovery_rate = float(info['statistics']["recovery_rate"].strip('%'))
        mortality_rate = float(info['statistics']["mortality_rate"].strip('%'))

        # Display global statistics
        st.write(f"## Global Statistics for {info['name']}")
        st.write(f"Total Cases: {info['statistics']['total_cases']}")

        # Bar chart for recovery and mortality rates
        chart_data = pd.DataFrame(
            {
                "Recovery Rate": [recovery_rate],
                "Mortality Rate": [mortality_rate],
            },
            index=["Rate"]
        )
        st.bar_chart(chart_data)

        # Pie chart for global distribution
        if "global_distribution" in info:
            st.write("## Global Distribution")
            distribution_data = pd.DataFrame.from_dict(info['global_distribution'], orient='index', columns=['Cases'])
            st.pyplot(create_pie_chart(distribution_data))

        # Display recovery options
        st.write("## Recovery Options")
        for option, description in info['recovery_options'].items():
            st.subheader(option)
            st.write(description)

        # Display medication
        st.write("## Medication")
        medication = info['medication']
        for idx, (med_name, med_info) in enumerate(medication.items()):
            st.subheader(f"{idx + 1}. {med_name}")
            st.write(f"Side Effects: {', '.join(med_info['side_effects'])}")
            st.write(f"Dosage: {med_info['dosage']}")

        # Download data as CSV
        st.download_button("Download Data as CSV", convert_to_csv(info), "disease_info.csv", "text/csv")

    except json.JSONDecodeError:
        st.error("Failed to decode the response into JSON. Please check the format of the OpenAI response.")


def create_pie_chart(distribution_data):
    """
    Create a pie chart for global distribution.
    """
    fig, ax = plt.subplots()
    ax.pie(distribution_data['Cases'], labels=distribution_data.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    return fig


def convert_to_csv(info):
    """
    Convert the JSON information to a CSV-friendly format.
    """
    df = pd.DataFrame.from_dict(info, orient='index')
    return df.to_csv().encode('utf-8')


# Streamlit app layout
st.title("Enhanced Disease Information Dashboard")

with st.sidebar:
    st.header("User Settings")
    disease_name = st.text_input("Enter the name of the disease:")

if disease_name:
    disease_info = get_disease_info(disease_name)
    display_disease_info(disease_info)
