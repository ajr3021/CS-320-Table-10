import './App.css';

import React, {useState, useEffect} from 'react';

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5050/message", {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    }).then(res => {
      console.log(res);
      return res.json()
    }).then(data => {
        console.log(data);
        setData(data);
    })
  }, [])

  const deleteElement = (id) => {
    const copy = [...data]
    const result = copy.filter(collection => collection[0] !== id);
    setData(result);

    fetch(`http://localhost:5050/api/collection/${id}`, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      method: 'DELETE',
    })
  }

  return (
    <div className="App">
      {data.length > 0 && data.map(collection => {
        return(
          <div key={collection[0]} className="collection">
            <p>{collection[0]} {collection[1]}</p>
            <button id="delete" onClick={() => deleteElement(collection[0])}>Delete</button>
          </div>
        )
      })}
    </div>
  );
}

export default App;
