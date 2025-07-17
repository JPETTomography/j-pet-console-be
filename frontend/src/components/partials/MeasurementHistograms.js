import React, { useState } from "react"
import Plot from "react-plotly.js"
import api from "../../api"

const MeasurementHistograms = ({ measurement, referenceData = null }) => {
  const [displayMode, setDisplayMode] = useState("side-by-side")
  const [startDateTime, setStartDateTime] = useState("")
  const [endDateTime, setEndDateTime] = useState("")
  const [filteredData, setFilteredData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchAggregatedData = async () => {
    if (!startDateTime && !endDateTime) {
      setError("Please select at least one date/time filter")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()
      if (startDateTime) {
        params.append("start_time", new Date(startDateTime).toISOString())
      }
      if (endDateTime) {
        params.append("end_time", new Date(endDateTime).toISOString())
      }

      const response = await api.get(
        `/measurements/${measurement.id}/histogram-data?${params}`
      )
      setFilteredData(response.data)
    } catch (err) {
      setError(err.message)
      setFilteredData(null)
    } finally {
      setIsLoading(false)
    }
  }

  // Clear filters
  const clearFilters = () => {
    setStartDateTime("")
    setEndDateTime("")
    setFilteredData(null)
    setError(null)
  }

  const getReferenceDataByIndex = (histogramIndex) => {
    let referenceHistograms = []

    if (referenceData) {
      if (referenceData.reference_plots) {
        referenceHistograms = referenceData.reference_plots
      } else if (referenceData.histogram) {
        referenceHistograms = referenceData.histogram
      }
    }

    if (!referenceHistograms || !Array.isArray(referenceHistograms)) return null

    return referenceHistograms[histogramIndex] || null
  }

  const aggregateLocalData = (measurement) => {
    if (!measurement.data_entry || measurement.data_entry.length === 0) {
      return null
    }

    if (measurement.data_entry.length === 1) {
      return {
        data_entry: [
          {
            ...measurement.data_entry[0],
            name: `${measurement.data_entry[0].name} (1 data entry)`
          }
        ],
        total_entries_aggregated: 1
      }
    }

    const firstEntry = measurement.data_entry[0]
    const aggregatedHistograms = []

    if (firstEntry.data && Array.isArray(firstEntry.data)) {
      for (let histIndex = 0; histIndex < firstEntry.data.length; histIndex++) {
        const firstHist = firstEntry.data[histIndex]
        const aggregatedHist = { ...firstHist }

        if (aggregatedHist.y && Array.isArray(aggregatedHist.y)) {
          const aggregatedY = [...aggregatedHist.y]

          for (
            let entryIndex = 1;
            entryIndex < measurement.data_entry.length;
            entryIndex++
          ) {
            const entry = measurement.data_entry[entryIndex]
            if (
              entry.data &&
              entry.data[histIndex] &&
              entry.data[histIndex].y
            ) {
              for (let i = 0; i < aggregatedY.length; i++) {
                aggregatedY[i] += entry.data[histIndex].y[i] || 0
              }
            }
          }
          const numEntries = measurement.data_entry.length
          aggregatedHist.y = aggregatedY.map((val) => val / numEntries)
        }

        if (aggregatedHist.content && Array.isArray(aggregatedHist.content)) {
          const aggregatedContent = aggregatedHist.content.map((row) => [
            ...row
          ])

          for (
            let entryIndex = 1;
            entryIndex < measurement.data_entry.length;
            entryIndex++
          ) {
            const entry = measurement.data_entry[entryIndex]
            if (
              entry.data &&
              entry.data[histIndex] &&
              entry.data[histIndex].content
            ) {
              for (let i = 0; i < aggregatedContent.length; i++) {
                for (let j = 0; j < aggregatedContent[i].length; j++) {
                  aggregatedContent[i][j] +=
                    entry.data[histIndex].content[i][j] || 0
                }
              }
            }
          }
          const numEntries = measurement.data_entry.length
          aggregatedHist.content = aggregatedContent.map((row) =>
            row.map((val) => val / numEntries)
          )
        }

        if (aggregatedHist.name || aggregatedHist.Title) {
          const originalName = aggregatedHist.name || aggregatedHist.Title
          aggregatedHist.name = originalName
          aggregatedHist.Title = `Normalized ${originalName}`
        }

        aggregatedHistograms.push(aggregatedHist)
      }
    }

    return {
      data_entry: [
        {
          id: "normalized_all",
          name: `All Data Normalized (${measurement.data_entry.length} data entries)`,
          data: aggregatedHistograms,
          acquisition_date: firstEntry.acquisition_date,
          measurement_id: measurement.id,
          histo_dir: firstEntry.histo_dir
        }
      ],
      total_entries_aggregated: measurement.data_entry.length
    }
  }

  const getDisplayData = () => {
    if (filteredData) {
      return filteredData
    }
    return aggregateLocalData(measurement)
  }

  const displayData = getDisplayData()

  const hasAnyReferenceData =
    referenceData &&
    ((referenceData.reference_plots &&
      referenceData.reference_plots.length > 0) ||
      (referenceData.histogram && referenceData.histogram.length > 0))

  return (
    <div className="flex flex-col gap-4">
      {/* Date/Time Filter UI */}
      <div className="bg-white p-6 shadow rounded mb-6">
        <h3 className="text-lg font-semibold mb-4">
          Filter Histograms by Date/Time
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date/Time
            </label>
            <input
              type="datetime-local"
              value={startDateTime}
              onChange={(e) => setStartDateTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date/Time
            </label>
            <input
              type="datetime-local"
              value={endDateTime}
              onChange={(e) => setEndDateTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex gap-2 justify-between">
          <div className="flex gap-2">
            <button
              onClick={fetchAggregatedData}
              disabled={isLoading || (!startDateTime && !endDateTime)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? "Loading..." : "Apply Filter"}
            </button>

            <button
              onClick={clearFilters}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            >
              Clear Filters
            </button>
          </div>

          {hasAnyReferenceData && (
            <button
              onClick={() =>
                setDisplayMode(
                  displayMode === "side-by-side" ? "overlay" : "side-by-side"
                )
              }
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                displayMode === "side-by-side"
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-green-600 text-white hover:bg-green-700"
              }`}
            >
              {displayMode === "side-by-side"
                ? "📊 Switch to Overlay View"
                : "📋 Switch to Side-by-Side View"}
            </button>
          )}
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>

      {/* Always display aggregated data */}
      {displayData &&
      displayData.data_entry &&
      displayData.data_entry.length > 0 ? (
        displayData.data_entry.map((de, entryIndex) => {
          const histograms = de.data
          if (!histograms || !Array.isArray(histograms)) return null

          return (
            <div key={entryIndex} className="flex flex-col gap-4">
              <h2 className="text-lg font-bold text-center">
                {de.name}
                <span className="text-sm text-gray-600 block">
                  (Aggregated from {displayData.total_entries_aggregated || 1}{" "}
                  data entries)
                </span>
              </h2>
              {histograms.map((histogram, histoIndex) => {
                const type = histogram.histo_type
                if (!histogram) return null

                const referenceDataForHisto =
                  getReferenceDataByIndex(histoIndex)

                let gridCols
                if (!hasAnyReferenceData) {
                  gridCols = "lg:grid-cols-12"
                } else if (displayMode === "overlay") {
                  gridCols = "lg:grid-cols-12"
                } else {
                  gridCols = "lg:grid-cols-12"
                }

                return (
                  <div
                    key={`${entryIndex}-${histoIndex}`}
                    className="bg-white p-6 shadow rounded"
                  >
                    <div
                      className={`grid grid-cols-1 ${gridCols} gap-6 items-start`}
                    >
                      <div className="lg:col-span-4">
                        <h3 className="font-semibold text-lg mb-3">
                          {histogram.Title || `Histogram ${histoIndex + 1}`}
                        </h3>

                        {histogram.Description && (
                          <div className="mb-4">
                            <h4 className="font-medium text-gray-700 mb-2">
                              Description:
                            </h4>
                            <p
                              className="text-sm text-gray-600 leading-relaxed"
                              dangerouslySetInnerHTML={{
                                __html: histogram.Description
                              }}
                            />
                          </div>
                        )}

                        {histogram["Selection criteria"] && (
                          <div className="mb-4">
                            <h4 className="font-medium text-gray-700 mb-2">
                              Obtained with selection criteria:
                            </h4>
                            <p className="text-sm text-gray-600 leading-relaxed">
                              {histogram["Selection criteria"]}
                            </p>
                          </div>
                        )}
                      </div>

                      {displayMode === "overlay" &&
                      hasAnyReferenceData &&
                      referenceDataForHisto ? (
                        <div className="lg:col-span-8 flex flex-col">
                          {type === "TH1D" ||
                          referenceDataForHisto.histo_type === "TH1D" ? (
                            <h4 className="font-medium text-gray-700 mb-2 text-center">
                              Current vs Reference
                              <span className="text-xs text-gray-500 block">
                                🔵 Current | 🔴 Reference
                              </span>
                            </h4>
                          ) : (
                            <h4 className="font-medium text-gray-700 mb-2 text-center">
                              Difference (Current - Reference)
                              <span className="text-xs text-gray-500 block">
                                🔴 Positive | 🔵 Negative
                              </span>
                            </h4>
                          )}
                          {(type === "TH1D" ||
                            referenceDataForHisto.histo_type === "TH1D") && (
                            <div className="w-full flex-1 overflow-hidden">
                              <TH1DOverlayPlot
                                currentData={{ x: histogram.x, y: histogram.y }}
                                referenceData={{
                                  x: referenceDataForHisto.x,
                                  y: referenceDataForHisto.y
                                }}
                              />
                            </div>
                          )}

                          {(type === "TH2D" ||
                            referenceDataForHisto.histo_type === "TH2D") && (
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
                                  z:
                                    referenceDataForHisto.content ||
                                    referenceDataForHisto.z
                                }}
                              />
                            </div>
                          )}
                        </div>
                      ) : (
                        <>
                          <div
                            className={`${
                              hasAnyReferenceData
                                ? "lg:col-span-4"
                                : "lg:col-span-8"
                            } flex flex-col`}
                          >
                            <h4 className="font-medium text-gray-700 mb-2 text-center">
                              Current Data
                            </h4>
                            {type === "TH1D" && (
                              <div className="w-full flex-1 overflow-hidden">
                                <TH1DPlot
                                  x={histogram.x}
                                  y={histogram.y}
                                  title="Current"
                                />
                              </div>
                            )}

                            {type === "TH2D" && (
                              <div className="w-full flex-1 overflow-hidden">
                                <TH2DPlot
                                  x={histogram.x}
                                  y={histogram.y}
                                  z={histogram.content}
                                  title="Current"
                                />
                              </div>
                            )}
                          </div>

                          {hasAnyReferenceData && (
                            <div className="lg:col-span-4 flex flex-col">
                              <h4 className="font-medium text-gray-700 mb-2 text-center">
                                Reference Data
                              </h4>
                              {referenceDataForHisto ? (
                                <>
                                  {(type === "TH1D" ||
                                    referenceDataForHisto.histo_type ===
                                      "TH1D") && (
                                    <div className="w-full flex-1 overflow-hidden">
                                      <TH1DPlot
                                        x={referenceDataForHisto.x}
                                        y={referenceDataForHisto.y}
                                        title="Reference"
                                        color="red"
                                      />
                                    </div>
                                  )}

                                  {(type === "TH2D" ||
                                    referenceDataForHisto.histo_type ===
                                      "TH2D") && (
                                    <div className="w-full flex-1 overflow-hidden">
                                      <TH2DPlot
                                        x={referenceDataForHisto.x}
                                        y={referenceDataForHisto.y}
                                        z={
                                          referenceDataForHisto.content ||
                                          referenceDataForHisto.z
                                        }
                                        title="Reference"
                                      />
                                    </div>
                                  )}
                                </>
                              ) : (
                                <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[350px]">
                                  <p className="text-gray-500 text-sm">
                                    No reference data available
                                  </p>
                                </div>
                              )}
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )
        })
      ) : (
        <div className="bg-white p-6 shadow rounded">
          <div className="text-center py-8">
            <p className="text-gray-500 text-lg">No histogram data available</p>
            <p className="text-gray-400 text-sm mt-2">
              {startDateTime || endDateTime
                ? "No data found for the selected date/time range. Try adjusting your filters or clearing them to see all available data."
                : "No data entries found for this measurement."}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

const TH1DPlot = ({ x, y, title = "Data", color = "blue" }) => {
  if (!x || !y || !Array.isArray(x) || !Array.isArray(y)) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Plot data not available</p>
      </div>
    )
  }

  return (
    <Plot
      data={[
        {
          x,
          y,
          type: "bar",
          marker: {
            color: color,
            line: { color: "rgba(0,0,0,0.3)", width: 0.5 }
          },
          name: title
        }
      ]}
      layout={{
        height: 250,
        margin: { t: 30, l: 40, r: 20, b: 40 },
        title: { text: title, font: { size: 12 } },
        xaxis: {
          title: { text: "X Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        yaxis: {
          title: { text: "Y Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        font: { size: 10 },
        showlegend: false,
        bargap: 0.1
      }}
      config={{ responsive: true, displayModeBar: true, displaylogo: false }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
    />
  )
}

const TH2DPlot = ({ x, y, z, title = "Data" }) => {
  if (
    !x ||
    !y ||
    !z ||
    !Array.isArray(x) ||
    !Array.isArray(y) ||
    !Array.isArray(z)
  ) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Plot data not available</p>
      </div>
    )
  }

  return (
    <Plot
      data={[
        {
          z: z,
          x: x,
          y: y,
          type: "heatmap",
          colorscale: "Viridis",
          showscale: false,
          name: title
        }
      ]}
      layout={{
        height: 250,
        margin: { t: 30, l: 40, r: 20, b: 40 },
        title: { text: title, font: { size: 12 } },
        xaxis: {
          title: { text: "X Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        yaxis: {
          title: { text: "Y Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        font: { size: 10 }
      }}
      config={{ responsive: true, displayModeBar: true, displaylogo: false }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
    />
  )
}

const TH1DOverlayPlot = ({ currentData, referenceData }) => {
  if (
    !currentData?.x ||
    !currentData?.y ||
    !referenceData?.x ||
    !referenceData?.y ||
    !Array.isArray(currentData.x) ||
    !Array.isArray(currentData.y) ||
    !Array.isArray(referenceData.x) ||
    !Array.isArray(referenceData.y)
  ) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Overlay data not available</p>
      </div>
    )
  }

  return (
    <Plot
      data={[
        {
          x: currentData.x,
          y: currentData.y,
          type: "bar",
          marker: {
            color: "rgba(0, 100, 255, 0.7)",
            line: { color: "rgba(0, 100, 255, 1)", width: 0.5 }
          },
          name: "Current",
          opacity: 0.7
        },
        {
          x: referenceData.x,
          y: referenceData.y,
          type: "bar",
          marker: {
            color: "rgba(255, 0, 0, 0.7)",
            line: { color: "rgba(255, 0, 0, 1)", width: 0.5 }
          },
          name: "Reference",
          opacity: 0.7
        }
      ]}
      layout={{
        height: 250,
        margin: { t: 30, l: 40, r: 20, b: 40 },
        title: { text: "Overlay", font: { size: 12 } },
        xaxis: {
          title: { text: "X Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        yaxis: {
          title: { text: "Y Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        font: { size: 10 },
        barmode: "overlay",
        bargap: 0.1,
        legend: {
          x: 0.7,
          y: 0.9,
          bgcolor: "rgba(255,255,255,0.8)",
          font: { size: 8 }
        }
      }}
      config={{ responsive: true, displayModeBar: true, displaylogo: false }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
    />
  )
}

const TH2DComparisonPlot = ({ currentData, referenceData }) => {
  if (
    !currentData?.z ||
    !referenceData?.z ||
    !Array.isArray(currentData.z) ||
    !Array.isArray(referenceData.z)
  ) {
    return (
      <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
        <p className="text-gray-500 text-sm">Comparison data not available</p>
      </div>
    )
  }

  const diffZ = currentData.z.map((row, i) => {
    if (!Array.isArray(row)) return []
    return row.map((val, j) => {
      const refRow = referenceData.z[i]
      const refVal =
        Array.isArray(refRow) && refRow[j] !== undefined ? refRow[j] : 0
      return (val || 0) - refVal
    })
  })

  return (
    <Plot
      data={[
        {
          z: diffZ,
          x: currentData.x,
          y: currentData.y,
          type: "heatmap",
          colorscale: "RdBu",
          showscale: true,
          name: "Difference",
          colorbar: {
            title: "Current - Reference",
            titlefont: { size: 8 },
            tickfont: { size: 8 },
            len: 0.5
          }
        }
      ]}
      layout={{
        height: 250,
        margin: { t: 30, l: 40, r: 60, b: 40 },
        title: { text: "Difference", font: { size: 12 } },
        xaxis: {
          title: { text: "X Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        yaxis: {
          title: { text: "Y Axis", font: { size: 10 } },
          tickfont: { size: 8 }
        },
        font: { size: 10 }
      }}
      config={{ responsive: true, displayModeBar: true, displaylogo: false }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
    />
  )
}

export default MeasurementHistograms
