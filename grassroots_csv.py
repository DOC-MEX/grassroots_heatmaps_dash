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


    # additional headers
    if  ( 'harvest_date' in row_json ):
        harvest_date = row_json['harvest_date']
    if  ( 'sowing_date' in row_json ):
        sowing_date  = row_json['sowing_date']
 
    width        = row_json['width']
    length       = row_json['length']

    extra_headers  = ['width','length','Rack','Sowing date', 'Harvest date']
    extra          = [width, length, rack, sowing_date, harvest_date]

    variables.extend(headers)
    variables.extend(extra_headers)
    raw_value.extend(mandatory)
    raw_value.extend(extra)

    dict_row = dict(zip(variables, raw_value))
    return dict_row

