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

  useEffect(() => {
    const localData = localStorage.getItem('homeTop10')
    if(localData && localData !== '[]'){
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
    if(localData2 && localData2 !== '[]'){
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
    if(localData3 && localData3 !== '[]'){
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
    if(localData4 && localData4 !== '[]'){
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
    console.log(localData5)
    if(localData5 && localData5 !== '[]' && localData5 !== '{}'){
      const resultJson = JSON.parse(localData5);
      setDataGenre({
        "genre": resultJson
      })
    }else{
      console.log("FETCHING")
      fetch(`http://localhost:5050/api/videogame/recommended/genre`, {
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
          },

          method: 'GET',
      }).then(res => {
        console.log(res)
          return res.json();
      }).then(js => {
        console.log("GENRE")
        console.log(js)
          setDataGenre({
            "genre": js,
          });

          if(js.length !== 0){
            localStorage.setItem('homeRecGenre', JSON.stringify(js))
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
        <h1>Top Game by Genre: </h1>
        <VideoGamePreview games={dataGenre.genre} deleteGame={null}/>
      </div>
    </div>
  );
}

export default Home;
