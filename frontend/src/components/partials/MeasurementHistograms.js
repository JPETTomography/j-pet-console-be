import React, { useState } from 'react';
import Plot from 'react-plotly.js';

const MeasurementHistograms = ({ measurement, referenceData = null }) => {
  const [displayMode, setDisplayMode] = useState('side-by-side');

  const getReferenceDataByIndex = (histogramIndex) => {
    let referenceHistograms = [];
    
    if (referenceData) {
      if (referenceData.reference_plots) {
        referenceHistograms = referenceData.reference_plots;
      } else if (referenceData.histogram) {
        referenceHistograms = referenceData.histogram;
      }
    }
    
    if (!referenceHistograms || !Array.isArray(referenceHistograms)) return null;
    
    return referenceHistograms[histogramIndex] || null;
  };

  const hasAnyReferenceData = referenceData && (
    (referenceData.reference_plots && referenceData.reference_plots.length > 0) ||
    (referenceData.histogram && referenceData.histogram.length > 0)
  );

  return (
    <div className="flex flex-col gap-4">
      {hasAnyReferenceData && (
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setDisplayMode(displayMode === 'side-by-side' ? 'overlay' : 'side-by-side')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              displayMode === 'side-by-side'
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {displayMode === 'side-by-side' ? '📊 Switch to Overlay View' : '📋 Switch to Side-by-Side View'}
          </button>
        </div>
      )}
      
      {measurement.data_entry.map((de, entryIndex) => {
        const histograms = de.data;
        if (!histograms || !Array.isArray(histograms)) return null;

        return (
          <div key={entryIndex} className="flex flex-col gap-4">
            <h2 className="text-lg font-bold text-center">
              Data Entry {entryIndex + 1} - {de.name}
            </h2>
            {histograms.map((histogram, histoIndex) => {
              const type = histogram.histo_type;
              if (!histogram) return null;

              const referenceDataForHisto = getReferenceDataByIndex(histoIndex);
              
              let gridCols;
              if (!hasAnyReferenceData) {
                gridCols = "lg:grid-cols-12";
              } else if (displayMode === 'overlay') {
                gridCols = "lg:grid-cols-12";
              } else {
                gridCols = "lg:grid-cols-12";
              }

              return (
                <div key={`${entryIndex}-${histoIndex}`} className="bg-white p-6 shadow rounded">
                  <div className={`grid grid-cols-1 ${gridCols} gap-6 items-start`}>
                    <div className="lg:col-span-4">
                      <h3 className="font-semibold text-lg mb-3">
                        {histogram.Title || `Histogram ${histoIndex + 1}`}
                      </h3>
                      
                      {histogram.Description && (
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-700 mb-2">Description:</h4>
                          <p 
                            className="text-sm text-gray-600 leading-relaxed"
                            dangerouslySetInnerHTML={{ __html: histogram.Description }}
                          />
                        </div>
                      )}
                      
                      {histogram["Selection criteria"] && (
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-700 mb-2">Obtained with selection criteria:</h4>
                          <p className="text-sm text-gray-600 leading-relaxed">
                            {histogram["Selection criteria"]}
                          </p>
                        </div>
                      )}
                    </div>

                    {displayMode === 'overlay' && hasAnyReferenceData && referenceDataForHisto ? (
                      <div className="lg:col-span-8 flex flex-col">
                        {(type === 'TH1D' || referenceDataForHisto.histo_type === 'TH1D') ? (
                          <h4 className="font-medium text-gray-700 mb-2 text-center">
                            Current vs Reference 
                            <span className="text-xs text-gray-500 block">🔵 Current | 🔴 Reference</span>
                          </h4>
                        ) : (
                          <h4 className="font-medium text-gray-700 mb-2 text-center">
                            Difference (Current - Reference)
                            <span className="text-xs text-gray-500 block">🔴 Positive | 🔵 Negative</span>
                          </h4>
                        )}
                        {(type === 'TH1D' || referenceDataForHisto.histo_type === 'TH1D') && (
                          <div className="w-full flex-1 overflow-hidden">
                            <TH1DOverlayPlot 
                              currentData={{ x: histogram.x, y: histogram.y }}
                              referenceData={{ x: referenceDataForHisto.x, y: referenceDataForHisto.y }}
                            />
                          </div>
                        )}

                        {(type === 'TH2D' || referenceDataForHisto.histo_type === 'TH2D') && (
                          <div className="w-full flex-1 overflow-hidden">
                            <TH2DComparisonPlot 
                              currentData={{ 
                                x: histogram.x, 
                                y: histogram.y, 
                                z: histogram.content 
                              }}
                              referenceData={{ 
                                x: referenceDataForHisto.x, 
                                y: referenceDataForHisto.y, 
                                z: referenceDataForHisto.content || referenceDataForHisto.z 
                              }}
                            />
                          </div>
                        )}
                      </div>
                    ) : (
                      <>
                        <div className={`${hasAnyReferenceData ? 'lg:col-span-4' : 'lg:col-span-8'} flex flex-col`}>
                          <h4 className="font-medium text-gray-700 mb-2 text-center">Current Data</h4>
                          {type === 'TH1D' && (
                            <div className="w-full flex-1 overflow-hidden">
                              <TH1DPlot x={histogram.x} y={histogram.y} title="Current" />
                            </div>
                          )}

                          {type === 'TH2D' && (
                            <div className="w-full flex-1 overflow-hidden">
                              <TH2DPlot x={histogram.x} y={histogram.y} z={histogram.content} title="Current" />
                            </div>
                          )}
                        </div>

                        {hasAnyReferenceData && (
                          <div className="lg:col-span-4 flex flex-col">
                            <h4 className="font-medium text-gray-700 mb-2 text-center">Reference Data</h4>
                            {referenceDataForHisto ? (
                              <>
                                {(type === 'TH1D' || referenceDataForHisto.histo_type === 'TH1D') && (
                                  <div className="w-full flex-1 overflow-hidden">
                                    <TH1DPlot 
                                      x={referenceDataForHisto.x} 
                                      y={referenceDataForHisto.y} 
                                      title="Reference"
                                      color="red"
                                    />
                                  </div>
                                )}

                                {(type === 'TH2D' || referenceDataForHisto.histo_type === 'TH2D') && (
                                  <div className="w-full flex-1 overflow-hidden">
                                    <TH2DPlot 
                                      x={referenceDataForHisto.x} 
                                      y={referenceDataForHisto.y} 
                                      z={referenceDataForHisto.content || referenceDataForHisto.z} 
                                      title="Reference"
                                    />
                                  </div>
                                )}
                              </>
                            ) : (
                              <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
                                <p className="text-gray-500 text-sm">No reference data available</p>
                              </div>
                            )}
                          </div>
                        )}
                      </>
                    )}

                  </div>
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

const TH1DPlot = ({ x, y, title = "Data", color = "blue" }) => {
  if (!x || !y || !Array.isArray(x) || !Array.isArray(y)) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Plot data not available</p>
      </div>
    );
  }

  return (
    <Plot
      data={[
        {
          x,
          y,
          type: 'scatter',
          mode: 'lines+markers',
        marker: { color: color, size: 3 },
        line: { shape: 'linear', width: 1 },
        name: title,
      },
    ]}
    layout={{
      height: 250,
      margin: { t: 30, l: 40, r: 20, b: 40 },
      title: { text: title, font: { size: 12 } },
      xaxis: { title: { text: 'X Axis', font: { size: 10 } }, tickfont: { size: 8 } },
      yaxis: { title: { text: 'Y Axis', font: { size: 10 } }, tickfont: { size: 8 } },
      font: { size: 10 },
      showlegend: false,
    }}
    config={{ responsive: true, displayModeBar: true, displaylogo: false }}
    useResizeHandler={true}
    style={{ width: "100%", height: "100%" }}
  />
  );
};

const TH2DPlot = ({ x, y, z, title = "Data" }) => {
  if (!x || !y || !z || !Array.isArray(x) || !Array.isArray(y) || !Array.isArray(z)) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Plot data not available</p>
      </div>
    );
  }

  return (
    <Plot
      data={[
        {
          z: z,
          x: x,
          y: y,
          type: 'heatmap',
          colorscale: 'Viridis',
          showscale: false,
          name: title,
        },
      ]}
      layout={{
        height: 250,
        margin: { t: 30, l: 40, r: 20, b: 40 },
        title: { text: title, font: { size: 12 } },
        xaxis: { title: { text: 'X Axis', font: { size: 10 } }, tickfont: { size: 8 } },
        yaxis: { title: { text: 'Y Axis', font: { size: 10 } }, tickfont: { size: 8 } },
        font: { size: 10 },
      }}
      config={{ responsive: true, displayModeBar: true, displaylogo: false }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
    />
  );
};

const TH1DOverlayPlot = ({ currentData, referenceData }) => {
  if (!currentData?.x || !currentData?.y || !referenceData?.x || !referenceData?.y ||
      !Array.isArray(currentData.x) || !Array.isArray(currentData.y) ||
      !Array.isArray(referenceData.x) || !Array.isArray(referenceData.y)) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Overlay data not available</p>
      </div>
    );
  }

  return (
    <Plot
      data={[
        {
          x: currentData.x,
          y: currentData.y,
          type: 'scatter',
          mode: 'lines+markers',
          marker: { color: 'blue', size: 3 },
          line: { shape: 'linear', width: 1 },
          name: 'Current',
        },
        {
          x: referenceData.x,
          y: referenceData.y,
          type: 'scatter',
          mode: 'lines+markers',
          marker: { color: 'red', size: 3 },
          line: { shape: 'linear', width: 1 },
          name: 'Reference',
        },
    ]}
    layout={{
      height: 250,
      margin: { t: 30, l: 40, r: 20, b: 40 },
      title: { text: 'Overlay', font: { size: 12 } },
      xaxis: { title: { text: 'X Axis', font: { size: 10 } }, tickfont: { size: 8 } },
      yaxis: { title: { text: 'Y Axis', font: { size: 10 } }, tickfont: { size: 8 } },
      font: { size: 10 },
      legend: { 
        x: 0.7, 
        y: 0.9, 
        bgcolor: 'rgba(255,255,255,0.8)',
        font: { size: 8 }
      },
    }}
    config={{ responsive: true, displayModeBar: true, displaylogo: false }}
    useResizeHandler={true}
    style={{ width: "100%", height: "100%" }}
  />
  );
};

const TH2DComparisonPlot = ({ currentData, referenceData }) => {
  if (!currentData?.z || !referenceData?.z || !Array.isArray(currentData.z) || !Array.isArray(referenceData.z)) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Comparison data not available</p>
      </div>
    );
  }

  const diffZ = currentData.z.map((row, i) => {
    if (!Array.isArray(row)) return [];
    return row.map((val, j) => {
      const refRow = referenceData.z[i];
      const refVal = (Array.isArray(refRow) && refRow[j] !== undefined) ? refRow[j] : 0;
      return (val || 0) - refVal;
    });
  });

  return (
    <Plot
      data={[
        {
          z: diffZ,
          x: currentData.x,
          y: currentData.y,
          type: 'heatmap',
          colorscale: 'RdBu',
          showscale: true,
          name: 'Difference',
          colorbar: {
            title: 'Current - Reference',
            titlefont: { size: 8 },
            tickfont: { size: 8 },
            len: 0.5,
          },
        },
      ]}
      layout={{
        height: 250,
        margin: { t: 30, l: 40, r: 60, b: 40 },
        title: { text: 'Difference', font: { size: 12 } },
        xaxis: { title: { text: 'X Axis', font: { size: 10 } }, tickfont: { size: 8 } },
        yaxis: { title: { text: 'Y Axis', font: { size: 10 } }, tickfont: { size: 8 } },
        font: { size: 10 },
      }}
      config={{ responsive: true, displayModeBar: true, displaylogo: false }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
    />
  );
};

export default MeasurementHistograms;
