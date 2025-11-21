const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-sky-400"></div>
      <p className="text-white text-lg">Loading resort data...</p>
    </div>
  )
}

export default LoadingSpinner

