import pandas as pd
import numpy as np
import re
import spacy
from collections import Counter
from sklearn.cluster import DBSCAN
from math import radians

nlp_en = spacy.load("en_core_web_sm", disable=["tagger","parser","lemmatizer","textcat"])
nlp_ru = spacy.load("ru_core_news_sm", disable=["tagger","parser","lemmatizer","textcat"])
df = pd.read_csv("PastVu_database.csv")

# WORKING WITH YEARS 

bins = [1880, 1900, 1920, 1940, 1960, 1980, 2000, 2020]
labels = [
    "1880-1900",
    "1900-1920",
    "1920-1940",
    "1940-1960",
    "1960-1980",
    "1980-2000",
    "2000-2020"
]

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["year_group"] = pd.cut(df["year"], bins=bins, labels=labels, right=False)
photos_by_year_group = df["year_group"].value_counts().rename_axis("year_group").reset_index(name="photo_count")

# WORKING WITH GEO 

geo_df = df.dropna(subset=["lat", "lon"]).copy()
coords = np.radians(geo_df[["lat", "lon"]].values)
desired_meters = 80 
eps_rad = desired_meters / 6371000

# Starting clusterization 
clusterer = DBSCAN(
    eps=eps_rad,
    min_samples=5,   
    metric="haversine"
)

labels = clusterer.fit_predict(coords)
geo_df["geo_cluster"] = labels

df = df.merge(geo_df[["login","name","geo_cluster"]], on=["login","name"], how="left")


# WORKING WITH COUNTRIES 

photos_by_country = df["country"].value_counts().rename_axis("country").reset_index(name="photo_count")

country_photo_dict = photos_by_country.set_index("country")["photo_count"].to_dict()
df["photos_in_country"] = df["country"].map(country_photo_dict)

# WORKING WITH USERS 

unique_users = df["login"].nunique()
photos_per_user = df["login"].value_counts().rename_axis("login").reset_index(name="photo_count")
user_sex_dist = df.drop_duplicates(subset=["login"])["sex"].value_counts().rename_axis("sex").reset_index(name="user_count")

# WORKING WITH OBJECTS AND ADDRESSES 
def extract_entities_batch(texts, nlp_model, whitelist):
    results = []
    for doc in nlp_model.pipe(texts, batch_size=256):
        ents = [ent.text for ent in doc.ents if ent.label_ in whitelist]
        results.append(ents if ents else None)
    return results

OBJ_LABELS = ("FAC", "ORG", "LOC", "GPE")

texts = df["name"].fillna("").astype(str).tolist()
objects_en = extract_entities_batch(texts, nlp_en, OBJ_LABELS)
objects_ru = extract_entities_batch(texts, nlp_ru, OBJ_LABELS)
objects_merged = []
for e1, e2 in zip(objects_en, objects_ru):
    if e1 or e2:
        combined = []
        if e1: combined.extend(e1)
        if e2: combined.extend(e2)
        objects_merged.append(combined)
    else:
        objects_merged.append([])

df["objects"] = objects_merged

ADDRESS_PATTERNS = [
    r"\b(?:ул\.?|улица)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:проспект|пр-т|пр\.?)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:переулок|пер\.?)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:бульвар|бул\.?)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:площадь|пл\.?)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:набережная|наб\.?)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:шоссе|ш\.)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:тракт)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:проезд)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:аллея)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:квартал|кв-л)\s+[A-ЯЁA-Za-z0-9\- ]+",
    r"\b(?:линия)\s+[A-ЯЁA-Za-z0-9\- ]+",   
    r"\b(?:street|st\.?)\s+[A-Za-z0-9\- ]+",
    r"\b(?:avenue|ave\.?)\s+[A-Za-z0-9\- ]+",
    r"\b(?:road|rd\.?)\s+[A-Za-z0-9\- ]+",
    r"\b(?:lane|ln\.?)\s+[A-Za-z0-9\- ]+",
    r"\b(?:drive|dr\.?)\s+[A-Za-z0-9\- ]+",
    r"\b(?:highway|hwy\.?)\s+[A-Za-z0-9\- ]+",
    r"\b(?:boulevard|blvd\.?)\s+[A-Za-z0-9\- ]+",
    r"\b(?:square)\s+[A-Za-z0-9\- ]+",
    r"\b(?:quay)\s+[A-Za-z0-9\- ]+",
    r"\b(?:embankment)\s+[A-Za-z0-9\- ]+",
    r"\b(?:promenade)\s+[A-Za-z0-9\- ]+",
    r"\b(?:alley)\s+[A-Za-z0-9\- ]+",
]

