export default {
	async scheduled(controller, env, ctx) {
		let state = "";
		const states = ["no_data", "stale", "ok"];
		console.log("cron processed");
		const url = "http://127.0.0.1:8000/lastcall";
		try {
			const response = await fetch(url, {method: "GET", signal: AbortSignal.timeout(5000)});
			if (!response.ok) {
				throw new Error("Failed to fetch lastcall :" + response.status);
			}
			const data = await response.json();
			if (!(data.status in states)) {
				state = "unknown";
			} else {
				state = data.status;
			}

		} catch (err) {
			state = "api_down";
			console.error(`API Down : ${err}`);
		}
		console.log(state);
		let message = {
			"content": state
		};
		try {
			const webhook_response = await fetch(env.WEBHOOK_URL, {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify(message)
			});

			if (!webhook_response.ok) {
				throw new Error(`Discord webhook error: ${webhook_response.status} ${webhook_response.statusText}`);
			}
		} catch (err) {
			console.error(err);
		}

	}
	,
	async fetch(request, env, ctx) {
		return new Response("Hello Nova!");
	}
	,
}
;
