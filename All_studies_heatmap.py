################### DASH ############################
import dash
from dash import html, Input, Output, dcc
import dash_bootstrap_components as dbc          
from dash.exceptions import PreventUpdate        

#################################################
import json
import csv
import os
from grassroots_csv import getRowCsv
from grass_plots import get_all_fieldtrials     
from grass_plots import get_plot
from grass_plots import dict_phenotypes
from grass_plots import numpy_data
from grass_plots import treatments
from grass_plots import plotly_plot
import operator                                   
import numpy as np                               
import requests 
#################################################
#from plotly.offline import plot as plotlyOffline

all_studies  = get_all_fieldtrials()
all_studies = json.loads(all_studies)


studiesIDs = []
names      = []
for i in range(len(all_studies['results'][0]['results'])):
        uuid  = all_studies['results'][0]['results'][i]['data']['_id']['$oid']
        name = all_studies['results'][0]['results'][i]['data']['so:name']

        if 'phenotypes' in all_studies['results'][0]['results'][i]['data']:
            studiesIDs.append(uuid)
            names.append(name)

studiesIDs.remove('619e159b87a279348474145b')           # DFW Academic Toolkit RRes, Harvest 2021   
names.remove('DFW Academic Toolkit RRes, Harvest 2021') # DFW Academic Toolkit RRes, Harvest 2021   
studiesIDs.remove('6225dfde93b7641e4b5acb85')  #  NIAB CSSL AB Glasshouse exp 
names.remove('NIAB CSSL AB Glasshouse exp ')   #
studiesIDs.remove('5dd8009ade68e75a927a8274')  #
names.remove('1st vs 3rd wheat take-all resistance trial')   #

optionsNames = [{'label': names[i], 'value':studiesIDs[i]} for i in range(len(names))]
    
optionsNames.sort(key=operator.itemgetter('label'))  # Sort list of dictionaries by key 'label'
#print("sorted: ", optionsNames)


#app = DashProxy(__name__, transforms=[ServersideOutputTransform()],external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


########################----------LAYOUT-----------############################################
app.layout = html.Div([

    #dcc.Store(id='STORE'),
    html.Div(children=[
      html.Label(['List of studies:'],style={'font-weight': 'bold', "text-align": "left"}),

      dcc.Dropdown(id='DROPDOWN1',
          options = optionsNames,
          value   = optionsNames[0]['value'],
          searchable = True,
          style={'width':"100%"},
          #search_value='',
      ),
      html.Div(id='STUDY'),
      html.Br(),
      
    ]),    
#----------------------------------------------------------------------------  
    html.Div(children=[
    dbc.Row(
      dbc.Col(
          html.Label(['Select phenotype:'],style={'font-weight': 'bold', "text-align": "left"})  ),

    ),# Row 1

    dbc.Row([
      dbc.Col(
          dcc.Dropdown( id='DROPDOWN2',
              options = [],
              #value   = 'SpkPop_CalcGbSamp_m2', 
              searchable = True,
              style={'width':"100%"},
          )   ),
      dbc.Col(
          html.Div(id='CO')  ),

     ], align="start"  ),# Row 2

     dbc.Row([
      dbc.Col(
          html.Div("Crop Ontology website:"), width=6  ),

      dbc.Col(
          html.Pre(id='web_link',
            style={'white-space': 'pre-wrap','word-break': 'break-all',
                 'text-align': 'left',
                 'padding': '12px 12px 12px 12px', 'color':'blue',
                 'margin-top': '14px'}
          )  ),

     ],  align="center"),# Row 2, 2 columns


     dbc.Row([
      dbc.Col(
          html.Div(id='CLICK'), width=3    ),   # Raw data value or N/A message
      dbc.Col(
          html.Div(id='ACC_XY'), width=3  ),
      dbc.Col(
          html.Pre(id='SEEDSTOR',
                 style={'white-space': 'pre-wrap','word-break': 'break-all',
                 'text-align': 'left',
                 'padding': '12px 12px 12px 12px', 'color':'blue',
                 'margin-top': '6px'}
          )   ),

     ],   align="center"),# Row 3. 3 Columns

          html.Br(),
          html.Button("Download CSV file", id="btn-download-txt"),
          dcc.Download(id="download-text"),
          html.Br(),
          dcc.Graph(id='HEATMAP'),
          dcc.Store(id='XYZ'),
          dcc.Store(id='ACCESSION'),
     
    ]),

#-----------------------------------------------------------------------------

        #html.Div(id='PHENOTYPE'),

#-----------------------------------------------------------------------------
#   html.Div(children=[
#       ##html.Div(id='TEST'),
#       html.Br(),
#       dcc.Graph(id='HEATMAP'),
#   ]),  


])
############################################################################################
########################--print UUID of study from dropdown 1-- #############################
@app.callback(
    Output('STUDY', 'children'),
    Input('DROPDOWN1', 'value')
)

def print_uuid(uuid):

    if uuid is None:
        raise PreventUpdate

    return ('Study uuid: {} '.format(uuid))

