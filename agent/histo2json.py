# taken from https://github.com/JPETTomography/j-pet-console-agent/commit/6b6a7fc69211a79567ecbfd4ea80f6f05387b097
#######################################################################
# 
# Script for converting ROOT histograms to JSON format
# Add meta infomration from the file with histo definitions
# Running:
# python histo2json.py histoDef.json root_with_histo.root
# 
# First argument is the file with the definitions and meta information
# Second - ROOT file to convert
# 
# Output: JSON file with the same name as input ROOT file
# 
# TODO: handle the error if defined histogram was not found in the file
# 
#######################################################################

import sys
import ROOT
import json
import numpy
from pathlib import Path

# File with the definitions of chosen histograms to convert
histo_def_file = sys.argv[1]

# Input ROOT file 
file_name = sys.argv[2]
root_file = ROOT.TFile(file_name, "READ")

# Open and read the JSON file
with open(histo_def_file, 'r') as file:
    histo_list = json.load(file)

# Initialising the output
histo_json_all = {
    "file" : file_name,
    "histogram" : []}

# Going through the contents of the file
for histo_desc in histo_list['Plots']:
    
    # Getting the histogram
    root_dir = root_file.GetDirectory(histo_desc['Directory'])
    histogram = root_dir.Get(histo_desc['Histo'])
    # To know if histogram is 1 or 2-dimensional
    histo_class = histogram.IsA().GetName()

    histo_json = {}

    # For 1-dim
    if "TH1D" in histo_class:
        nbins = histogram.GetNbinsX()
        x = numpy.array([histogram.GetBinCenter(i) for i in range(1, nbins+1)])
        y = numpy.array([histogram.GetBinContent(i) for i in range(1, nbins+1)])
        # Output
        histo_json = {
            "Title": histo_desc['Title'],
            "Options": histo_desc['Options'],
            "Description": histo_desc['Description'],
            "Selection criteria": histo_desc['Selection criteria'],
            "x": x.tolist(),
            "y": y.tolist()
        }
        
    # For 2-dim
    if "TH2D" in histo_class:
        x_edges = numpy.array([histogram.GetXaxis().GetBinLowEdge(i) for i in range(1, histogram.GetNbinsX() + 2)])
        y_edges = numpy.array([histogram.GetXaxis().GetBinLowEdge(i) for i in range(1, histogram.GetNbinsX() + 2)])
        content = numpy.array([[histogram.GetBinContent(i, j) for j in range(1, histogram.GetNbinsY()+1)] for i in range(1, histogram.GetNbinsX()+1)])
        # Output
        histo_json = {
            "Title": histo_desc['Title'],
            "Options": histo_desc['Options'],
            "Description": histo_desc['Description'],
            "Selection criteria": histo_desc['Selection criteria'],
            "x": x_edges.tolist(),
            "y": y_edges.tolist(),
            "content": content.tolist()    
        }

    # Adding current histo to main JOSN
    histo_json_all["histogram"].append(histo_json)


# Creating the output with the same name as ROOT file
output_json_name = Path(file_name).stem+".json"
with open(output_json_name, 'w') as file:
    json.dump(histo_json_all, file)        
