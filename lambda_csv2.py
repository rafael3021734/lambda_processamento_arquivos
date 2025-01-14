import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Union


def carregar_json(json_str: str) -> Dict:
    """
    Converte uma string JSON em um dicionário Python.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao carregar JSON: {e}")


def obter_maior_parcela(parcelas: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Retorna a maior parcela com base no número da parcela.
    """
    return max(parcelas, key=lambda x: int(x["numero_parcela"]))


def obter_maior_saldo(valores: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Retorna o maior saldo com base no valor do saldo.
    """
    return max(valores, key=lambda x: float(x["saldo"]))


def obter_historico_atual(historicos: Union[List[Dict], Dict]) -> Optional[str]:
    """
    Retorna a data de referência do histórico marcado como "hist_atual": "true".
    """
    if isinstance(historicos, dict):
        historicos = [historicos]

    historico_atual = next((h for h in historicos if h.get("hist_atual") == "true"), None)
    return historico_atual["data_referencia"] if historico_atual else ""


def criar_diretorio(caminho: Path) -> None:
    """
    Cria o diretório se ele não existir.
    """
    if not caminho.exists():
        caminho.mkdir(parents=True, exist_ok=True)


def escrever_csv(nome_arquivo: Path, contratos: List[Dict]) -> None:
    """
    Escreve os dados dos contratos em um arquivo CSV, gerando uma linha para cada pagamento ou amortização.
    """
    with nome_arquivo.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")

        # Cabeçalho
        writer.writerow([
            "cod_contrato", "sigla", "maior_numero_parcela", "valor_maior_parcela",
            "maior_saldo", "data_maior_saldo", "data_referencia_hist_atual",
            "tipo_registro", "data_evento", "valor_evento"
        ])

        for contrato in contratos:
            maior_parcela = obter_maior_parcela(contrato["parcelas"])
            maior_saldo = obter_maior_saldo(contrato["valor"])
            data_hist_atual = obter_historico_atual(contrato.get("dados_historicos_marcacao_contrato", []))

            pagamentos = contrato.get("pagamentos_realizados", [])
            amortizacoes = contrato.get("amortizacoes", [])

            eventos = [
                          ("Pagamento", p["data_pagamento"], p["valor_pago"]) for p in pagamentos
                      ] + [
                          ("Amortização", a["data_amortizacao"], a["valor_amortizado"]) for a in amortizacoes
                      ]

            if not eventos:
                eventos.append(("", "", ""))  # Garante que o contrato apareça no CSV

            for tipo, data, valor in eventos:
                writer.writerow([
                    contrato["cod_contrato"],
                    contrato["sigla"],
                    maior_parcela["numero_parcela"],
                    maior_parcela["valor|"],
                    maior_saldo["saldo"],
                    maior_saldo["data_processamento"],
                    data_hist_atual,
                    tipo,
                    data,
                    valor
                ])


def main():
    """
    Função principal que carrega o JSON, processa os contratos e gera um CSV.
    """
    json_str = '''
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
                    "parcelas": [
                        {"numero_parcela": "1", "valor|": "150"},
                        {"numero_parcela": "2", "valor|": "250"}
                    ],
                    "valor": [
                        {"saldo": "700.00", "data_processamento": "2024-06-18"},
                        {"saldo": "600.00", "data_processamento": "2024-06-19"}
                    ]
                }
            ]
        }
    }
    '''

    # Carregar JSON
    dados = carregar_json(json_str)

    # Obter lista de contratos
    contratos = dados["dados"]["contratos"]

    # Caminho do diretório e do arquivo CSV
    diretorio = Path("C:/Users/Rafael/Documents/lambda/lambda-python")
    nome_arquivo = diretorio / "contratos.csv"

    # Criar diretório se não existir
    criar_diretorio(diretorio)

    # Gerar CSV
    escrever_csv(nome_arquivo, contratos)

    print(f"Arquivo CSV criado em: {nome_arquivo}")


# Executar script apenas se chamado diretamente
if __name__ == "__main__":
    main()
