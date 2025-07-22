import SymptomsForm from "./components/SymptomsForm";
import bgImage from "./assets/medical.jpg";

function App() {
  const handleSubmit = (formData) => {
    console.log("Form Data : ", formData);
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-no-repeat flex items-center justify-center px-4 py-10"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="relative z-10 w-full max-w-3xl">
        <SymptomsForm onsubmit={handleSubmit} />
      </div>
    </div>
  );
}

export default App;