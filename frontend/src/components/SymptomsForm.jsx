import React, { useState } from "react";
import { allSymptoms } from "../services/Service";
import axios from "axios";

const SymptomsForm = ({ onSubmit }) => {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [query, setQuery] = useState("");
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);

  const filteredSymptoms = allSymptoms.filter(
    (symptom) =>
      symptom.toLowerCase().includes(query.toLowerCase()) &&
      !selectedSymptoms.includes(symptom)
  );

  const handleAddSymptom = (symptom) => {
    setSelectedSymptoms([...selectedSymptoms, symptom]);
    setQuery("");
  };

  const handleRemoveSymptom = (symptom) => {
    setSelectedSymptoms(selectedSymptoms.filter((s) => s !== symptom));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !age || !gender || selectedSymptoms.length === 0) {
      alert("Please fill all the fields.");
      return;
    }
    const data = {
      name,
      age,
      gender,
      symptoms: selectedSymptoms,
    };
    onSubmit(data); // pass to parent component
    try {
      const response = await axios.post(
        "https://disease-symptoms-analyzer-backend-ba0u.onrender.com/analyze",
        data
      );
      console.log("Result", response.data);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-10 p-6 md:p-10 bg-black text-white rounded-2xl shadow-2xl">
      <h2 className="text-3xl font-extrabold text-orange-500 mb-6 text-center">
        🩺 Disease Analyzer from Symptoms
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Name */}
        <div>
          <label className="block mb-1 font-semibold text-orange-400">
            Name:
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-orange-300 focus:outline-none focus:ring-2 focus:ring-orange-500 text-black"
            placeholder="Enter your name"
          />
        </div>

        {/* Age */}
        <div>
          <label className="block mb-1 font-semibold text-orange-400">
            Age:
          </label>
          <input
            type="number"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-orange-300 focus:outline-none focus:ring-2 focus:ring-orange-500 text-black"
            placeholder="Enter your age"
          />
        </div>

        {/* Gender */}
        <div>
          <label className="block mb-1 font-semibold text-orange-400">
            Gender:
          </label>
          <div className="flex flex-wrap gap-6">
            {["male", "female", "other"].map((opt) => (
              <label
                key={opt}
                className="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="radio"
                  name="gender"
                  value={opt}
                  onChange={(e) => setGender(e.target.value)}
                  className="accent-orange-500"
                />
                <span className="capitalize">{opt}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Symptom Search */}
        <div>
          <label className="block mb-1 font-semibold text-orange-400">
            Search Symptoms:
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-orange-300 focus:outline-none focus:ring-2 focus:ring-orange-500 text-black"
            placeholder="Type to search symptoms..."
          />

          {query && filteredSymptoms.length > 0 && (
            <ul className="mt-2 max-h-40 overflow-y-auto bg-white text-black border border-orange-300 rounded-lg shadow-inner">
              {filteredSymptoms.map((symptom) => (
                <li
                  key={symptom}
                  onClick={() => handleAddSymptom(symptom)}
                  className="px-4 py-2 hover:bg-orange-100 cursor-pointer"
                >
                  {symptom}
                </li>
              ))}
            </ul>
          )}

          {selectedSymptoms.length > 0 && (
            <div className="mt-4">
              <p className="font-semibold mb-2 text-orange-400">
                Selected Symptoms:
              </p>
              <div className="flex flex-wrap gap-2">
                {selectedSymptoms.map((symptom) => (
                  <span
                    key={symptom}
                    className="bg-orange-300 text-black px-3 py-1 rounded-full text-sm cursor-pointer hover:bg-orange-400"
                    onClick={() => handleRemoveSymptom(symptom)}
                  >
                    {symptom} ✕
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="text-center pt-4">
          <button
            type="submit"
            onClick={handleSubmit}
            className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-xl text-lg font-semibold transition-all duration-200"
          >
            🔍 Analyze
          </button>
        </div>
      </form>
    </div>
  );
};

export default SymptomsForm;
