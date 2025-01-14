import json
import csv

# JSON de exemplo
import os
import tempfile

json_data = '''
{
    "dados": {
        "contratos": [
            {
                "cod_contrato": "1111",
                "sigla": "OD",
                "parcelas": [
                    {"numero_parcela": "1", "valor|": "100"},
                    {"numero_parcela": "2", "valor|": "200"}
                ],
                "valor": [
                    {"saldo": "500.00", "data_processamento": "2024-06-18"},
                    {"saldo": "400.00", "data_processamento": "2024-06-19"}
                ],
                "pagamentos_realizados": [
                    {"data_pagamento": "2024-06-10", "valor_pago": "50"},
                    {"data_pagamento": "2024-06-15", "valor_pago": "75"},
                    {"data_pagamento": "2024-06-20", "valor_pago": "100"}
                ],
                "amortizacoes": [
                    {"data_amortizacao": "2024-06-05", "valor_amortizado": "30"},
                    {"data_amortizacao": "2024-06-25", "valor_amortizado": "40"}
                ],
                "dados_historicos_marcacao_contrato": [
                    {"marcacao": "1", "data_referencia": "2024-04-28", "hist_atual": "false"},
                    {"marcacao": "1", "data_referencia": "2024-05-02", "hist_atual": "true"}
                ]
            },
            {
                "cod_contrato": "2222",
                "sigla": "OD",
                "dados_historicos_marcacao_contrato": {
                    "marccao": "1",
                    "data_referencia": "2024-03-23",
                    "hist_atual": "true"
                },
                "parcelas": [
                    {"numero_parcela": "1", "valor|": "100"},
                    {"numero_parcela": "2", "valor|": "200"}
                ],
                "valor": [
                    {"saldo": "500.00", "data_processamento": "2024-06-18"},
                    {"saldo": "400.00", "data_processamento": "2024-06-19"}
                ]
            }
        ]
    }
}
'''

# Carregar JSON
data = json.loads(json_data)

# Nome do arquivo CSV
arquivo_csv = "contratos.csv"

# Caminho onde você quer salvar o arquivo
temp_dir = r"C:\Users\Rafael\Documents\lambda\lambda-python"  # No Windows
# caminho_diretorio = "/home/usuario/meu_diretorio"  # No Linux/macOS

# Verifique se o diretório existe, se não, cria
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
    csv_file_path = os.path.join(temp_dir, "contratos.csv")

# Criar e escrever no arquivo CSV
with open(arquivo_csv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")

    # Cabeçalho do CSV
    writer.writerow([
        "cod_contrato", "sigla", "maior_numero_parcela", "valor_maior_parcela",
        "maior_saldo", "data_maior_saldo", "data_referencia_hist_atual",
        "tipo_registro", "data_evento", "valor_evento"
    ])

    # Iterar sobre os contratos
    for contrato in data["dados"]["contratos"]:
        # Encontrar a maior parcela
        maior_parcela = max(contrato["parcelas"], key=lambda x: int(x["numero_parcela"]))

        # Encontrar o maior saldo
        maior_saldo = max(contrato["valor"], key=lambda x: float(x["saldo"]))

        # Tratar "dados_historicos_marcacao_contrato" para garantir que sempre seja uma lista
        historicos = contrato.get("dados_historicos_marcacao_contrato", [])
        if isinstance(historicos, dict):  # Se for um único objeto, transforma em lista
            historicos = [historicos]

        # Buscar a data de referência do histórico marcado como "hist_atual": "true"
        data_referencia_hist_atual = ""
        historico_atual = next((h for h in historicos if h.get("hist_atual") == "true"), None)
        if historico_atual:
            data_referencia_hist_atual = historico_atual["data_referencia"]

        # Processar os pagamentos
        pagamentos = contrato.get("pagamentos_realizados", [])
        for p in pagamentos:
            writer.writerow([
                contrato["cod_contrato"],
                contrato["sigla"],
                maior_parcela["numero_parcela"],
                maior_parcela["valor|"],
                maior_saldo["saldo"],
                maior_saldo["data_processamento"],
                data_referencia_hist_atual,
                "Pagamento",
                p["data_pagamento"],
                p["valor_pago"]
            ])

        # Processar as amortizações
        amortizacoes = contrato.get("amortizacoes", [])
        for a in amortizacoes:
            writer.writerow([
                contrato["cod_contrato"],
                contrato["sigla"],
                maior_parcela["numero_parcela"],
                maior_parcela["valor|"],
                maior_saldo["saldo"],
                maior_saldo["data_processamento"],
                data_referencia_hist_atual,
                "Amortização",  # ✅ Com acento
                a["data_amortizacao"],
                a["valor_amortizado"]
            ])

        # Se não houver pagamentos ou amortizações, criar uma linha vazia para esse contrato
        if not pagamentos and not amortizacoes:
            writer.writerow([
                contrato["cod_contrato"],
                contrato["sigla"],
                maior_parcela["numero_parcela"],
                maior_parcela["valor|"],
                maior_saldo["saldo"],
                maior_saldo["data_processamento"],
                data_referencia_hist_atual,
                "",  # Campo "tipo_registro" vazio
                "",
                ""
            ])

print(f"Arquivo CSV criado: {arquivo_csv}")
