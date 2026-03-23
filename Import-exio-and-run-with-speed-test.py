import pandas as pd
import numpy as np
import bw2calc as bc
import bw2data as bd
import bw2io as bi
import os
os.getcwd() 
os.chdir("/Users/massimo/Documents/AAU/Research/PyLCA/bw2.5-scripts/import-exio-bw25")

bd.projects.set_current('test_exio3_import_2026')

# Fresh start

#bd.databases
#del bd.databases['ee_exio22pxp']
#del bd.databases['exio22pxp']

# the exiobase tables ar etaken from here: https://zenodo.org/records/18937492
# for this tutorial the 2022 table is used

# Import original IO matrix
A_raw = pd.read_table('IOT_2022_pxp/A.txt')

# Extract metadata
countries = A_raw['region'].drop_duplicates().iloc[2:].tolist()
sectors = list(A_raw.iloc[2:,1].drop_duplicates())
activities = [ x + '-' + y for x in countries for y in sectors] # created ad hoc ad IDs for activities, by combining country and sector names
activities_units = (['MEUR' for i in range(0,len(activities))])

# quick check
len(sectors)
len(activities)
len(activities) == len(activities_units)

# put the IO matrix in LCA format

A_IO = A_raw.iloc[2:,2:].astype('float').values
I = np.identity(len(A_IO))
A_ = I - A_IO
A = -A_
np.fill_diagonal(A, -A.diagonal()) # then change back again, but only the diagonal
print(A[0:,:5])

len(A[:,1])
len(A[1,:])
len([i for i in A[:,1] if i != 0]) # non-zero values
len([i for i in A[:,1] if i == 0]) # zero values
A.shape

len([i for i in A[:,1] if i != 0]) # non-zero values
len([i for i in A[:,:] if i == 0]) # zero values
np.count_nonzero(A)/(9800*9800)


# Import environemental extensions, create the biosphere database and write to brightway

F_raw = pd.read_table("IOT_2022_pxp/air_emissions/F.txt", header=[0,1], index_col=[0])

ee_names = list(F_raw.index.values) # ee means "environmental extension"

# Decide which ones to use for testing, to avoid having to write too many biosphere flows and exchanges in brightway

ee_set = ["CO2 - combustion - air",
            "CH4 - combustion - air",
            "N2O - combustion - air"]

# Create a biosphere matrix with only the selected flows, to be used for writing the biosphere database in brightway
F = F_raw.loc[ee_set]

B = F.to_numpy()

B.shape
len(B[:,1])
len(B[1,:]) == len(A[1,:])
len([i for i in B[:,1] if i != 0]) # non-zero values
len([i for i in B[:,1] if i == 0]) # zero values

# Extract metadata on units.
F_units = pd.read_table("IOT_2022_pxp/air_emissions/unit.txt", header=[0], index_col=[0])
F_units_set = F_units.loc[ee_set]
F_units_set
F_units_set.loc['CO2 - combustion - air']['unit']
F_units_set.iloc[1]['unit']

F_units_set.iloc[:,0].values[2]
F_units_set.values[1][0] # check the units look correct, should be kg

# Create a dictionary and write in brightway database.
ee_dbname = 'ee_exio22pxp'

#bio_exio_d = {('ee_exio22pxp', ee_set[i].replace(" ", "")): {'name': ee_set[i], 'unit':F_units_set.iloc[:,0].values[i], 'type': 'biosphere'} for i in range(len(ee_set))}
bio_exio_d = {(ee_dbname, ee_set[i]): {'name': ee_set[i], 'unit':F_units_set.iloc[:,0].values[i], 'type': 'biosphere'} for i in range(len(ee_set))}
bio_exio3 = bd.Database(ee_dbname)
bio_exio3.write(bio_exio_d)

bd.databases

for act in bio_exio3:
    act.as_dict()
    act.key

char_fact = [[act.key, 1.0] for act in bio_exio3] # characterisation factors (all set to 1 for testing)

CF_method_id = (ee_dbname, 'Carbon footprint', 'Climate Change', 'Exiobase Testing')
CF_method = bd.Method(CF_method_id)
CF_method.register()
CF_method.validate(char_fact)
CF_method.write(char_fact)
CF_method.load()



