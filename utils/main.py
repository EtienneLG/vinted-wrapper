from requests import Session
import json

brands = [
    "Nike",
    "Puma"
]
letters = sorted(list(set([x[0] for x in brands])))

session = Session()
session.headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

session.get("https://www.vinted.fr")

print("INSERT INTO client_apiparameter(section, name, value) VALUES")
for i, b in enumerate(brands):
    response = session.get(f"https://www.vinted.fr/api/v2/catalog/filters/search?filter_search_code=brand&filter_search_text={b.replace(" ", "+")}")
    infos = response.json()
    if infos.get("options") and len(infos["options"]) > 0:
        print(f"('Marques', '{infos['options'][0]['title']}', {infos['options'][0]['id']})",
              end=(";" if i == len(brands) - 1 else ",\n"))
    else:
        print(f"-- {b} --")
        print(json.dumps(infos, indent=2))
        print("----")