ADDRESS_REGEX = re.compile("|".join(ADDRESS_PATTERNS), flags=re.IGNORECASE)
df["addresses"] = df["name"].apply(
    lambda x: ADDRESS_REGEX.findall(x) if isinstance(x, str) else []
)

obj_counter = Counter()
addr_counter = Counter()

ARCHITECTURE_KEYWORDS = [
    "дворец", "замок", "церковь", "храм", "собор", "мечеть", "синагога",
    "башня", "вокзал", "порт", "аэропорт", "станция", "платформа",
    "мост", "плотина", "элеватор", "больница", "санаторий",
    "библиотека", "музей", "театр", "кинотеатр", "филармония",
    "завод", "фабрика", "мануфактура", "комбинат",
    "университет", "институт", "академия", "школа", "гимназия",
    "парк", "сквер", "ботанический сад", "дендропарк",
    "памятник", "мемориал", "ансамбль", "усадьба", "бульвар",
    "арка", "ротонда", "колонна", "обелиск",
    "башня", "фортеция", "крепость", "кремль"
]

def is_architecture_object(text):
    t = text.lower()
    return any(kw in t for kw in ARCHITECTURE_KEYWORDS)

df["objects_cleaned"] = df["objects"].apply(
    lambda lst: [o for o in lst if is_architecture_object(o)] if isinstance(lst, list) else []
)

for lst in df["objects_cleaned"]:
    obj_counter.update(lst)

for lst in df["addresses"]:
    addr_counter.update(lst)

df["object_count"] = df["objects_cleaned"].apply(len)
df["address_count"] = df["addresses"].apply(len)

def get_object_popularity(lst):
    return sum(obj_counter[o] for o in lst) if lst else 0

def get_address_popularity(lst):
    return sum(addr_counter[a] for a in lst) if lst else 0

df["object_popularity"] = df["objects_cleaned"].apply(get_object_popularity)
df["address_popularity"] = df["addresses"].apply(get_address_popularity)

if len(df) > 0:
    objects_expanded = []
    for idx, row in df.iterrows():
        objects = row["objects_cleaned"]
        if objects:
            for i, obj in enumerate(objects):
                objects_expanded.append({
                    "original_index": idx,
                    "object_rank": i + 1,
                    "object_name": obj,
                    "object_frequency": obj_counter[obj],
                    "object_popularity": row["object_popularity"]
                })
    
    objects_df = pd.DataFrame(objects_expanded)
    
    addresses_expanded = []
    for idx, row in df.iterrows():
        addresses = row["addresses"]
        if addresses:
            for i, addr in enumerate(addresses):
                addresses_expanded.append({
                    "original_index": idx,
                    "address_rank": i + 1,
                    "address_text": addr,
                    "address_frequency": addr_counter[addr],
                    "address_popularity": row["address_popularity"]
                })
    
    addresses_df = pd.DataFrame(addresses_expanded)

# SAVING

df.to_csv("photos_2.csv", index=False)


print("Geo clusters")
print(geo_df["geo_cluster"].value_counts().head())

print("\nPhotos by countries")
print(photos_by_country.head())

print("\nPhotos by years")
print(photos_by_year_group)

print("\nUnique users number")
print(unique_users)

print("\nPhotos by users")
print(photos_per_user.head())

print("\nGender distribution of users")
print(user_sex_dist)