########################--CLEARING #############################
@app.callback(
    [Output('ACCESSION', 'clear_data'), Output('XYZ', 'clear_data')],
    Input('DROPDOWN1', 'value')
)
def clear_store(uuid):

    if uuid is None:
        raise PreventUpdate

    return True, True


########################### **update dropdown 2 (List of phenotypes)** ###########################
@app.callback(
    [Output('DROPDOWN2', 'options'),
     Output('DROPDOWN2', 'value') ],
     Input( 'DROPDOWN1', 'value') )

def update_dropdown_menu(uuid):

    if uuid is None:
        raise PreventUpdate

    single_study = get_plot(uuid)
    study_json   = json.loads(single_study)

    studies_ids =[]

    if 'phenotypes' in study_json['results'][0]['results'][0]['data']:
        studies_ids.append(uuid)
        #print("Study has phenotypes", studies_ids)


    plot_data         = study_json['results'][0]['results'][0]['data']['plots']
    phenotypes        = study_json['results'][0]['results'][0]['data']['phenotypes']

    dictTraits = dict_phenotypes(phenotypes, plot_data)  

    phenoKeys   = list(dictTraits.keys())
    phenoValues = list(dictTraits.values())

    options = [{'label': phenoValues[i], 'value':phenoKeys[i]} for i in range(len(phenoKeys))]

    value   = list(dictTraits.keys())[0]
    return options, value

###############################new Download CSV #################################################
@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'CSVs'))
    csv_data = os.path.join(path, "plot_data.csv")

    return dcc.send_file(csv_data)

################################################################################################
######################  ACTUAL HEATMAP FIGURE ################################################
@app.callback(
    #[Output('HEATMAP', 'figure'), Output('ACCESSION', 'data'), Output('ROWS','data'), Output('COLUMNS','data') ],
    [Output('HEATMAP', 'figure'), Output('ACCESSION', 'data') ],
    [Input('DROPDOWN2', 'value'), Input('DROPDOWN1', 'value')] )

def update_heatmap(phenotypeDropdown, uuid):

    if phenotypeDropdown is None:
        raise PreventUpdate


    #print("------------DASH: input HEATMAP Value 1---------", phenotypeDropdown)
    #print("------------DASH: input HEATMAP Value 2---------", uuid)

    single_study = get_plot(uuid)
    study_json   = json.loads(single_study)

    studies_ids =[]

    if 'phenotypes' in study_json['results'][0]['results'][0]['data']:
        studies_ids.append(uuid)
        print("Study has phenotypes", studies_ids)


    plot_data         = study_json['results'][0]['results'][0]['data']['plots']
    name              = study_json['results'][0]['results'][0]['data']['so:name']
    treatment_factors = study_json['results'][0]['results'][0]['data']['treatment_factors']
    total_rows        = study_json['results'][0]['results'][0]['data']['num_rows']
    total_columns     = study_json['results'][0]['results'][0]['data']['num_columns']
    phenotypes        = study_json['results'][0]['results'][0]['data']['phenotypes']
    
    phenoHeaders = []
    for key in phenotypes:
        phenoHeaders.append(key)   # for csv file. Includes non-numerical phenotypes

    print("study name :", name)

    dictTraits = dict_phenotypes(phenotypes, plot_data)  #create dictionary of phenotypes keys and their traits
    default    = list(dictTraits.keys())[0]              #use first one as default.

    print (dictTraits[default])

    phenoKeys   = list(dictTraits.keys())
    phenoValues = list(dictTraits.values())

    selected_phenotype = default
 
    print("DASH number of phenotypes observations: ", len(phenoKeys))

    matrices  = numpy_data(plot_data, phenotypes, phenotypeDropdown,
             total_rows, total_columns)

    row     = matrices[0]
    column  = matrices[1]
    row_raw = matrices[2]
    row_acc = matrices[3]
    traitName = matrices[4]
    units     = matrices[5]
    plotID   = matrices[6]

    treatment=[]
    if ( len(treatment_factors)>0):
          treatment = treatments(plot_data, row, column)
          ### print("treatments", treatment)
    #-------------------------------------------------------------
    array_rows  = []
    pheno_names = []
    extra_headers = []

    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'CSVs'))
    filename = os.path.join(path, "plot_data.csv")
    print(filename)

    #mandatory headers
    headers = ['Plot ID', 'Row', 'Column', 'Accession']

    #loop through plot and get each row for csv file
    for r in range(len(plot_data)):
            #j = int( plot_data[r]['column_index'] )
            row_list = getRowCsv(plot_data[r])
            array_rows.append(row_list)

    # if treatments available add them to the headers.
    if len(treatment_factors)>0:
        treatments_csv=[]
        for i in range(len(treatment_factors)):
            treatments_csv.append(treatment_factors[i]['treatment']['so:sameAs'])

        headers.extend(treatments_csv)

    #extra headers
    extra_headers = ['width','length','Rack','Sowing date', 'Harvest date']
    
    headers.extend(extra_headers)
    headers.extend(phenoHeaders)

    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer = csv.DictWriter(f, fieldnames = headers)
        writer.writeheader()
        writer.writerows(array_rows)

    f.close()
    #-------------------------------------------------------------


    matrix   = row_raw.reshape(row,column)

    accession  = row_acc.reshape(row,column)    #!! at this point 2D array has not been flipped!
    plotIDs    = plotID.reshape(row,column)
    
    #print("original unflipped accession---: ", np.shape(accession))

    optionsDropdown = [{'label': phenoValues[i], 'value':phenoKeys[i]} for i in range(len(phenoKeys))]
    #fig = plotly_plot(row_raw, accession, traitName, units, plotIDs, treatment)
    figure = plotly_plot(row_raw, accession, traitName, units, plotIDs, treatment)
    #return figure, accession, row, column
    return figure, accession



