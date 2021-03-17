# thesis-daniel-benchmark-thermo

Benchmark for thermodynamic models

Compare a thermodynamic (sofware) model with experimental data stored offline.
Multiple models shall be supported.

## characteristics in Excel table

* convert Excel table to database (possibly use JSON for first experiments)

## Intended Usage

* holy grail: create report for model with all supported component combinations
  * calculate assessment criteria

* software model provides characteristics for two components
  * SW model has a Python interface (components/desired characteristic,parameters in, data out)
  * output data should be stored for re-use -> use DB with same layout as for offline data

* database query: two components (methane, ethane), characteristic (e.g. isothermal phase diagram)
    optional: temperature or pressure
  return x or x,y or x,y,z data
