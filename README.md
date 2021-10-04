# thesis-daniel-benchmark-thermo

Benchmark for thermodynamic models

Compare a thermodynamic (sofware) model with experimental data stored offline.
Multiple models are supported. The software contains three parts.
* Database  (store experimental data)
* Model (base class of a thermodynamic model)
* Comparison (execute benchmark)

## overview

* all experimental data can be found at location /Datenbank/Experimente. For each system a .json file containing all data is there.

* model results are stored in the same fashion at location /Datenbank/Modelle/"model name"

* results are stored in /Ergebnisse/"model name"/"test name".json

* all needed code is in directory ./Software/dev

## setup

1. First install all required python packages e.g. "python -m pip install -r requirements.txt"

2. Setup all needed files by running ./setup.py

3. Setup database by running ./test_database.py

4. Run model test to make shure everything is working e.g. ./test_srk_model.py


## adding new model

1. Have a look at exsisting model

2. Copy exsisting model an change needed parts

    * file name
    * class name
    * eqtype
    * mixtype
    * (implement check_model_components method if needed. otherwise default method of base class will be used)

3. Copy exsisting test file and modify setUpModule method

4. Run 1 Test to check constructor (uncomment all other lines like " @unittest.skip("Skipping Test02")")

5. Add mappings_"model name".json file that contains the mapping between benchmark names and names used in TREND

5. Run other Tests by comment skipping lines --> "# @unittest.skip("Skipping Test03")