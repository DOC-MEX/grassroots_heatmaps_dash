################### DASH ############################
import dash
#import dash_core_components as dcc  #DEPRECATED
from dash import dcc
#import dash_html_components as html   #DEPRECATED
from dash import html
from dash import Input, Output
#################################################
import json
from grass_plots import get_all_fieldtrials     # NEW!
from grass_plots import get_plot
from grass_plots import dict_phenotypes
from grass_plots import numpy_data
from grass_plots import treatments
from grass_plots import plotly_plot
import operator                                    #NEW!

#################################################
import plotly.express as px
from plotly.offline import plot as plotlyOffline

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

optionsNames = [{'label': names[i], 'value':studiesIDs[i]} for i in range(len(names))]
    
optionsNames.sort(key=operator.itemgetter('label'))  # Sort list of dictionaries by key 'label'
#print("sorted: ", optionsNames)


app = dash.Dash(__name__)


###################################################################################
app.layout = html.Div([

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
      html.Label(['Choose phenotype:'],style={'font-weight': 'bold', "text-align": "left"}),

      dcc.Dropdown(id='DROPDOWN2',
          options = [],
          #value   = options[0]['value'],
          searchable = True,
          style={'width':"70%"},
      ),
      html.Div(id='PHENOTYPE'),
      html.Div(id='CO')
      
    ]), 
#-----------------------------------------------------------------------------
   html.Div([
       html.Br(),
       dcc.Graph(id='HEATMAP')
   ]),  


])

################################################################################################
########################### **update dropdown 2 (List of phenotypes)** ###########################
@app.callback(
    [Output('DROPDOWN2', 'options'),
     Output('DROPDOWN2', 'value')],
     Input( 'DROPDOWN1', 'value') )

def update_dropdown_menu(uuid):

    print("UPDATE DROPDOWN 2 menu with study", uuid)
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
    #options2 = options
    #print("original", options)
    #print("***************************************")
    #options2.sort(key=operator.itemgetter('value'))
    #print("sorted", options2)

    value   = list(dictTraits.keys())[0]

    return options, value

################################################################################################
######################  ACTUAL HEATMAP FIGURE ################################################
@app.callback(
    Output('HEATMAP', 'figure'),
     [Input('DROPDOWN2', 'value'), Input('DROPDOWN1', 'value')] )

def update_heatmap(phenotypeDropdown, uuid):


    print("------------DASH: input HEATMAP Value 1---------", phenotypeDropdown)
    print("------------DASH: input HEATMAP Value 2---------", uuid)
    #    print("------------DASH: input Value 3---------", defaultPheno)

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

    matrix   = row_raw.reshape(row,column)

    accession  = row_acc.reshape(row,column)
    plotIDs    = plotID.reshape(row,column)


    optionsDropdown = [{'label': phenoValues[i], 'value':phenoKeys[i]} for i in range(len(phenoKeys))]
    #fig = plotly_plot(row_raw, accession, traitName, units, plotIDs, treatment)
    figure = plotly_plot(row_raw, accession, traitName, units, plotIDs, treatment)
    return figure


########################--print UUID of study-- #####################################
@app.callback(
    Output('STUDY', 'children'),
    Input('DROPDOWN1', 'value')
)

def build_graph(data_chosen):
    return ('Study uuid: {} '.format(data_chosen))

###########-------Display selected value from dropdown menu--------##################
@app.callback(
    Output('PHENOTYPE', component_property='children'),
    Input('DROPDOWN2', 'value')
)

def build_graph(data_chosen):
    return ('Phenotype actual name:  {} '.format(data_chosen))

###########---------------##################
@app.callback(
    Output('CO', component_property='children'),
    [Input('DROPDOWN2', 'value'), Input('DROPDOWN1', 'value')] )

def fina_name(phenotypeSelected, uuid):

    single_study = get_plot(uuid)
    study_json   = json.loads(single_study)

    #phenotype = "'"+phenotypeSelected+"'"
    phenotype = phenotypeSelected.replace('"', "'")

    COname  = study_json['results'][0]['results'][0]['data']['phenotypes'][phenotype]['definition']['variable']['so:sameAs']

    return ('Phenotype CO name:  {} '.format(COname))


app.run_server(debug=True)
