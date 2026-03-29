import os, json
import pandas as pd

# set format of the files   
path_to_json = '/home/tanya/Programming/Projects/temp/pastvu_photos'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

# enumerate required columns 
jsons_data = pd.DataFrame(columns=['login', 'sex', 'name', 'lon', 'lat', 'year', 'country', 'city'])


# SAVING INFORMATION 
for index, js in enumerate(json_files):
    with open(os.path.join(path_to_json, js)) as json_file:
        json_text = json.load(json_file) 
    
    try:
        if "title" not in json_text:
            continue
            
        if "y" not in json_text:
            continue
            
        if "regions" not in json_text or len(json_text["regions"]) == 0:
            continue
        
        login = json_text["result"]["photo"]["user"]["login"]
        sex = json_text["result"]["photo"]["user"]["sex"]
        name = json_text["result"]["photo"]["title"]
        lat = json_text["result"]["photo"]["geo"][1]
        lon = json_text["result"]["photo"]["geo"][0]
        year = json_text["result"]["photo"]["y"]
        country = json_text["result"]["photo"]["regions"][0]["title_local"]
        city = json_text["result"]["photo"]["regions"][1]["title_local"]
        
        jsons_data.loc[index] = [login, sex, name, lat, lon, year, country, city]
        
    except Exception as e:
        import traceback
        traceback.print_exc()

#jsons_data.to_csv('PastVu_database.csv', index=True)
print(jsons_data)