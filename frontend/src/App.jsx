import SymptomsForm from "./components/SymptomsForm";
import ResultPage from "./components/ResultPage";
import bgImage from "./assets/medical.jpg";
import axios from "axios";
import { useState } from "react";

function App() {
  const [results, setResults] = useState(null);
  const [plotBase64, setPlotBase64] = useState(null); // changed from plotUrl
  const [userData, setUserData] = useState(null);

  const handleSubmit = async (formData) => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/analyze", {
        symptoms: formData.symptoms,
      });
      setResults(res.data.results);
      setPlotBase64(res.data.plotUrl);
      setUserData(formData);
    } catch (error) {
      console.error("Error analyzing symptoms:", error);
      alert("There was a problem analyzing your symptoms. Please try again.");
    }
  };

  const handleReset = () => {
    setResults(null);
    setPlotBase64(null);
    setUserData(null);
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="bg-black bg-opacity-70 min-h-screen flex items-center justify-center p-6">
        <div className="relative z-10 w-full max-w-3xl">
          {!results ? (
            <SymptomsForm onSubmit={handleSubmit} />
          ) : (
            <ResultPage
              userData={userData}
              results={results}
              plotBase64={plotBase64}
              onReset={handleReset}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
