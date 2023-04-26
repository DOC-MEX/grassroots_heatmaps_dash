import os
import csv
import operator
#############################################################################
def getRowCsv(row_json):
    # Get mandatory values
    plotID = row_json['rows'][0]['study_index']
    row    = row_json['row_index']
    column = row_json['column_index']
    rack = ''
    harvest_date = ''
    sowing_date  = ''
    replicate    = ''

    if  ( 'discard' in row_json['rows'][0] ):
        accession = "Discarded"
    elif  ( 'blank' in row_json['rows'][0] ):
        accession = 'Discarded'
    elif  ( 'material' in row_json['rows'][0] ):
        accession = row_json['rows'][0]['material']['accession']
        rack      = row_json['rows'][0]['rack_index']
        replicate = row_json['rows'][0]['replicate']

    
    # Get rest of phenotype raw values
    phenotypeNames = []  
    raw_value = []
    if  ( 'observations' in row_json['rows'][0] ):
        observations = row_json['rows'][0]['observations']
        for i in range(len(observations)):
            if  ( 'corrected_value' in observations[i] ):                
                raw_value.append(observations[i]['corrected_value'])
                phenotypeNames.append(observations[i]['phenotype']['variable'])  
            elif ( 'raw_value' in observations[i] ):            
                raw_value.append(observations[i]['raw_value'])
                phenotypeNames.append(observations[i]['phenotype']['variable'])  
            
            if ( 'date' in observations[i] ):
                only_date = observations[i]['date'].split('T')[0]
                phenotype_date = phenotypeNames[i] + " " + only_date
                if 'end_date' in observations[i]:
                        end_date = observations[i]['end_date'].split('T')[0]
                        phenotype_date = phenotypeNames[i] + " " + only_date + " " + end_date                        
                phenotypeNames[i] = phenotype_date # Replace name                
            
            sample = observations[i]['index']
            #Check if sample exists and add it to the name      
            if sample==1 and (i < len(observations)-1):                                    
                    current_name = observations[i]['phenotype']['variable']                    
                    
                    for j in range(i+1, len(observations)):
                        name = observations[j]['phenotype']['variable'] # J
                        check_sample2 = observations[j]['index']  # J
                        if current_name == name:                            
                            if 'date' in observations[j]:
                                if 'date' not in observations[i]:
                                    only_date=None
                                date = observations[j]['date'].split('T')[0]
                                if date==only_date:
                                    if check_sample2==2 and date==only_date:                                                        
                                        phenotype_sample = name + " " + only_date + " sample_1" 
                                        phenotypeNames[i] = phenotype_sample                                        
                                        break
                                    
                            elif 'date' not in observations[j]:
                                if 'date' in observations[i]:
                                    break                                
                                if check_sample2==2:                                                                                            
                                    phenotype_sample1 = name + " sample_1" 
                                    phenotypeNames[i] = phenotype_sample1                                    
                                    break                                                

            if  sample>1:                
                phenotype_sample = phenotypeNames[i] + " sample_" + str(sample)
                phenotypeNames[i] = phenotype_sample
    

    if  ( 'treatments' in row_json['rows'][0] ):
        treatments = row_json['rows'][0]['treatments']
        for i in range(len(treatments)):            
            raw_value.append(treatments[i]['label'])
            phenotypeNames.append(treatments[i]['so:sameAs'])



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

    extra_headers  = ['Width','Length','Rack','Sowing date', 'Harvest date', 'Replicate']
    extra          = [width, length, rack, sowing_date, harvest_date, replicate]


    ##variables[:0] = headers
    phenotypeNames.extend(headers)
    phenotypeNames.extend(extra_headers)
    raw_value.extend(mandatory)
    raw_value.extend(extra)

    dict_row = dict(zip(phenotypeNames, raw_value))
    return dict_row


