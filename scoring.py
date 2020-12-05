import pandas as pd
import ast
import numpy as np

def generate_efficacy(patient_response, mech_symptom_data):
    # where patient_response is of the format dict[symptom] = label
    #       - this is the user input ranging from -1 to 1
    # mech_symptom_data is of the format dict[mechanic][symptom][field] = value
    # the resulting dict from this function, is what will be called when scoring each mech in a drug for ranking

    efficacy_dict = dict()

    for (mechanic, symptom_dict) in mech_symptom_data.items():
        symptom_keys = symptom_dict.keys()
        # filter to only those in patient response
        s_keys = [s for s in symptom_keys if s in patient_response.keys()]

        high_score = 0
        if len(s_keys) > 0:
            # get mech-symptom weights filtered to those in patient response
            m_s_scores = [mech_symptom_data[mechanic][k]['max_score'] for k in s_keys]
            # get max_id
            max_ids = [mech_symptom_data[mechanic][k]['max_id'] for k in s_keys]
            # get labels
            labels = [patient_response[k] for k in s_keys]
            # zip together lists and take product
            pairings = zip(m_s_scores, labels)
            products = [n1*n2 for (n1, n2) in pairings]
            product_tuples = [(products[i], (mechanic, max_ids[i])) for i in range(len(products))]
            #print("unsorted", products)
            # take highest score, label, product
            sorted_products = sorted(product_tuples, key=lambda x: x[0])
            #print("sorted", sorted_products)
            high_score = sorted_products.pop()
        efficacy_dict[mechanic] = high_score
    
    return efficacy_dict

def get_mechanics(drug_name, drugdb):
    # this should return a list of mechanics for the given drug name
    """Looks up drug name using pandas, then finds corresponding mechanics list
    and converts it from a pandas series containing one string to a list"""
    return ast.literal_eval(drugdb.loc[drugdb["name"] == drug_name.lower()]["mechanics"].tolist()[0])

def score_drug(drug_name, efficacy_dict, drugdb, similarities, drugs, anchor):
    """Returns a tuple, where first element is sum of efficiacy scores,
    second element is a list of tuples with (target, pmid)"""
    # this makes no assumptions about the format of drug, but if its a list of mechanics that is formatted
    # to make key access work smoothly with efficacy_dict, that is ideal

    drug = get_mechanics(drug_name, drugdb)

    eff_scores = []
    ids = []
    for mechanic in drug:
        score = efficacy_dict[mechanic][0]*similarities[anchor][drugs.index(drug_name)]
        eff_scores.append(score)
        ids.append(efficacy_dict[mechanic][1])
    return sum(eff_scores), ids



