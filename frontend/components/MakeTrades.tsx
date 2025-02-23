export default function MakeTrades() {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Execute Trade</h2>
      {/* Add a form for making trades here */}
      <form>
        <div className="mb-4">
          <label htmlFor="symbol" className="block mb-2">
            Symbol
          </label>
          <input type="text" id="symbol" className="border p-2 w-full" />
        </div>
        <div className="mb-4">
          <label htmlFor="quantity" className="block mb-2">
            Quantity
          </label>
          <input type="number" id="quantity" className="border p-2 w-full" />
        </div>
        <div className="mb-4">
          <label htmlFor="action" className="block mb-2">
            Action
          </label>
          <select id="action" className="border p-2 w-full">
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
        </div>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Execute Trade
        </button>
      </form>
    </div>
  )
}

