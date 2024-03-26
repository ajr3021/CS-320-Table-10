import React, {useState, useEffect} from 'react';
import { Link, useNavigate } from 'react-router-dom'

const Home = () => {
  const [data, setData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    setData([
      {
        "cid": 0,
        "name": "Collection 1",
        "numGames": 3,
        "totalTimePlayed": "4:56"
      },
      {
        "cid": 1,
        "name": "Collection 2",
        "numGames": 33,
        "totalTimePlayed": "14:56"
      },
      {
        "cid": 2,
        "name": "Classics",
        "numGames": 5,
        "totalTimePlayed": "46:56"
      },
      {
        "cid": 3,
        "name": "New",
        "numGames": 1,
        "totalTimePlayed": "0:56"
      },
      {
        "cid": 4,
        "name": "Adventure Games",
        "numGames": 3,
        "totalTimePlayed": "6:06"
      }
    ])
  }, [])

  const deleteElement = (id) => {
    const copy = [...data]
    const result = copy.filter(collection => collection.cid !== id);
    setData(result);

    fetch(`http://localhost:5050/api/collection/${id}`, {
      method: 'DELETE',
    })
  }

  const noColletions = () => {
    return (
      <tr>
        <td>No Collections to Display</td>
      </tr>
    )
  }

  const redirectToCollection = (cid) => {
    navigate("/collection/" + cid);
  } 

  const hasCollections = () => {
    return (
      data.map(collection => {
        return(
          <tr key={collection.cid} onClick={() => redirectToCollection(collection.cid)}>
            <td><Link to={"/collection/" + collection.cid}>{collection.name}</Link></td>
            <td>{collection.numGames}</td>
            <td>{collection.totalTimePlayed}</td>
            <td> <button className="btn-danger" id="delete" onClick={() => deleteElement(collection.cid)}>Delete</button></td>
          </tr>
        )
      })
    )
  }

  return (
    <div id='collections-container'className='container'>
      <table>
        <thead>
          <tr className='head'>
            <th>Name</th>
            <th>Number of Games</th>
            <th>Total Time Played</th>
            <th>Delete</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? noColletions(): hasCollections()}
        </tbody>
      
      </table>
    </div>
  );
}

export default Home;
