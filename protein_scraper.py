import requests
import json
import matplotlib.pyplot as plt


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

def count_amino_acids(sequences):
    """Count amino acid occurrences across all sequences."""
    counts = {}
    total = 0

    for entry in sequences:
        for amino_acid in entry["sequence"]:
            counts[amino_acid] = counts.get(amino_acid, 0) + 1
            total += 1

    return counts, total

def calculate_frequencies(counts, total):
    """Convert raw amino acid counts to sorted percentage frequencies."""
    frequencies = {}

    for aa, count in counts.items():
        frequencies[aa] = round((count / total) * 100, 2)

    return dict(sorted(frequencies.items()))

def save_results(sequences, frequencies, total, disease_keyword):
    """Save analysis results to a JSON file."""
    results = {
        "disease": disease_keyword,
        "protein_count": len(sequences),
        "total_residues": total,
        "frequencies": frequencies,
        "proteins": [
            {"accession": s["accession"], "name": s["name"], "length": s["length"]}
            for s in sequences
        ],
    }

    filename = f"{disease_keyword.lower()}_amino_acid_frequencies.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {filename}")
    return filename


def main():
    disease = "Alzheimer"

    print(f"Fetching {disease}-related proteins from UniProt...")
    proteins = fetch_proteins(disease)
    print(f"Retrieved {len(proteins)} proteins\n")

    print("Extracting sequences...")
    sequences = extract_sequences(proteins)
    print(f"Successfully extracted {len(sequences)} sequences\n")

    for entry in sequences[:5]:
        print(f"  {entry['accession']}: {entry['name']} ({entry['length']} aa)")
    if len(sequences) > 5:
        print(f"  ... and {len(sequences) - 5} more\n")

    print("Counting amino acids...")
    counts, total = count_amino_acids(sequences)
    frequencies = calculate_frequencies(counts, total)

    print(f"\nAmino Acid Frequencies ({total:,} total residues):")
    print("-" * 40)
    for aa, freq in frequencies.items():
        print(f"  {aa}: {freq}% ({counts[aa]:,})")

    save_results(sequences, frequencies, total, disease)

if __name__ == "__main__":
    main()