###########-------DISPLAY INFO ABOUT PHENOTYPE CHOSEN--------####### --> CALLS get_plot***
@app.callback(
    [Output('web_link', 'children'), Output('CO', 'children')],
    [Input('DROPDOWN2', 'value'), Input('DROPDOWN1', 'value')] )

def check_PhenoName(phenotypeSelected, uuid):

    if phenotypeSelected is None:
        raise PreventUpdate


    single_study = get_plot(uuid)
    study_json   = json.loads(single_study)
    
    #print("***************    " , )
        
    crop_ontology_url = "https://cropontology.org/term/"
    phenotype = phenotypeSelected.replace('"', "'")

    sameAsName  = study_json['results'][0]['results'][0]['data']['phenotypes'][phenotype]['definition']['variable']['so:sameAs']

    if sameAsName.startswith('CO'):
        crop_ontology_url = crop_ontology_url + sameAsName
        link = html.A(crop_ontology_url, href=crop_ontology_url, target="_blank")
        #print(link)
        sameAsName= 'Crop Ontology name:  {} '.format(sameAsName)
        return (link, sameAsName)
    else:
        #return ('Alternative name:  {} '.format(sameAsName))
        link = "term not available in cropontology.org"
        return (link, sameAsName)

###################--Print raw data of plot clicked -- #########################
@app.callback(
    Output('CLICK', 'children'),
    [Input('HEATMAP', 'clickData'), Input('HEATMAP', 'hoverData')])

def display_click_data(clickData, hoverData):

    if clickData is None:
        return 'Click on heatmaps'
    else:
        #print("----------",hoverData)
        z = clickData['points'][0]['z']
        if z == None:
            z= 'N/A'
        rawValue = 'Raw Value:  {}'.format(z)
        return  rawValue  

###########-------PRINTING TEST. Retrieve data in XYZ dcc.Store --------##################
@app.callback(
    [Output('SEEDSTOR', 'children'), Output('ACC_XY', 'children')],
    [Input('XYZ', 'data'), Input('ACCESSION', 'data'), Input('DROPDOWN2', 'value')]  
)

def printing(xy, array, phenotypeSelected):
    accession = np.flipud(array)   # Flip it to match same order as in heatmap!
    #print("---------dropdown2---", phenotypeSelected) # no really need it

    if phenotypeSelected is None:
        raise PreventUpdate

    if xy is None:
        raise PreventUpdate
    else:
        x = xy[0]
        y = xy[1]
        
    print("CHECK", xy)
    plotAccession = accession[x][y]
    if plotAccession=="nan":
        plotAccession = "Discarded" #Replace text when NaN value. 
                                    #NaN actually produces a valid value in grassroots.tool/seedstor    
    text = 'Accession: {}'.format(plotAccession)
    url= 'https://grassroots.tools/seedstor/apisearch-unified.php?query='+plotAccession
    print(url)

    try:
        response = requests.get(url)
        seedstorResponse = response.json()

    except:
        print("No response from server")
        seedstorResponse = []

    if(len(seedstorResponse) > 0):
        print(seedstorResponse[0]['idPlant'])
        idPlant  = seedstorResponse[0]['idPlant']
        seedstor = 'https://www.seedstor.ac.uk/search-infoaccession.php?idPlant='+idPlant
        print(seedstor)
        link = html.A(seedstor, href=seedstor, target="_blank")
        #text = 'Seedstore link: {}'.format(seedstor)
        return link, text

    else:
        link = "Accession not available in seedstor.ac.uk"
        #text = 'Accession: {}'.format(plotAccession) 
        return link, text


 ###################--TEST saving data in DCC.STORE -- #########################
@app.callback(
    Output('XYZ', 'data'),
    [Input('HEATMAP', 'clickData')])
    #[Input('HEATMAP', 'clickData'), Input('HEATMAP', 'hoverData')])

#def display_hoverData(clickData, hoverData):
def display_hoverData(clickData):

    if clickData is None:
        raise PreventUpdate
    else:
        #xyz = clickData['points'][0]
        #xyz = {"x", clickData['points'][0]['x']}
        xy = []
        xy = np.append(xy, int(clickData['points'][0]['y']))
        xy = np.append(xy, int(clickData['points'][0]['x']))
        #print(clickData['points'])
        rawValue = 'Raw Value  {} '.format(clickData['points'][0]['z'])
        return xy
        
       

#app.run_server(debug=True)
app.run_server(host='10.0.152.67', port='8080' ,debug=True)
