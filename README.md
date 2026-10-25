# face-keypoints

Семестровый проект по дисциплине «Технологии и инструментарий машинного обучения»:
система анализа изображений лица для определения ключевых точек и оценки пропорций.

Специалист загружает фото клиента, система ставит 8 точек и считает индексы пропорций
(ширина носа и рта относительно межзрачкового расстояния, симметрия).
Основная метрика — NME, нормированная на межзрачковое расстояние.

## Точки (нумерация 300W с 1)

| точка | откуда |
|---|---|
| центр левого глаза | среднее 37–42 |
| центр правого глаза | среднее 43–48 |
| кончик носа | 31 |
| крылья носа | 32 и 36 |
| уголки рта | 49 и 55 |
| подбородок | 9 |

## Данные

Набор 300W (https://ibug.doc.ic.ac.uk/resources/300-W/): 600 снимков, 300 indoor и 300 outdoor,
у каждого 68 точек. Сами картинки (~2 ГБ) в git не хранятся, их нужно положить в `data/raw/300w/`.

## Структура

```
data/
  raw/300w/            исходные .png и .pts (01_Indoor, 02_Outdoor), не в git
  raw/landmarks_300w.csv            все 600 строк: путь, subset, размер, x1..y68
  raw/landmarks_300w.manifest.json  число строк, sha256, источник
  interim/initial.csv  исходная часть для EDA и обучения (360 строк)
  incoming/batch_01..04.csv  порции «новых» данных по 60 строк
notebooks/eda.ipynb    разведочный анализ
reports/figures/       графики из EDA
reports/pr2_results.md сводка для отчета по ПР2
docs/diagrams/         C4 и UML диаграммы (.puml и .png)
src/facekp/data/       make_csv.py, split.py
```

## Запуск

```bash
uv venv --python 3.11 .venv          # или python -m venv .venv
source .venv/Scripts/activate        # Windows (Git Bash)
pip install -r requirements.txt

python src/facekp/data/make_csv.py   # .pts -> data/raw/landmarks_300w.csv
python src/facekp/data/split.py      # initial.csv + 4 порции в data/incoming

jupyter nbconvert --to notebook --execute --inplace notebooks/eda.ipynb
```

Диаграммы рендерятся через PlantUML:

```bash
java -jar plantuml.jar -tpng docs/diagrams/*.puml
```
