import json
import numpy as np

import csv
import os
from functools import reduce
#####################################################################
def lookup_keys(dictionary, keys, default=None):
     return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)

#######################################################################
def search_phenotype_index(list_observations, value):

    for i in range(len(list_observations)):

        dic            = list_observations[i]
        phenotype_name = lookup_keys(dic, 'phenotype.variable')
        if  (phenotype_name == value ):
              return i
 
###################################################################
def searchPhenotypeTrait(listPheno, value):

    name = listPheno[value]['definition']['trait']['so:name']

    return name

###################################################################
def searchPhenotypeUnit(listPheno, value):

    name = listPheno[value]['definition']['unit']['so:name']

    return name

############################################################################
def search_phenotype(list_observations, value):

    found = False
    for i in range(len(list_observations)):

        dic            = list_observations[i]
        phenotype_name = lookup_keys(dic, 'phenotype.variable')
        if  (phenotype_name == value ):
              return True
              break

    return found

#############################################################################
def getRowCsv(row_json):

    # Get mandatory values
    plotID = row_json['rows'][0]['study_index']
    row    = row_json['row_index']
    column = row_json['column_index']
    rack = ''
    harvest_date = ''
    sowing_date  = ''

    if  ( 'discard' in row_json['rows'][0] ):
        accession = "Discarded"
    if  ( 'blank' in row_json['rows'][0] ):
        accession = ''
    if  ( 'material' in row_json['rows'][0] ):
        accession = row_json['rows'][0]['material']['accession']
        rack      = row_json['rows'][0]['rack_index']


    # Get rest of phenotype raw values
    variables = []  # header names
    raw_value = []    
    if  ( 'observations' in row_json['rows'][0] ):
        observations = row_json['rows'][0]['observations']
        for i in range(len(observations)):
            variables.append(observations[i]['phenotype']['variable'])
            raw_value.append(observations[i]['raw_value'])


    if  ( 'treatments' in row_json['rows'][0] ):
        treatments = row_json['rows'][0]['treatments']
        for i in range(len(treatments)):
            variables.append(treatments[i]['so:sameAs'])
            raw_value.append(treatments[i]['label'])



    #mandatory headears and values
    headers   = ['Plot ID', 'Row', 'Column', 'Accession']
    mandatory = [plotID, row, column, accession]

    # addional headers
    if  ( 'harvest_date' in row_json ):
        harvest_date = row_json['harvest_date']
    if  ( 'sowing_date' in row_json ):
        sowing_date  = row_json['sowing_date']
    width        = row_json['width']
    length       = row_json['length']

    extra_headers  = ['width','length','Rack','Sowing date', 'Harvest date']
    extra          = [width, length, rack, sowing_date, harvest_date]

    
    #walking_order = row_json['walking_order']
    #if walking_order is None:
    

    ##variables[:0] = headers
    variables.extend(headers)
    variables.extend(extra_headers)
    raw_value.extend(mandatory)
    raw_value.extend(extra)

    dict_row = dict(zip(variables, raw_value))
    return dict_row


