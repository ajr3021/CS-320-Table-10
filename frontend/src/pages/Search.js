import VideoGamePreview from "../components/VideoGamePreview";
import "../css/Search.css"
import { useState, useEffect } from 'react';

const Search = () => {
    
    const [text, setText] = useState("Ascending")
    const [searchBy, setSearchBy] = useState("Search By")
    const [sortBy, setSortBy] = useState("Sort By")

    const [games, setGames] = useState([])

    useEffect(() => {
      setGames([
        {
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
        },
        {
            "vid": "3",
            "title": "Team Fortress",
            "esrb_rating": "T",
            "rating": 4.5,
            "banner": "https://steamcdn-a.akamaihd.net/steam/apps/20/header.jpg?t=1528732825",
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
            "description": `One of the most popular online action games of all time, Team Fortress Classic features over nine character classes -- from Medic to Spy to Demolition Man -- enlisted in a unique style of online team warfare. Each character class possesses unique weapons, items, and abilities, as teams compete online in a variety of game play modes.`,
          },
          {
            "vid": "4",
            "title": "Day of Defeat",
            "esrb_rating": "T",
            "banner": "https://steamcdn-a.akamaihd.net/steam/apps/30/header.jpg?t=1512413490",
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
            "description": `Enlist in an intense brand of Axis vs. Allied teamplay set in the WWII European Theatre of Operations. Players assume the role of light/assault/heavy infantry, sniper or machine-gunner class, each with a unique arsenal of historical weaponry at their disposal. Missions are based on key historical operations.`
          },
          {
            "vid": "5",
            "title": "Death Match Classic",
            "banner": "https://steamcdn-a.akamaihd.net/steam/apps/40/header.jpg?t=1528733362",
            "esrb_rating": "T",
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
            "description": `Return to the Black Mesa Research Facility as one of the military specialists assigned to eliminate Gordon Freeman. Experience an entirely new episode of single player action. Meet fierce alien opponents, and experiment with new weaponry. Named 'Game of the Year' by the Academy of Interactive Arts and Sciences.`
          },
          {
            "vid": "6",
            "title": "Half-Life",
            "esrb_rating": "T",
            "banner": "https://steamcdn-a.akamaihd.net/steam/apps/50/header.jpg?t=1542245736",
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
            "description": `A futuristic action game that challenges your agility as well as your aim, Ricochet features one-on-one and team matches played in a variety of futuristic battle arenas.`
          },
          {
            "vid": "7",
            "title": "Richochet",
            "banner": "https://steamcdn-a.akamaihd.net/steam/apps/60/header.jpg?t=1528733092",
            "esrb_rating": "T",
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
            "description": `Named Game of the Year by over 50 publications, Valve's debut title blends action and adventure with award-winning technology to create a frighteningly realistic world where players must think to survive. Also includes an exciting multiplayer mode that allows you to play against friends and enemies around the world.`,
          }
      ])
    }, [])

    const changeText = (e) => {
        e.preventDefault();
        if(text === "Ascending"){
            setText("Descending")
        }else{
            setText("Ascending")
        }
    }

    const search = (e) => {
      e.preventDefault();

      console.log(e.target.form[0].value)
      console.log(text)
      console.log(searchBy)
      console.log(sortBy);

      // set request

      // update results
    }

    const deleteGame = (vid) => {
      const copy = [...games]
      const results = copy.filter(game => game.vid !== vid);

      setGames(results)
    }

    return (
        <div className="main-content">
            <form action="" id="search">
                <input type="text" name="" id="" placeholder="Search for a Game..."/>
                <div className="dropdown">
                    <button className="btn-drop btn-secondary btn-wide">{searchBy}</button>
                    <div className="dropdown-content">
                        <div onClick={() => setSearchBy("Name")}>Name</div>
                        <div onClick={() => setSearchBy("Platform")}>Platform</div>
                        <div onClick={() => setSearchBy("Release Date")}>Release Date</div>
                        <div onClick={() => setSearchBy("Developer")}>Developer</div>
                        <div onClick={() => setSearchBy("Price")}>Price</div>
                        <div onClick={() => setSearchBy("Genre")}>Genre</div>
                    </div>
                </div>
                <div className="dropdown">
                    <button className="btn-drop btn-secondary btn-wide">{sortBy}</button>
                    <div className="dropdown-content">
                        <div onClick={() => setSortBy("Name")}>Name</div>
                        <div onClick={() => setSortBy("Price")}>Price</div>
                        <div onClick={() => setSortBy("Genre")}>Genre</div>
                        <div onClick={() => setSortBy("Release Year")}>Release Year</div>
                    </div>
                </div>
                <button className="btn-secondary btn-wide" onClick={(e) => changeText(e)}>{text}</button>
                <button className="btn-primary btn-wide" onClick={(e) => search(e)}>Search</button>
            </form>

        <VideoGamePreview games={games} deleteGame={deleteGame}/>
        </div>
        
    )
};

export default Search;