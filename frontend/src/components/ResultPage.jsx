import React from "react";

const ResultPage = ({ userData, results, plotUrl, onReset }) => {
  return (
    <div className="bg-white bg-opacity-95 shadow-xl rounded-xl p-6 sm:p-8 space-y-6 text-gray-800">
      <h2 className="text-2xl sm:text-3xl font-bold text-orange-600 text-center">
        🩺 Analysis Results
      </h2>

      {/* User Details */}
      <div className="text-sm sm:text-base text-center space-y-1">
        <p>
          <strong>Name:</strong> {userData.name}
        </p>
        <p>
          <strong>Age:</strong> {userData.age}
        </p>
        <p>
          <strong>Gender:</strong> {userData.gender}
        </p>
        <p>
          <strong>Symptoms:</strong> {userData.symptoms.join(", ")}
        </p>
      </div>

      {/* Results List */}
      <div>
        <h3 className="text-lg font-semibold mb-2 text-black">
          Top Disease Matches:
        </h3>
        <ul className="list-disc list-inside space-y-1">
          {Object.entries(results).map(([disease, score]) => (
            <li key={disease} className="text-gray-700">
              <span className="font-medium">{disease}:</span>{" "}
              {Math.round(score * 100)}% match
            </li>
          ))}
        </ul>
      </div>

      {/* Plot Image */}
      {plotUrl && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold text-black mb-2">
            Visual Analysis:
          </h3>
          <img
            src={`http://127.0.0.1:5000${plotUrl}`}
            alt="Disease match chart"
            className="w-full max-h-[400px] object-contain rounded-lg shadow"
          />
        </div>
      )}

      {/* Reset Button */}
      <div className="text-center">
        <button
          onClick={onReset}
          className="mt-6 bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 transition"
        >
          🔁 New Analysis
        </button>
      </div>
    </div>
  );
};

export default ResultPage;
