
import requests
import streamlit as st

url = "https://v3.football.api-sports.io/players"

headers = {
    "x-apisports-key": st.secrets["API_FOOTBALL_KEY"]
}

params = {
    "id": 278,
    "team": 85,
    "season": 2023
}


response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=15
)

response.raise_for_status()
data = response.json()

if data.get("errors"):
    print("API-feil:", data["errors"])
elif not data.get("response"):
    print("Fant ingen spillere.")
else:
     for resultat in data["response"]:
        spiller = resultat["player"]

        print("Navn:", spiller["name"])
        print("Spiller-ID:", spiller["id"])

        for stats in resultat.get("statistics", []):
            print("Liga:", stats["league"]["name"])
            print("Liga-ID:", stats["league"]["id"])
            print("Sesong:", stats["league"]["season"])
            print("Kamper:", stats["games"]["appearences"])
            print("Mål:", stats["goals"]["total"])
            print("Assists:", stats["goals"]["assists"])
            print("----------------------")
