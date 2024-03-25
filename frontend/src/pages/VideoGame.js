import { useParams } from "react-router-dom";

const VideoGame = () => {
    const { videoGameId } = useParams();

    return (
        <p>
            Showing videoGame {videoGameId}
        </p>
    )
};

export default VideoGame;