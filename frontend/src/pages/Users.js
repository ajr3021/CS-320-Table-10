import { useState, useEffect } from 'react';

const Users = () => {

    const [users, setUsers] = useState([]);
    const [friends, setFriends] = useState([]);

    useEffect(() => {
        setUsers([
            {
                "username": "john",
                "email": "john@gmail.com",
            },
            {
                "username": "jane",
                "email": "jane@gmail.com",
            },
            {
                "username": "jack",
                "email": "jack@gmail.com",
            },
            {
                "username": "james",
                "email": "james@gmail.com",
            },
            {
                "username": "jeff",
                "email": "jeff@gmail.com",
            },
        ])
    }, [])

    useEffect(() => {
        setFriends([
        {
            "username": "john",
            "email": "john@gmail.com",
        },
        {
            "username": "jane",
            "email": "jane@gmail.com",
        },
        {
            "username": "jack",
            "email": "jack@gmail.com",
        },
        {
            "username": "james",
            "email": "james@gmail.com",
        },
        {
            "username": "jeff",
            "email": "jeff@gmail.com",
        },
    ])}, []);

    const displayUsers = () => {
        return(
            users.map((user) =>  {
                return(
                    <tr>
                        <td>{user.username}</td>
                        <td>{user.email}</td>
                        <td><button className='btn-primary' onClick={() => follow(user.username)}>Follow</button></td>
                    </tr>
                )
            })
        )
    }

    const displayFriends = () => {
        return(
            friends.map((user) =>  {
                return(
                    <tr>
                        <td>{user.username}</td>
                        <td>{user.email}</td>
                        <td><button className='btn-primary' onClick={() => unfollow(user.username)}>Unfollow</button></td>
                    </tr>
                )
            })
        )
    }

    const noResults = () => {
        return (
            <tr>
                <td>No Users Found</td>
                <td></td>
                <td></td>
            </tr>
            
        )
    }

    const follow = (username) => {
        const friend = users.find(user => user.username === username)
        const newFriends = [...friends, friend]

        setFriends(newFriends)

        const copy = [...users]
        const result = copy.filter(user => user.username !== username);
        setUsers(result);
    }

    const unfollow = (username) => {
        const copy = [...friends]
        const result = copy.filter(user => user.username !== username);
        setFriends(result);
    }

    const search = (e) => {
        e.preventDefault();
        const email = e.target.form[0].value;

        // make fetch request

        // update results
    }

    return (
        <div className='main-content'>
            <form action="" id="search">
                <input type="text" name="" id="" placeholder="Search by email..."/>
                <button className="btn-primary btn-wide" onClick={(e) => search(e)}>Search</button>
            </form>
            <div className="users">
                <h1>Search Results:</h1>
                <table>
                    <thead className='head'>
                        <tr>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Follow</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.length === 0 ? noResults() : displayUsers()}
                    </tbody>
                </table>
                <h1>Following:</h1>
                <table>
                    <thead className='head'>
                        <tr>
                            <th>Username</th>
                            <th>Email</th>
                            <th>UnFollow</th>
                        </tr>
                    </thead>
                    <tbody>
                        {friends.length === 0 ? noResults() : displayFriends()}
                    </tbody>
                </table>
            </div>
        </div>
    )
};

export default Users;