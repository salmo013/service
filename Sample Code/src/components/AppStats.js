import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://nginx/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);
    console.log(stats)
    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Motion</th>
							<th>Door Motion</th>
						</tr>
						<tr>
							<td># E1: {stats['Total of event 1']}</td>
							<td># E2: {stats['Total of event 2']}</td>
						</tr>
						<tr>
							<td colspan="2">How many couch sits: {stats['Couch sits']}</td>
						</tr>
						<tr>
							<td colspan="2">How many doors are open: {stats['Doors open']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['Last_update']}</h3>

            </div>
        )
    }
}
