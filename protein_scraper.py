import requests
import json


API_URL = "https://rest.uniprot.org/uniprotkb/search"


# Set query parameters to find Alzheimer's-related human proteins
params = {
    "query": "(keyword:Alzheimer) AND (organism_id:9606) AND (reviewed:true)",
    "format": "json",
    "size": 5,
}

# Send a GET request to UniProt's search endpoint
response = requests.get(API_URL, params=params)
data = response.json()

# Loop through each protein and display key details
for protein in data["results"]:
    accession = protein["primaryAccession"]
    name = protein["proteinDescription"]["recommendedName"]["fullName"]["value"]
    sequence_preview = protein["sequence"]["value"][:50]
    print(f"{accession}: {name}")
    print(f"  Sequence preview: {sequence_preview}...\n")