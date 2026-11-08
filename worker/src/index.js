const limit_seconds = 180;

export default {
	async scheduled(controller, env, ctx) {
		let state = "";
		console.log("cron processed");
		const url = "http://127.0.0.1:8000/lastcall";
		try {
			const response = await fetch(url, {method: "GET", signal: AbortSignal.timeout(5000)});
			if (!response.ok) {
				throw new Error("Failed to fetch lastcall :" + response.status);
			}
			const data = await response.json();
			if (data.status === "no_data") {
				state = data.status;
			} else if (data.status === "ok" && typeof data.last_call == "number") {
				if (data.last_call > limit_seconds) {
					state = "stale";
				} else {
					state = "ok";
				}
			} else {
				state = "unknown";
			}
		} catch (err) {
			state = "api_down";
			console.log("API Down :" + err)
		}
		console.log(state);
	},
	async fetch(request, env, ctx) {
		return new Response("Hello Nova!");
	},
};
