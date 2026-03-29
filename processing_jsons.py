import os, json
import pandas as pd

path_to_json = '/home/tanya/Programming/Projects/temp/Pastvu/pastvu_photos'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
all_data = []

# PROCESSING JSONs
for index, js in enumerate(json_files):
    try:
        with open(os.path.join(path_to_json, js), 'r', encoding='utf-8') as json_file:
            json_text = json.load(json_file)
        photo_data = json_text.get("result", {}).get("photo", {})
        
        if not photo_data:
            continue

        if not all(key in photo_data for key in ["title", "y", "regions", "geo", "user"]):
            continue

        # getting data 
        login = photo_data["user"].get("login", "")
        sex = photo_data["user"].get("sex", "")
        name = photo_data.get("title", "")
        geo = photo_data.get("geo", [])
        if len(geo) >= 2:
            lon = geo[1]
            lat = geo[0]
        else:
            continue 
        year = photo_data.get("y", "")
        regions = photo_data.get("regions", [])
        country = regions[0].get("title_local", "") if len(regions) > 0 else ""
        city = regions[1].get("title_local", "") if len(regions) > 1 else ""
        
        all_data.append({
            'login': login,
            'sex': sex,
            'name': name,
            'lon': lon,
            'lat': lat,
            'year': year,
            'country': country,
            'city': city,
            'filename': js 
        })
            
    except Exception as e:
        # print(f"Error for {js}: {str(e)[:50]}...")
        continue 

# SAVING
if all_data:
    jsons_data = pd.DataFrame(all_data)
    print(jsons_data.head())

    output_path = '/home/tanya/Programming/Projects/temp/Pastvu/PastVu_database.csv'
    jsons_data.to_csv(output_path, index=False, encoding='utf-8')
    
else:
    print("Processing failed.")
