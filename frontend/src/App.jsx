import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DetailsPage from './pages/DetailsPage'

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/details" element={<DetailsPage />} />
      </Routes>
    </Router>
  )
}

export default App

