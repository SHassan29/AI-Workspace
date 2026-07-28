import { useEffect, useState } from "react";


function Tasks() {

    const [tasks, setTasks] = useState([]);


    useEffect(() => {

        fetch("http://127.0.0.1:8000/tasks")
            .then(response => response.json())
            .then(data => {
                setTasks(data);
            });

    }, []);


    return (
        <div>

            <h2>Tasks</h2>

            <ul>

                {tasks.map(task => (
                    <li key={task.id}>
                        {task.title}
                    </li>
                ))}

            </ul>

        </div>
    );

}


export default Tasks;