"""Exporta el modelo final desde MLflow a servicio/modelo.joblib.

    python servicio/exportar_modelo.py            # la corrida con candidato=final
    python servicio/exportar_modelo.py <run_id>   # una corrida concreta

Se corre desde psets/proyecto/, con MLFLOW_TRACKING_URI apuntando al servidor.
modelo.joblib no se sube al repositorio: se regenera con este script.
"""

import sys

import joblib
import mlflow
import mlflow.sklearn

EXPERIMENTO = "m5-demanda-CA_1"
RUTA_SALIDA = "servicio/modelo.joblib"


def run_id_final():
    experimento = mlflow.get_experiment_by_name(EXPERIMENTO)
    corridas = mlflow.search_runs(
        experiment_ids=[experimento.experiment_id],
        filter_string="tags.candidato = 'final'",
    )
    if len(corridas) != 1:
        raise SystemExit(f"Se esperaba una corrida con candidato=final y hay {len(corridas)}")
    return corridas.loc[0, "run_id"]


if __name__ == "__main__":
    run_id = sys.argv[1] if len(sys.argv) > 1 else run_id_final()
    modelo = mlflow.sklearn.load_model(f"runs:/{run_id}/modelo")
    joblib.dump(modelo, RUTA_SALIDA)
    print(f"Modelo de la corrida {run_id} guardado en {RUTA_SALIDA}")
