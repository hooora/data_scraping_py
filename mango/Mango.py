import json
import re
data_json = open("data.json", encoding='utf-8')
data = json.load(data_json)
FeatureCollection = {
    "type": "FeatureCollection",
    "features": []
}

def parseAdresse(add):
    addr = {
        "housenumber": "",
        "street": ""
    }

    if  re.match ("\d+\s{0,1}(b|bis|t|ter|q|quater|B|BIS|T|TER|Q|QUARTER|Bis)\s", add.strip()):
        return {
        "housenumber": re.match("\d+\s{0,1}(b|bis|t|ter|q|quater|B|BIS|T|TER|Q|QUARTER|Bis)\s", add.strip())[0].strip(),
        "street": re.split("\d+\s{0,1}(b|bis|t|ter|q|quater|B|BIS|T|TER|Q|QUARTER|Bis)\s", add.strip(), 1)[-1].strip().lstrip(',').strip()
        }

    elif  re.match ("[0-9\s\-\/]*", add.strip()):
        return{
           "housenumber": re.findall("[0-9\s\-\/]*", add.strip())[0].strip(), 
           "street": re.split("[0-9\s\-\/]*", add.strip(), 1)[-1].strip().lstrip(',').strip()
        }
    else:
        return{
            "housenumber": re.findall("[0-9]*", add.strip())[0].strip(), 
           "street": re.split("[0-9]*", add.strip(), 1)[-1].strip().lstrip(',').strip()
        }



for shop in data["stores"]:

    addr = parseAdresse(shop["addresses"]["address"]);
    
    if len(shop["phone"]) == 10:
        phone_number = "+33" + " " + shop["phone"][1] + " " + shop["phone"][2:4] + \
            " " + shop["phone"][4:6] + " " + \
            shop["phone"][6:8] + " " + shop["phone"][8:]
    else:
        phone_number = ''

    day_hour_agg = []
    for element in shop["timeSchedule"]:
        count = 0
        for openhour in element["timeList"] or []:
            if len(openhour["openHour"]) != 1 and len(openhour["closeHour"]) != 1:
                count += 1
                if count == 1:
                    day_hour = (
                        element["dayOfWeek"], openhour["openHour"].zfill(5) + "-" + openhour["closeHour"].zfill(5))
                   
                if count == 2:
                    day_hour_agg = day_hour_agg[:-1]
                    day_hour = (element["dayOfWeek"], day_hour[-1] + "," +
                                openhour["openHour"] + "-" + openhour["closeHour"])
                day_hour_agg.append(day_hour)
    list_day = []
    lst = []
    for i in (range(len(day_hour_agg) - 1)):
        if i == 0:
            lst.append("list0")
            list_day.append({f"list{i}": [day_hour_agg[0]]})
        if (day_hour_agg[i][1] == day_hour_agg[i+1][1]):
            list_day[-1][max(lst)].append(day_hour_agg[i+1])
        else:
            lst.append(f"list{i+1}")
            list_day.append({f"list{i+1}": [day_hour_agg[i+1]]})
    tabhour = []
    for element in list_day:
        for j in element.values():
            if len(j) == 1:
                tabhour.append(j[0][0][:2] + " " + j[0][1])
            else:
                tabhour.append(j[0][0][:2] + "-" + j[-1]
                                   [0][:2] + " " + j[0][1])
    
    Yohour = "; ".join(tabhour)

    for r in (("Lu", "Mo"), ("Ma", "Tu"), ("Me", "We"), ("Je", "Th"), ("Ve", "Fr"), ("Sa", "Sa"), ("Di", "Su")):
        Yohour = Yohour.replace(*r)
    
    collections=";".join(shop["collections"])
    for r in (("Femme", "women"), ("Homme", "men"), ("Enfants", "children")):
        collections = collections.replace(*r)

    new_dict = {
        "type": "Feature",
        "properties": {
            "brand": "Mango",
            "name": "Mango",
            "ref:fr:mango:id": shop["id"],
            "addr:housenumber": addr['housenumber'],
            "addr:street": addr['street'],
            "addr:zipcode": shop["addresses"]["postalCode"],
            "addr:city": shop["addresses"]["city"].title(),
            "phone": phone_number,
            "opening_hours": Yohour,
            "collections": collections,
            "shop": "clothes"
        },
        "geometry": {
            "coordinates": [
                shop["addresses"]["coordinates"]["longitude"],
                shop["addresses"]["coordinates"]["latitude"]
                ],
            "type": "Point",
        },
    }

    FeatureCollection["features"].append(new_dict)

with open('mango.geojson', 'w', encoding='utf-8') as fp:
    json.dump(FeatureCollection, fp, ensure_ascii=False, indent=2)
