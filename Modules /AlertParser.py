from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()  

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def FormatPrompt(alertPrompt):
    prompt = f"""
            The following is an AMBER Alert. Parse the alert to extract the following attributes, if available:
            
            Suspect Name, Vehicle Make, Vehicle Model, Vehicle Color, License Plate, Last Seen Victim Location, Last Seen Victim Time, Last Seen Suspect Location, Last Seen Suspect Time, Direction or Heading.
            
            Return ONLY the values in a single comma-separated line in this exact order. If a value is unknown or missing, return 'NONE'. Do NOT include labels or additional text.
            
            Example:
            John Doe,Ford,Explorer,Black,ABC123,I-35 and Grand Ave,12:30 PM,NONE,NONE,Northbound on Highway 235
            
            Now parse this alert:
            
            {alertPrompt}
            """

    return prompt


def GPTCall(prompt, model="gpt-4o"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a criminal investigation database"},
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        
        #print(completion.choices[0].message.content)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def FormatResponse(response):
    schema = ['SuspectName', 'VehicleMake', 'VehicleModel', 'VehicleColor', 'LicensePlate', 'LastSeenVictimLocation', 
              'LastSeenVictimTime', 'LastSeenSuspectLocation', 'LastSeenSuspectTime','Heading']

    values = [v.strip() for v in response.split(',')]
    values = (values + ['NONE'] * len(schema))[:len(schema)]
    return dict(zip(schema, values))

def Parser(alert):
    prompt = FormatPrompt(alert)
    response = GPTCall(prompt, model="gpt-4o")
    dataExtract = FormatResponse(response)
    return dataExtract


if __name__ == "__main__":
    
    sample_alert = """ 
                AMBER ALERT – IOWA: 8 y/o girl, Harper Johnson, abducted near Union Park in Des Moines at 4:12 PM.¶
                White female, blonde hair, blue eyes, last seen in purple jacket and pink leggings.
                Taken by unknown male in dark blue Chevy Tahoe, IA plate JVK129. Vehicle last seen heading east on I-235. 
                Call 911 immediately if seen.
                """
    
    print(Parser(sample_alert))
