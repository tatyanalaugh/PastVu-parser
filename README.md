# PastVu parser

PastVu is an online platform for curating, annotating, attributing, and discussing vintage pictures around the world.
This project provides a tool for downloading a custom number and range of photos from pastvu.com, along with collecting metadata such as countries, years, coordinates, users, objects, and addresses into a CSV file for further statistical survey with Counter and ML libraries. 

## Structure
The project consists of 3 Python scripts:
* **getting_jsons.py** — downloads photo metadata to a local directory in JSON format. A separate JSON file is created for each photo. 
* **processing_jsons.py** — reads JSON files from the local directory and extracts information such as photo names, user gender and usernames, coordinates, years, countries, and cities, saving the results into a CSV file.
* **adding_data.py** — enriches the dataset by adding basic statistics and applying simple machine learning techniques using libraries spaCy and scikit-learn.

As a result, you will obtain additional columns with:

* historical periods,
* geo clusters,
* photo counts by country and by user,
* most frequent objects and addresses.

The scripts can be run independently or as part of a pipeline.

## Usage 
The project is easy to set up. You only need to update the directory paths in **processing_jsons.py** so they match your local environment:. 

```python
path_to_json = '/path/to/your/json/files'
output_path = '/path/to/output/PastVu_database.csv'
```
## Example of application 
I personally used these scripts to prepare a DataLens infographic based on data from pastvu.com. You can find it on [Google Drive](https://drive.google.com/file/d/1sg2f6C2HGVvtM0uqt3Rw-aOLD5XfqGT8/view?usp=sharing)
