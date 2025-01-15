# taken from https://github.com/JPETTomography/j-pet-console-agent/commit/6b6a7fc69211a79567ecbfd4ea80f6f05387b097

import sys
import ROOT
import json
import numpy
from pathlib import Path

def fill_in_histo(x,y,histo_desc):
    histo_json = {
        "Title": histo_desc['Title'],
        "Options": histo_desc['Options'],
        "Description": histo_desc['Description'],
        "Selection criteria": histo_desc['Selection criteria'],
        "x": x.tolist(),
        "y": y.tolist()
    }
    return histo_json

def process_th1d(histogram, histo_desc):
    nbins = histogram.GetNbinsX()
    x = numpy.array([histogram.GetBinCenter(i)
                    for i in range(1, nbins+1)])
    y = numpy.array([histogram.GetBinContent(i)
                    for i in range(1, nbins+1)])
    histo_json = fill_in_histo(x, y, histo_desc)
    return histo_json

def process_th2d(histogram, histo_desc):
    x_edges = numpy.array([histogram.GetXaxis().GetBinLowEdge(
        i) for i in range(1, histogram.GetNbinsX() + 2)])
    y_edges = numpy.array([histogram.GetXaxis().GetBinLowEdge(
        i) for i in range(1, histogram.GetNbinsX() + 2)])
    content = numpy.array([[histogram.GetBinContent(i, j) for j in range(
        1, histogram.GetNbinsY()+1)] for i in range(1, histogram.GetNbinsX()+1)])
    histo_json = fill_in_histo(x_edges, y_edges, histo_desc)
    histo_json["content"] = content.tolist()
    return histo_json

def root_to_json(histo_list, root_file):
    for histo_desc in histo_list['Plots']:
        root_dir = root_file.GetDirectory(histo_desc['Directory'])
        histogram = root_dir.Get(histo_desc['Histo'])
        histo_class = histogram.IsA().GetName()
        histo_json = {}
        if "TH1D" in histo_class:
            histo_json = process_th1d(histogram, histo_desc)
            histo_json['histo_type'] = "TH1D"
        if "TH2D" in histo_class:
            histo_json = process_th2d(histogram, histo_desc)
            histo_json['histo_type'] = "TH2D"
        histo_json['histo_dir'] = root_dir.GetName()
    return histo_json

def root_file_to_json(histo_def_file, file_name):
    root_file = ROOT.TFile(file_name, "READ")
    with open(histo_def_file, 'r') as file:
        histo_list = json.load(file)
    histo_json_all = {
        "file": file_name,
        "histogram": []}
    histo_json = root_to_json(histo_list, root_file)
    histo_json_all["histogram"].append(histo_json)
    root_file.Close()
    return histo_json_all

if __name__ == "__main__":
    histo_def_file = sys.argv[1]
    file_name = sys.argv[2]
    output_json_name = Path(file_name).stem+".json"
    histo_in_json = root_file_to_json(histo_def_file, file_name)
    with open(output_json_name, 'w') as file:
        json.dump(histo_in_json, file)
