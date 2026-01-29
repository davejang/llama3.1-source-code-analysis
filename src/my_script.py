import pandas as pd
import requests
import os

API_KEY = "12345-ABCDE-SECRET-KEY"

def fetch_and_process_data():
    response = requests.get(f"https://api.example.com/data?key={API_KEY}")
    data = response.json()
    
    df = pd.DataFrame(data)
    
    results = []
    for i in range(len(df)):
        row = df.iloc[i]
        val = row['value'] * 1.1
        results.append(val)
    
    df['new_value'] = results
    
    df.to_csv("C:/data/output.csv") 
    print("작업 완료")

if __name__ == "__main__":
    fetch_and_process_data()