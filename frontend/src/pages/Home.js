import React, {useEffect, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import '../css/Home.css';
import VideoGamePreview from "../components/VideoGamePreview";

const Home = () => {

  const navigate = useNavigate();

  const [data, setData] = useState({"top10": []});
  const [data90, setData90] = useState({"top90": []})

  useEffect(() => {
    const localData = localStorage.getItem('homeTop10')
    if(localData && localData !== '[]'){
      const resultJson = JSON.parse(localData);
      setData({
        "top10": resultJson,
        "top90": data.top90
      })
    }else{
      fetch(`http://localhost:5050/api/videogame/1/topTenGamesByRating`, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },

            method: 'GET',
        }).then(res => {
            return res.json();
        }).then(js => {

            setData({
              "top10": js
            });
            if(js.length !== 0){
              localStorage.setItem('homeTop10', JSON.stringify(js))
            }
      })
    }

    fetch(`http://localhost:5050/api/videogame/popular/90`, {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },

        method: 'GET',
    }).then(res => {
        return res.json();
    }).then(js => {
        setData90({
          "top90": js,
        });
    })
  }, [])

  return (
    <div className='home'>
      <div className="top10">
        <h1>Top 10 Games by Rating: </h1>
        <VideoGamePreview games={data.top10} deleteGame={null}/>
      </div>
      <div className="top90">
        <h1>Top 20 Games in the Last 90 Days: </h1>
        <VideoGamePreview games={data90.top90} deleteGame={null}/>
      </div>
    </div>
  );
}

export default Home;
