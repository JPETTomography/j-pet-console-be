import { React, useState, useCallback, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useParams } from "react-router-dom"

import Svg from "../partials/Svg"

import Page from "../partials/Page"
import {
  measurementTabs,
  measurementContextContent
} from "../../utils/measurements"
import Tabs from "../partials/Tabs"
import Tag from "../partials/Tag"
import ButtonGroup from "../partials/ButtonGroup"
import ButtonBack from "../partials/ButtonBack"
import ButtonEdit from "../partials/ButtonEdit"

import FetchLoading from "../partials/FetchLoading"
import FetchError from "../partials/FetchError"
import api from "../../api"

const Measurement = () => {
  const navigate = useNavigate()

  const { measurement_id } = useParams()

  const [measurement, setMeasurement] = useState({})
  const [referenceData, setReferenceData] = useState(null)
  const [context, setContext] = useState(measurementTabs[0].id)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchMeasurement = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await api.get(`/measurements/${measurement_id}`)
      setMeasurement(response.data)

      if (response.data.experiment_id) {
        try {
          const refResponse = await api.get(
            `/experiments/${response.data.experiment_id}/reference-data`
          )
          console.log("Reference data fetched:", refResponse.data)
          setReferenceData(refResponse.data.reference_data)
        } catch (refError) {
          console.log("No reference data available for this experiment")
          setReferenceData(null)
        }
      }
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/")
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }, [measurement_id, navigate])

  useEffect(() => {
    fetchMeasurement()
  }, [fetchMeasurement, measurement_id])

  return (
    <Page>
      <ButtonBack path={`/experiments/${measurement.experiment_id}`}>
        Back to the experiment
      </ButtonBack>
      {loading ? (
        <FetchLoading />
      ) : error ? (
        <FetchError error={error} fetchFun={fetchMeasurement} />
      ) : (
        <>
          <div className="flex flex-col gap-8">
            <h1>{measurement.name}</h1>

            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="flex justify-between items-start gap-6">
                <div className="flex-1">
                  <p className="text-xl mb-4">{measurement.description}</p>
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Svg src="/icons/command-line.svg" className="w-6 h-6" />
                      {measurement.directory}
                    </div>
                    {measurement.radioisotopes.length > 0 && (
                      <div className="flex gap-2 text-sm">
                        <Svg src="/icons/beaker.svg" className="w-6 h-6" />
                        <ul className="list-none flex flex-col">
                          {measurement.radioisotopes.map(
                            (radioisotope, index) => (
                              <li key={index}>{radioisotope.name}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-col gap-4">
                  <ul className="list-none empty:hidden flex flex-wrap gap-2">
                    {measurement.tags.map((tag, index) => (
                      <li key={index}>
                        <Tag {...tag} />
                      </li>
                    ))}
                  </ul>
                  <ButtonGroup>
                    <ButtonEdit
                      path={`/experiments/${measurement.experiment_id}/measurements/${measurement.id}/edit`}
                    />
                  </ButtonGroup>
                </div>
              </div>
            </div>

            <Tabs
              tabs={measurementTabs}
              active={context}
              changeContext={setContext}
            />
            {measurementContextContent(
              context,
              measurement,
              setMeasurement,
              referenceData
            )}
          </div>
        </>
      )}
    </Page>
  )
}

export default Measurement