###################################################################
def create_CSV(plot_data, phenotypes, treatment_factors, plot_id):
    array_rows  = []
    pheno_headers = list(phenotypes.keys())
    new_headers = pheno_headers.copy()
    #CHECK IF DATES OR SAMPLES EXIST. if so, add them to the name
    for data in plot_data:
        if 'observations' in data['rows'][0]:
            observations = data['rows'][0]['observations']
            for i, observation in enumerate(observations):                
                phenoname = observation['phenotype']['variable']                
                #Check if date exists and add it to the name
                if 'date' in observation:                    
                    only_date = observation['date'][:10]                    
                    dated_name = phenoname + " " + only_date
                    if 'end_date' in observation:
                        end_date = observation['end_date'][:10]
                        dated_name = phenoname + " " + only_date + " " + end_date                        
                    if phenoname in new_headers:                        
                        index = new_headers.index(phenoname)
                        new_headers[index] = dated_name 
                        phenoname = dated_name                          
                    elif dated_name not in new_headers:                        
                        new_headers.append(dated_name)
                        phenoname = dated_name
                        index = new_headers.index(phenoname)

                sample = observation['index'] #index always exists when no samples used and it is 1
                # To check if current observation has sample on its name...
                # ... you need to check if its next observation (if any) has a index>2                                
                if sample==1 and (i < len(observations)-1):                
                    phenoname = observation['phenotype']['variable']
                    for j in range(i+1, len(observations)):
                        next_name = observations[j]['phenotype']['variable']                        
                        if phenoname == next_name:
                            check_sample2 = observations[j]['index']                            
                            if 'date' in observations[j]:
                                date = observations[j]['date'].split('T')[0]                            
                                if check_sample2==2 and date==only_date:
                                    phenotype_dated = phenoname + " " + only_date
                                    if phenotype_dated in new_headers:
                                        new_headers[index] = phenotype_dated + " sample_1"                                        
                            if 'date' not in observations[j]:   
                                if check_sample2==2:                    
                                    if phenoname in new_headers:
                                        index = new_headers.index(phenoname)                                        
                                        new_headers[index] = phenoname + " sample_1"                                         
                                        
                if  sample>1:                    
                    if 'date' in observation:                        
                        only_date = observation['date'][:10]                                            
                        sampled_name = phenoname + " sample_" + str(sample)
                        new_headers[index] = sampled_name #Replace name with sampled name
                    if 'date' not in observation:                        
                        sampled_name = phenoname + " sample_" + str(sample)
                        new_headers.append(sampled_name)

    #name = plot_id + '.csv'
    #path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'filedownload/Files'))
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'CSVs'))
    filename = os.path.join(path, "plot_data.csv")
    #filename = os.path.join(path, name)
    print(filename)

    # Actual order of columns given by these headers
    #headers = ['Plot ID', 'Row', 'Column', 'Accession']
    headers = ['Plot ID','Sowing date','Harvest date','Width','Length','Row','Column','Replicate','Rack','Accession']

    #loop through plot and get each row for csv file
    for r in range(len(plot_data)):
            i = int( plot_data[r]['row_index'] )
            j = int( plot_data[r]['column_index'] )
            row_list = getRowCsv(plot_data[r])
            #if(i==1 and j==3):
            #    print("CHECK**********",row_list)
            array_rows.append(row_list)

    #extra_headers = ['width','length','Rack','Replicate','Sowing date', 'Harvest date']
    #headers.extend(extra_headers)

    # if treatments available add them to the headers.
    if len(treatment_factors)>0:
        treatments_csv=[]
        for i in range(len(treatment_factors)):
            treatments_csv.append(treatment_factors[i]['treatment']['so:sameAs'])

        headers.extend(treatments_csv)

    # initial headers completed add headers of observation listed in phenotypes key from json file
    #headers.extend(phenoHeaders)
    headers.extend(new_headers)

    array_rows.sort(key=operator.itemgetter('Plot ID'))

    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer = csv.DictWriter(f, fieldnames = headers)
        writer.writeheader()
        writer.writerows(array_rows)

    f.close()