############################################################################
############################################################################
'''
Create CSV file from JSON study data
'''
def create_CSV(json, pheno, treatment_factors ,current_name, total_rows, total_columns):
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'CSVs'))
    filename = os.path.join(path, "test.csv")
    print(filename)

    array_rows  = []
    pheno_names = []
    for key in pheno:
        pheno_names.append(key)    #from full list of phenotypes on top of study file


    for r in range(len(json)):
            i = int( json[r]['row_index']    )
            j = int( json[r]['column_index'] )
            #print("row, column:", i, j)
            row_list = getRowCsv(json[r])
            array_rows.append(row_list)

    headers = ['Plot ID', 'Row', 'Column', 'Accession']


        
    # Check if there are treatments
    if len(treatment_factors)>0:
        treatments = []
        for i in range(len(treatment_factors)):
            treatments.append(treatment_factors[i]['treatment']['so:sameAs'])
            
        headers.extend(treatments)

    # add names of phenotypes
    headers.extend(pheno_names)


    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer = csv.DictWriter(f, fieldnames = headers)
        writer.writeheader()
        writer.writerows(array_rows)
    
    f.close()





    traitName = searchPhenotypeTrait(pheno, current_name)
    unit      = searchPhenotypeUnit( pheno, current_name)

    dtID= np.dtype(('U', 4))

    row_raw   = np.array([])
    matrix    = np.array([])
    row_acc   = np.array([])
    accession = np.array([])
    plotsIds  = np.array([], dtype=dtID)  #format of strings

    matrices = []
    
    num_columns = 1
    
    row    = 1
    column = 1
    #loop throght observations in the same fashion as in old JS code. 
    for j in range(len(json)):
        if ( int( json[j]['row_index'] ) == row ):
            if  (int( json[j]['column_index'] ) == column): 
               if column > num_columns:
                   num_columns = column

               if   ( 'discard' in json[j]['rows'][0] ):
                    row_raw  = np.append(row_raw, np.nan )  # use NaN for discarded plots
                    row_acc  = np.append(row_acc, np.nan )  
                    plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )
               elif ( 'blank' in json[j]['rows'][0] ):
                    row_raw  = np.append(row_raw, np.nan )  # use NaN for discarded plots
                    row_acc  = np.append(row_acc, np.nan )  
                    plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )
     
               elif ( 'observations' in json[j]['rows'][0] ):
                    if( search_phenotype(json[j]['rows'][0]['observations'], current_name) ):
                        indexCurrentPhenotype = search_phenotype_index (json[j]['rows'][0]['observations'], current_name)
                        row_raw  = np.append(row_raw, json[j]['rows'][0]['observations'][indexCurrentPhenotype]['raw_value']) 
                        row_acc  = np.append(row_acc, json[j]['rows'][0]['material']['accession']) 
                        plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )
                    else:
                        row_raw  = np.append(row_raw, np.inf )  # use infinity for N/A data
                        row_acc  = np.append(row_acc, json[j]['rows'][0]['material']['accession'])  
                        plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )
               else:
                  if('rows' in json[j]):      # when plots have rows but no observations!!
                        row_raw = np.append(row_raw, np.inf ) #   use infinity for N/A data
                        row_acc = np.append(row_acc, json[j]['rows'][0]['material']['accession'])  
                        plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )  
         
  
               column+=1
               columns = json[j]['column_index']#

        elif ( int( json[j]['row_index'] ) > row  ):
            if column > num_columns:
                   num_columns = column

            if   ( 'discard' in json[j]['rows'][0] ):
                    row_raw  = np.append(row_raw, np.nan )  
                    row_acc  = np.append(row_acc, np.nan )  
                    plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )
            elif ( 'blank' in json[j]['rows'][0] ):
                    row_raw  = np.append(row_raw, np.nan )  # use NaN for discarded plots
                    row_acc  = np.append(row_acc, np.nan )  
                    plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )

            elif ( 'observations' in json[j]['rows'][0] ):
                    if( search_phenotype(json[j]['rows'][0]['observations'], current_name) ):
                        indexCurrentPhenotype = search_phenotype_index (json[j]['rows'][0]['observations'], current_name)
                        row_raw  = np.append(row_raw, json[j]['rows'][0]['observations'][indexCurrentPhenotype]['raw_value'])  
                        row_acc  = np.append(row_acc, json[j]['rows'][0]['material']['accession']) 
                        plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )
                    else:
                        row_raw  = np.append(row_raw, np.inf )
                        row_acc  = np.append(row_acc, json[j]['rows'][0]['material']['accession'])  
                        plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )
            else:
                  if('rows' in json[j]):      # when plots have rows but no observations!!
                        row_raw = np.append(row_raw, np.inf ) #   use infinity for N/A data
                        row_acc = np.append(row_acc, json[j]['rows'][0]['material']['accession'])  
                        plotsIds = np.append(plotsIds, json[j]['rows'][0]['study_index'] )  
            

            row+=1
            column=2
            columns = json[j]['column_index']


    column = num_columns-1
    
    if column<columns:
        column=columns #correction when only 1 row.
    
    #print("number of plots and shape check", len(json), row, column, row*(column) )
    if (len(json) != row*column):
        print("NOT rectangular")
        if(total_columns!=None):
           if(column<total_columns):
               column=total_columns
        # fit odd shape plot into bigger rectangular plot.
        #row_raw  = oddShapeValues(   json, row, column, current_name)
        #row_acc  = oddShapeAccession(json, row, column, current_name)
        #plotsIds = oddShapePlotID(   json, row, column, current_name)
   
    #matrices.append(row)
    #matrices.append(column)
    #matrices.append(row_raw)
    #matrices.append(row_acc)
    #matrices.append(traitName)
    #matrices.append(unit)
    #matrices.append(plotsIds)
    
    #return matrices

