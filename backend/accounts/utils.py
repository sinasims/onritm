import requests
from django.conf import settings

def send_sms_via_smsir(phone_number, code):
    if not phone_number:
        return False
    api_key = getattr(settings, 'SMS_IR_API_KEY', None)
    templateId = int(getattr(settings, 'SMS_IR_TEMPLATE_ID'))
    if not api_key:
        return False

    url = "https://api.sms.ir/v1/send/verify"
    
    headers = {
        "x-api-key": api_key,
        "Accept": "text/plain",
        "Content-Type": "application/json"
    }
    payload = {
        "mobile": str(phone_number),
        "templateId": templateId,
        "parameters": [
            {
                "name": "CODE",
                "value": str(code)
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10.0)
        result = response.json()

        if response.status_code == 200 and result.get("status") == 1:
            print(f"SMS sent successfully to {phone_number}")
            print(f"CODE OTP= {code}")
            return response.ok
        else:
            return False

    except Exception as e:
        return False

