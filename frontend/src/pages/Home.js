import React, {useEffect, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import '../css/Home.css';
import VideoGamePreview from "../components/VideoGamePreview";

const Home = () => {

  const navigate = useNavigate();

  const [data, setData] = useState({});

  useEffect(() => {
    fetch(`http://localhost:5050/api/videogame/1/topTenGamesByRating`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
          return res.json();
      }).then(data => {

          setData({
            "top10": data
          });
          console.log("TOP 10")
          console.log(data.top10)
      })
  }, [])

  return (
    <div className='home'>
      <div className="top10">
        <h1>Top 10 Games by Rating: </h1>
        <VideoGamePreview games={data.top10} deleteGame={null}/>
      </div>
    </div>
  );
}

export default Home;
