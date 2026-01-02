from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import ItemsHistory, APIParameter, UserPresets
from requests import Session
from requests.utils import dict_from_cookiejar, cookiejar_from_dict
from random import choice
import json


def home(request):
    options = get_options()
    presets = get_presets()
    return render(request, 'client/base.html', {"options": options, "presets": presets})


def get_options():
    params = []
    for section in APIParameter.objects.values("section").distinct():
        params.append({
            "sectionTitle": section["section"],
            "type": "checkbox",
            "params": []
        })
    for non_sub_section_choice in APIParameter.objects.filter(sub_section__isnull=True):
        section = [p for p in params if p["sectionTitle"] == non_sub_section_choice.section][0]
        existing_choices = [p for p in section["params"] if p["name"] == non_sub_section_choice.name]
        if len(existing_choices) > 0:
            existing_choices[0]["value"].append(non_sub_section_choice.value)
        else:
            section["params"].append({
                "name": non_sub_section_choice.name,
                "type": "choice",
                "value": [non_sub_section_choice.value]
            })
    for sub_section in APIParameter.objects.filter(sub_section__isnull=False).values("section", "sub_section").distinct():
        section = [p for p in params if p["sectionTitle"] == sub_section["section"]][0]
        section["params"].append({
            "name": sub_section["sub_section"],
            "type": "subSection",
            "params": []
        })
    for sub_section_choice in APIParameter.objects.filter(sub_section__isnull=False):
        section = [p for p in params if p["sectionTitle"] == sub_section_choice.section][0]
        sub_section = [p for p in section["params"] if p["name"] == sub_section_choice.sub_section][0]
        existing_choices = [p for p in sub_section["params"] if p["name"] == sub_section_choice.name]
        if len(existing_choices) > 0:
            existing_choices[0]["value"].append(sub_section_choice.value)
        else:
            sub_section["params"].append({
                "name": sub_section_choice.name,
                "type": "choice",
                "value": [sub_section_choice.value]
            })
    marques = [p for p in params if p["sectionTitle"] == "Marques"][0]
    marques["params"].sort(key=lambda x: x["name"])
    return params


def get_presets():
    print("Loading presets...", end="")

    presets = list(UserPresets.objects.values_list("name", flat=True).distinct())

    print("DONE")
    return presets

@csrf_exempt
def load_preset(request):
    print("Loading preset...", end="")

    try:
        data = json.loads(request.body.decode("utf-8"))
        preset_name = data.get("presetName", "")
        choices = list(UserPresets.objects.filter(name=preset_name).values_list("choice", flat=True))

        print("DONE")
        return JsonResponse({"choices": choices})
    except Exception as e:
        print("ERROR")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def save_preset(request):
    print("Saving preset...", end="")

    try:
        data = json.loads(request.body.decode("utf-8"))
        preset_name = data.get("presetName", "")
        new_presets = set(data.get("choices", {}))
        old_presets = set(UserPresets.objects.filter(name=preset_name).values_list("choice", flat=True))
        for deleted_p in old_presets - new_presets:
            c1 = Q(name=preset_name)
            c2 = Q(choice=deleted_p)
            UserPresets.objects.filter(c1 & c2).delete()
        for added_p in new_presets - old_presets:
            saving_preset, created = UserPresets.objects.get_or_create(name=preset_name, choice=added_p)

        print("DONE")
        return JsonResponse({"status": "Presets Saved"})
    except Exception as e:
        print("ERROR")
        return JsonResponse({"error": str(e)}, status=500)


def setup_session(request):
    try:
        print("setup session...")

        session = Session()
        session.headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }
        """
        Banned:
            107.172.163.27:6543
            198.23.239.134:6540
            23.95.150.145:6114
        """
        all_proxies = [
            "23.95.150.145:6114",
            "198.23.239.134:6540",
            "45.38.107.97:6014",
            "207.244.217.165:6712",
            "107.172.163.27:6543",
            "104.222.161.211:6343",
            "64.137.96.74:6641",
            "216.10.27.159:6837",
            "136.0.207.84:6661",
            "142.147.128.93:6593",
        ]
        used_proxy = choice(all_proxies)
        #session.proxies.update({'https': f'http://sgtfdmmp:91g633ipv8v4@{used_proxy}'})

        response = session.get("https://vinted.fr/")

        if response.status_code in (401, 403):
            print(f"-- ERROR {response.status_code} --")
            print(response.url)
            print(used_proxy)
            if "Please wait" in response.text:
                print("Too many requests")
            elif "banned" in response.text:
                print("Banned IP")
            else:
                print(response.text)
            return JsonResponse({"error": str(response.text)}, status=response.status_code)
        elif response.status_code != 200:
            print(f"-- ERROR {response.status_code} -- \n{response.url} \n{response.text}")
            return JsonResponse({"error": str(response.text)}, status=500)

        print(f"using {used_proxy}")
        return JsonResponse({"cookies": dict_from_cookiejar(session.cookies), "proxy": used_proxy})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_vinted_articles(request):
    try:
        print("\nfetching clothes...")

        data = json.loads(request.body.decode("utf-8"))
        cookies = data.get("cookies", {})
        proxy = data.get("proxy", "")
        user_params = data.get("params", {})

        print(user_params)
        params = {
            "per_page": "96",
            "catalog_ids": ",".join(user_params["categories"]),
            "order": "newest_first",
            "size_ids": ",".join(user_params["sizes"]),
            "brand_ids": ",".join(user_params["brands"]),
            "price_to": user_params["price"],
            "page": 1,
        }
        
        session = Session()
        session.headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }
        session.cookies.update(cookiejar_from_dict(cookies))
        #session.proxies.update({'https': f'http://sgtfdmmp:91g633ipv8v4@{proxy}'})
        
        response = session.get("https://www.vinted.fr/api/v2/catalog/items", params=params)

        print(response.url)

        if response.status_code in (401, 403):
            print(f"-- ERROR {response.status_code} --")
            print(response.url)
            print(proxy)
            if "Please wait" in response.text:
                print("Too many requests")
            elif "banned" in response.text:
                print("Banned IP")
            else:
                print(response.text)
            return JsonResponse({"error": str(response.text)}, status=response.status_code)
        elif response.status_code != 200:
            print(f"-- ERROR {response.status_code} -- \n{response.url} \n{response.text}")
            return JsonResponse({"error": str(response.text)}, status=500)

        return filter_new_articles(user_params, response.json()["items"])   
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def filter_new_articles(current_params, items):
    db_params, created = ItemsHistory.objects.get_or_create(api_params=current_params)
    
    i = len(items) - 1
    while i >= 0 and items[i]["id"] <= db_params.last_id:
        items[i]["seen"] = "old"
        i -= 1
    while i >= 0:
        items[i]["seen"] = "new"
        i -= 1

    
    db_params.last_id = max(max(x["id"] for x in items), db_params.last_id)
    db_params.save()

    return JsonResponse({ "items": [
        {
            "id": x["id"],
            "img": x["photo"]["url"], 
            "price": x["price"]["amount"], 
            "url": x["url"],
            "title": x["title"],
            "size": x["size_title"],
            "brand": x["brand_title"],
            "status": x["status"],
            "seen": x["seen"],
        }
        for x in items
    ]})