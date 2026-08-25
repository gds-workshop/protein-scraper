import requests
import json


API_URL = "https://rest.uniprot.org/uniprotkb/search"


def fetch_proteins(disease_keyword, max_results=25):
    """Fetch reviewed human proteins associated with a disease keyword from UniProt."""
    params = {
        "query": f"(keyword:{disease_keyword}) AND (organism_id:9606) AND (reviewed:true)",
        "format": "json",
        "size": max_results,
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data["results"]

def extract_sequences(proteins):
    """Extract protein names and amino acid sequences from API results."""
    sequences = []

    for protein in proteins:
        try:
            accession = protein["primaryAccession"]
            name = protein["proteinDescription"]["recommendedName"]["fullName"]["value"]
            sequence = protein["sequence"]["value"]
            sequences.append({
                "accession": accession,
                "name": name,
                "sequence": sequence,
                "length": len(sequence),
            })
        except (KeyError, TypeError):
            accession = protein.get("primaryAccession", "Unknown")
            print(f"  Skipping {accession}: missing expected fields")

    return sequences

def save_results(sequences, disease_keyword):
    """Save extracted sequences to a JSON file."""
    filename = f"{disease_keyword.lower()}_sequences.json"
    with open(filename, "w") as f:
        json.dump(sequences, f, indent=2)
    print(f"Results saved to {filename}")


def main():
    disease = "Alzheimer"

    print(f"Fetching {disease}-related proteins from UniProt...")
    proteins = fetch_proteins(disease, max_results=25)
    print(f"Retrieved {len(proteins)} proteins\n")

    print("Extracting sequences...")
    sequences = extract_sequences(proteins)
    print(f"Successfully extracted {len(sequences)} sequences\n")

    save_results(sequences, disease)


if __name__ == "__main__":
    main()