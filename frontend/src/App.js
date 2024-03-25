import './App.css';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from './Layout'
import Home from './pages/Home';
import Collection from './pages/Collection';
import Users from './pages/Users';
import VideoGame from './pages/VideoGame';
import Search from './pages/Search';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Layout />}>
          <Route index element={<Home />}></Route>
          <Route path='/collection/:collectionId' element={<Collection />}></Route>
          <Route path='/videoGame/:videoGameId' element={<VideoGame />}></Route>
          <Route path='/users' element={<Users />}></Route>
          <Route path='/search' element={<Search />}></Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App;