# Write A and B matrices to brightway in one go

dbname = 'exio22pxp'

## First create a dictionary per each activity

act_dicts = []

for a in range(0, len(activities)):
    if a % 111 == 0:
        print(f"Processing activity {a+1}/{len(activities)}: {activities[a]}")
    A_technosphere_a = [{'input': (dbname, activities[i]), 'amount': A[:,a][i], 'unit' : activities_units[i], 'type': 'technosphere'} for i in range(0, len(activities)) if (i != a and A[:,a][i] !=0)]
    A_production_a = [{'input': (dbname, activities[i]), 'amount': A[:,a][i],  'unit' : activities_units[i], 'type': 'production'} for i in range(0, len(activities)) if i == a]
    B_biosphere_a = [{'input': ('ee_exio22pxp', ee_set[i]), 'amount': B[:,a][i],  'unit': F_units_set.iloc[i]['unit'], 'type': 'biosphere'} for i in range(0, len(ee_set)) if B[:,a][i] !=0]
    exchanges_a = A_production_a + A_technosphere_a + B_biosphere_a
    act_dict_a = {(dbname, activities[a]): {'name': activities[a], 'unit': activities_units[a], 'exchanges': exchanges_a}}
    act_dicts.append(act_dict_a)


## Then merge all activity-dictionaries in a larger dictionary
exio_dict = {}
for d in act_dicts:
    exio_dict.update(d)
len(exio_dict)

# test it worked
exio_dict[(dbname, activities[1])] # check the exchanges for one activity, should be a list of dicts with input, amount, unit and type

## Finally write to brightway
if dbname in bd.databases: 
    print('database extist already, will now be removed')
    del(bd.databases[dbname])

t_exio = bd.Database(dbname)
t_exio.write(exio_dict)

# Doing checks on the written database

#myact = t_exio.random()
myactcode = [act['code'] for act in t_exio if ("Wheat" in act['name'] and "AT" in act['name'])][0]
myact = t_exio.get(myactcode)
myact['name']

len(list(myact.exchanges()))
len(list(myact.exchanges())) == len(exio_dict[(dbname, activities[activities.index(myact['name'])])]['exchanges']) 

for exc in list(myact.exchanges())[0:10]:
    print(exc)

for exc in list(myact.exchanges()):
        if exc['type'] == 'biosphere':
            print(exc)

for exc in list(myact.exchanges()):
        if exc['type'] == 'production':
            print(exc)

# seems alright
import time
start = time.time()
functional_unit = {myact: 1}
mymethod = ('ee_exio22pxp', 'Carbon footprint', 'Climate Change', 'Exiobase Testing')
lca = bc.LCA(functional_unit, mymethod)
lca.lci() # To allow for reusing results? Not sure
lca.lcia()
lca.score
end = time.time()

print("Elapsed time:", end - start, "seconds")



CFs = [1] * len(ee_set)

len(ee_set) == len(CFs)

C = np.matrix(np.zeros((len(CFs), len(CFs))))
C_diag = np.matrix(CFs)
np.fill_diagonal(C, C_diag)
C.shape

# check with normal matrix operation
f = np.zeros(len(A))
act_index = activities.index(myact['name'])

f[act_index] = 1 # functional unit
io_score = np.sum(C.dot(B.dot((np.linalg.inv(A_)).dot(f)))) # matrix operation

print('brighway calculated lca score is', lca.score, 
      'manually calculated numpy score is',  io_score,
      'difference is', lca.score - io_score)


from bw2calc import JacobiGMRESLCA, LCA

import time
start = time.time()

lca2 = JacobiGMRESLCA(
    demand={myact: 1},
    method=mymethod,
    rtol=1e-6
)
lca2.lci()
lca2.lcia()
print(lca2.score)

end = time.time()

print("Elapsed time:", end - start, "seconds")


import time
start = time.time()
io_score = np.sum(C.dot(B.dot((np.linalg.inv(A_)).dot(f)))) # matrix operation
print(io_score)
end = time.time()
print("Elapsed time:", end - start, "seconds")