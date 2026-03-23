# exio-to-bw

Import Exiobase v3 into brightway2

Quick script to import tables of the Multi-Regional Input-Output database Exiobase version 3 into the python-baseed Brightway (v2.5) LCA framework. 

Testing different calculation methods too.

# Run the code

Works with 2022 pxp version downloaded [here](https://zenodo.org/records/18937492) 


1. Import the HIO sheet from txt file (A matrix), transform it so it fits LCA format
2. Import extensions from another txt file (F matrix)
3. Select only some extensions and create a LCIA method 
4. Create a brighway-format dictionary with all activities and exchanges
5. Write the dictionary as bw database
6. Do calculations
 
# Notes and limitations

- Steps 4 and 5 take quite long time.
- This code is only for the IO table monetary units.
- Right now only three GHG emissions are included in the calculation.
- Final demand not included either. 


# This was done mainly as a test, code is messy

