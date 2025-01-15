import csv
import json

import csv
import json


def converter_csv_para_json(arquivo_csv: str, arquivo_json: str):
    dados = []

    with open(arquivo_csv, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')  # Definir delimitador correto

        for row in csvreader:
            dados.append(row)

    with open(arquivo_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(dados, jsonfile, ensure_ascii=False, indent=4)


# Exemplo de uso:
converter_csv_para_json("contratos.csv", "saida.json")

print(f"Conversão concluída! O arquivo saida_json foi gerado.")