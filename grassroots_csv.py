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
    variables = []  # header names
    raw_value = []
    if  ( 'observations' in row_json['rows'][0] ):
        observations = row_json['rows'][0]['observations']
        for i in range(len(observations)):
            if  ( 'corrected_value' in observations[i] ):
                variables.append(observations[i]['phenotype']['variable'])  # correction!!
                raw_value.append(observations[i]['corrected_value'])
            elif ( 'raw_value' in observations[i] ):
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

    extra_headers  = ['Width','Length','Rack','Sowing date', 'Harvest date', 'Replicate']
    extra          = [width, length, rack, sowing_date, harvest_date, replicate]



    ##variables[:0] = headers
    variables.extend(headers)
    variables.extend(extra_headers)
    raw_value.extend(mandatory)
    raw_value.extend(extra)

    dict_row = dict(zip(variables, raw_value))
    return dict_row


###################################################################
def create_CSV(plot_data, phenotypes, treatment_factors, plot_id):
    array_rows  = []
    pheno_names = []
    extra_headers = []

    phenoHeaders = []
    for key in phenotypes:
        phenoHeaders.append(key)

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
    headers.extend(phenoHeaders)

    array_rows.sort(key=operator.itemgetter('Plot ID'))

    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer = csv.DictWriter(f, fieldnames = headers)
        writer.writeheader()
        writer.writerows(array_rows)

    f.close()

