import { useParams } from "react-router-dom";

const Collection = () => {
    const { collectionId } = useParams();

    return (
        <p>
            Showing collection {collectionId}
        </p>
    )
};

export default Collection;