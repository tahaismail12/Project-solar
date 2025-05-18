from flask_cors import CORS
from flask import Flask, jsonify
from collections import defaultdict
import requests
from datetime import datetime
import time
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

# Load credentials from .env
load_dotenv()
tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
resource = os.getenv("RESOURCE")
url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

access_token = None
token_expiry = 0

def get_access_token():
    global access_token, token_expiry
    if access_token and time.time() < token_expiry:
        return access_token

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": resource
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        token_expiry = time.time() + int(token_data['expires_in']) - 60
        return access_token
    else:
        raise Exception("Token generation failed: " + response.text)

api_url = "https://cds.api.crm.dynamics.com/api/data/v9.2/leads?%24select=ala_utmcampaign%2Cala_utmcampaignname%2Cala_utmcontent%2Cala_utmmedium%2Cala_utmsource%2Cala_utmterm%2Cfirstname%2Clastname%2Cemailaddress1%2Cala_marketsegment%2Cstatecode%2Ccreatedon"

@app.route('/leads', methods=['GET'])
def get_leads():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "OData-Version": "4.0",
        "OData-MaxVersion": "4.0"
    }

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": response.text}), response.status_code

    data = response.json()
    leads = data.get('value', [])
    total_leads = len(leads)

    program_classification = defaultdict(int)
    brand_classification = defaultdict(int)
    utm_medium_classification = defaultdict(int)

    daily_leads = defaultdict(int)
    weekly_leads = defaultdict(int)
    monthly_leads = defaultdict(int)

    open_leads = 0
    qualified_leads = 0
    disqualified_leads = 0

    details = []

    for lead in leads:
        program = lead.get('ala_utmcampaignname', 'Unknown Program')
        brand = lead.get('ala_marketsegment', 'Unknown Brand')
        utm_medium = lead.get('ala_utmmedium', 'Unknown UTM Medium')
        stateCode = lead.get('statecode', 'Unknown')
        CreatedOn = lead.get('createdon', None)

        lead_status = "Unknown"
        if isinstance(stateCode, int):
            if stateCode == 0:
                lead_status = "Open"
                open_leads += 1
            elif stateCode == 1:
                lead_status = "Qualified"
                qualified_leads += 1
            elif stateCode == 2:
                lead_status = "Disqualified"
                disqualified_leads += 1

        if CreatedOn:
            created_date = datetime.strptime(CreatedOn, "%Y-%m-%dT%H:%M:%SZ")
            day_str = created_date.strftime("%Y-%m-%d")
            week_str = created_date.strftime("%Y-W%U")
            month_str = created_date.strftime("%Y-%m")
            daily_leads[day_str] += 1
            weekly_leads[week_str] += 1
            monthly_leads[month_str] += 1

        program_classification[str(program)] += 1
        brand_classification[str(brand)] += 1
        utm_medium_classification[str(utm_medium)] += 1

        details.append({
            "program": program,
            "brand": brand,
            "utm_medium": utm_medium,
            "statecode": stateCode,
            "lead_status": lead_status,
            "createdon": CreatedOn
        })

    return jsonify({
        "total_leads": total_leads,
        "open_leads": open_leads,
        "qualified_leads": qualified_leads,
        "disqualified_leads": disqualified_leads,
        "program_classification": dict(program_classification),
        "brand_classification": dict(brand_classification),
        "utm_medium_classification": dict(utm_medium_classification),
        "daily_leads": dict(daily_leads),
        "weekly_leads": dict(weekly_leads),
        "monthly_leads": dict(monthly_leads),
        "lead_details": details
    })

if __name__ == '__main__':
    app.run(debug=True)
