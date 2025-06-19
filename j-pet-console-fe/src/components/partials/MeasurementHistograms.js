// eslint-disable-next-line
import Chart from "chart.js/auto"; // must have, although not used
import { Line } from "react-chartjs-2";

const MeasurementHistograms = (props) => {
  const { measurement } = props;

  return (
    <div className="grid lg:grid-cols-2 gap-4">
      {measurement.data_entry.map((de, index) => {
        return (
          de.data && (
            <div className="flex justify-center h-80">
              <Line
                key={index}
                data={{
                  labels: de.data.x,
                  datasets: [
                    {
                      type: "bar",
                      label: "Measurement",
                      data: de.data.y,
                    },
                    {
                      label: "Reference",
                      data: de.data.y,
                    },
                  ],
                }}
                options={{
                  plugins: {
                    title: {
                      color: "#1e293b",
                      display: true,
                      font: { size: 20 },
                      padding: {
                        top: 10,
                      },
                      text: de.data.Title,
                    },
                  },
                }}
              />
            </div>
          )
        );
      })}
    </div>
  );
};

export default MeasurementHistograms;
