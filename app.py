# This Flask program defines various routes used to retrieve information from the
#   input CSV files, and passed to the index.html file which renders these
#   data in the form of various plots (please app.js in the static/ directory for
#   further details).
# These CSV files are initially loaded into various dataframes for subsequent processing.
# The high level design of all the routes is similar: for a given sample ID, retrieve
#   data from the relevant dataframes and return as a jsonified object.
import pandas as pd
from flask import Flask, render_template, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Dataframes setup
#################################################
csv_path1 = "data/Belly_Button_Biodiversity_Metadata.csv"
csv_path2 = "data/belly_button_biodiversity_otu_id.csv"
csv_path3 = "data/belly_button_biodiversity_samples.csv"
csv_path4 = "data/metadata_columns.csv"

meta_data_df = pd.read_csv(csv_path1)
out_id_df = pd.read_csv(csv_path2)
samples_df = pd.read_csv(csv_path3)
metadata_columns_df = pd.read_csv(csv_path4)

#################################################
# Flask Routes
#################################################

# This route handles the initial loading of the page by rendering index.html which
#   is located in the templates directory.
@app.route("/")
def home():
    """Render the Home Page"""
    return render_template("index.html")

# This route returns all the sample names/IDs included in the input data set.
@app.route("/sample_names")
def sample_names():
    """Return a list of sample names to be used for dropdown menu selection"""
    list_of_sample_names = []
    for i in samples_df.columns:
        list_of_sample_names.append(i)
    return jsonify(list_of_sample_names[1:])

# This route returns a list of all OTU descriptions, which are used as hover text in
#   the pie and bubble charts.
@app.route("/otu")
def otu():
    """Return a list of OTU descriptions"""
    list_of_OTU_desc = []
    for i in range(0,len(out_id_df['otu_id'])):
        list_of_OTU_desc.append(out_id_df['lowest_taxonomic_unit_found'][i])
    return jsonify(list_of_OTU_desc)

# This route returns metadata information for a given sample.  The specific info
#   returned is age, bbtype, ethinicity, gender and location.
@app.route("/metadata/<sample_id>")
def meta_data(sample_id):
    s_id=int(sample_id.split('_')[1])
    record = meta_data_df.loc[meta_data_df['SAMPLEID']==s_id]
    idx = meta_data_df.loc[meta_data_df['SAMPLEID']==s_id].index.tolist()[0]
    age = int(record.AGE)
    bbtype = record.BBTYPE[idx]
    ethnicity = record.ETHNICITY[idx]
    gender = record.GENDER[idx]
    location = record.LOCATION[idx]
    sample_metadata_dict = {'AGE': age, 'BBTYPE': bbtype, 'ETHNICITY': ethnicity,
                             'GENDER': gender, 'LOCATION': location, 'SAMPLEID': sample_id}
    return jsonify(sample_metadata_dict)

# The following route returns the weekly washing frequency which is retrieved from the
#   meta_data_df dataframe.
@app.route("/wfreq/<sample_id>")
def wash_freq(sample_id):
    """For a given sample_id, return weekly washing frequency as an integer value"""
    s_id=int(sample_id.split('_')[1])
    freq = int(meta_data_df.loc[meta_data_df['SAMPLEID']==s_id].WFREQ)
    return jsonify(freq)

# This route returns a list of dictionaries containing sorted (in descending order)
#   of lists of otu_ids and samples_values.
@app.route("/samples/<sample_id>")
def ids_values(sample_id):
    """For a given sample_id, return list of dictionaries containing sorted lists of
       otu_ids and sample_values"""
    otu_ids = []
    sample_vals = []
    return_list = []
    for i in range(0,len(samples_df[sample_id])):
              if (samples_df[sample_id][i] > 0.0):
                  otu_ids.append(i)
                  sample_vals.append(int(samples_df[sample_id][i]))
    df = pd.DataFrame ({'otu_ids': otu_ids, 'sample_values': sample_vals})
    df = df.sort_values(by=['sample_values'], ascending=False)
    otu_ids = df['otu_ids'].tolist()
    sample_vals = df['sample_values'].tolist()
    otu_dict = {'otu_ids': otu_ids, 'sample_values': sample_vals}
    return_list.append(otu_dict)
    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=False)
