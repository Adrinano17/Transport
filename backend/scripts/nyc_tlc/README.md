# NYC TLC Taxi — Data Preparation & EDA

## Download data

Yellow Taxi Parquet (recommended):

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Example — January 2024:

```powershell
mkdir -Force ..\..\..\data\raw\nyc_tlc
curl -L -o ..\..\..\data\raw\nyc_tlc\yellow_tripdata_2024-01.parquet `
  https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
```

## Install extras

```powershell
cd backend
pip install pandas pyarrow matplotlib seaborn scikit-learn
```

## Run pipeline

```powershell
cd backend\scripts\nyc_tlc
python prepare_data.py -i ..\..\..\data\raw\nyc_tlc\yellow_tripdata_2024-01.parquet
```

Outputs → `data/processed/nyc_tlc/`:

- `cleaned_full.parquet`
- `train.parquet`, `test.parquet`
- `X_train.parquet`, `X_test.parquet`, `y_train.parquet`, `y_test.parquet`
- `preparation_report.json`

## Run EDA

On raw file (runs light cleaning first):

```powershell
python eda.py -i ..\..\..\data\raw\nyc_tlc\yellow_tripdata_2024-01.parquet --prepare-first
```

On cleaned file:

```powershell
python eda.py -i ..\..\..\data\processed\nyc_tlc\cleaned_full.parquet
```

Figures → `data/reports/nyc_tlc/eda/`
