import React, {useEffect, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import '../css/Home.css';
import VideoGamePreview from "../components/VideoGamePreview";

const Home = () => {

  const navigate = useNavigate();

  const [data, setData] = useState({"top10": []});
  const [data90, setData90] = useState({"top90": []})
  const [data20, setData20] = useState({"top20": []})
  const [data5, setData5] = useState({"top5": []})
  const [dataGenre, setDataGenre] = useState({"genre": []})
  const [dataDev, setDataDev] = useState({"dev": []})
  const [dataPlatform, setDataPlatform] = useState({"platform": []})
  const [dataRating, setDataRating] = useState({"rating": []})

  useEffect(() => {
    const localData = localStorage.getItem('homeTop10')
    if(localData && localData !== '[]' && localData !== '{}'){
      const resultJson = JSON.parse(localData);
      setData({
        "top10": resultJson
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

    const localData2 = localStorage.getItem('homeTop90')
    if(localData2 && localData2 !== '[]' && localData2 !== '{}'){
      const resultJson = JSON.parse(localData2);
      setData90({
        "top90": resultJson
      })
    }else{
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

          if(js.length !== 0){
            localStorage.setItem('homeTop90', JSON.stringify(js))
          }
      })
    }

    const localData3 = localStorage.getItem('homeTop20')
    if(localData3 && localData3 !== '[]' && localData3 !== '{}'){
      const resultJson = JSON.parse(localData3);
      setData20({
        "top20": resultJson
      })
    }else{
      fetch(`http://localhost:5050/api/videogame/friends/1/top20`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
          return res.json();
      }).then(js => {
          setData20({
            "top20": js,
          });

          if(js.length !== 0){
            localStorage.setItem('homeTop20', JSON.stringify(js))
          }
      })
    }

    const localData4 = localStorage.getItem('homeTop5')
    if(localData4 && localData4 !== '[]' && localData4 !== '{}'){
      const resultJson = JSON.parse(localData4);
      setData5({
        "top5": resultJson
      })
    }else{
      fetch(`http://localhost:5050/api/videogame/rating/top5`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
          return res.json();
      }).then(js => {
          setData5({
            "top5": js,
          });

          if(js.length !== 0){
            localStorage.setItem('homeTop20', JSON.stringify(js))
          }
      })
    }

    const localData5 = localStorage.getItem('homeRecGenre')
    if(localData5 && localData5 !== '[]' && localData5 !== '{}'){
      const resultJson = JSON.parse(localData5);
      const result = resultJson.slice(0, 3);
      setDataGenre({
        "genre": result
      })
    }else{
      fetch(`http://localhost:5050/api/videogame/recommended/genre`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
          return res.json();
      }).then(js => {
          const result = js

          setDataGenre({
            "genre": result,
          });

          if(js.length !== 0){
            localStorage.setItem('homeRecGenre', JSON.stringify(result))
          }
      })
    }

    const localData6 = localStorage.getItem('homeRecDev')
    if(localData6 && localData6 !== '[]' && localData6 !== '{}'){
      const resultJson = JSON.parse(localData6);
      const result = resultJson.slice(0, 3);
      setDataDev({
        "dev": result
      })
    }else{
      fetch(`http://localhost:5050/api/videogame/recommended/developer`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
          return res.json();
      }).then(js => {
          const result = js

          setDataDev({
            "dev": result,
          });

          if(js.length !== 0){
            localStorage.setItem('homeRecDev', JSON.stringify(result))
          }
      })
    }

    const localData7 = localStorage.getItem('homeRecPlatform')
    if(localData7 && localData7 !== '[]' && localData7 !== '{}'){
      const resultJson = JSON.parse(localData7);
      const result = resultJson.slice(0, 3);
      setDataPlatform({
        "platform": result
      })
    }else{
      fetch(`http://localhost:5050/api/videogame/recommended/platform`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
          return res.json();
      }).then(js => {
          const result = js

          setDataPlatform({
            "platform": result,
          });

          if(js.length !== 0){
            localStorage.setItem('homeRecPlatform', JSON.stringify(result))
          }
      })
    }

    const localData8 = localStorage.getItem('homeRecRating')
    if(localData8 && localData8 !== '[]' && localData8 !== '{}'){
      const resultJson = JSON.parse(localData8);
      const result = resultJson.slice(0, 3);
      setDataRating({
        "rating": result
      })
    }else{
      fetch(`http://localhost:5050/api/videogame/recommended/ratings`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
          return res.json();
      }).then(js => {
          const result = js

          setDataRating({
            "rating": result,
          });

          if(js.length !== 0){
            localStorage.setItem('homeRecRating', JSON.stringify(result))
          }
      })
    }

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
      <div className="top20">
        <h1>Top 20 Games by Followers: </h1>
        <VideoGamePreview games={data20.top20} deleteGame={null}/>
      </div>
      <div className="top5">
        <h1>Top 5 Games This Month: </h1>
        <VideoGamePreview games={data5.top5} deleteGame={null}/>
      </div>
      <div className="genre">
        <h1>Recommended Games by Genre: </h1>
        <VideoGamePreview games={dataGenre.genre} deleteGame={null}/>
      </div>
      <div className="dev">
        <h1>Recommended Games by Developer: </h1>
        <VideoGamePreview games={dataDev.dev} deleteGame={null}/>
      </div>
      <div className="platform">
        <h1>Recommended Games by Platform: </h1>
        <VideoGamePreview games={dataPlatform.platform} deleteGame={null}/>
      </div>
      <div className="rating">
        <h1>Recommended Games by Rating: </h1>
        <VideoGamePreview games={dataRating.rating} deleteGame={null}/>
      </div>
    </div>
  );
}

export default Home;
