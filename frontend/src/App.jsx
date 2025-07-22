import SymptomsForm from "./components/SymptomsForm";
import ResultPage from "./components/ResultPage";
import bgImage from "./assets/medical.jpg";
import axios from "axios";
import { useState } from "react";

function App() {
  const [results, setResults] = useState(null);
  const [plotUrl, setPlotUrl] = useState(null);
  const [userData, setUserData] = useState(null);

  const handleSubmit = async (formData) => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/analyze", {
        symptoms: formData.symptoms,
      });
      setResults(res.data.results);
      setPlotUrl(res.data.plotUrl);
      setUserData(formData);
    } catch (error) {
      console.error("Error analyzing symptoms:", error);
      alert("There was a problem analyzing your symptoms. Please try again.");
    }
  };

  const handleReset = () => {
    setResults(null);
    setPlotUrl(null);
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
              plotUrl={plotUrl}
              onReset={handleReset}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
