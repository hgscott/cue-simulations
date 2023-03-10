import cobra
import pickle
import pandas as pd
import numpy as np

# Import my own CUE functions
# I want the CUE functions to eventually be their own package, but for
# now I'm just importing them from a different folder in the same
# repository
import sys
sys.path.insert(0, 'cue_utils')
from utils import (
                   atomExchangeMetabolite,
                   calculate_cue,
                   calculate_gge,
                   extract_c_fates)

# This script runs and saves the results from a COBRApy simulation of
# the E. coli full model, with varying nitrogen, carbon, and ATP
# maintenance

# Load the E. coli full model, using the built in model from COBRApy
model = cobra.io.load_model("iJO1366")

# Get the exchange reactions
c_ex_rxns = atomExchangeMetabolite(model)

########################################################################
# Varying Nitrogen
########################################################################
# Make a dataframe to store the results
data = []
# Loop through the carbon concentrations
for ammonia in range(0, 100, 10): # What range should I use?
    # Update glucose in the medium
    medium = model.medium
    medium['EX_nh4_e'] = ammonia

    # Check that there are no other media components with nitrogen
    # for r in medium:
    #     for met in model.reactions.get_by_id(r).metabolites:
    #         if 'N' in met.elements:
    #             print(r + ": " + str(met.elements['N']))
    # Cob(I)alamin (vitamin B12) is the only other metabolite with
    # nitrogen in the medium
    # Should I be setting that to 0 as well?

    for vm in np.linspace(0, 20, 5):
        # Update maintainance flux
        model.reactions.ATPM.lower_bound = vm

        # Perform FBA
        sol = model.optimize()

        # Calculate CUE
        cue = calculate_cue(sol, c_ex_rxns)

        # Calculate GGE
        gge = calculate_gge(sol, c_ex_rxns)
        
        # Save
        d = {'ammonia': ammonia, 'vm': vm, 'cue': cue, 'gge': gge}
        data.append(d)

nitrogen_results = pd.DataFrame(data)

########################################################################
# Varying Carbon
########################################################################
# Make a dataframe to store the results
data = []
# Loop through the carbon concentrations
for glc in range(10, 21):
    # Update glucose in the medium
    medium = model.medium
    medium['EX_glc__D_e'] = glc

    # Check that the export reaction bounds are 0 for all carbon sources
    # except glucose
    # for rxn in c_ex_rxns:
    #     print(rxn + ": " + str(model.reactions.get_by_id(rxn).bounds))

    for vm in np.linspace(0, 20, 5):
        # Update maintainance flux
        model.reactions.ATPM.lower_bound = vm

        # Perform FBA
        sol = model.optimize()

        # Calculate CUE
        cue = calculate_cue(sol, c_ex_rxns)

        # Calculate GGE
        gge = calculate_gge(sol, c_ex_rxns)

        # Save
        d = {'glc': glc, 'vm': vm, 'cue': cue, 'gge': gge}
        data.append(d)

carbon_results = pd.DataFrame(data)

########################################################################
# Varying ATP Maintenance
########################################################################
# Make a dataframe to store the results
data = []
for vm in np.linspace(0, 20, 5):
    # Update maintainance flux
    model.reactions.ATPM.lower_bound = vm

    # Perform FBA
    sol = model.optimize()

    # Calculate CUE
    cue = calculate_cue(sol, c_ex_rxns)

    # Calculate GGE
    gge = calculate_gge(sol, c_ex_rxns)

    # Save
    d = {'vm': vm, 'cue': cue, 'gge': gge}
    data.append(d)

vm_results = pd.DataFrame(data)

########################################################################
# Save the results
########################################################################
results = [nitrogen_results, carbon_results, vm_results]
with open('ecoli_full_model/basic_fba/results.pkl', 'wb') as f:
    pickle.dump(results, f)