import React, { useState } from "react";
import _ from "lodash";
import axios from "axios";

const ResultPage = ({ userData, results, plotUrl, onReset }) => {
  const [advice, setAdvice] = useState({});
  const [loadingAdvice, setLoadingAdvice] = useState(false);

  const generateAdvice = async () => {
    setLoadingAdvice(true);
    try {
      const response = await axios.post(
        "https://disease-symptoms-analyzer-backend-ba0u.onrender.com/generate_advice",
        {
          diseases: Object.keys(results),
        }
      );

      let rawAdvice = response.data.advice;
      //console.log("Result Object:", rawAdvice);

      if (typeof rawAdvice === "object" && rawAdvice.raw) {
        rawAdvice = rawAdvice.raw;
      }

      rawAdvice = rawAdvice
        .replace(/^```json\s*/i, "")
        .replace(/```$/, "")
        .trim();

      // Attempt to parse the response (fix common format issues)
      const parsed = JSON.parse(rawAdvice); // parse as JSON
      setAdvice(parsed);
    } catch (error) {
      console.error("Error generating advice:", error);
      alert("❌ Failed to generate AI advice. Please try again.");
    } finally {
      setLoadingAdvice(false);
    }
  };

  return (
    <div className="bg-black text-white rounded-2xl shadow-2xl p-4 sm:p-6 md:p-10 max-w-5xl mx-auto mt-6 md:mt-10 w-full">
      <h2 className="text-2xl sm:text-3xl font-extrabold text-orange-500 mb-4 sm:mb-6 text-center">
        🩺 Analysis Results
      </h2>

      {/* User Details */}
      <div className="text-sm sm:text-base text-orange-200 text-center space-y-1 mb-4 sm:mb-6">
        <p>
          <span className="font-semibold text-orange-400">Name:</span>{" "}
          {_.capitalize(userData.name)}
        </p>
        <p>
          <span className="font-semibold text-orange-400">Age:</span>{" "}
          {_.capitalize(userData.age)}
        </p>
        <p>
          <span className="font-semibold text-orange-400">Gender:</span>{" "}
          {_.capitalize(userData.gender)}
        </p>
        <p>
          <span className="font-semibold text-orange-400">Symptoms:</span>{" "}
          {_.capitalize(userData.symptoms.join(", "))}
        </p>
      </div>

      {/* Results List */}
      <div className="mb-6 px-2 sm:px-4">
        <h3 className="text-lg sm:text-xl font-semibold text-orange-400 mb-3">
          Top Disease Matches:
        </h3>
        <ul className="space-y-2 list-inside">
          {Object.entries(results).map(([disease, score]) => (
            <li key={disease} className="text-orange-200 text-sm sm:text-base">
              <span className="font-medium text-orange-300">{disease}:</span>{" "}
              {Math.round(score * 100)}% match
            </li>
          ))}
        </ul>
      </div>

      {/* Plot Image */}
      {plotUrl && (
        <div className="mb-8 px-2 sm:px-4">
          <h3 className="text-lg sm:text-xl font-semibold text-orange-400 mb-3">
            Visual Analysis:
          </h3>
          <div className="flex justify-center items-center">
            <img
              src={plotUrl}
              alt="Disease match chart"
              className="w-full max-w-3xl h-auto max-h-[400px] object-contain rounded-lg shadow-lg border border-orange-300"
            />
          </div>
        </div>
      )}

      {/* AI Advice Button */}
      <div className="text-center mb-6">
        <button
          onClick={generateAdvice}
          disabled={loadingAdvice}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl text-base sm:text-lg font-semibold transition-all duration-200 disabled:opacity-50"
        >
          🧠 {loadingAdvice ? "Generating..." : "Generate AI Advice"}
        </button>
      </div>

      {/* AI Advice Display */}
      {Object.keys(advice).length > 0 && (
        <div className="bg-gray-900 border border-orange-300 rounded-xl p-4 sm:p-6 mb-6 space-y-4">
          <h3 className="text-lg sm:text-xl font-semibold text-orange-400 mb-2">
            🧠 AI-Driven Solutions & Precautions:
          </h3>
          {Object.entries(advice).map(([disease, info]) => (
            <div key={disease} className="text-sm sm:text-base text-orange-200">
              <p className="font-semibold text-orange-300">{disease}</p>
              <p>
                <span className="text-orange-400">Precautions:</span>{" "}
                {info.precautions || "N/A"}
              </p>
              <p>
                <span className="text-orange-400">Solutions:</span>{" "}
                {info.solution || "N/A"}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Reset Button */}
      <div className="text-center">
        <button
          onClick={onReset}
          className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-xl text-base sm:text-lg font-semibold transition-all duration-200"
        >
          🔁 New Analysis
        </button>
      </div>
    </div>
  );
};

export default ResultPage;
