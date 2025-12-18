function getSchedules(id, day) {
    fetch("/api/get-schedules", {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "day": day,
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        console.log(data)
    });
}


