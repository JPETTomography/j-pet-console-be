import React, { useState, useEffect, useCallback } from "react"
import Plot from "react-plotly.js"
import api from "../../api"

const MeasurementHistograms = ({ measurement, referenceData = null }) => {
  const [displayMode, setDisplayMode] = useState("side-by-side")
  
  const getDefaultDateTimes = () => {
    const now = new Date()
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)
    
    const formatDateTime = (date) => {
      return date.toISOString().slice(0, 16)
    }
    
    return {
      start: formatDateTime(yesterday),
      end: formatDateTime(now)
    }
  }
  
  const defaultDates = getDefaultDateTimes()
  const [startDateTime, setStartDateTime] = useState(defaultDates.start)
  const [endDateTime, setEndDateTime] = useState(defaultDates.end)
  const [filteredData, setFilteredData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchFilteredData = useCallback(async (startDate, endDate) => {
    setIsLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()
      if (startDate) {
        params.append("start_time", new Date(startDate).toISOString())
      }
      if (endDate) {
        params.append("end_time", new Date(endDate).toISOString())
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
  }, [measurement?.id])

  useEffect(() => {
    if (measurement?.id) {
      const defaultDates = getDefaultDateTimes()
      fetchFilteredData(defaultDates.start, defaultDates.end)
    }
  }, [measurement?.id, fetchFilteredData])

  const fetchAggregatedData = async () => {
    await fetchFilteredData(startDateTime, endDateTime)
  }

  const resetTo24h = () => {
    const defaultDates = getDefaultDateTimes()
    
    setStartDateTime(defaultDates.start)
    setEndDateTime(defaultDates.end)
    setError(null)
    
    fetchFilteredData(defaultDates.start, defaultDates.end)
  }

  const showAllData = () => {
    setStartDateTime("")
    setEndDateTime("")
    setError(null)
    fetchFilteredData("", "")
  }

  const getReferenceDataByIndex = (histogramIndex) => {
    if (!referenceData) return null

    const referenceHistograms = referenceData.reference_plots || referenceData.histogram
    if (!referenceHistograms || !Array.isArray(referenceHistograms)) return null

    const refData = referenceHistograms[histogramIndex]
    return refData ? normalizeHistogramData(refData) : null
  }

  const normalizeHistogramData = (histogram) => {
    if (!histogram) return histogram
    
    const normalized = { ...histogram }
    
    // Normalize 2D content data
    if (normalized.content && Array.isArray(normalized.content) && normalized.content.length > 0) {
      const maxValue = Math.max(...normalized.content.flat().filter(val => val != null && !isNaN(val)))
      
      if (maxValue > 0) {
        normalized.content = normalized.content.map(row => 
          Array.isArray(row) ? row.map(val => (val || 0) / maxValue) : row
        )
      }
    }
    // Normalize 1D y-axis data
    else if (normalized.y && Array.isArray(normalized.y) && normalized.y.length > 0) {
      const maxValue = Math.max(...normalized.y.filter(val => val != null && !isNaN(val)))
      if (maxValue > 0) {
        normalized.y = normalized.y.map(val => (val || 0) / maxValue)
      }
    }
    
    return normalized
  }

  const getDisplayData = () => {
    if (filteredData) {
      const normalizedFilteredData = {
        ...filteredData,
        data_entry: filteredData.data_entry.map(entry => ({
          ...entry,
          data: entry.data ? entry.data.map(hist => normalizeHistogramData(hist)) : []
        }))
      }
      return normalizedFilteredData
    }
    return null
  }

  const displayData = getDisplayData()

  const hasAnyReferenceData =
    referenceData &&
    ((referenceData.reference_plots &&
      referenceData.reference_plots.length > 0) ||
      (referenceData.histogram && referenceData.histogram.length > 0))

  return (
    <div className="flex flex-col gap-4">
      <div className="bg-white p-6 shadow rounded mb-6">
        <h3 className="text-lg font-semibold mb-4">
          Filter Histograms by Date/Time
          <span className="text-sm text-gray-500 block font-normal">
            {filteredData ? `Showing filtered data (${startDateTime || 'start'} to ${endDateTime || 'end'})` : 'Showing all available data'}
          </span>
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
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? "Loading..." : "Apply Date Filter"}
            </button>

            <button
              onClick={resetTo24h}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            >
              Reset to Last 24h
            </button>

            <button
              onClick={showAllData}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Show All Data
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
              </h2>
              {histograms.map((histogram, histoIndex) => {
                const type = histogram.histo_type
                if (!histogram) return null

                const referenceDataForHisto =
                  getReferenceDataByIndex(histoIndex)

                return (
                  <div
                    key={`${entryIndex}-${histoIndex}`}
                    className="bg-white p-6 shadow rounded"
                  >
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
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
                ? "No data found for the selected date/time range. Try adjusting your date filters or resetting to the last 24 hours."
                : "No histogram data found for this measurement."}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

const PlotErrorFallback = ({ message = "Plot data not available" }) => (
  <div className="w-full flex-1 bg-gray-100 rounded flex items-center justify-center min-h-[250px]">
    <p className="text-gray-500 text-sm">{message}</p>
  </div>
)

const getBaseLayout = (title, rightMargin = 20) => ({
  height: 250,
  margin: { t: 30, l: 40, r: rightMargin, b: 40 },
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
})

const plotConfig = { responsive: true, displayModeBar: true, displaylogo: false }
const plotStyle = { width: "100%", height: "100%" }

const TH1DPlot = ({ x, y, title = "Data", color = "blue" }) => {
  if (!x || !y || !Array.isArray(x) || !Array.isArray(y)) {
    return <PlotErrorFallback />
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
        ...getBaseLayout(title),
        showlegend: false,
        bargap: 0.1
      }}
      config={plotConfig}
      useResizeHandler={true}
      style={plotStyle}
    />
  )
}

const TH2DPlot = ({ x, y, z, title = "Data" }) => {
  if (!x || !y || !z || !Array.isArray(x) || !Array.isArray(y) || !Array.isArray(z)) {
    return <PlotErrorFallback />
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
      layout={getBaseLayout(title)}
      config={plotConfig}
      useResizeHandler={true}
      style={plotStyle}
    />
  )
}

const TH1DOverlayPlot = ({ currentData, referenceData }) => {
  const isValidData = (data) => data?.x && data?.y && Array.isArray(data.x) && Array.isArray(data.y)
  
  if (!isValidData(currentData) || !isValidData(referenceData)) {
    return <PlotErrorFallback message="Overlay data not available" />
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
        ...getBaseLayout("Overlay"),
        barmode: "overlay",
        bargap: 0.1,
        legend: {
          x: 0.7,
          y: 0.9,
          bgcolor: "rgba(255,255,255,0.8)",
          font: { size: 8 }
        }
      }}
      config={plotConfig}
      useResizeHandler={true}
      style={plotStyle}
    />
  )
}

const TH2DComparisonPlot = ({ currentData, referenceData }) => {
  if (!currentData?.z || !referenceData?.z || !Array.isArray(currentData.z) || !Array.isArray(referenceData.z)) {
    return <PlotErrorFallback message="Comparison data not available" />
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
      layout={getBaseLayout("Difference", 60)}
      config={plotConfig}
      useResizeHandler={true}
      style={plotStyle}
    />
  )
}

export default MeasurementHistograms
