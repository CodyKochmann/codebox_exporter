#!/usr/bin/env python

import json
from sources import xmltodict
#import xmltodict
import base64

def get_file_text(file_path):
    # returns all text from a file. 
    # Warning this may block up scripts for long files.
    with open(file_path,"r") as f:
        return(str(f.read()))

workspace={}
old_db = get_file_text("codebox_snippet_database.cbxml").replace("\n","")
codebox_db = xmltodict.parse(old_db)
snippet_db = codebox_db["database"]["object"]

collection={
    "SNIPPET":[],
    "TAG":[],
    "SEARCH":[],
    "ASSET":[]
}
for i in snippet_db:
    collection[i["@type"]].append(i)

collection={
    "SNIPPET":collection["SNIPPET"],
    "ASSET":collection["ASSET"]
}
print len(collection["SNIPPET"]), "found."

digits="1234567890".split()
new_collection={}
collected=0
snippet_array=[]
for snippet in collection["SNIPPET"]:
    output={}
    for i in snippet["attribute"]:
        if i["@name"] == "name":
            output["name"]=(str(i["#text"]))
        if i["@name"] == "modified":
            output["modified"]=(str(i["#text"]))
    # for i in snippet["relationship"]:
    #     if i["@name"] == "assets":
    #         output.append(str(i["@idrefs"]))
    current_asset = collection["ASSET"][collected]
    for i in current_asset["attribute"]:
        if i["@name"] == "notes":
            output["notes"]=(base64.b64encode(str(i["#text"])))
        if i["@name"] == "content":
            output["content"]=(str(i["#text"]))
    collected+=1
    required="name modified notes content".split(" ")
    for i in required:
        if i not in output:
            output[i]="none"
    snippet_array.append(output)
    print output["name"]

cleaner_snippet_database={
    "snippet_db":snippet_array
}
output_filename="cb_extract"
with open("extracted_files/"+output_filename+".json", "w") as f:
    f.write(json.dumps(cleaner_snippet_database))

import csv

with open("extracted_files/"+output_filename+'.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter='|')
    spamwriter.writerow(["name","modified","notes","content"])
    for i in cleaner_snippet_database["snippet_db"]:
        print i
        spamwriter.writerow([ i["name"], i["modified"], i["notes"], i["content"] ])
#=====================================================================================
# all code below extracts the code from the csv and generages the files it represents.
#=====================================================================================
import csv, base64

def make_file(file_name,file_content):
    try:
        file_name="./extracted_files/"+file_name
        with open(file_name,"w") as f:
            f.write(base64.b64decode(file_content))
        print("created "+file_name)
    except:
        pass

with open('extracted_files/cb_extract.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='|')
    row_guide=0
    for row in spamreader:
        if row_guide == 0:
            row_guide=row
        make_file(row[0], row[3])
        make_file(row[0]+".notes", row[2])
