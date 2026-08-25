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

def create_bar_chart(frequencies, disease_keyword, protein_count, total_residues):
    """Create and save a bar chart of amino acid frequencies."""
    amino_acids = list(frequencies.keys())
    percentages = list(frequencies.values())

    plt.figure(figsize=(12, 6))
    plt.bar(amino_acids, percentages, color="steelblue", edgecolor="white")

    plt.title(
        f"Amino Acid Frequencies in {disease_keyword}-Related Human Proteins\n"
        f"({protein_count} proteins, {total_residues:,} total residues)",
        fontsize=14,
    )
    plt.xlabel("Amino Acid", fontsize=12)
    plt.ylabel("Frequency (%)", fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    filename = f"{disease_keyword.lower()}_amino_acid_chart.png"
    plt.savefig(filename, dpi=150)
    print(f"Chart saved to {filename}")
    plt.show()

def analyze_disease(disease_keyword, max_results=25):
    """Run full pipeline for a single disease: fetch, extract, count, save."""
    print(f"\nFetching {disease_keyword}-related proteins from UniProt...")
    proteins = fetch_proteins(disease_keyword, max_results)
    print(f"Retrieved {len(proteins)} proteins")

    sequences = extract_sequences(proteins)
    print(f"Extracted {len(sequences)} sequences")

    counts, total = count_amino_acids(sequences)
    frequencies = calculate_frequencies(counts, total)

    save_results(sequences, frequencies, total, disease_keyword)

    return {
        "disease": disease_keyword,
        "protein_count": len(sequences),
        "total_residues": total,
        "frequencies": frequencies,
    }

def create_comparison_chart(data1, data2):
    """Create a grouped bar chart comparing amino acid frequencies between two diseases."""
    all_amino_acids = sorted(
        set(list(data1["frequencies"].keys()) + list(data2["frequencies"].keys()))
    )

    freq1 = [data1["frequencies"].get(aa, 0) for aa in all_amino_acids]
    freq2 = [data2["frequencies"].get(aa, 0) for aa in all_amino_acids]

    x = range(len(all_amino_acids))
    width = 0.35

    plt.figure(figsize=(14, 6))
    plt.bar(
        [i - width / 2 for i in x], freq1, width,
        label=data1["disease"], color="steelblue",
    )
    plt.bar(
        [i + width / 2 for i in x], freq2, width,
        label=data2["disease"], color="coral",
    )

    plt.title(
        f"Amino Acid Frequency Comparison: {data1['disease']} vs {data2['disease']}",
        fontsize=14,
    )
    plt.xlabel("Amino Acid", fontsize=12)
    plt.ylabel("Frequency (%)", fontsize=12)
    plt.xticks(list(x), all_amino_acids, fontsize=10)
    plt.legend(fontsize=11)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig("disease_comparison_chart.png", dpi=150)
    print("Comparison chart saved to disease_comparison_chart.png")
    plt.show()

def main():
    alzheimer_data = analyze_disease("Alzheimer")
    parkinson_data = analyze_disease("Parkinson")

    print("\nGenerating comparison chart...")
    create_comparison_chart(alzheimer_data, parkinson_data)

    print("\nGenerating individual charts...")
    create_bar_chart(
        alzheimer_data["frequencies"],
        alzheimer_data["disease"],
        alzheimer_data["protein_count"],
        alzheimer_data["total_residues"],
    )
    create_bar_chart(
        parkinson_data["frequencies"],
        parkinson_data["disease"],
        parkinson_data["protein_count"],
        parkinson_data["total_residues"],
    )

if __name__ == "__main__":
    main()