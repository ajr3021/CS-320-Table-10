import './App.css';

import React, {useState, useEffect} from 'react';

function App() {
  const [data, setData] = useState([{}]);

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

  return (
    <div className="App">
      <p>The message is {data.message}</p>
    </div>
  );
}

export default App;
