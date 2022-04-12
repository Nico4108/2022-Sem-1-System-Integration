import pandas as pd

file = pd.read_csv('Bibob - Ark1.tsv', sep='\t')

for note in file['note']:
    print(note)

#print(file.note.to_string(index=False))

