import { useParams } from "react-router-dom";
import { useState, useEffect } from 'react';
import '../css/VideoGame.css'
import VideoGamePreview from "../components/VideoGamePreview";

const VideoGame = () => {
    const { videoGameId } = useParams();

    const [data, setData] = useState({});

    const [collections, setCollections] = useState([]);

    let timePlayedInSeconds = 0;

    let checkedCollectionIds = new Set();

    useEffect(() => {
        setData({
            "vid": "2",
            "title": "Counter Strike",
            "esrb_rating": "T",
            "banner": "https://steamcdn-a.akamaihd.net/steam/apps/10/header.jpg?t=1528733245",
            "rating": 4.5,
            "gameplay": 100.7,
            "genres": [
              "Action",
              "Horror"
            ],
            "platforms": [
              "Windows",
              "Xbox 360"
            ],
            "developers": [
              "Windows",
              "Xbox 360"
            ],
            "price": 40,
            "description": "Play the world's number 1 online action game. Engage in an incredibly realistic brand of terrorist warfare in this wildly popular team-based game. Ally with teammates to complete strategic missions. Take out enemy sites. Rescue hostages. Your role affects your team's success. Your team's success affects your role.",
          })
    }, [])

    useEffect(() => {
        setCollections([
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
              "cid": 12,
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

    const displayTime = () => {
        let minutes = Math.floor(timePlayedInSeconds / 60).toString();
        let seconds = (timePlayedInSeconds % 60).toString();

        if(minutes.length === 1){
            minutes = minutes.padStart(2, '0')
        }

        if(seconds.length === 1){
            seconds = seconds.padStart(2, '0')
        }

        return minutes + ":" + seconds
    }

    const play = (e) => {
        e.preventDefault();
       
        console.log(e.target.form[0].value);
        console.log(e.target.form[1].value);
    }

    const rate = (e) => {
        e.preventDefault();

        console.log(e.target.form[0].value);
    }

    const addToCollection = (e) => {
        e.preventDefault();
        console.log(checkedCollectionIds);
    }

    const updateMap = (id) => {
        if(checkedCollectionIds.has(id)){
            checkedCollectionIds.delete(id);
        }else{
            checkedCollectionIds.add(id);
        }
    }

    return (
        <div>
            <div className="full-game-display">
                <div className="full-banner">
                    <img src={data.banner} alt="" />
                </div>
                <div className="padded">
                    <div className="header">
                        <h1>{data.title}</h1>
                        <p>Price: ${data.price}</p>
                    </div>
                    <div className="desc">
                        <h1>Description:</h1>
                        <p>{data.description}</p>
                    </div>
                    <div className="info">
                        <div className="ratings">
                            <h1>Ratings:</h1>
                            <ul>
                                <li>ESRB: {data.esrb_rating}</li>
                                <li>Quality Rating: {data.rating}</li>
                            </ul>
                        </div>
                        <div className="genres">
                            <h1>Genres:</h1>
                            <ul>
                                {data.genres && data.genres.map((genre) => {
                                    return(
                                        <li key={genre}>{genre}</li>
                                    )
                                } )}
                            </ul>
                        </div>
                        <div className="platforms">
                            <h1>Platforms:</h1>
                            <ul>
                                {data.platforms && data.platforms.map((platform) => {
                                    return(
                                        <li key={platform}>{platform}</li>
                                    )
                                } )}
                            </ul>
                        </div>
                        <div className="developers">
                            <h1>Developers:</h1>
                            <ul>
                                {data.developers && data.developers.map((developer) => {
                                    return(
                                        <li key={developer}>{developer}</li>
                                    )
                                } )}
                            </ul>
                        </div>
                    </div>
                    <div className="forms">
                            <div className="bottom-forms">
                                    <form action="">
                                        <h1>Play Game:</h1>
                                        <div className="time-form">
                                            <div className="not-button">
                                            <div><label htmlFor="start">Start Time</label>
                                            <input type="time" id="start"/></div>
                                            
                                            <div>
                                            <label htmlFor="stop">End Time</label>
                                            <input type="time" id="stop"/>
                                            </div>
                                            </div>
                                        </div>
                                        <button className="btn-primary" onClick={(e) => play(e)}>Submit Time</button>
                                    </form>
                                
                            
                            </div>
                            <div id="collections-form" className="bottom-forms">
                                <form action="">
                                    <h1>Add Game to Collection(s)</h1>
                                    <div className="collection-checkboxes">
                                        {
                                            collections && collections.map((collection) => {
                                                return (
                                                    <div className="collection-checkbox" key={collection.cid}>
                                                        <input type="checkbox" name={collection.cid} id={collection.cid} onChange={() => updateMap(collection.cid)}/>
                                                        <label htmlFor={collection.cid}>{collection.name}</label>
                                                    </div>   
                                                )
                                            })
                                        }
                                    </div>        
                                    <button type="submit" className="btn-primary" onClick={(e) => addToCollection(e)}>Add</button>
                                </form>
                            </div>

                            <div className="game-form">
                                <h1>Rate Game:</h1>
                                <form action="">
                                    <input type="number" name="" id="rateGame" min={1} max={5} placeholder={1}/>
                                    <button className="btn-primary" onClick={(e) => rate(e)}>Rate</button>
                                </form>
                            </div>
                        </div>
                </div>
            </div>
        </div>
    )
};

export default VideoGame;